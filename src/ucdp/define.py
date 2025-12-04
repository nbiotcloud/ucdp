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
        >>> u.Define(u.UintType(6), "param_p")
        Define(UintType(6), 'param_p')

        Complex types are NOT supported.

        >>> param = u.Define(u.UintType(6), "param_p")
        >>> for item in param:
        ...     print(repr(item))
        Define(UintType(6), 'param_p')
"""

from typing import Any, ClassVar

from .casting import Casting
from .consts import PAT_IDENTIFIER
from .doc import Doc
from .expr import Expr
from .nameutil import split_suffix
from .object import Field, Light, NamedObject, PosArgs
from .typescalar import AScalarType


class Define(Expr, NamedObject, Light):
    """Define.

    Args:
        type_: Type.
        name: Name.

    Attributes:
        doc: Documentation Container
        value (Any): Value.

    ??? Example "Define Examples"
        Example:

            >>> import ucdp as u
            >>> cnt = u.Define(u.UintType(6), "cnt_p")
            >>> cnt
            Define(UintType(6), 'cnt_p')
            >>> cnt.type_
            UintType(6)
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

            >>> int(u.Define(u.UintType(6, default=2), "cnt_p"))
            2
            >>> int(u.Define(u.UintType(6, default=2), "cnt_p", value=4))
            4

        Define are Singleton:

            >>> u.Define(u.UintType(6), "cnt_p") is u.Define(u.UintType(6), "cnt_p")
            True
    """

    type_: AScalarType
    name: str = Field(pattern=PAT_IDENTIFIER)
    doc: Doc = Doc()
    value: Any = None

    _posargs: ClassVar[PosArgs] = ("type_", "name")

    def __init__(self, type_: AScalarType, name: str, **kwargs):
        super().__init__(type_=type_, name=name, **kwargs)  # type: ignore[call-arg]

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
        value = self.value
        if value is None:
            value = self.type_.default
        return int(value or 0)

    def __iter__(self):
        yield self

    def cast(self, other: "Define") -> Casting:
        """Cast self=cast(other)."""
        return None
