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
Array Type.
"""
from icdutil.slices import UP, Slice

from ..attrs import ReusedFrozen, field, frozen
from .base import ACompositeType, AType


@frozen
class ArrayType(ACompositeType, ReusedFrozen):

    """
    Array of `type_`.

    Args:
        type_ (AType): Element Type.
        depth (int):    depth.

    Example:

    >>> import ucdp
    >>> mem = ucdp.ArrayType(ucdp.UintType(16), 10)
    >>> mem
    ArrayType(UintType(16), 10)

    Arrays can be nested and combined with all other types.

    >>> class BusType(ucdp.AStructType):
    ...     def _build(self):
    ...         self._add('data', ucdp.UintType(8))
    ...         self._add('valid', ucdp.BitType())
    ...         self._add('accept', ucdp.BitType(), orientation=ucdp.BWD)

    >>> structmatrix = ucdp.ArrayType(ucdp.ArrayType(BusType(), 10), 22)
    >>> structmatrix
    ArrayType(ArrayType(BusType(), 10), 22)

    Systemverilog Declaration:

    Slicing:

    >>> structmatrix[0:15]
    ArrayType(ArrayType(BusType(), 10), 16)
    >>> structmatrix[3]
    ArrayType(BusType(), 10)
    >>> structmatrix[3][3]
    BusType()
    """

    type_: AType = field()
    depth: int = field()
    left: int = field(default=0)

    _yield = False  # Do not yield on iterations

    @property
    def slice_(self):
        """Get Slice of Matrix"""
        return Slice(left=self.left, right=self.depth - 1)

    def is_connectable(self, other):
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
        return isinstance(other, ArrayType) and self.depth == other.depth and self.type_.is_connectable(other.type_)

    def __getitem__(self, slice_):
        slice_ = Slice.cast(slice_, direction=UP)
        if slice_.width == 1:
            return self.type_
        return ArrayType(self.type_, slice_.width, left=slice_.left)

    @property
    def bits(self):
        """Size in Bits."""
        return self.depth * self.type_.bits
