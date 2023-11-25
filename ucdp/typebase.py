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

DOCME

* :any:`Type` - Base Class for all Types
* :any:`ScalarType` - Base Class for all Single Value Types
* :any:`VecType` - Base Class for all vector-mapped Scalars.
* :any:`CompositeType` - Base class for all assembling Types.
"""
from typing import Any, Optional

from icdutil.slices import DOWN, Slice
from pydantic import model_validator

from .object import Light, Object


class Type(Object):
    """
    Base Class for all Types.

    Documentation defaults are empty by default:

    >>> import ucdp
    >>> ucdp.Type().title
    >>> ucdp.Type().descr
    >>> ucdp.Type().comment
    """

    # Defaults
    title: Optional[str] = None
    descr: Optional[str] = None
    comment: Optional[str] = None

    def new(self, **kwargs) -> "Type":
        """Return A Copy With Updated Attributes."""
        data = self.model_dump(exclude_unset=True, exclude_defaults=True)
        data.update(kwargs)
        return self.__class__(**data)

    def is_connectable(self, other: "Type"):
        """
        Check For Valid Connection To `other`.

        This method has to be overwritten.
        """
        raise NotImplementedError()

    def cast(self, other: "Type"):
        """
        How to cast an input of type `self` from a value of type `other`.

        `self = cast(other)`
        """
        return NotImplemented

    @property
    def bits(self):
        """
        Size in Bits.

        This method has to be overwritten.
        """
        raise NotImplementedError()


class ScalarType(Type, Light):
    """
    Base Type For All Native Types.
    """

    width: Any = 1
    default: int = 0

    @model_validator(mode="after")
    def _check_default(self) -> "ScalarType":
        default = self.default
        if default is not None:
            self.check(default, what="default")
        return self

    def check(self, value, what="Value"):
        """
        Check if `value` can be handled by type`.

        >>> import ucdp
        >>> atype = ucdp.ScalarType()
        >>> atype.check(1)
        1
        """
        return value  # pragma: no cover

    def encode(self, value, usedefault=False):
        """
        Encode Value.

        >>> import ucdp
        >>> atype = ucdp.ScalarType()
        >>> atype.encode(1)
        1
        """
        return int(value)

    def get_hex(self, value=None):
        """
        Return Hex Value.

        >>> import ucdp
        >>> ucdp.ScalarType().get_hex()
        """
        return None

    def __getitem__(self, slice_):
        """
        Return Sliced Variant.

        >>> import ucdp
        >>> ucdp.ScalarType()[4]
        Traceback (most recent call last):
            ...
        ValueError: Cannot slice (4) from ScalarType()
        """
        slice_ = Slice.cast(slice_, direction=DOWN)
        raise ValueError(f"Cannot slice ({slice_}) from {self}")

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

    @property
    def bits(self):
        """Size in Bits."""
        return self.width


class VecType(ScalarType):
    """Base Class for all Vector Types."""

    right: Any = 0

    _posargs: tuple[str, ...] = ("width",)

    def __init__(self, width, **kwargs):
        super().__init__(width=width, **kwargs)

    #     @width.validator
    #     def _width_validator(self, attribute, value):
    #         assert not isinstance(value, float)

    #     @default.validator
    #     def _default_validator(self, attribute, value):
    #         self.check(value, what="default")

    @property
    def slice_(self):
        """Slice."""
        return Slice(left=self.right + self.width - 1, right=self.right)


class CompositeType(Type):
    """Base Class For All Composite Types."""
