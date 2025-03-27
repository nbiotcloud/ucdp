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

from .object import Light
from .typebase import BaseType


class StringType(BaseType, Light):
    """
    Native String.

    Example:
    >>> import ucdp as u
    >>> example = u.StringType()
    >>> example
    StringType()
    >>> example = u.StringType(default='data')
    >>> example
    StringType(default='data')
    >>> example[1:3]
    StringType(default='at')
    """

    default: str = ""

    def is_connectable(self, other) -> bool:
        """
        Check For Valid Connection To `other`.

        Connections are only allowed to other :any:`StringType`.

        >>> import ucdp as u
        >>> u.StringType().is_connectable(u.StringType())
        True

        A connection to other types is forbidden.

        >>> u.StringType().is_connectable(u.UintType(1))
        False
        """
        return isinstance(other, StringType)

    def __getitem__(self, slice_):
        """
        Return Sliced Variant.
        """
        return StringType(default=self.default[slice_])
