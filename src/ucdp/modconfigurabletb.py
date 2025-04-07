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
Testbench Module.
"""

from .config import BaseConfig
from .modbase import BaseMod
from .modtb import ATbMod
from .modutil import get_modname, get_topmodname
from .nameutil import join_names


class AConfigurableTbMod(ATbMod):
    """
    A Testbench Module Which Is Assembled According To A Recipe ([AConfig][ucdp.config.AConfig]).
    """

    config: BaseConfig
    is_default: bool

    def __init__(self, parent: BaseMod | None = None, name: str | None = None, **kwargs):
        is_default = False
        if "config" not in kwargs:
            try:
                kwargs["config"] = self.get_default_config()
                is_default = True
            except NotImplementedError:
                pass
        try:
            is_default = is_default or kwargs["config"].is_default
        except KeyError:
            if parent is not None:
                raise ValueError("'config' is required if 'parent' is given") from None
        super().__init__(parent=parent, name=name, is_default=is_default, **kwargs)  # type: ignore[call-arg]

    @property
    def modname(self) -> str:
        """Module Name."""
        config = self.config
        if config.modname:
            return config.modname
        name = config.name
        modbasename = get_modname(self.__class__)
        if not name and "config" in self.model_fields_set and not self.is_default:
            name = config.unique_name
        return join_names(modbasename, name)

    @property
    def topmodname(self) -> str:
        """Top Module Name."""
        return get_topmodname(self.__class__)

    def get_default_config(self) -> BaseConfig:
        """Create Default Configuration."""
        raise NotImplementedError
