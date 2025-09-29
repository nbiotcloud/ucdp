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

"""Top Reference."""

import re
from pathlib import Path
from typing import ClassVar, Literal, Optional, Union

from pydantic_core import PydanticUndefined

from .mod import AMod
from .modbase import BaseMod, ModCls
from .modconfigurable import AConfigurableMod
from .modgenerictb import AGenericTbMod
from .modref import ModRef
from .modtb import ATbMod
from .object import Field, LightObject, PosArgs
from .pathutil import absolute

RE_TOPMODREF = re.compile(
    # [tb]#
    r"((?P<tb>[a-zA-Z_0-9_\.]+)#)?"
    # top
    r"(?P<top>[a-zA-Z_0-9_\.]+)"
    # [-sub]
    r"(-(?P<sub>[a-zA-Z_0-9_\.]+))?"
)
PAT_TOPMODREF = "[tb_lib.tb#]top_lib.top[-sub_lib.sub]"
RE_MODREF = r"[a-zA-Z][a-zA-Z_0-9]*\.[a-zA-Z][a-zA-Z_0-9]*"


TbType = Literal["Static", "Generic", ""]


class TopModRef(LightObject):
    """
    Top Module Reference.

    Args:
        top: Top Module Reference

    Attributes:
        sub: Sub Module Reference
        tb: Testbench Module Reference

    ??? Example "Top Reference Examples"
        Example:

            >>> import ucdp as u
            >>> u.TopModRef.cast('top_lib.top_mod')
            TopModRef(ModRef('top_lib', 'top_mod'))
            >>> u.TopModRef.cast('top_lib.top_mod-sub_lib.sub_mod')
            TopModRef(ModRef('top_lib', 'top_mod'), sub='sub_lib.sub_mod')
            >>> u.TopModRef.cast('mod_tb_lib.mod_tb#top_lib.top_mod')
            TopModRef(ModRef('top_lib', 'top_mod'), tb=ModRef('mod_tb_lib', 'mod_tb'))
            >>> u.TopModRef.cast(TopModRef(ModRef('top_lib', 'top_mod')))
            TopModRef(ModRef('top_lib', 'top_mod'))

            Invalid Pattern:

            >>> TopModRef.cast('lib.mod:c-ls.1')
            Traceback (most recent call last):
            ..
            ValueError: 'lib.mod:c-ls.1' does not match pattern '[tb_lib.tb#]top_lib.top[-sub_lib.sub]'
    """

    top: ModRef
    sub: str | None = Field(default=None, pattern=RE_MODREF)
    tb: ModRef | None = None

    _posargs: ClassVar[PosArgs] = ("top",)

    def __init__(self, top: ModRef, sub: str | None = None, tb: ModRef | None = None):
        super().__init__(top=top, sub=sub, tb=tb)  # type: ignore[call-arg]

    def __str__(self) -> str:
        result = str(self.top)
        if self.sub:
            result = f"{result}-{self.sub}"
        if self.tb:
            result = f"{self.tb}#{result}"
        return result

    @staticmethod
    def cast(value: Union["TopModRef", Path, str]) -> "TopModRef":
        """Cast `value` to `TopModRef`."""
        if isinstance(value, TopModRef):
            return value

        if isinstance(value, Path):
            path = absolute(value)
            modname = path.stem
            libname = path.parent.name
            return TopModRef(top=ModRef(libname=libname, modname=modname))

        mat = RE_TOPMODREF.fullmatch(value)
        if mat:
            top = ModRef.cast(mat.group("top"))
            sub = mat.group("sub")
            tb = ModRef.cast(mat.group("tb")) if mat.group("tb") else None
            return TopModRef(top=top, sub=sub, tb=tb)

        raise ValueError(f"{value!r} does not match pattern {PAT_TOPMODREF!r}")

    @staticmethod
    def from_mod(mod: BaseMod) -> Optional["TopModRef"]:
        """From Module."""
        if get_tb(mod.__class__) == "Generic":
            tbref = mod.get_modref(minimal=True)
            mod = mod.dut
        else:
            tbref = None
        if not is_top(mod.__class__):
            sub = f"{mod.libname}.{mod.modname}"
            while mod is not None:
                if is_top(mod.__class__):
                    break
                if isinstance(mod, AConfigurableMod):
                    # no standalone configuration
                    mod = None
                    break
                mod = mod.parent
        else:
            sub = None
        if mod is None:
            return None
        modref = mod.get_modref(minimal=True)
        return TopModRef(top=modref, sub=sub, tb=tbref)


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
