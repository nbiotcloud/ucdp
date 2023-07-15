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

"""
Top Loading.

* :any:`load()` is one and only method to pickup and instantiate the topmost hardware module.
"""
import logging
from functools import lru_cache
from importlib import import_module
from typing import Union

from caseconverter import pascalcase

from .mod.base import BaseMod
from .mod.iter import get_mod
from .mod.mods import ATbMod
from .modref import ModRef
from .top import Top
from .topref import TopRef

_LOGGER = logging.getLogger("ucdp")


def load(topref: Union[TopRef, str]) -> Top:
    """
    Load Module from ``topref`` and return :any:`Top`.

    Args:
        topref (TopRef):

    Load ``topref.top``.

    In case of a given ``topref.sub`` search for a submodule named ``sub`` within the
    module hierarchy of ``topmod`` using :any:`Top.get_mod()`.

    In case of a given ``tb`` search for a testbench ``tb`` and pair it.
    """
    topref = TopRef.convert(topref)
    topmod = _load_topmod(topref)
    return Top(topref, topmod)


@lru_cache
def _load_topmod(topref: TopRef) -> BaseMod:
    _LOGGER.info("Loading %s", topref)

    modcls = _load_modcls(topref.top)
    mod = _build_top(modcls)
    if topref.sub:
        mod = get_mod(mod, str(topref.sub))
    if topref.tb:
        tbcls = _load_modcls(topref.tb)
        if not issubclass(tbcls, ATbMod):
            raise ValueError(f"{tbcls} is not a testbench module")
        return tbcls.build_tb(mod)
    return mod


@lru_cache
def _build_top(modcls, **kwargs):
    return modcls.build_top(**kwargs)


@lru_cache
def _load_modcls(modref: ModRef):
    """Load Module Class."""
    pymodname = f"{modref.pkg}.{modref.mod}" if modref.pkg else modref.mod
    pymod = import_module(pymodname)
    clsname = modref.cls if modref.cls else f"{pascalcase(modref.mod)}Mod"
    return getattr(pymod, clsname)
