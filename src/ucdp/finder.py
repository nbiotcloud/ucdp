#
# MIT License
#
# Copyright (c) 2024 nbiotcloud
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
Finder.
"""

from collections.abc import Iterator

from uniquer import unique

from ._modloader import (
    Paths,
    Patterns,
    TopModRefPat,
    build_top,
    find_modrefs,
    get_topmodrefpats,
    load_modcls,
)
from .iterutil import namefilter
from .modbase import ModCls
from .moditer import get_mods
from .modref import ModRef
from .modtb import AGenericTbMod
from .modtopref import TopModRef
from .modtoprefinfo import TopModRefInfo, is_top
from .util import extend_sys_path


def find(paths: Paths | None = None, patterns: Patterns | None = None, glob: bool = False) -> Iterator[TopModRefInfo]:
    """List All Available Module References."""
    pats = tuple(get_topmodrefpats(patterns))
    infos = unique(_find_infos(paths, pats, glob), key=lambda modrefinfo: str(modrefinfo.topmodref))

    yield from sorted(infos, key=lambda modrefinfo: str(modrefinfo.topmodref))


def _find_infos(paths: Paths | None, pats: tuple[TopModRefPat, ...], glob: bool = False) -> Iterator[TopModRefInfo]:
    with extend_sys_path(paths, use_env_default=True):
        modclsrefs = tuple(find_modrefs())
        for pat in pats:
            if pat.tb:
                # testbench with top
                tbfilter = namefilter(pat.tb)
                for tbmodref in modclsrefs:
                    # filter by name
                    if not tbfilter(str(tbmodref)):
                        continue
                    # load tbmodcls
                    tbmodcls = load_modcls(tbmodref)
                    # skip non-generic testbenches
                    if not issubclass(tbmodcls, AGenericTbMod):
                        continue
                    # search tops
                    modclss = tuple(tbmodcls.dut_modclss)
                    yield from _find_tops(modclsrefs, pat.top, pat.sub, glob, modclss=modclss, tbmodref=tbmodref)
            else:
                # top only
                yield from _find_tops(modclsrefs, pat.top, pat.sub, glob)


def _find_tops(
    modclsrefs: tuple[ModRef, ...],
    toppat: str,
    subpat: str | None,
    glob: bool,
    modclss: tuple[ModCls, ...] | None = None,
    tbmodref: ModRef | None = None,
) -> Iterator[TopModRefInfo]:
    topfilter = namefilter(toppat)
    for topmodref in modclsrefs:
        # filter by name
        if not topfilter(str(topmodref)):
            continue
        topmodcls = load_modcls(topmodref)
        if subpat:
            # skip non-top
            if not is_top(topmodcls):
                continue
            # sub
            try:
                topmod = build_top(topmodcls)
            except Exception:  # noqa: S112
                continue
            for inst in get_mods(topmod, subpat):
                # skip modules, which should not be tested
                if modclss and not isinstance(inst, modclss):
                    continue
                yield _create(TopModRef(tb=tbmodref, top=topmodref, sub=inst.qualname))
        else:
            # skip modules, which should not be tested
            if not glob and modclss and not issubclass(topmodcls, modclss):
                continue
            yield _create(TopModRef(tb=tbmodref, top=topmodref))


def _create(topmodref: TopModRef) -> TopModRefInfo:
    modcls = load_modcls(topmodref.tb or topmodref.top)
    return TopModRefInfo.create(topmodref, modcls)
