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

"""Router."""

import re
from collections.abc import Iterable

from .expr import Expr
from .iterutil import split
from .note import Note
from .object import LightObject, model_validator
from .signal import BaseSignal

_RE_PATH = re.compile(
    r"(?P<beg>(((cast)|(optcast)|(create))\()*)"
    r"(?P<path>((([a-zA-Z0-9_]+)|(\.\.))/)*)?(?P<expr>[^/]+?)"
    r"(?P<end>\)*)"
)


class RoutePath(LightObject):
    """
    Routing Path.

    Attributes:
        expr: Expression
        path: Module Path
        create: Create signal/port referenced by `expr`
        cast: `True` (required), `None` (optional) or `False` (forbidden) type casting.
    """

    expr: str | BaseSignal | Note
    path: str | None = None
    create: bool = False
    cast: bool | None = False

    @model_validator(mode="after")
    def __post_init(self) -> "RoutePath":
        if not (not self.create or not self.cast):
            raise ValueError(f"{self}: [opt]cast() and create() are mutually exclusive.")
        return self

    @property
    def parts(self) -> tuple[str, ...]:
        """Path Parts."""
        if not self.path:
            return ()
        return tuple(self.path.split("/"))

    def __str__(self):
        if self.path:
            res = f"{self.path}/{self.expr}"
        else:
            res = str(self.expr)
        if self.cast is True:
            res = f"cast({res})"
        elif self.cast is None:
            res = f"optcast({res})"
        if self.create:
            res = f"create({res})"
        return res


Routeable = RoutePath | Expr | str | Note
Routeables = Routeable | Iterable[Routeable]


def parse_routepath(value: Routeable, basepath: str | None = None) -> RoutePath:
    """
    Parse Path.

    >>> parse_routepath('clk_i')
    RoutePath(expr='clk_i')
    >>> parse_routepath('u_sub/u_bar/clk_i')
    RoutePath(expr='clk_i', path='u_sub/u_bar')
    >>> parse_routepath('create(port_i)')
    RoutePath(expr='port_i', create=True)
    >>> parse_routepath('cast(port_i)')
    RoutePath(expr='port_i', cast=True)
    >>> parse_routepath('optcast(port_i)')
    RoutePath(expr='port_i', cast=None)
    >>> parse_routepath('u_sub/u_bar/port_i')
    RoutePath(expr='port_i', path='u_sub/u_bar')
    >>> parse_routepath('../port_i')
    RoutePath(expr='port_i', path='..')

    >>> parse_routepath('')
    Traceback (most recent call last):
    ...
    ValueError: Invalid route path ''
    >>> parse_routepath('/')
    Traceback (most recent call last):
      ...
    ValueError: Invalid route path '/'
    >>> parse_routepath('u_sub/u_bar/')
    Traceback (most recent call last):
      ...
    ValueError: Invalid route path 'u_sub/u_bar/'
    >>> parse_routepath('.../')
    Traceback (most recent call last):
      ..
    ValueError: Invalid route path '.../'
    """
    if isinstance(value, RoutePath):
        return value
    if isinstance(value, (Expr, Note)):
        return RoutePath(expr=value, path=basepath or None)
    mat = _RE_PATH.fullmatch(value)
    if mat:
        path = mat.group("path")
        if path:
            path = path[:-1]
        if path and basepath:
            path = f"{basepath}/{path}"
        else:
            path = basepath or path
        path = path or None
        expr = mat.group("expr")
        # create = bool(mat.group("crt"))
        beg = (mat.group("beg") or "").split("(")
        end = (mat.group("end") or "").split(")")
        if len(beg) == len(end):
            create = "create" in beg
            if "optcast" in beg:
                cast = None
            else:
                cast = "cast" in beg
            return RoutePath(expr=expr, path=path, create=create, cast=cast)
    raise ValueError(f"Invalid route path {value!r}")


def parse_routepaths(routepaths: Routeables | None, basepath: str | None = None) -> tuple[RoutePath, ...]:
    """
    Parse `routepaths`.

    >>> parse_routepaths('clk_i')
    (RoutePath(expr='clk_i'),)
    >>> parse_routepaths((RoutePath(expr='clk_i'),))
    (RoutePath(expr='clk_i'),)
    >>> parse_routepaths(RoutePath(expr='clk_i'))
    (RoutePath(expr='clk_i'),)
    >>> parse_routepaths('clk_i; rst_an_i')
    (RoutePath(expr='clk_i'), RoutePath(expr='rst_an_i'))
    >>> parse_routepaths('clk_i, rst_an_i')
    (RoutePath(expr='clk_i, rst_an_i'),)
    """
    if not routepaths:
        return ()
    if isinstance(routepaths, (RoutePath, Expr, Note)):
        return (parse_routepath(routepaths, basepath=basepath),)
    if isinstance(routepaths, str):
        return tuple(parse_routepath(path, basepath=basepath) for path in split(routepaths))
    return tuple(parse_routepath(path, basepath=basepath) for path in routepaths)
