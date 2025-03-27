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
Basic Types.

DOCME

* :any:`Type` - Base Class for all Types
* :any:`AScalarType` - Base Class for all Single Value Types
* :any:`VecType` - Base Class for all vector-mapped Scalars.
* :any:`CompositeType` - Base class for all assembling Types.
"""

from abc import abstractmethod
from typing import Any, ClassVar

from pydantic import model_validator

from .casting import Casting
from .doc import Doc
from .object import Light, Object, PosArgs
from .slices import DOWN, Slice


class BaseType(Object):
    """
    Base Class for all Types.
    """

    title: str | None = None
    descr: str | None = None
    comment: str | None = None

    @property
    def doc(self) -> Doc:
        """Documentation."""
        return Doc(title=self.title, descr=self.descr, comment=self.comment)

    def is_connectable(self, other: "BaseType"):
        """
        Check For Valid Connection To `other`.

        This method has to be overwritten.
        """
        raise NotImplementedError

    def cast(self, other: "BaseType") -> Casting:
        """
        How to cast an input of type `self` from a value of type `other`.

        `self = cast(other)`
        """
        return None

    @property
    def bits(self):
        """
        Size in Bits.

        This method has to be overwritten.
        """
        raise NotImplementedError

    @abstractmethod
    def __getitem__(self, slice_):
        """
        Return Sliced Variant.
        """


class BaseScalarType(BaseType):
    """
    Base Type For All Native Types.
    """

    default: Any | None = None


class AScalarType(BaseScalarType, Light):
    """
    Abstract Type For All Native Types.
    """

    width: Any = 1

    @model_validator(mode="after")
    def __post_init(self) -> "AScalarType":
        default = self.default
        if default is not None:
            self.check(default, what="default")
        return self

    def check(self, value, what="Value"):
        """
        Check if `value` can be handled by type`.

        >>> import ucdp as u
        >>> atype = u.AScalarType()
        >>> atype.check(1)
        1
        """
        return value  # pragma: no cover

    def encode(self, value, usedefault=False):
        """
        Encode Value.

        >>> import ucdp as u
        >>> atype = u.AScalarType()
        >>> atype.encode(1)
        1
        """
        return int(value)

    def get_hex(self, value=None):
        """
        Return Hex Value.

        >>> import ucdp as u
        >>> u.AScalarType().get_hex()
        """
        return

    def __getitem__(self, slice_):
        """
        Return Sliced Variant.

        >>> import ucdp as u
        >>> u.AScalarType()[4]
        Traceback (most recent call last):
            ...
        ValueError: Cannot slice (4) from AScalarType()
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


class AVecType(AScalarType):
    """Base Class for all Vector Types."""

    default: Any = 0
    """Default Value."""

    right: Any = 0
    """Right Bit Position."""

    logic: bool = True
    """Include X and Z states, not just numeric values."""

    _posargs: ClassVar[PosArgs] = ("width",)

    def __init__(self, width, **kwargs):
        super().__init__(width=width, **kwargs)

    @property
    def slice_(self):
        """Slice."""
        return Slice(width=self.width, right=self.right)


class ACompositeType(BaseType):
    """Base Class For All Composite Types."""
