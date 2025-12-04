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
Define.

??? Example "Define Examples"
    Usage:

        >>> from tabulate import tabulate
        >>> import ucdp as u
        >>> u.Define("param_p")
        Define('param_p')

        Complex types are NOT supported.

        >>> param = u.Define("param_p")
        >>> for item in param:
        ...     print(repr(item))
        Define('param_p')
"""

from typing import Any, ClassVar

from .consts import PAT_IDENTIFIER
from .doc import Doc
from .namespace import Namespace
from .nameutil import split_suffix
from .object import Field, Light, NamedObject, PosArgs


class Define(NamedObject, Light):
    """Define.

    Args:
        name: Name.

    Attributes:
        doc: Documentation Container
        value (Any): Value.

    ??? Example "Define Examples"
        Example:

            >>> import ucdp as u
            >>> cnt = u.Define("cnt_p")
            >>> cnt
            Define('cnt_p')
            >>> cnt.name
            'cnt_p'
            >>> cnt.basename
            'cnt'
            >>> cnt.suffix
            '_p'
            >>> cnt.doc
            Doc()
            >>> cnt.value

        If the parameter is casted via `int()` it returns `value` if set, other `type_.default`.

            >>> int(u.Define("cnt_p"))
            0
            >>> int(u.Define("cnt_p", value=4))
            4

        Define are Singleton:

            >>> u.Define("cnt_p") is u.Define("cnt_p")
            True
    """

    name: str = Field(pattern=PAT_IDENTIFIER)
    doc: Doc = Doc()
    value: Any = None

    _posargs: ClassVar[PosArgs] = ("name",)

    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, **kwargs)  # type: ignore[call-arg]

    @property
    def basename(self):
        """Base Name."""
        return split_suffix(self.name)[0]

    @property
    def suffix(self):
        """Suffix."""
        return split_suffix(self.name)[1]

    def __str__(self) -> str:
        return self.name

    def __int__(self):
        return int(self.value or 0)

    def __iter__(self):
        yield self


class Defines(Namespace):
    """Defines."""
