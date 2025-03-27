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
Tailored Module.

"""

from abc import abstractmethod
from typing import Any, ClassVar

from ._modbuilder import build
from .modbase import BaseMod
from .modfilelist import ModFileLists
from .modutil import get_libpath, get_topmodname, is_tb_from_modname
from .nameutil import join_names
from .object import PrivateField


class ATailoredMod(BaseMod):
    """
    Module Which Is Tailored For Every Use Case By The Parent Module, Mainly The Number And Names Of Ports.

    See :any:`BaseMod` for arguments, attributes and details.

    Due to the frozen instance approach, implementation specific containers have to be implemented
    via `u.field()`.

    The source code files are typically generated next to the parent module of tailored module.
    Also the module name is based on the parent module and extended by the instance name.
    A :any:`ATailoredMod` requires a Mako template mostly. The default template is typically located
    next to the python file of the tailored module.

    Tailored modules have **two** build methods:

    * `_build`
    * `_build_dep`
    * `_build_final`

    Please take the following points into account:

    * `_build` should be used for all **static** code and initialization.
    * Tailored modules should provide `add` methods to tailor the module instance to the needs of
      the parent module.
    * `_build_dep` is called **after** all `add` methods have been called and should be used for all
      **dynamic** aspects which can only be known after the parent module made its adjustments.

    Attributes:
        filelists: Filelists.

    ??? Example "Module Reference Examples"
        Example Definition:

            >>> import logging
            >>> import ucdp as u
            >>> LOGGER = logging.getLogger(__name__)
            >>> class DmxMod(u.ATailoredMod):
            ...     slaves: u.Namespace = u.Field(default_factory=u.Namespace, init=False)
            ...
            ...     def add_slave(self, name, route=None):
            ...         self.slaves[name] = slave = Slave(dmx=self, name=name)
            ...         portname = f"slv_{name}_o"
            ...         self.add_port(u.UintType(16), portname)
            ...         if route:
            ...             self.con(portname, route)
            ...         return slave
            ...
            ...     def _build(self) -> None:
            ...         pass#self.add_port(u.UintType(16), "mst_i")
            ...
            ...     def _build_dep(self):
            ...         if not self.slaves:
            ...             LOGGER.warning("%r: has no APB slaves", self)
            ...
            >>> class Slave(u.NamedObject):
            ...     dmx: u.BaseMod = u.Field(repr=False)

        Example Usage:

            >>> import ucdp as u
            >>> class TopMod(u.AMod):
            ...     def _build(self) -> None:
            ...         dmx = DmxMod(self, 'u_dmx')
            ...         dmx.add_slave('a')
            ...         dmx.add_slave('b')
            >>> top = TopMod()
            >>> top
            <ucdp.modtailored.TopMod(inst='top', libname='ucdp', modname='top')>
            >>> top.get_inst('u_dmx')
            <ucdp.modtailored.DmxMod(inst='top/u_dmx', libname='ucdp', modname='top_dmx')>
            >>> top.get_inst('u_dmx').slaves
            Namespace([Slave(name='a'), Slave(name='b')])
    """

    filelists: ClassVar[ModFileLists] = ()
    """File Lists."""

    _has_build_dep: bool = PrivateField(default=True)
    _has_build_final: bool = PrivateField(default=True)

    @property
    def modname(self) -> str:
        """Module Name."""
        modname = self.basename
        if self.parent:
            return join_names(self.parent.modname, modname)
        return modname

    @property
    def topmodname(self) -> str:
        """Top Module Name."""
        if self.parent:
            return self.parent.topmodname
        return get_topmodname(self)

    @property
    def libpath(self) -> str:
        """Library Path."""
        if self.parent:
            return self.parent.libpath
        return get_libpath(self.__class__)

    @property
    def is_tb(self) -> bool:
        """Determine if module belongs to Testbench or Design."""
        if self.parent:
            return self.parent.is_tb
        return is_tb_from_modname(self.modname)

    @abstractmethod
    def _build(self) -> None:
        """Build."""

    def _build_dep(self):
        """Build Dependent Parts."""

    def _build_final(self):
        """Build Post."""

    def model_post_init(self, __context: Any) -> None:
        """Run Build."""
        if self.parent:
            self.parent.add_inst(self)

        self._build()
        if not self.parent:
            build(self)
