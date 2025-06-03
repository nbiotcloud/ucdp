# MIT License
#
# Copyright (c) 2025 nbiotcloud
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
"""Create Utilities."""

from pathlib import Path
from typing import Literal

from caseconverter import pascalcase, snakecase, titlecase
from makolator import Datamodel

from .consts import PAT_IDENTIFIER_LOWER
from .generate import get_makolator
from .object import Field, Object

TYPE_CHOICES = [
    "AConfigurableMod",
    "AConfigurableTbMod",
    "AGenericTbMod",
    "AMod",
    "ATailoredMod",
    "ATbMod",
]

TYPE_CHOICES_TB = [
    "AConfigurableTbMod",
    "AGenericTbMod",
    "ATbMod",
]

TB_MAP = {
    "AConfigurableMod": "AGenericTbMod",
    "AMod": "ATbMod",
    "ATailoredMod": "AGenericTbMod",
}


class CreateInfo(Object):
    """Module Skeleton Information."""

    module: str = Field(pattern=PAT_IDENTIFIER_LOWER)
    """Module Name."""

    library: str = Field(pattern=PAT_IDENTIFIER_LOWER)
    """Library Name."""

    regf: bool = False
    """Include Register File."""

    descr: str = ""
    """Description."""

    flavour: Literal["AConfigurableMod", "AConfigurableTbMod", "AGenericTbMod", "AMod", "ATailoredMod", "ATbMod"] = (
        "AMod"
    )
    """Flavour."""

    @property
    def module_pascalcase(self) -> str:
        """Module Name In Pascalcase."""
        return pascalcase(self.module)

    @property
    def module_snakecase(self) -> str:
        """Module Name In Snakecase."""
        return snakecase(self.module)

    @property
    def module_titlecase(self) -> str:
        """Module Name In Titlecase."""
        return titlecase(self.module)

    @property
    def descr_or_default(self) -> str:
        """Module Description Or A Nice Default."""
        if self.descr:
            return self.descr
        return f"{self.module_titlecase} Module"

    @property
    def is_tb(self) -> bool:
        """Module Name In Titlecase."""
        return self.flavour in TYPE_CHOICES_TB


def create(info: CreateInfo, force: bool) -> None:
    """Creates A Module Skeleton Based On `info`."""
    mklt = get_makolator(force=force)
    mklt.datamodel = Datamodel(info=info)
    mklt.gen([Path("mod.py.mako")], dest=Path(f"{info.library}/{info.module}.py"))
