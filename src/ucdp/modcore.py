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
Core Module.
"""

from typing import ClassVar

from .modbase import BaseMod
from .modfilelist import ModFileLists
from .nameutil import join_names
from .object import model_validator


class ACoreMod(BaseMod):
    """
    Intermediate Module Hierarchy.

    See [BaseMod][ucdp.modbase.BaseMod] for arguments, attributes and details.

    A [ACoreMod][uart_lib.uart.UartCoreMod] should be use to create intermediate module hierarchies.
    [ACoreMod][uart_lib.uart.UartCoreMod] do **not** have a `_build` method. They have to be built by the parent module.

    The source code files are typically generated/located next to the parent module of core module.
    Remember to set the `gen` attribute accordingly to control the file generation.
    Also the module name is based on the parent module and extended by the instance name.
    A [ACoreMod][uart_lib.uart.UartCoreMod] can have a Mako template.

    Attributes:
        filelists: File Lists.
        parent: parent module.
    """

    filelists: ClassVar[ModFileLists] = ()
    """File Lists."""

    parent: BaseMod

    @property
    def modname(self) -> str:
        """Module Name."""
        return join_names(self.parent.modname, self.basename)

    @property
    def libname(self) -> str:
        """Library Name."""
        return self.libpath.name

    @property
    def libpath(self) -> str:
        """Library Path."""
        return self.parent.libpath

    @property
    def topmodname(self) -> str:
        """Top Module Name."""
        return self.parent.topmodname

    @property
    def is_tb(self) -> bool:
        """Determine if module belongs to Testbench or Design."""
        return self.parent.is_tb

    @model_validator(mode="after")
    def __post_init(self) -> "ACoreMod":
        self.parent.add_inst(self)
        return self
