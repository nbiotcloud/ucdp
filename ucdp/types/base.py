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
Basic Types.
"""

from typing import Any, Optional

from icdutil.slices import DOWN, Slice

from ..attrs import ReusedFrozen, evolve, field, frozen

tailoredtype = frozen


@frozen
class AType:
    """
    Base Class for all Types.


    Documentation defaults are empty by default:

    >>> import ucdp
    >>> ucdp.AType.title
    >>> ucdp.AType.descr
    >>> ucdp.AType.comment
    """

    # Defaults
    title: Optional[str] = None
    descr: Optional[str] = None
    comment: Optional[str] = None
    width: Optional[Any] = None
    min_: Optional[Any] = None
    max_: Optional[Any] = None

    _dynamic = False
    _yield = True

    def new(self, **kwargs) -> "AType":
        """Return A Copy With Updated Attributes."""
        return evolve(self, **kwargs)

    def check(self, value, what="Value"):
        """
        Check if `value` can be handled by type`.

        >>> import ucdp
        >>> atype = ucdp.AType()
        >>> atype.check(1)
        1
        """
        # pylint: disable=unused-argument
        return value  # pragma: no cover

    def encode(self, value, usedefault=False):
        """
        Encode Value.

        >>> import ucdp
        >>> atype = ucdp.AType()
        >>> atype.encode(1)
        1
        """
        # pylint: disable=unused-argument
        return int(value)

    def get_hex(self, value=None):
        """
        Return Hex Value.

        >>> import ucdp
        >>> ucdp.AType().get_hex()
        """
        # pylint: disable=unused-argument
        return None

    def __getitem__(self, slice_):
        """
        Return Sliced Variant.

        >>> import ucdp
        >>> ucdp.AType()[4]
        Traceback (most recent call last):
            ...
        ValueError: Cannot slice (4) from AType()
        """
        slice_ = Slice.cast(slice_, direction=DOWN)
        raise ValueError(f"Cannot slice ({slice_}) from {self}")

    @property
    def bits(self):
        """
        Size in Bits.

        This method has to be overwritten.
        """
        raise NotImplementedError()

    def is_connectable(self, other):
        """
        Check For Valid Connection To `other`.

        This method has to be overwritten.
        """
        raise NotImplementedError()

    def cast(self, other):
        """
        How to cast an input of type `self` from a value of type `other`.

        `self = cast(other)`
        """
        # pylint: disable=unused-argument
        return NotImplemented

    def __contains__(self, item):
        try:
            if isinstance(item, range):
                items = tuple(item)
                self.check(self.encode(items[0]))
                self.check(self.encode(items[-1]))
            else:
                self.check(self.encode(item))
            return True
        except ValueError:
            return False


@frozen
class AScalarType(AType):

    """
    Base Type For All Native Types.

    All subclasses will carry later-on the systemverilog construct 'logic' or 'wire'.
    """

    default: int = field(default=0, kw_only=True)
    width = 1

    @default.validator
    def _default_validator(self, attribute, value):
        # pylint: disable=unused-argument
        self.check(value, what="default")

    def is_connectable(self, other):
        """
        Check For Valid Connection To `other`.

        This method has to be overwritten.
        """
        raise NotImplementedError()

    @property
    def bits(self):
        """Size in Bits."""
        return self.width


@frozen
class AVecType(AScalarType, ReusedFrozen):

    """Base Class for all Vector Types."""

    width = field()
    right = field(default=0, kw_only=True)
    default = field(default=0, kw_only=True)

    @width.validator
    def _width_validator(self, attribute, value):
        # pylint: disable=unused-argument
        assert not isinstance(value, float)

    @default.validator
    def _default_validator(self, attribute, value):
        # pylint: disable=unused-argument
        self.check(value, what="default")

    @property
    def slice_(self):
        """Slice."""
        return Slice(left=self.right + self.width - 1, right=self.right)

    def is_connectable(self, other):
        """
        Check For Valid Connection To `other`.

        This method has to be overwritten.
        """
        raise NotImplementedError()

    @property
    def bits(self):
        """Size in Bits."""
        return self.width


@frozen
class ACompositeType(AType):

    """Base Class For All Composite Types."""

    @property
    def bits(self):
        """Size in Bits."""
        raise NotImplementedError()
