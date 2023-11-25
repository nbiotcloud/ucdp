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

"""Scalar Types aka native Types."""


from .object import Light
from .typebase import Type


class StringType(Type, Light):
    """
    Native String.

    Example:
    >>> import ucdp
    >>> example = ucdp.StringType()
    >>> example
    StringType()
    """

    def is_connectable(self, other):
        """
        Check For Valid Connection To `other`.

        Connections are only allowed to other :any:`StringType`.
        The default and isolation value have no influence.

        >>> import ucdp
        >>> ucdp.StringType().is_connectable(ucdp.StringType())
        True

        A connection to other types is forbidden.

        >>> ucdp.StringType().is_connectable(ucdp.UintType(1))
        False
        """
        return isinstance(other, StringType)
