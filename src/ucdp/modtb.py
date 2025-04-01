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

from collections.abc import Sequence
from typing import ClassVar

from .modbase import BaseMod
from .modbasetop import BaseTopMod
from .modfilelist import ModFileLists
from .modutil import get_libpath, get_modname, get_topmodname
from .object import Field
from .test import Test


class ATbMod(BaseTopMod):
    """
    Testbench Module.

    Attributes:
        filelists: File Lists.
        dut_modclss: Testbench is limited to these kind of modules.
        title: Title.
        dut: Module Under Test.
        parent: Parent.
    """

    filelists: ClassVar[ModFileLists] = ()
    """File Lists."""

    title: str = "Testbench"

    parent: BaseMod | None = Field(default=None, init=False)

    @property
    def modname(self) -> str:
        """Module Name."""
        return get_modname(self.__class__)

    @property
    def topmodname(self) -> str:
        """Top Module Name."""
        return get_topmodname(self.__class__)

    @property
    def libpath(self) -> str:
        """Library Path."""
        return get_libpath(self.__class__)

    @property
    def is_tb(self) -> bool:
        """Determine if module belongs to Testbench or Design."""
        return True

    def get_tests(self) -> Sequence[Test]:
        """Get Tests."""
        return ()
