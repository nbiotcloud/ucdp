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
Expression Resolver.
"""

from .expr import (
    BoolOp,
    ConcatExpr,
    ConstExpr,
    Expr,
    Log2Expr,
    MaximumExpr,
    MinimumExpr,
    Op,
    RangeExpr,
    SliceOp,
    SOp,
    TernaryExpr,
)
from .ident import Ident
from .namespace import Namespace
from .object import Object
from .slices import Slice
from .typebase import BaseScalarType, BaseType
from .typeenum import BaseEnumType
from .typescalar import BitType, BoolType, IntegerType, RailType, SintType, UintType
from .typestring import StringType


class ExprResolver(Object):
    """
    Expression Resolver.

    ??? Example "Maximum Parser Example"
        Basics:

            >>> import ucdp as u
            >>> idents = u.Idents([
            ...     u.Signal(u.UintType(16), 'uint_s'),
            ...     u.Signal(u.SintType(16), 'sint_s'),
            ... ])
            >>> parser = u.ExprParser(namespace=idents)
            >>> expr = parser.parse('uint_s') * parser.const(2)
            >>> expr
            Op(Signal(UintType(16), 'uint_s'), '*', ConstExpr(IntegerType(default=2)))

            >>> resolver = u.ExprResolver(namespace=idents)
            >>> resolver.resolve(expr)
            '(uint_s * 2)'
    """

    namespace: Namespace | None = None

    def resolve(self, expr: Expr) -> str:
        """Resolve.

        Args:
            expr: Expression

        """
        return self._resolve(expr)

    def _resolve(self, expr: Expr) -> str:  # noqa: C901, PLR0911, PLR0912
        if isinstance(expr, Ident):
            return self._resolve_ident(expr)
        if isinstance(expr, Op):
            return self._resolve_op(expr)
        if isinstance(expr, BoolOp):
            return self._resolve_boolop(expr)
        if isinstance(expr, SOp):
            return self._resolve_sop(expr)
        if isinstance(expr, SliceOp):
            return self._resolve_sliceop(expr)
        if isinstance(expr, SOp):
            return self._resolve_sop(expr)
        if isinstance(expr, ConstExpr):
            return self._resolve_constexpr(expr)
        if isinstance(expr, ConcatExpr):
            return self._resolve_concatexpr(expr)
        if isinstance(expr, TernaryExpr):
            return self._resolve_ternaryexpr(expr)
        if isinstance(expr, Log2Expr):
            return self._resolve_log2expr(expr)
        if isinstance(expr, MinimumExpr):
            return self._resolve_minimumexpr(expr)
        if isinstance(expr, MaximumExpr):
            return self._resolve_maximumexpr(expr)
        if isinstance(expr, RangeExpr):
            return self._resolve_rangeexpr(expr)
        raise ValueError(expr)

    def _resolve_ident(self, ident: Ident) -> str:
        # Check if in namespace?
        return ident.name

    def _resolve_op(self, op: Op) -> str:
        left = self._resolve(op.left)
        right = self._resolve(op.right)
        sign = op.sign
        if sign == "//":
            sign = "/"
        return f"({left} {sign} {right})"

    def _resolve_boolop(self, op: BoolOp) -> str:
        left = self._resolve(op.left)
        right = self._resolve(op.right)
        return f"({left} {op.sign} {right})"

    def _resolve_sop(self, op: SOp) -> str:
        one = self._resolve(op.one)
        return f"{op.sign}{one}"

    def _resolve_sliceop(self, op: SliceOp) -> str:
        one = self._resolve(op.one)
        return f"{one}{self._resolve_slice(op.slice_)}"

    def _resolve_slice(self, slice_: Slice) -> str:
        left = slice_.left
        right = slice_.right
        if left == right:
            if isinstance(left, int):
                return f"[{left}]"
            return f"[{self.resolve(left)}]"

        if not isinstance(left, int):
            left = self.resolve(left)
        if not isinstance(right, int):
            right = self.resolve(right)
        if isinstance(left, int) and isinstance(right, int) and right == 0:
            return f"[{left+1}-1:0]"
        return f"[{left}:{right}]"

    def _resolve_concatexpr(self, expr: ConcatExpr) -> str:
        items = ", ".join(self._resolve(item) for item in expr.items)
        return f"{{{items}}}"

    def _resolve_ternaryexpr(self, expr: TernaryExpr) -> str:
        cond = self._resolve(expr.cond)
        one = self._resolve(expr.one)
        other = self._resolve(expr.other)
        return f"{cond} ? {one} : {other}"

    def _resolve_log2expr(self, expr: Log2Expr) -> str:
        raise NotImplementedError

    def _resolve_minimumexpr(self, expr: MinimumExpr) -> str:
        raise NotImplementedError

    def _resolve_maximumexpr(self, expr: MaximumExpr) -> str:
        raise NotImplementedError

    def _resolve_rangeexpr(self, expr: RangeExpr) -> str:
        raise NotImplementedError

    def _resolve_constexpr(self, expr: ConstExpr) -> str:
        try:
            return self._resolve_value(expr.type_)
        except ValueError as exc:
            raise ValueError(f"{expr} {exc}") from None

    def _resolve_value(self, type_: BaseType, value=None) -> str:  # noqa: C901, PLR0911, PLR0912
        if not isinstance(type_, BaseScalarType):
            raise ValueError("")

        # ensure value
        if value is None:
            value = type_.default

        # None
        if value is None:
            return ""

        # Expr
        if isinstance(value, Expr):
            return self.resolve(value)

        while isinstance(type_, BaseEnumType):
            type_ = type_.keytype

        if isinstance(type_, BitType):
            return self._get_bit_value(int(value))

        if isinstance(type_, UintType):
            width = int(type_.width)
            if width < 1:
                raise ValueError(f"Invalid width {width}")
            return self._get_uint_value(value, width)

        if isinstance(type_, SintType):
            width = int(type_.width)
            if width < 1:
                raise ValueError(f"Invalid width {width}")
            return self._get_sint_value(value, width)

        if isinstance(type_, IntegerType):
            return self._get_integer_value(value)

        if isinstance(type_, RailType):
            return self._get_rail_value(int(value))

        if isinstance(type_, BoolType):
            return self._get_bool_value(value)

        if isinstance(type_, StringType):
            return self._get_string_value(value)

        raise ValueError(type_)

    @staticmethod
    def _get_rail_value(value: int) -> str:
        return str(value)

    @staticmethod
    def _get_bit_value(value: int) -> str:
        return str(value)

    @staticmethod
    def _get_uint_value(value: int, width: int) -> str:
        return str(value)

    @staticmethod
    def _get_sint_value(value: int, width: int) -> str:
        return str(value)

    @staticmethod
    def _get_integer_value(value: int) -> str:
        return str(value)

    @staticmethod
    def _get_bool_value(value: bool) -> str:
        return str(value)
