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

"""Module Path Support."""
import re
from typing import List, Optional, Tuple

from .attrs import define, evolve, field, frozen
from .expr import ConstExpr, Expr, InvalidExpr, get_idents
from .ident import Ident
from .nameutil import join_names, split_prefix
from .signal import Port
from .types.base import AType
from .types.orientation import Direction
from .util import split

_RE_PATH = re.compile(
    r"(?P<beg>(((cast)|(optcast)|(create))\()*)"
    r"(?P<path>((([a-zA-Z0-9_]+)|(\.\.))/)*)?(?P<expr>[^/]*?)"
    r"(?P<end>\)*)"
)
_UPWARDS = ".."


@frozen
class RoutePath:
    """
    Routing Path.

    Args:
        expr: Expression

    Keyword Args:
        path: Module Path
        create: Create signal/port referenced by `expr`
        cast: `True` (required), `None` (optional) or `False` (forbidden) type casting.
    """

    expr: str = field()
    path: Optional[str] = field(default=None)
    create: bool = field(kw_only=True, default=False)
    cast: Optional[bool] = field(kw_only=True, default=False)

    def __attrs_post_init__(self):
        if not (not self.create or not self.cast):
            raise ValueError(f"{self}: [opt]cast() and create() are mutally exclusive and forbidden.")

    @property
    def parts(self) -> tuple:
        """Path Parts."""
        if self.path:
            return tuple(self.path.split("/"))
        return tuple()

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


def parsepath(routepath, basepath=None):
    """
    Parse Path.

    >>> parsepath('clk_i')
    RoutePath('clk_i')
    >>> parsepath('u_sub/u_bar/clk_i')
    RoutePath('clk_i', path='u_sub/u_bar')
    >>> parsepath('create(port_i)')
    RoutePath('port_i', create=True)
    >>> parsepath('cast(port_i)')
    RoutePath('port_i', cast=True)
    >>> parsepath('optcast(port_i)')
    RoutePath('port_i', cast=None)
    >>> parsepath('')
    RoutePath('')
    >>> parsepath('u_sub/u_bar/')
    RoutePath('', path='u_sub/u_bar')
    >>> parsepath('../')
    RoutePath('', path='..')

    >>> parsepath('/')
    Traceback (most recent call last):
      ..
    ucdp.expr.InvalidExpr: /
    >>> parsepath('.../')
    Traceback (most recent call last):
      ..
    ucdp.expr.InvalidExpr: .../
    """
    if isinstance(routepath, RoutePath):
        return routepath
    if isinstance(routepath, AType):
        return RoutePath(ConstExpr(routepath), basepath or None)
    if isinstance(routepath, Expr):
        return RoutePath(routepath, basepath or None)
    mat = _RE_PATH.fullmatch(routepath)
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
            return RoutePath(expr, path, create=create, cast=cast)
    raise InvalidExpr(routepath)


def parsepaths(routepaths, basepath=None):
    """
    Parse `routepaths`.

    >>> parsepaths('clk_i')
    (RoutePath('clk_i'),)
    >>> parsepaths('clk_i; rst_an_i')
    (RoutePath('clk_i'), RoutePath('rst_an_i'))
    >>> parsepaths('clk_i, rst_an_i')
    (RoutePath('clk_i, rst_an_i'),)
    >>> parsepaths((RoutePath('clk_i, rst_an_i'),))
    (RoutePath('clk_i, rst_an_i'),)
    >>> parsepaths(RoutePath('clk_i, rst_an_i'))
    (RoutePath('clk_i, rst_an_i'),)
    """
    if isinstance(routepaths, (RoutePath, AType, Expr)):
        return (parsepath(routepaths, basepath=basepath),)
    if isinstance(routepaths, str):
        routepaths = [""] if routepaths == "" else split(routepaths)
    return tuple(parsepath(path, basepath=basepath) for path in routepaths or [])


def resolve(mod, routepath):
    """Resolve `routepath` on `mod`."""
    routepath = parsepath(routepath)
    mod = mod.get_inst(routepath.path) if routepath.path else mod
    return mod.parse(routepath.expr)


@define
class Router:

    """The One And Only Router."""

    mod = field(repr=False)
    __routes: List[Tuple[RoutePath, RoutePath]] = field(factory=list)

    def add(self, tpath: RoutePath, spath: RoutePath):
        """Add route from `source` to `tpath`."""
        item = self._create(tpath, spath)
        self.__routes.append(item)

    def flush(self):
        """Create Pending Routes."""
        mod = self.mod
        # pylint: disable=not-an-iterable
        for tpath, spath in self.__routes:
            try:
                tpath, spath = self._create(tpath, spath)
                Router._route(mod, tpath, spath)
            except NameError as err:
                raise NameError(f"{err}\n\nCannot route '{spath}' to '{tpath}' at '{mod.pathstr}'") from None
            except InvalidExpr as err:
                raise InvalidExpr(f"{err}\n{mod}: {tpath} = {spath}") from None
        self.__routes.clear()

    def _create(self, tpath, spath) -> Tuple[RoutePath, RoutePath]:
        if tpath.create:
            if self.__create(spath, tpath):
                tpath = evolve(tpath, create=False)
        elif spath.create:
            if self.__create(tpath, spath):
                spath = evolve(spath, create=False)
        return tpath, spath

    def __create(self, rpath, cpath) -> bool:
        """Create `cpath` based on `rpath`."""
        assert not rpath.create
        assert cpath.create
        mod = self.mod
        # Resolve reference path
        try:
            rmod = mod.get_inst(rpath.path) if rpath.path else mod
            rident = rmod.parse(rpath.expr)
            cmod = mod.get_inst(cpath.path) if cpath.path else mod
        except (ValueError, NameError):
            return False
        self.__create_port_or_signal(cmod, rident, cpath.expr)
        return True

    @staticmethod
    def _route(mod, tpath, spath):
        # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        # Referenced modules
        tmod = mod.get_inst(tpath.path) if tpath.path else mod
        smod = mod.get_inst(spath.path) if spath.path else mod
        # Referenced expression/signal
        texpr = tmod.parse(tpath.expr)
        sexpr = smod.parse(spath.expr)
        tident = None if not isinstance(texpr, Ident) else texpr
        sident = None if not isinstance(sexpr, Ident) else sexpr
        tparts = tpath.parts
        sparts = spath.parts
        # One of the both sides need to exist
        rident = tident or sident
        assert rident is not None
        direction = (
            tident.direction * sident.direction
            if tident and tident.direction is not None and sident and sident.direction is not None
            else rident.direction
        )

        cast = _merge_cast(tpath.cast, spath.cast)
        assert len(tparts) in (0, 1)
        assert len(sparts) in (0, 1)
        if tparts:
            # target is submodule
            assert tparts[0] != ".."
            if sparts:
                assert sparts[0] != ".."
                # source and target are submodules
                tcon = None if tident is None else mod.get_instcons(tmod).get(tident)
                scon = None if sident is None else mod.get_instcons(smod).get(sident)
                if tcon is None and scon is None:
                    modname = split_prefix(tmod.name)[1]
                    name = join_names(modname, rident.name, "s")
                    rsig = mod.add_signal(rident.type_, name, ifdef=rident.ifdef, direction=direction)
                    Router.__routesubmod(mod, tmod, rident, texpr, rsig, tname=tpath.expr, cast=tpath.cast)
                    Router.__routesubmod(mod, smod, rident, sexpr, rsig, tname=spath.expr, cast=spath.cast)
                elif tcon is None:
                    Router.__routesubmod(mod, tmod, rident, texpr, scon, tname=tpath.expr, cast=tpath.cast)
                elif scon is None:
                    Router.__routesubmod(mod, smod, rident, sexpr, tcon, tname=spath.expr, cast=spath.cast)
                else:
                    mod.assign(tcon, scon, cast=cast)
            else:
                tcon = None if tident is None else mod.get_instcons(tmod).get(tident)
                if tcon is None:
                    Router.__routesubmod(mod, tmod, rident, texpr, sexpr, tpath.expr, spath.expr, cast=cast)
                else:
                    if sexpr is None:
                        sexpr = Router.__create_port_or_signal(mod, rident, spath.expr)
                    mod.assign(tcon, sexpr, cast=cast)
        else:
            # source is submodule
            if sparts:
                scon = None if sident is None else mod.get_instcons(smod).get(sident)
                assert sparts[0] != ".."
                if scon is None:
                    Router.__routesubmod(mod, smod, rident, sexpr, texpr, spath.expr, tpath.expr, cast=cast)
                else:
                    if texpr is None:
                        texpr = Router.__create_port_or_signal(mod, rident, tpath.expr)
                    mod.assign(scon, texpr, cast=cast)
            else:
                # connect signals of `mod`
                if texpr is None:
                    texpr = Router.__create_port_or_signal(mod, rident, tpath.expr)
                if sexpr is None:
                    sexpr = Router.__create_port_or_signal(mod, rident, spath.expr)
                mod.assign(texpr, sexpr, cast=cast)

    @staticmethod
    def __routesubmod(mod, submod, rident, texpr, sexpr, tname=None, sname=None, cast=False) -> Expr:
        """
        Route `submod` with `mod`.

        Args:
            mod (BaseMod): Module to route within.
            submod (BaseMod): Submodule. Must not be locked yet.

        Keyword Args:
            rident (Ident): Reference identifier for routing. Must NOT be an expression. Used for reference whenever
                            a new signal is created. Needed if `texpr` or `sident` are `None`.
            texpr (Expr): Target Expression. Must be a :any:`Port`. Port of `submod`. Created if `None`.
            sexpr (Expr): Source Expression. Created if `None`.
            tname (str): Target name. Required if `texpr` is `None`.
            sname (str): Source name. Required if `sexpr` is `None`.
        """
        # pylint: disable=too-many-arguments
        if texpr is None:
            assert tname is not None
            assert rident is not None and rident.type_
            texpr = submod.add_port(rident.type_, tname, ifdef=rident.ifdef)
        if sexpr is None:
            sexpr = Router.__create_port_or_signal(mod, rident, sname)
        if not isinstance(texpr, Port):
            raise RouterError(f"Cannot route {type(texpr)} to module instance {submod}")
        try:
            mod.set_instcon(submod, texpr, sexpr, cast=cast)
        except TypeError as err:
            raise TypeError(f"{mod}: {err}") from None
        return sexpr

    @staticmethod
    def __create_port_or_signal(mod, rexpr, name):
        assert isinstance(rexpr, Ident), "TODO: support expr"  # just need to guess ifdef and direction
        assert name is not None
        assert rexpr is not None and rexpr.type_ is not None, (mod, name)
        type_ = rexpr.type_
        idents = get_idents(rexpr)
        assert idents
        rident = idents[0]
        direction = Direction.from_name(name)
        if direction is not None:
            return mod.add_port(type_, name, ifdef=rident.ifdef, direction=direction)
        return mod.add_signal(type_, name, ifdef=rident.ifdef, direction=rident.direction)


class RouterError(ValueError):
    """Routing Error."""


def _merge_cast(one, other):
    # TODO: get rid of this.
    if one or other:
        return True
    if one is None or other is None:
        return None
    return False
