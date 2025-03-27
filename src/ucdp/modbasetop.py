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
Base Top Module.
"""

from abc import abstractmethod
from typing import Any, ClassVar

from ._modbuilder import build
from .modbase import BaseMod
from .modfilelist import ModFileLists
from .modutil import get_libpath, is_tb_from_modname
from .object import PrivateField


class BaseTopMod(BaseMod):
    """Base Class For All Top Modules."""

    filelists: ClassVar[ModFileLists] = ()
    """File Lists."""

    _has_build_final: bool = PrivateField(default=True)

    @abstractmethod
    def _build(self) -> None:
        """Build Type."""

    def _build_final(self) -> None:
        """Build Post."""

    def model_post_init(self, __context: Any) -> None:
        """Run Build."""
        if self.parent:
            self.parent.add_inst(self)

        self._build()
        build(self)

    @property
    def libpath(self) -> str:
        """Library Path."""
        return get_libpath(self.__class__)

    @property
    def is_tb(self) -> bool:
        """Determine if module belongs to Testbench or Design."""
        return is_tb_from_modname(self.modname)
