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
Loader.

* [load()][ucdp.loader.load] is one and only method to pickup and instantiate the topmost hardware module.
"""

from collections.abc import Iterable
from pathlib import Path

from ._modloader import build_top, find_modrefs, load_modcls
from .logging import LOGGER
from .modbase import BaseMod
from .modgenerictb import AGenericTbMod
from .moditer import get_mod
from .modref import ModRef
from .modtopref import TopModRef
from .modtoprefinfo import get_modbasecls, is_top
from .nameutil import didyoumean
from .top import Top
from .util import extend_sys_path


def load(topmodref: TopModRef | Path | str, paths: Iterable[Path] | None = None) -> Top:
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
    with extend_sys_path(paths, use_env_default=True):
        topmodref = TopModRef.cast(topmodref)
        mod = _load_topmod(topmodref)
        return Top(ref=topmodref, mod=mod)


def _load_topmod(ref: TopModRef) -> BaseMod:
    LOGGER.info("Loading %r", str(ref))

    modcls = _load_modcls_dym(ref.top)
    if not is_top(modcls):
        modbasecls = get_modbasecls(modcls)
        raise ValueError(f"{ref.top} is not a top module as it bases on {modbasecls}")
    mod = build_top(modcls)
    if ref.sub:
        mod = get_mod(mod, ref.sub)
    if ref.tb:
        tbcls = _load_modcls_dym(ref.tb)
        if not issubclass(tbcls, AGenericTbMod):
            raise ValueError(f"{tbcls} is not a testbench module aka child of <class ucdp.AGenericTbMod>.")
        return tbcls.build_tb(mod)
    return mod


def _load_modcls_dym(modref: ModRef) -> type[BaseMod]:
    """Load Module Class."""
    try:
        return load_modcls(modref)
    except NameError as exc:
        modrefs = [str(modref) for modref in find_modrefs()]
        dym = didyoumean(str(modref), modrefs)
        raise NameError(f"{exc!s}{dym}") from None
