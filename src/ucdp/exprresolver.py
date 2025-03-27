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
Expression Resolver.
"""

from typing import Any, ClassVar

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
from .ident import Ident, Idents
from .namespace import Namespace
from .note import Note
from .object import Object
from .slices import Slice
from .typearray import ArrayType
from .typebase import BaseScalarType, BaseType
from .typeenum import BaseEnumType
from .typefloat import DoubleType, FloatType
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
            'uint_s * 2'
            >>> resolver.resolve(expr, brackets=True)
            '(uint_s * 2)'
    """

    namespace: Namespace | None = None
    remap: Idents | None = None

    _opremap: ClassVar[dict[str, str]] = {}
    _BRACKETTYPES: tuple[Any, ...] = (Op, BoolOp, SOp, TernaryExpr)

    def __call__(self, expr: Expr, brackets: bool = False) -> str:
        """
        Resolve.

        Args:
            expr: Expression
            brackets: Use brackets if necessary for topmost expr.
        """
        return self._resolve(expr, brackets=brackets)

    def resolve(self, expr: Expr | Note, brackets: bool = False) -> str:
        """
        Resolve.

        Args:
            expr: Expression
            brackets: Use brackets if necessary for topmost expr.
        """
        return self._resolve(expr, brackets=brackets)

    def _resolve(self, expr: Expr | Note, brackets: bool = False) -> str:  # noqa: C901, PLR0912
        if isinstance(expr, Ident):
            resolved = self._resolve_ident(expr)
        elif isinstance(expr, BoolOp):
            resolved = self._resolve_boolop(expr)
        elif isinstance(expr, SOp):
            resolved = self._resolve_sop(expr)
        elif isinstance(expr, Op):
            resolved = self._resolve_op(expr)
        elif isinstance(expr, SliceOp):
            resolved = self._resolve_sliceop(expr)
        elif isinstance(expr, ConstExpr):
            resolved = self._resolve_constexpr(expr)
        elif isinstance(expr, ConcatExpr):
            resolved = self._resolve_concatexpr(expr)
        elif isinstance(expr, TernaryExpr):
            resolved = self._resolve_ternaryexpr(expr)
        elif isinstance(expr, Log2Expr):
            resolved = self._resolve_log2expr(expr)
        elif isinstance(expr, MinimumExpr):
            resolved = self._resolve_minimumexpr(expr)
        elif isinstance(expr, MaximumExpr):
            resolved = self._resolve_maximumexpr(expr)
        elif isinstance(expr, RangeExpr):
            resolved = self._resolve_rangeexpr(expr)
        elif isinstance(expr, Note):
            resolved = self._get_note(expr)
        else:
            raise ValueError(f"{expr!r} is not a valid expression.")
        if brackets and isinstance(expr, self._BRACKETTYPES):
            resolved = f"({resolved})"
        return resolved

    def _resolve_ident(self, ident: Ident) -> str:
        # Remapping of identifier, i.e. on instance port list
        if self.remap is not None:
            if ident.name in self.remap.keys():
                ref = self.remap[ident.name]
                if ref.value is not None and ref.value != ref:
                    # resolve remappend identifier value
                    return self.resolve(ref.value)
                # just use default value
                return self._resolve_value(ident.type_)

        # Namespace checking
        if self.namespace is not None:
            # check if identifier exists in namespace.
            if ident.name not in self.namespace:
                raise ValueError(f"{ident!r} not known within current namespace.")

        return ident.name

    def _resolve_op(self, op: Op) -> str:
        left = self._resolve(op.left, brackets=True)
        right = self._resolve(op.right, brackets=True)
        sign = self._opremap.get(op.sign, op.sign)
        return f"{left} {sign} {right}"

    def _resolve_boolop(self, op: BoolOp) -> str:
        left = self._resolve(op.left, brackets=True)
        right = self._resolve(op.right, brackets=True)
        return f"{left} {op.sign} {right}"

    def _resolve_sop(self, op: SOp) -> str:
        one = self._resolve(op.one)
        return f"{op.sign}{one}{op.postsign}"

    def _resolve_sliceop(self, op: SliceOp) -> str:
        one = self._resolve(op.one)
        return f"{one}{self._resolve_slice(op.slice_, opt=True)}"

    def resolve_slice(self, slice_: Slice, opt: bool = True) -> str:
        """Resolve Slice."""
        return self._resolve_slice(slice_, opt=opt)

    def _resolve_slice(self, slice_: Slice, opt: bool = False) -> str:
        left = slice_.left
        right = slice_.right
        if opt and left is right:
            return f"[{left}]"

        if not isinstance(left, int):
            left = self.resolve(left)
        if not isinstance(right, int):
            right = self.resolve(right)
        return f"[{left}:{right}]"

    def _resolve_concatexpr(self, expr: ConcatExpr) -> str:
        items = ", ".join(self._resolve(item) for item in expr.items)
        return f"{{{items}}}"

    def _resolve_ternaryexpr(self, expr: TernaryExpr) -> str:
        cond = self._resolve(expr.cond, brackets=True)
        one = self._resolve(expr.one, brackets=True)
        other = self._resolve(expr.other, brackets=True)
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

    def resolve_value(self, type_: BaseType, value=None) -> str:
        """Resolve Value."""
        return self._resolve_value(type_, value=value)

    def _resolve_value(self, type_: BaseType, value=None) -> str:  # noqa: C901, PLR0911, PLR0912
        if isinstance(type_, ArrayType):
            # TODO: value
            itemvalue = self._resolve_value(type_.itemtype)
            return self._get_array_value(itemvalue, type_.slice_)

        if not isinstance(type_, (BaseScalarType, StringType, FloatType, DoubleType)):
            raise ValueError(f"Cannot resolve type {type_}")
        if value is None:
            value = type_.default

        if isinstance(type_, StringType):
            return self._get_string_value(value)

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
            return self._get_uint_value(value, type_.width)

        if isinstance(type_, SintType):
            width = int(type_.width)
            if width < 1:
                raise ValueError(f"Invalid width {width}")
            return self._get_sint_value(value, type_.width)

        if isinstance(type_, IntegerType):
            return self._get_integer_value(value)

        if isinstance(type_, RailType):
            return self._get_rail_value(value)

        if isinstance(type_, BoolType):
            return self._get_bool_value(value)

        if isinstance(type_, FloatType):
            return self._get_float_value(value)

        if isinstance(type_, DoubleType):
            return self._get_double_value(value)

        raise AssertionError

    @staticmethod
    def _get_rail_value(value: int) -> str:
        return str(value)

    @staticmethod
    def _get_bit_value(value: int) -> str:
        return str(value)

    @staticmethod
    def _get_uint_value(value: int, width: int | Expr) -> str:
        return f"0x{value:X}"

    @staticmethod
    def _get_sint_value(value: int, width: int | Expr) -> str:
        if value < 0:
            return f"-0x{-value:X}"
        return f"0x{value:X}"

    @staticmethod
    def _get_integer_value(value: int) -> str:
        return str(value)

    @staticmethod
    def _get_bool_value(value: bool) -> str:
        return str(value)

    @staticmethod
    def _get_string_value(value: int) -> str:
        return repr(value)

    @staticmethod
    def _get_note(note: Note) -> str:
        return repr(note.note)

    def _get_array_value(self, itemvalue: str, slice_: Slice) -> str:
        raise NotImplementedError

    @staticmethod
    def _get_float_value(value: float) -> str:
        return f"{value:.1f}"

    @staticmethod
    def _get_double_value(value: float) -> str:
        return f"{value:.1f}"
