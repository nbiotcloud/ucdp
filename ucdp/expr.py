#
# MIT License
#
# Copyright (c) 2023 nbiotcloud
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
Expression Engine.
"""

# pylint: disable=too-many-lines

import math
import operator
import re
from collections import deque
from typing import Callable, Optional, Tuple

from icdutil.num import unsigned_to_signed
from icdutil.slices import Slice

from .attrs import ReusedFrozen, field, frozen
from .namespace import Namespace
from .types.base import AType, AVecType
from .types.enum import BaseEnumType
from .types.scalar import BitType, BoolType, IntegerType, SintType, UintType

_re_ident = re.compile(r"\A[a-zA-Z][a-zA-Z0-9\_]*\Z")


def parse(
    expr, namespace: Optional[Namespace] = None, only=None, types=None, strict: bool = True, context=None
) -> "Expr":
    """
    Parse Constant, ConcatExpr or Expressions **WITHOUT** constants.

    Args:
        expr: Expression

    Keyword Args:
        namespace (Namespace): Symbol namespace
        only: Limit expression to these final element type.
        types: Limit expression type to to these types.
        strict (bool): Do not ignore missing symbols.

    >>> import ucdp
    >>> ucdp.parse('10')
    10
    >>> ucdp.parse((10, '10'))
    ConcatExpr((10, 10))
    >>> namespace = ucdp.Idents([
    ...     ucdp.Signal(ucdp.UintType(16, default=15), 'uint_s'),
    ...     ucdp.Signal(ucdp.SintType(16, default=-15), 'sint_s'),
    ... ])
    >>> expr = ucdp.parse('uint_s[2]', namespace)
    >>> expr
    SliceOp(Signal(UintType(16, default=15), 'uint_s'), Slice('2'))
    >>> expr = ucdp.parse('uint_s * sint_s[2:1]', namespace)
    >>> expr
    Op(Signal(UintType(16, default=15), 'uint_s'), '*', SliceOp(Signal(SintType(16, ...), 'sint_s'), Slice('2:1')))
    >>> int(expr)
    0

    A more complex:

    >>> namespace = ucdp.Idents([
    ...     ucdp.Signal(ucdp.UintType(2), 'a_s'),
    ...     ucdp.Signal(ucdp.UintType(4), 'b_s'),
    ...     ucdp.Signal(ucdp.SintType(8), 'c_s'),
    ...     ucdp.Signal(ucdp.SintType(16), 'd_s'),
    ... ])
    >>> expr = ucdp.parse("ternary(b_s, 2 * a_s + c_s, c_s)", namespace=namespace)
    >>> expr
    TernaryExpr(Signal(UintType(4), 'b_s'), Op(Op(2, '*', ... Signal(SintType(8), 'c_s'))

    Syntax Errors:

    >>> parse("sig_s[2")  # doctest: +SKIP
    Traceback (most recent call last):
      ...
    ucdp.expr.InvalidExpr: 'sig_s[2': '[' was never closed (<string>, line 1)
    """
    # pylint: disable=too-many-arguments
    if isinstance(expr, Expr):
        return expr
    if isinstance(expr, AType):
        return ConstExpr(expr)
    try:
        if isinstance(expr, (list, tuple)):
            return concat(expr, namespace=None)
        try:
            return const(expr)
        except InvalidExpr:
            pass
        expr = _parse(expr, namespace, strict)
    except NameError as exc:
        if context:
            raise NameError(f"{exc!s}\n\n{context}") from None
        raise exc
    if only and not isinstance(expr, only):
        raise ValueError(f"{expr!r} is not a {only}. It is a {type(expr)}") from None
    if types and not isinstance(expr.type_, types):
        raise ValueError(f"{expr!r} requires type_ {types}. It is a {expr.type_}") from None
    return expr


def const(value):
    """
    Parse Constant.

    >>> const('10')
    10

    >>> const(10)
    10
    """
    return ConstExpr.parse(value)


def concat(value, namespace=None):
    """
    Parse ConcatExpr.

    >>> concat((10, "20"))
    ConcatExpr((10, 20))

    >>> concat(ConcatExpr((10, 20)))
    ConcatExpr((10, 20))

    >>> bool(concat((10, "20")))
    True
    """
    return ConcatExpr.parse(value, namespace=namespace)


def ternary(cond, one, other, namespace=None):
    """
    TernaryExpr Statement.

    >>> import ucdp
    >>> cond = ucdp.Signal(ucdp.BitType(), 'if_s')
    >>> one = ucdp.Signal(ucdp.UintType(16, default=10), 'one_s')
    >>> other = ucdp.Signal(ucdp.UintType(16, default=20), 'other_s')
    >>> expr = ternary(cond, one, other)
    >>> expr
    TernaryExpr(Signal(BitType(), 'if_s'), Signal(UintType(16, default=10), 'one_s'), ... default=20), 'other_s'))
    >>> int(expr)
    20
    >>> expr.type_
    UintType(16, default=10)
    """
    cond = parse(cond, namespace=namespace)
    one = parse(one, namespace=namespace)
    other = parse(other, namespace=namespace)
    expr = TernaryExpr(cond, one, other)
    # check_booltype(str(expr), cond.type_, BoolType)
    return expr


def log2(expr, namespace=None):
    """
    Ceiling Logarithm to base of 2.

    >>> log = log2("8'h8")
    >>> log
    Log2Func(ConstExpr(UintType(8, default=8)))
    >>> int(log)
    3
    """
    expr = parse(expr, namespace=namespace)
    return Log2Func(expr)


def signed(expr, namespace=None):
    """
    Signed Conversion

    >>> import ucdp
    >>> expr = ucdp.Signal(ucdp.UintType(16), 'one_s')
    >>> expr = ucdp.signed(expr)
    >>> expr
    SignedFunc(Signal(UintType(16), 'one_s'))
    """
    expr = parse(expr, namespace=namespace)
    return SignedFunc(expr)


def unsigned(expr, namespace=None):
    """
    Unsigned Conversion

    >>> import ucdp
    >>> expr = ucdp.Signal(ucdp.SintType(16), 'one_s')
    >>> expr = ucdp.unsigned(expr)
    >>> expr
    UnsignedFunc(Signal(SintType(16), 'one_s'))
    """
    expr = parse(expr, namespace=namespace)
    return UnsignedFunc(expr)


def minimum(one, other, namespace=None):
    """
    Lower value of `one` and `other`.

    >>> val = minimum("8'h8", "8'h3")
    >>> val
    MinimumFunc(ConstExpr(UintType(8, default=8)), ConstExpr(UintType(8, default=3)))
    >>> int(val)
    3
    """
    one = parse(one, namespace=namespace)
    other = parse(other, namespace=namespace)
    return MinimumFunc(one, other)


def maximum(one, other, namespace=None):
    """
    Higher value of `one` and `other`.

    >>> val = maximum("8'h8", "8'h3")
    >>> val
    MaximumFunc(ConstExpr(UintType(8, default=8)), ConstExpr(UintType(8, default=3)))
    >>> int(val)
    8
    """
    one = parse(one, namespace=namespace)
    other = parse(other, namespace=namespace)
    return MaximumFunc(one, other)


def cast(expr):
    """
    Cast.

    Only allowed within routing. Forbidden here.

    >>> cast('port_i')
    Traceback (most recent call last):
      ...
    ucdp.expr.InvalidExpr: cast() is just allowed once within routing.
    """
    raise InvalidExpr("cast() is just allowed once within routing.")


def create(expr):
    """
    Create.

    Only allowed within routing. Forbidden here.

    >>> create('port_i')
    Traceback (most recent call last):
      ...
    ucdp.expr.InvalidExpr: create() is just allowed once within routing.
    """
    raise InvalidExpr("create() is just allowed once within routing.")


class InvalidExpr(ValueError):
    """Invalid Expression."""


@frozen(cmp=False, hash=True)
class Expr(ReusedFrozen):
    """Base Class for all Expressions."""

    def __lt__(self, other):
        if isinstance(other, str):
            other = parse(other)
        return BoolOp(self, operator.lt, "<", other)

    def __le__(self, other):
        if isinstance(other, str):
            other = parse(other)
        return BoolOp(self, operator.le, "<=", other)

    def __eq__(self, other):
        if isinstance(other, str):
            other = parse(other)
        return BoolOp(self, operator.eq, "==", other)

    def __ne__(self, other):
        if isinstance(other, str):
            other = parse(other)
        return BoolOp(self, operator.ne, "!=", other)

    def __ge__(self, other):
        if isinstance(other, str):
            other = parse(other)
        return BoolOp(self, operator.ge, ">=", other)

    def __gt__(self, other):
        if isinstance(other, str):
            other = parse(other)
        return BoolOp(self, operator.gt, ">", other)

    def __add__(self, other):
        if isinstance(other, str):
            other = parse(other)
        return Op(self, operator.add, "+", other)

    def __sub__(self, other):
        if isinstance(other, str):
            other = parse(other)
        return Op(self, operator.sub, "-", other)

    def __mul__(self, other):
        if isinstance(other, str):
            other = parse(other)
        return Op(self, operator.mul, "*", other)

    def __floordiv__(self, other):
        if isinstance(other, str):
            other = parse(other)
        return Op(self, operator.floordiv, "//", other)

    def __mod__(self, other):
        if isinstance(other, str):
            other = parse(other)
        return Op(self, operator.mod, "%", other)

    def __pow__(self, other):
        if isinstance(other, str):
            other = parse(other)
        return Op(self, operator.pow, "**", other)

    def __lshift__(self, other):
        if isinstance(other, str):
            other = parse(other)
        return Op(self, operator.lshift, "<<", other)

    def __rshift__(self, other):
        if isinstance(other, str):
            other = parse(other)
        return Op(self, operator.rshift, ">>", other)

    def __or__(self, other):
        if isinstance(other, str):
            other = parse(other)
        return Op(self, operator.or_, "|", other)

    def __and__(self, other):
        if isinstance(other, str):
            other = parse(other)
        return Op(self, operator.and_, "&", other)

    def __xor__(self, other):
        if isinstance(other, str):
            other = parse(other)
        return Op(self, operator.xor, "^", other)

    def __radd__(self, other):
        if isinstance(other, str):
            other = parse(other)
        return Op(other, operator.add, "+", self)

    def __rsub__(self, other):
        if isinstance(other, str):
            other = parse(other)
        return Op(other, operator.sub, "-", self)

    def __rmul__(self, other):
        if isinstance(other, str):
            other = parse(other)
        return Op(other, operator.mul, "*", self)

    def __rfloordiv__(self, other):
        if isinstance(other, str):
            other = parse(other)
        return Op(other, operator.floordiv, "//", self)

    def __rmod__(self, other):
        return Op(other, operator.mod, "%", self)

    def __rpow__(self, other):
        if isinstance(other, str):
            other = parse(other)
        return Op(other, operator.pow, "**", self)

    def __rlshift__(self, other):
        if isinstance(other, str):
            other = parse(other)
        return Op(other, operator.lshift, "<<", self)

    def __rrshift__(self, other):
        if isinstance(other, str):
            other = parse(other)
        return Op(other, operator.rshift, ">>", self)

    def __ror__(self, other):
        if isinstance(other, str):
            other = parse(other)
        return Op(other, operator.or_, "|", self)

    def __rand__(self, other):
        if isinstance(other, str):
            other = parse(other)
        return Op(other, operator.and_, "&", self)

    def __rxor__(self, other):
        if isinstance(other, str):
            other = parse(other)
        return Op(other, operator.xor, "^", self)

    def __abs__(self):
        return SOp(operator.abs, "abs(", self, ")")

    def __invert__(self):
        return SOp(operator.inv, "~", self)

    def __neg__(self):
        return SOp(operator.neg, "-", self)

    def __getitem__(self, slice_):
        slice_ = Slice.cast(slice_)
        return SliceOp(self, slice_)


@frozen(cmp=False, hash=True)
class Op(Expr):
    """Dual Operator Expression."""

    left = field()
    oper: Callable = field(repr=False)
    sign = field()
    right = field()

    def __int__(self):
        # pylint: disable=not-callable
        return int(self.oper(int(self.left), int(self.right)))

    @property
    def type_(self):
        """Type is always type of left side."""
        if isinstance(self.left, Expr):
            return self.left.type_
        return self.right.type_


@frozen(cmp=False, hash=True)
class BoolOp(Op):
    """Boolean Dual Operator Expression."""

    # pylint: disable=too-few-public-methods

    @property
    def type_(self):
        """Boolean Type."""
        return BoolType()


@frozen(cmp=False, hash=True)
class SOp(Expr):
    """Single Operator Expression."""

    oper = field(repr=False)
    sign = field()
    one = field()
    postsign = field(default="")

    # pylint: disable=too-few-public-methods

    def __int__(self):
        # pylint: disable=not-callable
        return self.oper(int(self.one))

    @property
    def type_(self):
        """Type."""
        return self.one.type_


@frozen(cmp=False, hash=True)
class SliceOp(Expr):
    """Slice Expression."""

    one = field()
    slice_ = field()

    def __int__(self):
        return int(self.one.type_[self.slice_].default)

    @property
    def type_(self):
        """Type."""
        return self.one.type_[self.slice_]


@frozen(cmp=False, hash=True)
class ConstExpr(Expr):
    """
    Constant.

    >>> import ucdp
    >>> const = ConstExpr(ucdp.UintType(5, default=5))
    >>> const
    ConstExpr(UintType(5, default=5))
    >>> int(const)
    5
    >>> bool(const)
    True
    """

    type_ = field()

    def __int__(self):
        # pylint: disable=not-callable
        return int(self.type_.default)

    def __getitem__(self, slice_):
        # pylint: disable=unsubscriptable-object
        return ConstExpr(self.type_[slice_])

    _RE = re.compile(
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

    @staticmethod
    def parse(value):
        """
        Parse Constant.

        >>> ConstExpr.parse('10')
        10
        >>> ConstExpr.parse("10'd20")
        ConstExpr(UintType(10, default=20))
        >>> ConstExpr.parse(ConstExpr(UintType(10, default=20)))
        ConstExpr(UintType(10, default=20))

        >>> ConstExpr.parse("4'h4")
        ConstExpr(UintType(4, default=4))
        >>> ConstExpr.parse("4'sh4")
        ConstExpr(SintType(4, default=4))
        >>> ConstExpr.parse("4'shC")
        ConstExpr(SintType(4, default=-4))
        """
        if isinstance(value, ConstExpr):
            return value
        strippedvalue = str(value).strip()
        matnum = ConstExpr._RE.fullmatch(strippedvalue)
        if matnum:
            return ConstExpr._parse(**matnum.groupdict())
        raise InvalidExpr(repr(value))

    @staticmethod
    def _parse(sign, width, is_signed, bnum, num):
        if num is None:
            base, num = bnum[0], bnum[1:]
            value = int(num, ConstExpr._NUM_BASEMAP[base])
            if sign == "-":
                value = -value
            width = int(width)
            if base == "b" and width == 1 and not is_signed:
                type_ = BitType(default=value)
            else:
                if is_signed:
                    if value > 0:
                        value = unsigned_to_signed(value, width)
                    type_ = SintType(width, default=value)
                else:
                    type_ = UintType(width, default=value)
            return ConstExpr(type_)
        return int(num)

    @staticmethod
    def replace(value):
        """
        Replace constants in `value`.

        >>> ConstExpr.replace("(foo_s == 2'b0) && (bla_s > 16'd0)")
        '(foo_s == ConstExpr(UintType(2))) && (bla_s > ConstExpr(UintType(16)))'
        >>> ConstExpr.replace(1)
        1
        """
        if isinstance(value, str):
            return ConstExpr._RE.sub(ConstExpr._replace, value)
        return value

    @staticmethod
    def _replace(mat):
        return repr(ConstExpr._parse(**mat.groupdict()))


@frozen(cmp=False, hash=True)
class ConcatExpr(Expr):

    """
    Concatenation.

    >>> import ucdp
    >>> sig = ucdp.Signal(ucdp.UintType(16, default=10), 'val_s')
    >>> expr = concat(("2'd0", sig, "2'b00"))
    >>> expr
    ConcatExpr((ConstExpr(UintType(2)), Signal(UintType(16, default=10), 'val_s'), ConstExpr(UintType(2))))
    >>> int(expr)
    40
    >>> expr.type_
    UintType(20, default=40)
    >>> concat(("2'd0",))
    ConcatExpr((ConstExpr(UintType(2)),))
    """

    items: Tuple[Expr, ...] = field()

    @items.validator
    def _items_validator(self, attribute, value):
        # pylint: disable=unused-argument
        assert len(value)

    def __int__(self):
        return sum(value << shift for value, shift in self.__iter_values())

    def __iter_values(self):
        # pylint: disable=not-an-iterable
        shift = 0
        for item in self.items:
            if isinstance(item, int):
                yield item, shift
                shift += 32
            else:
                yield int(item), shift
                shift += item.type_.width
        yield 0, shift

    @property
    def type_(self):
        """Type."""
        pairs = tuple(self.__iter_values())
        default = sum(value << shift for value, shift in pairs)
        width = pairs[-1][1] if pairs else 1
        return UintType(width, default=default)

    @staticmethod
    def parse(value, namespace=None):
        """
        Parse ConcatExpr.

        >>> ConcatExpr.parse((10, 20))
        ConcatExpr((10, 20))
        """
        if isinstance(value, ConcatExpr):
            return value
        return ConcatExpr(tuple(parse(item, namespace=namespace) for item in value))


@frozen(cmp=False, hash=True)
class TernaryExpr(Expr):

    """
    TernaryExpr Expression

    >>> import ucdp
    >>> cond = ucdp.Signal(ucdp.BitType(), 'if_s')
    >>> one = ucdp.Signal(ucdp.UintType(16, default=10), 'one_s')
    >>> other = ucdp.Signal(ucdp.UintType(16, default=20), 'other_s')
    >>> expr = TernaryExpr(cond, one, other)
    >>> expr
    TernaryExpr(Signal(BitType(), 'if_s'), Signal(UintType(16, default=10), 'one_s'), ... default=20), 'other_s'))
    >>> int(expr)
    20
    >>> expr.type_
    UintType(16, default=10)
    """

    cond: Expr = field()
    one: Expr = field()
    other: Expr = field()

    def __int__(self):
        if bool(int(self.cond)):
            return int(self.one)
        return int(self.other)

    @property
    def type_(self):
        """Type."""
        return self.one.type_


@frozen(cmp=False, hash=True)
class Log2Func(Expr):

    """
    Ceiling Logarithm to base of 2.
    """

    expr: Expr = field()

    def __int__(self):
        return int(math.log(int(self.expr), 2))

    @property
    def type_(self):
        """Type."""
        return self.expr.type_


@frozen(cmp=False, hash=True)
class SignedFunc(Expr):

    """
    Signed Conversion
    """

    expr: Expr = field()

    def __int__(self):
        return int(self.expr)  # TODO

    @property
    def type_(self):
        """Type."""
        return SintType(self.expr.type_.width)  # TODO: default conversion


@frozen(cmp=False, hash=True)
class UnsignedFunc(Expr):

    """
    Unsigned Conversion
    """

    expr: Expr = field()

    def __int__(self):
        return int(self.expr)  # TODO

    @property
    def type_(self):
        """Type."""
        return UintType(self.expr.type_.width)  # TODO: default conversion


@frozen(cmp=False, hash=True)
class MinimumFunc(Expr):

    """
    Smaller value of two.
    """

    one: Expr = field()
    other: Expr = field()

    def __int__(self):
        one = int(self.one)
        other = int(self.other)
        if one < other:
            return one
        return other

    @property
    def type_(self):
        """Type."""
        return self.one.type_


@frozen(cmp=False, hash=True)
class MaximumFunc(Expr):

    """
    Larger value of two.
    """

    one: Expr = field()
    other: Expr = field()

    def __int__(self):
        one = int(self.one)
        other = int(self.other)
        if one > other:
            return one
        return other

    @property
    def type_(self):
        """Type."""
        return self.one.type_


@frozen(cmp=False, hash=True)
class Range(Expr):

    """
    Value Range.

    >>> import ucdp
    >>> range_ = ucdp.Range(ucdp.UintType(4), range(2, 9))
    >>> range_.type_
    UintType(4)
    >>> range_.range_
    range(2, 9)
    >>> ucdp.Range(ucdp.UintType(2), range(2, 9))
    Traceback (most recent call last):
      ...
    ValueError: End Value 8 is not a 2-bit integer with range [0, 3]
    """

    # pylint: disable=too-few-public-methods

    type_: AVecType = field()
    range_ = field()

    @type_.validator
    def _type_validator(self, attribute, value):
        # pylint: disable=unused-argument
        assert isinstance(value, (UintType, SintType))

    @range_.validator
    def _range_validator(self, attribute, value):
        # pylint: disable=unused-argument
        assert isinstance(value, range)
        values = tuple(value)
        self.type_.check(values[0], what="Start Value")
        self.type_.check(values[-1], what="End Value")


@frozen(cmp=False, hash=True)
class CommentExpr(Expr):

    """
    Comment.
    """

    # pylint: disable=too-few-public-methods

    comment: str = field()

    @property
    def type_(self):
        """Type."""
        return None


TODO = CommentExpr("TODO")

EXPRGBLS = {
    # Expressions
    "Op": Op,
    "SOp": SOp,
    "BoolOp": BoolOp,
    "SliceOp": SliceOp,
    "ConstExpr": ConstExpr,
    "ConcatExpr": ConcatExpr,
    "TernaryExpr": TernaryExpr,
    "Log2Func": Log2Func,
    "MinimumFunc": MinimumFunc,
    "MaximumFunc": MaximumFunc,
    # Helper
    "const": const,
    "concat": concat,
    "ternary": ternary,
    "signed": signed,
    "unsigned": unsigned,
    "log2": log2,
    "minimum": minimum,
    "maximum": maximum,
    # Types
    "BitType": BitType,
    "IntegerType": IntegerType,
    "SintType": SintType,
    "UintType": UintType,
}


class _ExprGlobals(dict):
    def __init__(self, namespace, strict):
        super().__init__()
        self.namespace = namespace
        self.strict = strict

    def __missing__(self, key):
        # resolve from global symbols
        value = EXPRGBLS.get(key, None)
        # resolve from namespace
        if value is None and self.namespace:
            if self.strict:
                try:
                    return self.namespace.get(key)
                except ValueError as err:
                    raise NameError(err) from None
            else:
                try:
                    return self.namespace[key]
                except ValueError:
                    pass
        if value is None:
            if self.strict:
                raise KeyError(key)
            return key
        return value


def _parse(expr, namespace, strict) -> Expr:
    if namespace:
        if expr == "":
            return namespace[expr]
        # avoid eval call on simple identifiers
        if isinstance(expr, str) and _re_ident.match(expr):
            try:
                return namespace[expr]
            except ValueError:
                pass
    # pylint: disable=eval-used
    try:
        return eval(expr, _ExprGlobals(namespace, strict))
    except TypeError:
        raise InvalidExpr(expr) from None
    except SyntaxError as exc:
        raise InvalidExpr(f"{expr!r}: {exc!s}") from None


def get_idents(expr: Expr):
    """
    Determine used identifier in `expr`.
    """
    idents = {}
    heap = deque((expr,))
    while heap:
        item = heap.popleft()
        if isinstance(item, (ConstExpr, int, float)):
            pass
        elif isinstance(item, Op):
            heap.append(item.left)
            heap.append(item.right)
        elif isinstance(item, (SOp, SliceOp)):
            heap.append(item.one)
        elif isinstance(item, ConcatExpr):
            heap.extend(item.items)
        elif isinstance(item, TernaryExpr):
            heap.append(item.cond)
            heap.append(item.one)
            heap.append(item.other)
        elif isinstance(item, (MinimumFunc, MaximumFunc)):
            heap.append(item.one)
            heap.append(item.other)
        elif isinstance(item, (SignedFunc, UnsignedFunc, Log2Func)):
            heap.append(item.expr)
        else:
            if item.name not in idents:
                idents[item.name] = item
    return tuple(idents.values())


def cast_booltype(expr):
    """Cast to Boolean."""
    type_ = expr.type_
    if isinstance(type_, BoolType):
        return expr
    if isinstance(type_, (BitType, UintType, BaseEnumType)) and int(type_.width) == 1:
        return expr == ConstExpr(BitType(default=1))
    return expr
