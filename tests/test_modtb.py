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
"""Test Module File Information."""

import re
from typing import Any, ClassVar

import ucdp as u
from pytest import raises


class DutMod(u.ATailoredMod):
    """Example DUT."""

    def _build(self):
        self.add_port(u.ClkRstAnType(), "main_i")
        self.add_port(u.UintType(8), "data_i")
        self.add_port(u.UintType(8), "data_o")


class SubMod(u.AMod):
    """A Sub Module."""

    def _build(self):
        DutMod(self, "u_dut")


class TopMod(u.AMod):
    """A Top Module."""

    def _build(self):
        SubMod(self, "u_sub")
        DutMod(self, "u_dut")


class TbMod(u.ATbMod):
    """A Testbench Module."""

    dut_mods: ClassVar[tuple[Any, ...]] = (DutMod,)

    @classmethod
    def build_dut(cls, **kwargs) -> u.BaseMod:
        """Build DUT."""
        return DutMod()  # type: ignore[call-arg]

    def _build(self):
        dut = self.dut
        dut.con("main_i", "create(main_s)")


class TopTbMod(u.ATbMod):
    """A Top Testbench Module."""

    dut_mods: ClassVar[tuple[Any, ...]] = (TopMod,)

    @classmethod
    def build_dut(cls, **kwargs) -> u.BaseMod:
        """Build DUT."""
        return TopMod()  # type: ignore[call-arg]

    def _build(self):
        pass


def test_basic():
    """Test Basics."""
    tb = TbMod()
    dut = tb.dut
    assert isinstance(dut, DutMod)

    assert tb.modname == "tb_dut"
    assert tb.topmodname == "tb"
    assert tb.libname == "tests"
    assert tb.is_tb is True
    assert tuple(tb.get_tests()) == ()
    assert repr(tb) == (
        "<tests.test_modtb.TbMod(inst='tb_dut', libname='tests', modname='tb_dut', "
        "dut=<tests.test_modtb.DutMod(inst='dut', libname='tests', modname='dut')>)>"
    )
    assert tb.get_modref() == u.ModRef("tests", "test_modtb", modclsname="TbMod")

    assert dut.modname == "dut"
    assert dut.topmodname == "dut"
    assert dut.libname == "tests"
    assert dut.is_tb is False
    assert repr(dut) == "<tests.test_modtb.DutMod(inst='dut', libname='tests', modname='dut')>"
    assert dut.get_modref() == u.ModRef("tests", "test_modtb", modclsname="DutMod")


def test_wrong_mod():
    """Test Wrong Module."""
    msg = (
        "<class 'tests.test_modtb.TbMod'> can only test (<class 'tests.test_modtb.DutMod'>,) modules, "
        "but not <class 'tests.test_modtb.SubMod'> module"
    )
    with raises(TypeError, match=re.escape(msg)):
        TbMod.build_tb(SubMod())


def test_search():
    """Test Search."""
    top = TopMod()
    assert [repr(item) for item in TbMod.search_duts(top)] == [
        "<tests.test_modtb.DutMod(inst='top/u_sub/u_dut', libname='tests', modname='sub_dut')>",
        "<tests.test_modtb.DutMod(inst='top/u_dut', libname='tests', modname='top_dut')>",
    ]
    assert [repr(item) for item in TopTbMod.search_duts(top)] == [
        "<tests.test_modtb.TopMod(inst='top', libname='tests', modname='top')>",
    ]


def test_search_modrefs():
    """Test Mod Ref Search."""
    top = TopMod()
    assert [repr(item) for item in TbMod.search_dut_topmodrefs(top)] == [
        "TopModRef(ModRef('tests', 'test_modtb', modclsname='TopMod'), "
        "sub='tests.sub_dut', tb=ModRef('tests', 'test_modtb', "
        "modclsname='TbMod'))",
        "TopModRef(ModRef('tests', 'test_modtb', modclsname='TopMod'), "
        "sub='tests.top_dut', tb=ModRef('tests', 'test_modtb', "
        "modclsname='TbMod'))",
    ]

    assert [repr(item) for item in TopTbMod.search_dut_topmodrefs(top)] == [
        "TopModRef(ModRef('tests', 'test_modtb', modclsname='TopMod'), "
        "tb=ModRef('tests', 'test_modtb', modclsname='TopTbMod'))",
    ]
