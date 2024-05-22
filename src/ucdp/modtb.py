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
Testbench Module.
"""

from abc import abstractmethod
from collections.abc import Iterator
from typing import Any, ClassVar

from caseconverter import snakecase

from ._modbuilder import build
from .modbase import BaseMod
from .modfilelist import ModFileLists
from .moditer import ModPreIter
from .modtopref import TopModRef
from .modutil import get_libname, get_modname, get_topmodname
from .object import Field
from .test import Test


class ATbMod(BaseMod):
    """
    Testbench Module.

    Attributes:
        filelists: File Lists.
        dut_mods: Testbench is limited to these kind of modules.
        title: Title.
        dut: Module Under Test.
        parent: Parent.


    Create testbench for `dut`.

    The [TopModRef][ucdp.modtopref.TopModRef] and [load()][ucdp.loader.load] function
    allow to wrap any design module with a testbench.

    ??? Example "Module Testbench Examples"
        Example:

            >>> import ucdp as u
            >>> class MyMod(u.AMod):
            ...
            ...     def _build(self):
            ...         self.add_port(u.UintType(4), "data_i")
            ...         self.add_port(u.UintType(4), "data_o")
            ...
            >>> class OtherMod(u.AMod):
            ...
            ...     def _build(self):
            ...         self.add_port(u.UintType(4), "data_i")
            ...         self.add_port(u.UintType(4), "data_o")
            ...
            >>> class GenTbMod(u.ATbMod):
            ...
            ...     def _build(self):
            ...         # Build testbench for self.dut here
            ...         pass
            ...
            ...     @staticmethod
            ...     def build_dut():
            ...         return MyMod()

            >>> tb = GenTbMod()
            >>> tb
            <ucdp.modtb.GenTbMod(inst='gen_tb_my', libname='ucdp', modname='gen_tb_my', dut=<ucdp.modtb.MyMod(...)>)>
            >>> tb.dut
            <ucdp.modtb.MyMod(inst='my', libname='ucdp', modname='my')>
            >>> tb = GenTbMod(OtherMod())
            >>> tb
            <ucdp.modtb.GenTbMod(inst='gen_tb_other', libname='ucdp', modname='...', dut=<ucdp.modtb.OtherMod(...)>)>
            >>> tb.dut
            <ucdp.modtb.OtherMod(inst='other', libname='ucdp', modname='other')>

    [TopModRef][ucdp.modtopref.TopModRef] and [load()][ucdp.loader.load] handle that gracefully and
    allow pairing of testbench and dut on command line and in configuration files.
    """

    filelists: ClassVar[ModFileLists] = ()
    """File Lists."""

    dut_mods: ClassVar[tuple[Any, ...]] = ()
    """Testbench is limited to these kind of modules."""

    title: str = "Testbench"

    dut: BaseMod
    parent: BaseMod | None = Field(default=None, init=False)

    def __init__(self, dut: BaseMod | None = None, name: str | None = None, **kwargs):
        cls = self.__class__
        if dut is None:
            dut = cls.build_dut()
        if not name:
            basename = snakecase(cls.__name__.removesuffix("Mod"))
            name = f"{basename}_{dut.modname}"
        if cls.dut_mods:
            if not isinstance(dut, cls.dut_mods):
                raise TypeError(f"{cls} can only test {cls.dut_mods} modules, but not {dut.__class__} module")
        super().__init__(parent=None, name=name, dut=dut, **kwargs)  # type: ignore[call-arg]

    @property
    def modname(self) -> str:
        """Module Name."""
        modbasename = get_modname(self.__class__)
        return f"{modbasename}_{self.dut.modname}"

    @property
    def topmodname(self) -> str:
        """Top Module Name."""
        return get_topmodname(self.__class__)

    @property
    def libname(self) -> str:
        """Library Name."""
        return get_libname(self.__class__)

    @property
    def is_tb(self) -> bool:
        """Determine if module belongs to Testbench or Design."""
        return True

    @classmethod
    def build_tb(cls, dut, **kwargs) -> "ATbMod":
        """Build Testbench."""
        return cls(dut, **kwargs)

    @classmethod
    def build_dut(cls, **kwargs) -> BaseMod:
        """Build DUT."""
        raise NotImplementedError

    @classmethod
    def search_duts(cls, mod) -> Iterator[BaseMod]:
        """
        Iterate over `topmod` and return modules which can be tested by this testbench.
        """
        yield from ModPreIter(mod, filter_=lambda mod: isinstance(mod, cls.dut_mods), unique=True)

    @classmethod
    def search_dut_topmodrefs(cls, mod) -> Iterator[TopModRef]:
        """
        Iterate over `topmod` and return `TopModRef` for modules which can be tested by this testbench.
        """
        tbref = cls.get_modref()
        topref = mod.get_modref()
        topqualname = mod.qualname
        for dut in cls.search_duts(mod):
            dutqualname = dut.qualname
            if dutqualname != topqualname:
                yield TopModRef(top=topref, sub=dutqualname, tb=tbref)
            else:
                yield TopModRef(top=topref, tb=tbref)

    def get_tests(self) -> Iterator[Test]:
        """
        Yield Tests to be run on design.
        """
        yield from ()

    @abstractmethod
    def _build(self) -> None:
        """Build."""

    def model_post_init(self, __context: Any) -> None:
        """Run Build."""
        self.add_inst(self.dut)
        self._build()
        build(self)

    def __str__(self):
        modref = self.get_modref()
        return f"<{modref}(inst={self.inst!r}, libname={self.libname!r}, modname={self.modname!r}, dut={self.dut!s})>"

    def __repr__(self):
        modref = self.get_modref()
        return f"<{modref}(inst={self.inst!r}, libname={self.libname!r}, modname={self.modname!r}, dut={self.dut!r})>"


class AGenericTbMod(ATbMod):
    """A Generic Testbench which adapts to dut."""
