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

"""Module Reference Information."""

from inspect import getfile
from pathlib import Path
from typing import Literal

from pydantic_core import PydanticUndefined

from .consts import PKG_PATHS
from .mod import AMod
from .modbase import BaseMod, ModCls, ModTags
from .modconfigurable import AConfigurableMod
from .modconfigurabletb import AConfigurableTbMod
from .modcore import ACoreMod
from .modgenerictb import AGenericTbMod
from .modtailored import ATailoredMod
from .modtb import ATbMod
from .modtopref import TopModRef
from .object import Object

BASECLSS = (AConfigurableMod, ACoreMod, ATailoredMod, AMod, AGenericTbMod, ATbMod, BaseMod, AConfigurableTbMod)


TbType = Literal["Static", "Generic", ""]


class TopModRefInfo(Object):
    """Module Reference Information."""

    topmodref: TopModRef
    tags: ModTags
    modbasecls: ModCls
    filepath: Path
    is_top: bool
    is_local: bool
    tb: TbType

    @staticmethod
    def create(topmodref: TopModRef, modcls: ModCls, tbmodcls: ModCls | None = None) -> "TopModRefInfo":
        """Create."""
        topmodcls = tbmodcls or modcls
        modfilepath = Path(getfile(modcls))
        return TopModRefInfo(
            topmodref=topmodref,
            tags=topmodcls.tags,
            modbasecls=get_modbasecls(topmodcls),
            filepath=modfilepath,
            is_top=is_top(topmodcls) or bool(tbmodcls),
            is_local=is_local(modfilepath),
            tb=get_tb(topmodcls),
        )


def get_modbasecls(modcls: ModCls) -> type[BaseMod] | None:
    """Determine Module Base Class."""
    for basecls in BASECLSS:
        if issubclass(modcls, basecls):
            return basecls
    return None  # pragma: no cover


def is_local(filepath: Path) -> bool:
    """Determine If Module Is From Local Environment And Not Installed Through A Package."""
    return not any(filepath.is_relative_to(pkg_path) for pkg_path in PKG_PATHS)


def is_top(modcls: ModCls) -> bool:
    """Module is Direct Loadable."""
    if issubclass(modcls, AGenericTbMod):
        return modcls.build_dut.__qualname__ != AGenericTbMod.build_dut.__qualname__
    if issubclass(modcls, AConfigurableMod):
        if modcls.get_default_config is not AConfigurableMod.get_default_config:
            return True
        config_field = modcls.model_fields["config"]
        return config_field.default is not PydanticUndefined
    if issubclass(modcls, (AMod, ATbMod)):
        return True
    return modcls.build_top.__qualname__ != BaseMod.build_top.__qualname__


def get_tb(modcls: ModCls) -> TbType:
    """Module Testbench."""
    if issubclass(modcls, AGenericTbMod):
        return "Generic"
    if issubclass(modcls, ATbMod):
        return "Static"
    return ""
