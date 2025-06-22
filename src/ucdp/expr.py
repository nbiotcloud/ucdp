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
Expression Engine.
"""

import math
import operator
import re
from collections.abc import Callable, Iterator
from typing import ClassVar

from icdutil.num import calc_signed_width, calc_unsigned_width, unsigned_to_signed
from pydantic import ValidationError

from .exceptions import InvalidExpr
from .object import Field, Light, Object, PosArgs, model_validator
from .slices import Slice
from .typebase import BaseScalarType, BaseType
from .typehelper import BaseScalarTypes
from .typescalar import BitType, BoolType, IntegerType, SintType, UintType

_RE_CONST = re.compile(
    r"(?P<sign>[-+])?"
    r"(((?P<width>\d+)'?(?P<is_signed>s)?(?P<bnum>(b[01]+)|(o[0-7]+)|(d[0-9]+)|(h[0-9a-fA-F]+))))|(?P<num>[+-]?\d+)\b"
)
_NUM_BASEMAP = {
    "b": 2,
    "o": 8,
    "d": 10,
    "h": 16,
    None: 10,
}
_OPERMAP = {
    "<": operator.lt,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
    ">=": operator.ge,
    ">": operator.gt,
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "//": operator.floordiv,
    "%": operator.mod,
    "**": operator.pow,
    "<<": operator.lshift,
    ">>": operator.rshift,
    "|": operator.or_,
    "&": operator.and_,
    "^": operator.xor,
}
_SOPERMAP = {
    "abs(": operator.abs,
    "~": operator.inv,
    "-": operator.neg,
}


class Expr(Object):  # noqa: PLW1641
    """Base Class for all Expressions.

    Attributes:
        type_: Type.
    """

    type_: BaseType = Field(repr=False)

    def __lt__(self, other):
        if isinstance(other, int):
            other = _parse_const(other, reftype=self.type_)
        if not isinstance(other, Expr):
            return NotImplemented
        return BoolOp(self, "<", other)

    def __le__(self, other):
        if isinstance(other, int):
            other = _parse_const(other, reftype=self.type_)
        if not isinstance(other, Expr):
            return NotImplemented
        return BoolOp(self, "<=", other)

    def __eq__(self, other):
        if isinstance(other, int):
            other = _parse_const(other, reftype=self.type_)
        if not isinstance(other, Expr):
            return NotImplemented
        return BoolOp(self, "==", other)

    def __ne__(self, other):
        if isinstance(other, int):
            other = _parse_const(other, reftype=self.type_)
        if not isinstance(other, Expr):
            return NotImplemented
        return BoolOp(self, "!=", other)

    def __ge__(self, other):
        if isinstance(other, int):
            other = _parse_const(other, reftype=self.type_)
        if not isinstance(other, Expr):
            return NotImplemented
        return BoolOp(self, ">=", other)

    def __gt__(self, other):
        if isinstance(other, int):
            other = _parse_const(other, reftype=self.type_)
        if not isinstance(other, Expr):
            return NotImplemented
        return BoolOp(self, ">", other)

    def __add__(self, other) -> "Op":
        if isinstance(other, int):
            other = _parse_const(other, reftype=self.type_)
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(self, "+", other)

    def __sub__(self, other) -> "Op":
        if isinstance(other, int):
            other = _parse_const(other, reftype=self.type_)
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(self, "-", other)

    def __mul__(self, other) -> "Op":
        if isinstance(other, int):
            other = _parse_const(other, reftype=self.type_)
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(self, "*", other)

    def __floordiv__(self, other) -> "Op":
        if isinstance(other, int):
            other = _parse_const(other, reftype=self.type_)
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(self, "//", other)

    def __mod__(self, other) -> "Op":
        if isinstance(other, int):
            other = _parse_const(other, reftype=self.type_)
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(self, "%", other)

    def __pow__(self, other) -> "Op":
        if isinstance(other, int):
            other = _parse_const(other, reftype=self.type_)
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(self, "**", other)

    def __lshift__(self, other) -> "Op":
        if isinstance(other, int):
            other = _parse_const(other, reftype=self.type_)
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(self, "<<", other)

    def __rshift__(self, other) -> "Op":
        if isinstance(other, int):
            other = _parse_const(other, reftype=self.type_)
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(self, ">>", other)

    def __or__(self, other) -> "Op":
        if isinstance(other, int):
            other = _parse_const(other, reftype=self.type_)
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(self, "|", other)

    def __and__(self, other) -> "Op":
        if isinstance(other, int):
            other = _parse_const(other, reftype=self.type_)
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(self, "&", other)

    def __xor__(self, other) -> "Op":
        if isinstance(other, int):
            other = _parse_const(other, reftype=self.type_)
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(self, "^", other)

    def __radd__(self, other) -> "Op":
        if isinstance(other, int):
            other = _parse_const(other, reftype=self.type_)
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(other, "+", self)

    def __rsub__(self, other) -> "Op":
        if isinstance(other, int):
            other = _parse_const(other, reftype=self.type_)
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(other, "-", self)

    def __rmul__(self, other) -> "Op":
        if isinstance(other, int):
            other = _parse_const(other, reftype=self.type_)
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(other, "*", self)

    def __rfloordiv__(self, other) -> "Op":
        if isinstance(other, int):
            other = _parse_const(other, reftype=self.type_)
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(other, "//", self)

    def __rmod__(self, other) -> "Op":
        if isinstance(other, int):
            other = _parse_const(other, reftype=self.type_)
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(other, "%", self)

    def __rpow__(self, other) -> "Op":
        if isinstance(other, int):
            other = _parse_const(other, reftype=self.type_)
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(other, "**", self)

    def __rlshift__(self, other) -> "Op":
        if isinstance(other, int):
            other = _parse_const(other, reftype=self.type_)
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(other, "<<", self)

    def __rrshift__(self, other) -> "Op":
        if isinstance(other, int):
            other = _parse_const(other, reftype=self.type_)
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(other, ">>", self)

    def __ror__(self, other) -> "Op":
        if isinstance(other, int):
            other = _parse_const(other, reftype=self.type_)
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(other, "|", self)

    def __rand__(self, other) -> "Op":
        if isinstance(other, int):
            other = _parse_const(other, reftype=self.type_)
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(other, "&", self)

    def __rxor__(self, other) -> "Op":
        if isinstance(other, int):
            other = _parse_const(other, reftype=self.type_)
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(other, "^", self)

    def __abs__(self) -> "SOp":
        return SOp(sign="abs(", one=self)

    def __invert__(self) -> "SOp":
        return SOp(sign="~", one=self)

    def __neg__(self) -> "SOp":
        return SOp(sign="-", one=self)

    def __getitem__(self, slice_):
        if isinstance(slice_, Expr):
            slice_ = Slice(left=slice_, right=slice_)
        else:
            slice_ = Slice.cast(slice_)
        return SliceOp(one=self, slice_=slice_)


class Op(Expr, Light):
    """Dual Operator Expression.

    Args:
        left: left argument.
        sign: sign.
        right: right argument.

    Attributes:
        oper: Operator.
        type_: Type.

    ???+ bug "Todo"
        * fix inherited_members / Attributes Types
    """

    left: Expr
    oper: Callable = Field(repr=False)
    sign: str
    right: Expr

    _posargs: ClassVar[PosArgs] = ("left", "sign", "right")

    def __init__(self, left: Expr, sign: str, right: Expr, type_: BaseType | None = None):
        oper = _OPERMAP[sign]
        if type_ is None:
            type_ = left.type_
        super().__init__(left=left, oper=oper, sign=sign, right=right, type_=type_)  # type: ignore[call-arg]

    def __int__(self):
        return int(self.oper(int(self.left), int(self.right)))

    def __bool__(self):
        return bool(self.oper(int(self.left), int(self.right)))


class BoolOp(Op):
    """Boolean Dual Operator Expression.

    Args:
        left: left argument.
        sign: sign.
        right: right argument.

    Attributes:
        oper: Operator.
        type_: Type.

    ???+ bug "Todo"
        * fix inherited_members / Attributes Types
    """

    def __init__(self, left: Expr, sign: str, right: Expr):
        super().__init__(left=left, sign=sign, right=right, type_=BoolType())  # type: ignore[call-arg]


class SOp(Expr, Light):
    """Single Operator Expression.

    Args:
        sign: sign.
        one: Expression.

    Attributes:
        oper: Operator.
        postsign: postsign.
        type_: Type.

    ???+ bug "Todo"
        * fix inherited_members / Attributes Types

    """

    oper: Callable = Field(repr=False)
    sign: str
    one: Expr
    postsign: str = ""

    _posargs: ClassVar[PosArgs] = ("sign", "one")

    def __init__(self, sign: str, one: Expr):
        oper = _SOPERMAP[sign]
        postsign = ")" if "(" in sign else ""
        super().__init__(oper=oper, sign=sign, one=one, postsign=postsign, type_=one.type_)  # type: ignore[call-arg]

    def __int__(self):
        return self.oper(int(self.one))


class SliceOp(Expr, Light):
    """Slice Expression.

    Args:
        one: Expression.
        slice_: Slice

    Attributes:
        type_: Type.

    ???+ bug "Todo"
        * fix inherited_members / Attributes Types
    """

    one: Expr
    slice_: Slice

    _posargs: ClassVar[PosArgs] = ("one", "slice_")

    def __init__(self, one: Expr, slice_: Slice):
        super().__init__(one=one, slice_=slice_, type_=one.type_[slice_])  # type: ignore[call-arg]

    def __int__(self):
        return int(self.one.type_[self.slice_].default)


class ConstExpr(Expr, Light):
    """
    Constant.

    Args:
        type_: Type.

    ??? Example "ConstExpr Examples"
        Example.

            >>> import ucdp as u
            >>> const = u.ConstExpr(u.UintType(5, default=5))
            >>> const
            ConstExpr(UintType(5, default=5))
            >>> int(const)
            5
            >>> bool(const)
            True
    """

    type_: BaseType

    _posargs: ClassVar[PosArgs] = ("type_",)

    def __init__(self, type_: BaseType):
        super().__init__(type_=type_)  # type: ignore[call-arg]

    def __int__(self):
        return int(self.type_.default)

    def __getitem__(self, slice_):
        if isinstance(slice_, Expr):
            slice_ = Slice(left=slice_, right=slice_)
        return ConstExpr(self.type_[slice_])


class ConcatExpr(Expr, Light):
    """
    Concatenation.

    Args:
        items: Expressions.

    Attributes:
        type_: Type.

    ???+ bug "Todo"
        * fix inherited_members / Attributes Types

    ??? Example "ConcatExpr Examples"
        Example.

            >>> import ucdp as u
            >>> expr = u.ConcatExpr((
            ...     u.ConstExpr(u.UintType(5, default=5)),
            ...     u.ConstExpr(u.UintType(7, default=1)),
            ...     u.ConstExpr(u.UintType(16, default=3)),
            ... ))
            >>> expr
            ConcatExpr((ConstExpr(UintType(5, default=5)), ... ConstExpr(UintType(16, default=3))))
            >>> int(expr)
            12325
    """

    items: tuple[Expr, ...]

    _posargs: ClassVar[PosArgs] = ("items",)

    def __init__(self, items: tuple[Expr, ...]):
        for item in items:
            if not isinstance(item.type_, BaseScalarType):
                raise ValueError(f"Item {item} type is {item.type_}, but must be a Scalar Type")

        pairs = tuple(ConcatExpr.__iter_values(items))
        default = sum(value << shift for value, shift in pairs)
        width = pairs[-1][1] if pairs else 1
        type_ = UintType(width, default=default)
        super().__init__(items=items, type_=type_)  # type: ignore[call-arg]

    def __int__(self):
        return sum(int(value << shift) for value, shift in self.__iter_values(self.items))

    @staticmethod
    def __iter_values(items: tuple[Expr, ...]) -> Iterator[tuple[int, int]]:
        shift = 0
        for item in items:
            yield item, shift
            shift += item.type_.width  # type: ignore[attr-defined]
        yield 0, shift


class TernaryExpr(Expr, Light):
    """
    TernaryExpr Expression.

    Args:
        cond: BoolOp
        one: Expression
        other: Expression

    Attributes:
        type_: Type.

    ??? Example "TernaryExpr Examples"
        Example.

            >>> import ucdp as u
            >>> cond = u.Signal(u.UintType(2), 'if_s') == u.ConstExpr(UintType(2, default=1))
            >>> one = u.Signal(u.UintType(16, default=10), 'one_s')
            >>> other = u.Signal(u.UintType(16, default=20), 'other_s')
            >>> expr = TernaryExpr(cond=cond, one=one, other=other)
            >>> expr
            TernaryExpr(BoolOp(Signal(UintType(2), 'if_s'), ... Signal(UintType(16, default=20), 'other_s'))
            >>> int(expr)
            20
            >>> expr.type_
            UintType(16, default=10)
    """

    type_: BaseScalarTypes = Field(repr=False)
    cond: BoolOp
    one: Expr
    other: Expr

    _posargs: ClassVar[PosArgs] = ("cond", "one", "other")

    def __init__(self, cond: BoolOp, one: Expr, other: Expr):
        super().__init__(cond=cond, one=one, other=other, type_=one.type_)  # type: ignore[call-arg]

    def __int__(self):
        if bool(self.cond):
            return int(self.one)
        return int(self.other)


class Log2Expr(Expr, Light):
    """
    Ceiling Logarithm to base of 2.

    Args:
        expr: Expression

    Attributes:
        type_: Type.

    ??? Example "Log2Expr Examples"
        Example.

            >>> import ucdp as u
            >>> expr = u.Log2Expr(u.ConstExpr(u.UintType(5, default=5)))
            >>> expr
            Log2Expr(ConstExpr(UintType(5, default=5)))
            >>> int(expr)
            2
            >>> expr.type_
            UintType(5, default=5)
    """

    type_: BaseScalarTypes = Field(repr=False)
    expr: Expr

    _posargs: ClassVar[PosArgs] = ("expr",)

    def __init__(self, expr: Expr):
        super().__init__(expr=expr, type_=expr.type_)  # type: ignore[call-arg]

    def __int__(self):
        return int(math.log(int(self.expr), 2))


class MinimumExpr(Expr, Light):
    """
    Smallest Value.

    Args:
        items: Items

    Attributes:
        type_: Type.

    ??? Example "MinimumExpr Examples"
        Example.

            >>> import ucdp as u
            >>> expr = u.MinimumExpr((
            ...     u.ConstExpr(u.UintType(5, default=5)),
            ...     u.ConstExpr(u.UintType(7, default=1)),
            ...     u.ConstExpr(u.UintType(16, default=3)),
            ... ))
            >>> expr
            MinimumExpr((ConstExpr(UintType(5, default=5)), ... ConstExpr(UintType(16, default=3))))
            >>> int(expr)
            1
            >>> expr.type_
            UintType(5, default=5)
    """

    type_: BaseScalarTypes = Field(repr=False)
    items: tuple[Expr, ...]

    _posargs: ClassVar[PosArgs] = ("items",)

    def __init__(self, items: tuple[Expr, ...]):
        super().__init__(items=items, type_=items[0].type_)  # type: ignore[call-arg]

    def __int__(self):
        return min(int(item) for item in self.items)


class MaximumExpr(Expr, Light):
    """
    Largest Value.

    Args:
        items: Items

    Attributes:
        type_: Type.

    ??? Example "MaximumExpr Examples"
        Example.

            >>> import ucdp as u
            >>> expr = u.MaximumExpr((
            ...     u.ConstExpr(u.UintType(5, default=5)),
            ...     u.ConstExpr(u.UintType(7, default=1)),
            ...     u.ConstExpr(u.UintType(16, default=3)),
            ... ))
            >>> expr
            MaximumExpr((ConstExpr(UintType(5, default=5)), ... ConstExpr(UintType(16, default=3))))
            >>> int(expr)
            5
            >>> expr.type_
            UintType(5, default=5)
    """

    type_: BaseScalarTypes = Field(repr=False)
    items: tuple[Expr, ...]

    _posargs: ClassVar[PosArgs] = ("items",)

    def __init__(self, items: tuple[Expr, ...]):
        super().__init__(items=items, type_=items[0].type_)  # type: ignore[call-arg]

    def __int__(self):
        return max(int(item) for item in self.items)


class RangeExpr(Expr, Light):
    """
    Value Range.

    Attributes:
        type_: Type.
        range_: Range.

    ??? Example "RangeExpr Examples"
        Example.

            >>> import ucdp as u
            >>> range_ = u.RangeExpr(type_=u.UintType(4), range_=range(2, 9))
            >>> range_.type_
            UintType(4)
            >>> range_.range_
            range(2, 9)
    """

    type_: UintType | SintType
    range_: range

    @model_validator(mode="after")
    def __post_init(self) -> "RangeExpr":
        values = tuple(self.range_)
        self.type_.check(values[0], what="Start Value")
        self.type_.check(values[-1], what="End Value")
        return self


def _parse_const(value, reftype: BaseType | None = None) -> ConstExpr:
    strippedvalue = str(value).strip()
    matnum = _RE_CONST.fullmatch(strippedvalue)
    if matnum:
        return __parse_const(reftype=reftype, **matnum.groupdict())
    raise InvalidExpr(repr(value))


def __parse_const(sign, width, is_signed, bnum, num, reftype) -> ConstExpr:
    # Bin/Oct/Dec/Hex Number with given width
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

    # width-less integer
    intnum = int(num)
    if reftype is not None:
        try:
            return ConstExpr(reftype.new(default=intnum))
        except ValidationError:
            pass

    # Integer
    if IntegerType.min_ <= intnum <= IntegerType.max_:
        return ConstExpr(IntegerType(default=intnum))

    # signed vector
    if intnum < 0:
        width = calc_signed_width(intnum)
        return ConstExpr(SintType(width, default=intnum))

    # unsigned vector
    width = calc_unsigned_width(intnum)
    return ConstExpr(UintType(width, default=intnum))
