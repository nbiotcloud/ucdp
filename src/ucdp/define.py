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
        >>> for item in param.iter():
        ...     print(repr(item))
        Define('_MYEFINE')
        >>> for item in param.leveliter():
        ...     print(repr(item))
        (0, Define('_MYEFINE'))
"""

from collections.abc import Iterable, Iterator
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

    @property
    def title(self) -> str | None:
        """Alias to `doc.title`."""
        return self.doc.title

    @property
    def descr(self) -> str | None:
        """Alias to `doc.descr`."""
        return self.doc.descr

    @property
    def comment(self) -> str | None:
        """Alias to `doc.comment`."""
        return self.doc.comment

    @property
    def comment_or_title(self) -> str | None:
        """Return `comment` if set, otherwise `title`."""
        return self.doc.comment_or_title

    def __str__(self) -> str:
        return self.name

    def __int__(self):
        return int(self.value or 0)

    def __iter__(self):
        yield self

    def iter(self, filter_=None, stop=None, value=None) -> Iterator:
        """Iterate over Hierarchy."""
        for _, ident in _iters([self], filter_=filter_, stop=stop, value=value):
            yield ident

    def leveliter(self, filter_=None, stop=None, value=None) -> Iterator:
        """Iterate over Hierarchy."""
        yield from _iters([self], filter_=filter_, stop=stop, value=value)


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


def _iters(
    defines: Iterable[Define], filter_=None, stop=None, value=None, level: int = 0
) -> Iterator[tuple[int, Define]]:
    for define in defines:
        if stop and stop(define):
            break

        type_ = define.type_
        if value is not None:
            type_ = type_.new(default=value)
            define = define.new(type_=type_)  # noqa: PLW2901

        if not filter_ or filter_(define):
            yield level, define
