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
Expression Engine.
"""

import math
import operator
from collections.abc import Callable, Iterator

from .object import Field, LightObject, model_validator
from .slices import Slice
from .typebase import BaseScalarType, BaseType
from .typescalar import SintType, UintType

# TODO: check for BaseScalarType


class Expr(LightObject):
    """Base Class for all Expressions.

    Attributes:
        type_: Type.
    """

    type_: BaseType = Field(repr=False)

    def __lt__(self, other):
        if not isinstance(other, Expr):
            return NotImplemented
        return BoolOp(self, operator.lt, "<", other)

    def __le__(self, other):
        if not isinstance(other, Expr):
            return NotImplemented
        return BoolOp(self, operator.le, "<=", other)

    def __eq__(self, other):
        if not isinstance(other, Expr):
            return NotImplemented
        return BoolOp(self, operator.eq, "==", other)

    def __ne__(self, other):
        if not isinstance(other, Expr):
            return NotImplemented
        return BoolOp(self, operator.ne, "!=", other)

    def __ge__(self, other):
        if not isinstance(other, Expr):
            return NotImplemented
        return BoolOp(self, operator.ge, ">=", other)

    def __gt__(self, other):
        if not isinstance(other, Expr):
            return NotImplemented
        return BoolOp(self, operator.gt, ">", other)

    def __add__(self, other) -> "Op":
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(self, operator.add, "+", other)

    def __sub__(self, other) -> "Op":
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(self, operator.sub, "-", other)

    def __mul__(self, other) -> "Op":
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(self, operator.mul, "*", other)

    def __floordiv__(self, other) -> "Op":
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(self, operator.floordiv, "//", other)

    def __mod__(self, other) -> "Op":
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(self, operator.mod, "%", other)

    def __pow__(self, other) -> "Op":
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(self, operator.pow, "**", other)

    def __lshift__(self, other) -> "Op":
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(self, operator.lshift, "<<", other)

    def __rshift__(self, other) -> "Op":
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(self, operator.rshift, ">>", other)

    def __or__(self, other) -> "Op":
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(self, operator.or_, "|", other)

    def __and__(self, other) -> "Op":
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(self, operator.and_, "&", other)

    def __xor__(self, other) -> "Op":
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(self, operator.xor, "^", other)

    def __radd__(self, other) -> "Op":
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(other, operator.add, "+", self)

    def __rsub__(self, other) -> "Op":
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(other, operator.sub, "-", self)

    def __rmul__(self, other) -> "Op":
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(other, operator.mul, "*", self)

    def __rfloordiv__(self, other) -> "Op":
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(other, operator.floordiv, "//", self)

    def __rmod__(self, other) -> "Op":
        return Op(other, operator.mod, "%", self)

    def __rpow__(self, other) -> "Op":
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(other, operator.pow, "**", self)

    def __rlshift__(self, other) -> "Op":
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(other, operator.lshift, "<<", self)

    def __rrshift__(self, other) -> "Op":
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(other, operator.rshift, ">>", self)

    def __ror__(self, other) -> "Op":
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(other, operator.or_, "|", self)

    def __rand__(self, other) -> "Op":
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(other, operator.and_, "&", self)

    def __rxor__(self, other) -> "Op":
        if not isinstance(other, Expr):
            return NotImplemented
        return Op(other, operator.xor, "^", self)

    def __abs__(self) -> "SOp":
        return SOp(oper=operator.abs, sign="abs(", one=self, postsign=")")

    def __invert__(self) -> "SOp":
        return SOp(oper=operator.inv, sign="~", one=self)

    def __neg__(self) -> "SOp":
        return SOp(oper=operator.neg, sign="-", one=self)

    def __getitem__(self, slice_):
        slice_ = Slice.cast(slice_)
        return SliceOp(one=self, slice_=slice_)


class Op(Expr):
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

    _posargs: tuple[str, ...] = ("left", "sign", "right")

    def __init__(self, left: Expr, oper: Callable, sign: str, right: Expr):
        super().__init__(left=left, oper=oper, sign=sign, right=right, type_=left.type_)  # type: ignore[call-arg]

    def __int__(self):
        return int(self.oper(int(self.left), int(self.right)))


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

    def __bool__(self):
        return bool(self.oper(int(self.left), int(self.right)))


class SOp(Expr):
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

    _posargs: tuple[str, ...] = ("sign", "one")

    def __init__(self, oper: Callable, sign: str, one: Expr, postsign: str = ""):
        super().__init__(oper=oper, sign=sign, one=one, postsign=postsign, type_=one.type_)  # type: ignore[call-arg]

    def __int__(self):
        return self.oper(int(self.one))


class SliceOp(Expr):
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

    _posargs: tuple[str, ...] = ("one", "slice_")

    def __init__(self, one: Expr, slice_: Slice):
        super().__init__(one=one, slice_=slice_, type_=one.type_[slice_])  # type: ignore[call-arg]

    def __int__(self):
        return int(self.one.type_[self.slice_].default)


class ConstExpr(Expr):
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

    _posargs: tuple[str, ...] = ("type_",)

    def __init__(self, type_: BaseType):
        super().__init__(type_=type_)  # type: ignore[call-arg]

    def __int__(self):
        return int(self.type_.default)

    def __getitem__(self, slice_):
        return ConstExpr(self.type_[slice_])


class ConcatExpr(Expr):
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
            >>> expr.type_
            UintType(28, default=12325)
    """

    items: tuple[Expr, ...]

    _posargs: tuple[str, ...] = ("items",)

    def __init__(self, items: tuple[Expr, ...]):
        pairs = tuple(ConcatExpr.__iter_values(items))
        default = sum(value << shift for value, shift in pairs)
        width = pairs[-1][1] if pairs else 1
        type_ = UintType(width, default=default)
        super().__init__(items=items, type_=type_)  # type: ignore[call-arg]

    def __int__(self):
        return sum(value << shift for value, shift in self.__iter_values(self.items))

    @staticmethod
    def __iter_values(items: tuple[Expr, ...]) -> Iterator[tuple[int, int]]:
        shift = 0
        for item in items:
            if isinstance(item, int):
                yield item, shift
                shift += 32
            else:
                # TODO: fix type issue
                yield int(item), shift  # type: ignore[call-overload]
                shift += item.type_.width  # type: ignore[attr-defined]
        yield 0, shift


class TernaryExpr(Expr):
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

    type_: BaseScalarType = Field(repr=False)
    cond: BoolOp
    one: Expr
    other: Expr

    _posargs: tuple[str, ...] = ("cond", "one", "other")

    def __init__(self, cond: BoolOp, one: Expr, other: Expr):
        super().__init__(cond=cond, one=one, other=other, type_=one.type_)  # type: ignore[call-arg]

    def __int__(self):
        if bool(self.cond):
            return int(self.one)
        return int(self.other)


class Log2Expr(Expr):
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

    type_: BaseScalarType = Field(repr=False)
    expr: Expr

    _posargs: tuple[str, ...] = ("expr",)

    def __init__(self, expr: Expr):
        super().__init__(expr=expr, type_=expr.type_)  # type: ignore[call-arg]

    def __int__(self):
        return int(math.log(int(self.expr), 2))


class MinimumExpr(Expr):
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

    type_: BaseScalarType = Field(repr=False)
    items: tuple[Expr, ...]

    _posargs: tuple[str, ...] = ("items",)

    def __init__(self, items: tuple[Expr, ...]):
        super().__init__(items=items, type_=items[0].type_)  # type: ignore[call-arg]

    def __int__(self):
        return min(int(item) for item in self.items)


class MaximumExpr(Expr):
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

    type_: BaseScalarType = Field(repr=False)
    items: tuple[Expr, ...]

    _posargs: tuple[str, ...] = ("items",)

    def __init__(self, items: tuple[Expr, ...]):
        super().__init__(items=items, type_=items[0].type_)  # type: ignore[call-arg]

    def __int__(self):
        return max(int(item) for item in self.items)


class RangeExpr(Expr):
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
