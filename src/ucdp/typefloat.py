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

"""Scalar Types aka native Types."""

from typing import Any

from .object import Light
from .typebase import BaseType


class FloatType(BaseType, Light):
    """
    Native Floating Point Number.

    Example:
    >>> import ucdp as u
    >>> example = u.FloatType()
    >>> example
    FloatType()
    """

    default: Any = 0

    def is_connectable(self, other) -> bool:
        """
        Check For Valid Connection To `other`.

        Connections are only allowed to other :any:`FloatType`.

        >>> import ucdp as u
        >>> u.FloatType().is_connectable(u.FloatType())
        True

        A connection to other types is forbidden.

        >>> u.FloatType().is_connectable(u.UintType(1))
        False
        """
        return isinstance(other, FloatType)

    def __getitem__(self, slice_):
        """
        Return Sliced Variant.
        """
        raise ValueError("Slicing is not allowed floating point numbers")


class DoubleType(BaseType, Light):
    """
    Native Double Precision Floating Point Number.

    Example:
    >>> import ucdp as u
    >>> example = u.DoubleType()
    >>> example
    DoubleType()
    """

    default: Any = 0

    def is_connectable(self, other) -> bool:
        """
        Check For Valid Connection To `other`.

        Connections are only allowed to other :any:`DoubleType`.

        >>> import ucdp as u
        >>> u.DoubleType().is_connectable(u.DoubleType())
        True

        A connection to other types is forbidden.

        >>> u.DoubleType().is_connectable(u.UintType(1))
        False
        """
        return isinstance(other, DoubleType)

    def __getitem__(self, slice_):
        """
        Return Sliced Variant.
        """
        raise ValueError("Slicing is not allowed on floating point numbers")
