#
# MIT License
#
# Copyright (c) 2024-2025 nbiotcloud
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
Expression Parser.
"""

from collections.abc import Iterable
from functools import cached_property
from typing import Any

from ._castingnamespace import CastingNamespace
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
    _parse_const,
)
from .namespace import Namespace
from .note import Note
from .object import Object, computed_field
from .typebase import BaseScalarType, BaseType
from .typescalar import BoolType

Parseable = Expr | str | int | BaseType | list | tuple
Constable = int | str | ConstExpr
Concatable = list | tuple | ConcatExpr
Only = type[Expr] | Iterable[type[Expr]] | type[Note]
Types = type[BaseType] | Iterable[type[BaseType]]


class _Globals(dict):
    def __init__(self, globals: dict, namespace: Namespace | CastingNamespace | None, context: str | None):
        super().__init__(globals)
        self.namespace = namespace
        self.context = context

    def __missing__(self, key):
        if self.namespace:
            try:
                return self.namespace.get_dym(key)
            except ValueError as err:
                raise NameError(f"{self.context}: {err}") from None
        return NameError(key)


class ExprParser(Object):
    """
    ExprParser.

    Attributes:
        namespace (Namespace): Symbol namespace
    """

    namespace: Namespace | CastingNamespace | None = None
    context: str | None = None

    @computed_field
    @cached_property
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
        return _Globals(globals=globals_, namespace=self.namespace, context=self.context)

    def __call__(self, expr: Parseable, only: Only | None = None, types: Types | None = None) -> Expr:
        """
        Parse Expression.

        This is an alias to `parse`.

        Args:
            expr: Expression

        Keyword Args:
            only: Limit expression to these final element type.
            types: Limit expression type to to these types.
        """
        return self.parse(expr, only=only, types=types)

    def parse_note(self, expr: Parseable | Note, only: Only | None = None, types: Types | None = None) -> Expr | Note:
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

    def parse(self, expr: Parseable, only: Only | None = None, types: Types | None = None) -> Expr:
        """
        Parse Expression.

        Args:
            expr: Expression

        Keyword Args:
            only: Limit expression to these final element type.
            types: Limit expression type to to these types.

        ??? Example "Expression Parser Examples"
            Basics:

                >>> import ucdp as u
                >>> p = u.ExprParser()
                >>> p.parse(10)
                ConstExpr(IntegerType(default=10))
                >>> p.parse('3h3')
                ConstExpr(UintType(3, default=3))
                >>> p.parse('3h3') * p.const(2)
                Op(ConstExpr(UintType(3, default=3)), '*', ConstExpr(IntegerType(default=2)))
                >>> p.parse((10, '10'))
                ConcatExpr((ConstExpr(IntegerType(default=10)), ConstExpr(IntegerType(default=10))))
                >>> p = u.ExprParser(namespace=u.Idents([
                ...     u.Signal(u.UintType(16, default=15), 'uint_s'),
                ...     u.Signal(u.SintType(16, default=-15), 'sint_s'),
                ... ]))
                >>> expr = p.parse('uint_s[2]')
                >>> expr
                SliceOp(Signal(UintType(16, default=15), 'uint_s'), Slice('2'))
                >>> expr = p.parse('uint_s * sint_s[2:1]')
                >>> expr
                Op(Signal(UintType(16, ...), 'uint_s'), '*', SliceOp(Signal(SintType(16, ...), 'sint_s'), Slice('2:1')))
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

    def _check(self, expr: Expr | Note, only: Only | None, types: Types | None) -> None:
        if only and not isinstance(expr, only):  # type: ignore[arg-type]
            raise ValueError(f"{expr!r} is not a {only}. It is a {type(expr)}") from None
        if types:
            if isinstance(expr, Note):
                raise ValueError(f"{expr!r} does not meet type_ {types}.") from None
            if not isinstance(expr.type_, types):  # type: ignore[arg-type]
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
            return eval(expr, globals)  # noqa: S307
        except TypeError:
            raise InvalidExpr(expr) from None
        except SyntaxError as exc:
            raise InvalidExpr(f"{expr!r}: {exc!s}") from None

    def const(self, value: Constable) -> ConstExpr:
        """
        Parse Constant.

        ??? Example "Parser Example"
            Basics:

                >>> import ucdp as u
                >>> p = u.ExprParser()
                >>> p.const('10')
                ConstExpr(IntegerType(default=10))
                >>> p.const(10)
                ConstExpr(IntegerType(default=10))
                >>> p.const("10'd20")
                ConstExpr(UintType(10, default=20))
                >>> p.const(u.ConstExpr(u.UintType(10, default=20)))
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
        return _parse_const(value)

    def concat(self, value: Concatable) -> ConcatExpr:
        """
        Parse ConcatExpr.

        ??? Example "Concat Parser Example"
            Basics:

                >>> import ucdp as u
                >>> p = u.ExprParser()
                >>> p.concat((10, "20"))
                ConcatExpr((ConstExpr(IntegerType(default=10)), ConstExpr(IntegerType(default=20))))

                >>> bool(p.concat((10, "20")))
                True
        """
        if isinstance(value, ConcatExpr):
            return value
        return ConcatExpr(tuple(self.parse(item) for item in value))

    def ternary(self, cond: Parseable, one: Parseable, other: Parseable) -> TernaryExpr:
        """
        TernaryExpr Statement.

        ??? Example "Ternary Parser Example"
            Basics:

                >>> import ucdp as u
                >>> cond = u.Signal(u.UintType(2), 'if_s') == u.ConstExpr(u.UintType(2, default=1))
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

        ??? Example "Log2 Parser Example"
            Basics:

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

        ??? Example "Minimum Parser Example"
            Basics:

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

        ??? Example "Maximum Parser Example"
            Basics:

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
    if isinstance(type_, BaseScalarType) and int(type_.width) == 1:
        return expr == 1
    raise ValueError(f"{expr} does not result in bool")


_PARSER = ExprParser()
const = _PARSER.const
concat = _PARSER.concat
ternary = _PARSER.ternary
log2 = _PARSER.log2
minimum = _PARSER.minimum
maximum = _PARSER.minimum
