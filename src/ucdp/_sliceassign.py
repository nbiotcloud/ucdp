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
Driver Tracking.

"""

from functools import cached_property
from typing import Any

from pydantic import computed_field

from .drivers import Source
from .expr import ConcatExpr, ConstExpr, Expr
from .slices import Slice
from .typehelper import BaseScalarTypes

SliceMap = dict[Slice, Expr | None]


class SliceAssign(Expr):
    """Slice Assignment."""

    type_: BaseScalarTypes
    expr: Expr

    @computed_field
    @cached_property
    def _slicemap(self) -> SliceMap:
        return {
            Slice(width=self.type_.width): None,
        }

    def get_expr(self, default: Source | None) -> ConcatExpr:
        """Convert To Concatenate."""
        slicemap = self._slicemap
        exprs = []
        # Create default number in case of missing default or if default is a Note
        if default is None or not isinstance(default, Expr):
            default = ConstExpr(self.type_)
        for slice_, item in sorted(slicemap.items(), key=lambda pair: pair[0].right, reverse=True):
            if item is None:
                item = default[slice_]  # noqa: PLW2901
            exprs.append(item)
        return ConcatExpr(tuple(exprs))

    def set(self, slice_: Slice, expr: Expr, overwrite: bool):
        slicemap = self._slicemap
        width = self.type_.width
        if slice_.left >= width:
            raise ValueError(f"Slice {slice_} exceeds width ({width})")
        # Remove empty/overwritten slices
        for sslice in self._searchpadding(slicemap, slice_, overwrite):
            slicemap.pop(sslice)
        self._addpadding(slicemap, slice_.right - 1, sslice.right)
        slicemap[slice_] = expr
        self._addpadding(slicemap, sslice.left, slice_.left + 1)

    @staticmethod
    def _searchpadding(slicemap: SliceMap, slice_: Slice, overwrite: bool) -> list[Slice]:
        slices = []
        for islice, iitem in slicemap.items():
            if islice.mask & slice_.mask:
                if iitem and not overwrite:
                    raise ValueError(f"Slice {slice_} is already taken by {iitem}")
                slices.append(islice)
        return slices

    @staticmethod
    def _addpadding(slicemap: SliceMap, left: Any, right: Any):
        if left >= right:
            slice_ = Slice(left, right)
            slicemap[slice_] = None
