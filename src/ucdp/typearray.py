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
Array Type.
"""

from typing import Any, ClassVar

from .object import Light, PosArgs
from .slices import UP, Slice, SliceDirection
from .typebase import ACompositeType, BaseType


class ArrayType(ACompositeType, Light):
    """
    Array of `itemtype`.

    Args:
        itemtype (AType): Element Type.
        depth (int):    depth.

    Example:
        >>> import ucdp as u
        >>> mem = u.ArrayType(u.UintType(16), 10)
        >>> mem
        ArrayType(UintType(16), 10)

    Arrays can be nested and combined with all other types.

        >>> class BusType(u.AStructType):
        ...     def _build(self) -> None:
        ...         self._add('data', u.UintType(8))
        ...         self._add('valid', u.BitType())
        ...         self._add('accept', u.BitType(), orientation=u.BWD)

        >>> structmatrix = u.ArrayType(u.ArrayType(BusType(), 10), 22)
        >>> structmatrix
        ArrayType(ArrayType(BusType(), 10), 22)

    Slicing:

        >>> structmatrix.slice_
        Slice('0:21')
        >>> structmatrix[0:15]
        ArrayType(ArrayType(BusType(), 10), 16)
        >>> structmatrix[3]
        ArrayType(BusType(), 10)
        >>> structmatrix[3][3]
        BusType()
    """

    itemtype: BaseType
    depth: Any
    left: Any = None
    right: Any = None
    direction: SliceDirection = UP

    _posargs: ClassVar[PosArgs] = ("itemtype", "depth")

    def __init__(self, itemtype: BaseType, depth: Any, left=None, right=None, direction: SliceDirection = UP):
        if direction is UP:
            if (left == 0) and (right == depth - 1):
                left, right = None, None
        elif (right == 0) and (left == depth - 1):
            left, right = None, None
        super().__init__(itemtype=itemtype, depth=depth, left=left, right=right, direction=direction)  # type: ignore[call-arg]

    @property
    def slice_(self):
        """Get Slice of Matrix."""
        return Slice(left=self.left, right=self.right, width=self.depth, direction=self.direction)

    def is_connectable(self, other) -> bool:
        """
        Check For Valid Connection To `other`.

        Connections are only allowed to other :any:`ArrayType` of the same depth and type.

        >>> from ucdp import ArrayType, UintType, SintType
        >>> ArrayType(UintType(8), 8).is_connectable(ArrayType(UintType(8), 8))
        True
        >>> ArrayType(UintType(8), 8).is_connectable(ArrayType(UintType(8), 9))
        False
        >>> ArrayType(UintType(8), 8).is_connectable(ArrayType(SintType(8), 8))
        False
        """
        return (
            isinstance(other, ArrayType) and self.depth == other.depth and self.itemtype.is_connectable(other.itemtype)
        )

    def __getitem__(self, slice_):
        slice_ = Slice.cast(slice_)
        if slice_.width == 1:
            return self.itemtype
        return self.new(depth=slice_.width, left=slice_.left, right=slice_.right)

    @property
    def bits(self):
        """Size in Bits."""
        return self.depth * self.itemtype.bits
