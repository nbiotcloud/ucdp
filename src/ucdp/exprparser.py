#
# MIT License
#
# Copyright (c) 2024 nbiotcloud
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
"""
Expression ExprParser.
"""

import re
from typing import Any

from icdutil.num import calc_signed_width, unsigned_to_signed

from .consts import RE_IDENTIFIER
from .exceptions import InvalidExpr
from .expr import (
    BoolOp,
    ConcatExpr,
    ConstExpr,
    Expr,
    Log2Expr,
    MaximumExpr,
    MinimumExpr,
    Op,
    SliceOp,
    SOp,
    TernaryExpr,
)
from .namespace import Namespace
from .note import Note
from .object import Object, computed_field
from .typebase import BaseType
from .typeenum import BaseEnumType
from .typescalar import BitType, BoolType, SintType, UintType

_RE_CONST = re.compile(
    r"(?P<sign>[-+])?"
    r"(((?P<width>\d+)'?(?P<is_signed>s)?(?P<bnum>(b[01]+)|(o[0-7]+)|(d[0-9]+)|(h[0-9a-fA-F]+))))|(?P<num>\d+)\b"
)
_NUM_BASEMAP = {
    "b": 2,
    "o": 8,
    "d": 10,
    "h": 16,
    None: 10,
}
Parseable = Expr | str | int | BaseType | list | tuple
Constable = int | str | ConstExpr
Concatable = list | tuple | ConcatExpr


class _Globals(dict):
    def __init__(self, globals: dict, namespace: Namespace | None, strict: bool):
        super().__init__(globals)
        self.namespace = namespace
        self.strict = strict

    def __missing__(self, key):
        if self.namespace:
            if self.strict:
                try:
                    return self.namespace.get_dym(key)
                except ValueError as err:
                    raise NameError(err) from None
            try:
                return self.namespace[key]
            except ValueError:
                pass
        if self.strict:
            raise KeyError(key)
        return key


class ExprParser(Object):
    """
    ExprParser.

    Keyword Args:
        namespace (Namespace): Symbol namespace
        strict: Do not ignore missing symbols.

    """

    namespace: Namespace | None = None
    strict: bool = True

    @computed_field
    def _globals(self) -> _Globals:
        globals_ = {
            # Expressions
            "Op": Op,
            "SOp": SOp,
            "BoolOp": BoolOp,
            "SliceOp": SliceOp,
            "ConstExpr": ConstExpr,
            "ConcatExpr": ConcatExpr,
            "TernaryExpr": TernaryExpr,
            "Log2Expr": Log2Expr,
            "MinimumExpr": MinimumExpr,
            "MaximumExpr": MaximumExpr,
            # Helper
            "const": self.const,
            "concat": self.concat,
            "ternary": self.ternary,
            "log2": self.log2,
            "minimum": self.minimum,
            "maximum": self.maximum,
        }
        return _Globals(globals=globals_, namespace=self.namespace, strict=self.strict)

    def parse_note(self, expr: Parseable | Note, only=None, types=None) -> Expr | Note:
        """
        Parse Expression or Note.

        Args:
            expr: Expression

        Keyword Args:
            only: Limit expression to these final element type.
            types: Limit expression type to to these types.
        """
        if isinstance(expr, Note):
            self._check(expr, only=only, types=types)
            return expr
        return self.parse(expr, only=only, types=types)

    def parse(self, expr: Parseable, only=None, types=None) -> Expr:
        """
        Parse Expression.

        Args:
            expr: Expression

        Keyword Args:
            only: Limit expression to these final element type.
            types: Limit expression type to to these types.

        >>> import ucdp as u
        >>> p = u.ExprParser()
        >>> p.parse(10)
        ConstExpr(UintType(5, default=10))
        >>> p.parse('3h3')
        ConstExpr(UintType(3, default=3))
        >>> p.parse('3h3') * p.const(2)
        Op(ConstExpr(UintType(3, default=3)), '*', ConstExpr(UintType(3, default=2)))
        >>> p.parse((10, '10'))
        ConcatExpr((ConstExpr(UintType(5, default=10)), ConstExpr(UintType(5, default=10))))
        >>> p = u.ExprParser(namespace=u.Idents([
        ...     u.Signal(u.UintType(16, default=15), 'uint_s'),
        ...     u.Signal(u.SintType(16, default=-15), 'sint_s'),
        ... ]))
        >>> expr = p.parse('uint_s[2]')
        >>> expr
        SliceOp(Signal(UintType(16, default=15), 'uint_s'), Slice('2'))
        >>> expr = p.parse('uint_s * sint_s[2:1]')
        >>> expr
        Op(Signal(UintType(16, default=15), 'uint_s'), '*', SliceOp(Signal(SintType(16, ...), 'sint_s'), Slice('2:1')))
        >>> int(expr)
        0

        A more complex:

        >>> namespace = u.Idents([
        ...     u.Signal(u.UintType(2), 'a_s'),
        ...     u.Signal(u.UintType(4), 'b_s'),
        ...     u.Signal(u.SintType(8), 'c_s'),
        ...     u.Signal(u.SintType(16), 'd_s'),
        ... ])
        >>> p = u.ExprParser(namespace=namespace)
        >>> expr = p.parse("ternary(b_s == const('4h3'), a_s, c_s)")
        >>> expr
        TernaryExpr(BoolOp(Signal(UintType(4), 'b_s'), '==', ..., Signal(SintType(8), 'c_s'))

        Syntax Errors:

        >>> parse("sig_s[2")  # doctest: +SKIP
        Traceback (most recent call last):
        ...
        u.exceptions.InvalidExpr: 'sig_s[2': '[' was never closed (<string>, line 1)
        """
        result: Expr
        if isinstance(expr, Expr):
            result = expr
        elif isinstance(expr, BaseType):
            result = ConstExpr(expr)
        else:
            try:
                if isinstance(expr, (list, tuple)):
                    result = self.concat(expr)
                else:
                    try:
                        result = self.const(expr)
                    except InvalidExpr:
                        result = self._parse(str(expr))
            except NameError as exc:
                raise exc
        self._check(result, only=only, types=types)
        return result

    def _check(self, expr: Expr | Note, only, types) -> None:
        if only and not isinstance(expr, only):
            raise ValueError(f"{expr!r} is not a {only}. It is a {type(expr)}") from None
        if types:
            if isinstance(expr, Note):
                raise ValueError(f"{expr!r} does not meet type_ {types}.") from None
            if not isinstance(expr.type_, types):
                raise ValueError(f"{expr!r} requires type_ {types}. It is a {expr.type_}") from None

    def _parse(self, expr: str) -> Expr:
        if self.namespace:
            # avoid eval call on simple identifiers
            if isinstance(expr, str) and RE_IDENTIFIER.match(expr):
                try:
                    return self.namespace[expr]
                except ValueError:
                    pass
        try:
            globals: dict[str, Any] = self._globals  # type: ignore[assignment]
            return eval(expr, globals)  #  # noqa: S307
        except TypeError:
            raise InvalidExpr(expr) from None
        except SyntaxError as exc:
            raise InvalidExpr(f"{expr!r}: {exc!s}") from None

    def const(self, value: Constable) -> ConstExpr:
        """
        Parse Constant.

        >>> import ucdp as u
        >>> p = u.ExprParser()
        >>> p.const('10')
        ConstExpr(UintType(5, default=10))
        >>> p.const(10)
        ConstExpr(UintType(5, default=10))
        >>> p.const("10'd20")
        ConstExpr(UintType(10, default=20))
        >>> p.const(ConstExpr(UintType(10, default=20)))
        ConstExpr(UintType(10, default=20))
        >>> p.const("4'h4")
        ConstExpr(UintType(4, default=4))
        >>> p.const("4'sh4")
        ConstExpr(SintType(4, default=4))
        >>> p.const("4'shC")
        ConstExpr(SintType(4, default=-4))
        """
        if isinstance(value, ConstExpr):
            return value
        strippedvalue = str(value).strip()
        matnum = _RE_CONST.fullmatch(strippedvalue)
        if matnum:
            return self._parse_const(**matnum.groupdict())
        raise InvalidExpr(repr(value))

    @staticmethod
    def _parse_const(sign, width, is_signed, bnum, num) -> ConstExpr:
        if num is None:
            base, num = bnum[0], bnum[1:]
            value = int(num, _NUM_BASEMAP[base])
            if sign == "-":
                value = -value
            width = int(width)
            type_: BaseType
            if base == "b" and width == 1 and not is_signed:
                type_ = BitType(default=value)
            elif is_signed:
                if value > 0:
                    value = unsigned_to_signed(value, width)
                type_ = SintType(width, default=value)
            else:
                type_ = UintType(width, default=value)
            return ConstExpr(type_)
        intnum = int(num)
        width = calc_signed_width(intnum)
        return ConstExpr(UintType(width, default=intnum))

    def concat(self, value: Concatable) -> ConcatExpr:
        """
        Parse ConcatExpr.

        >>> import ucdp as u
        >>> p = u.ExprParser()
        >>> p.concat((10, "20"))
        ConcatExpr((ConstExpr(UintType(5, default=10)), ConstExpr(UintType(6, default=20))))
        >>> p.concat(ConcatExpr((ConstExpr(UintType(5, default=10)), ConstExpr(UintType(6, default=20)))))
        ConcatExpr((ConstExpr(UintType(5, default=10)), ConstExpr(UintType(6, default=20))))

        >>> bool(p.concat((10, "20")))
        True
        """
        if isinstance(value, ConcatExpr):
            return value
        return ConcatExpr(tuple(self.parse(item) for item in value))

    def ternary(self, cond: Parseable, one: Parseable, other: Parseable) -> TernaryExpr:
        """
        TernaryExpr Statement.

        >>> import ucdp as u
        >>> cond = u.Signal(u.UintType(2), 'if_s') == u.ConstExpr(UintType(2, default=1))
        >>> one = u.Signal(u.UintType(16, default=10), 'one_s')
        >>> other = u.Signal(u.UintType(16, default=20), 'other_s')
        >>> p = u.ExprParser()
        >>> expr = p.ternary(cond, one, other)
        >>> expr
        TernaryExpr(BoolOp(Signal(UintType(2), 'if_s'), '==', ..., Signal(UintType(16, default=20), 'other_s'))
        >>> int(expr)
        20
        >>> expr.type_
        UintType(16, default=10)
        """
        condp: BoolOp = self.parse(cond, only=BoolOp)  # type:ignore[assignment]
        onep = self.parse(one)
        otherp = self.parse(other)
        return TernaryExpr(cond=condp, one=onep, other=otherp)

    def log2(self, expr: Parseable):
        """
        Ceiling Logarithm to base of 2.

        >>> import ucdp as u
        >>> p = u.ExprParser()
        >>> log = p.log2("8'h8")
        >>> log
        Log2Expr(ConstExpr(UintType(8, default=8)))
        >>> int(log)
        3
        >>> p.parse("log2('8h8')")
        Log2Expr(ConstExpr(UintType(8, default=8)))
        """
        return Log2Expr(self.parse(expr))

    def minimum(self, *items):
        """
        Lower value of `one` and `other`.

        >>> import ucdp as u
        >>> p = u.ExprParser()
        >>> val = p.minimum("8'h8", "8'h3")
        >>> val
        MinimumExpr((ConstExpr(UintType(8, default=8)), ConstExpr(UintType(8, default=3))))
        >>> int(val)
        3
        >>> p.parse("minimum('8h8', '8h3')")
        MinimumExpr((ConstExpr(UintType(8, default=8)), ConstExpr(UintType(8, default=3))))
        """
        parsed = tuple(self.parse(item) for item in items)
        return MinimumExpr(parsed)

    def maximum(self, *items):
        """
        Higher value of `one` and `other`.

        >>> import ucdp as u
        >>> p = u.ExprParser()
        >>> val = p.maximum("8'h8", "8'h3")
        >>> val
        MaximumExpr((ConstExpr(UintType(8, default=8)), ConstExpr(UintType(8, default=3))))
        >>> int(val)
        8
        >>> p.parse("maximum('8h8', '8h3')")
        MaximumExpr((ConstExpr(UintType(8, default=8)), ConstExpr(UintType(8, default=3))))
        """
        parsed = tuple(self.parse(item) for item in items)
        return MaximumExpr(parsed)


def cast_booltype(expr):
    """Cast to Boolean."""
    type_ = expr.type_
    if isinstance(type_, BoolType):
        return expr
    if isinstance(type_, (BitType, UintType, BaseEnumType)) and int(type_.width) == 1:
        return expr == ConstExpr(BitType(default=1))
    raise ValueError("{expr} does not result in bool")


_PARSER = ExprParser()
const = _PARSER.const
