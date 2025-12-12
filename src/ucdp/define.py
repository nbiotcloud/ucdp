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

        >>> import ucdp as u
        >>> u.Define("_MYEFINE")
        Define('_MYEFINE')

        Complex types are NOT supported.

        >>> param = u.Define("_MYEFINE")
        >>> for item in param:
        ...     print(repr(item))
        Define('_MYEFINE')
"""

from typing import Any, ClassVar

from .consts import PAT_DEFINE
from .doc import Doc
from .expr import Expr, _parse_const
from .namespace import Namespace
from .nameutil import split_suffix
from .object import Field, Light, NamedObject, PosArgs
from .typebase import BaseType
from .typescalar import BoolType
from .typestring import StringType


class Define(Expr, NamedObject, Light):
    """Define.

    Args:
        name: Name.

    Attributes:
        doc: Documentation Container
        value (Any): Value.

    ??? Example "Define Examples"
        Example:

            >>> import ucdp as u
            >>> define = u.Define("_MYDEFINE")
            >>> define
            Define('_MYDEFINE')
            >>> define.name
            '_MYDEFINE'
            >>> define.basename
            '_MYDEFINE'
            >>> define.suffix
            ''
            >>> define.doc
            Doc()
            >>> define.value

        If the parameter is casted via `int()` it returns `value` if set, other `type_.default`.

            >>> int(u.Define("_MYDEFINE"))
            0
            >>> int(u.Define("_MYDEFINE", value=4))
            4

        Define are Singleton:

            >>> u.Define("_MYDEFINE") is u.Define("_MYDEFINE")
            True
    """

    name: str = Field(pattern=PAT_DEFINE)
    doc: Doc = Doc()
    value: Any = None

    _posargs: ClassVar[PosArgs] = ("name",)

    def __init__(self, name: str, type_: BaseType | None = None, value=None, **kwargs):
        if type_ is None:
            if value is None:
                type_ = BoolType()
            elif isinstance(value, str):
                type_ = StringType(default=value)
            else:
                type_ = _parse_const(value).type_
        super().__init__(name=name, type_=type_, value=value, **kwargs)  # type: ignore[call-arg]

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


def cast_defines(value: Defines | dict | None) -> Defines | None:
    """
    Cast Defines.

    >>> cast_defines({})
    Defines([])
    >>> defines = cast_defines({'A': None, '_BC': 42, 'DE': 'foo'})
    >>> defines
    Defines([Define('_A'), Define('_BC', value=42), Define('_DE', value='foo')])
    >>> cast_defines(defines)
    Defines([Define('_A'), Define('_BC', value=42), Define('_DE', value='foo')])
    >>> cast_defines(None)
    """
    if value is None:
        return None
    if isinstance(value, Defines):
        value.lock(ensure=True)
        return value
    if isinstance(value, dict):
        defines = Defines()
        for key, val in value.items():
            key = key if key.startswith("_") else f"_{key}"  # noqa: PLW2901
            defines.add(Define(key, value=val))
        defines.lock()
        return defines
    raise ValueError(value)
