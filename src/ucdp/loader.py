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
Loader.

* [load()][ucdp.loader.load] is one and only method to pickup and instantiate the topmost hardware module.
"""

from collections.abc import Iterable
from functools import lru_cache
from pathlib import Path

from ._modclsloader import _load_modcls as _load
from .finder import find
from .logging import LOGGER
from .modbase import BaseMod
from .moditer import get_mod
from .modref import ModRef
from .modtb import AGenericTbMod
from .modtopref import TopModRef
from .nameutil import didyoumean
from .top import Top
from .util import extend_sys_path


def load(topmodref: TopModRef | str, paths: Iterable[Path] | None = None) -> Top:
    """
    Load Module from ``topmodref`` and return :any:`Top`.

    In case of a given ``topref.sub`` search for a submodule named ``sub`` within the
    module hierarchy of ``topmod`` using :any:`Top.get_mod()`.

    In case of a given ``tb`` search for a testbench ``tb`` and pair it.

    Args:
        topmodref: Items.

    Keyword Args:
        paths: Additional Search Paths for Python Modules. UCDP_PATHS environment variable by default.

    Returns:
        Top: Top
    """
    with extend_sys_path(paths):
        topmodref = TopModRef.cast(topmodref)
        mod = _load_topmod(topmodref)
        return Top(ref=topmodref, mod=mod)


@lru_cache
def _load_topmod(ref: TopModRef) -> BaseMod:
    LOGGER.info("Loading %r", str(ref))

    modcls = _load_modcls(ref.top)
    mod = _build_top(modcls)
    if ref.sub:
        mod = get_mod(mod, ref.sub)
    if ref.tb:
        tbcls = _load_modcls(ref.tb)
        if not issubclass(tbcls, AGenericTbMod):
            raise ValueError(f"{tbcls} is not a testbench module aka child of <class ucdp.AGenericTbMod>.")
        return tbcls.build_tb(mod)
    return mod


@lru_cache
def _build_top(modcls, **kwargs):
    return modcls.build_top(**kwargs)


@lru_cache
def _load_modcls(modref: ModRef) -> type[BaseMod]:
    """Load Module Class."""
    try:
        return _load(modref)
    except NameError as exc:
        modrefs = [str(info.modref) for info in find(variants=True)]
        dym = didyoumean(str(modref), modrefs)
        raise NameError(f"{exc!s}{dym}") from None
