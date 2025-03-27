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
"""Test Module File Information."""

import re

from pytest import raises

import ucdp as u


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
        SubMod(self, "u_sub0")
        SubMod(self, "u_sub1")
        DutMod(self, "u_dut")


class TbMod(u.ATbMod):
    """A Testbench Module."""

    def _build(self):
        mod = DutMod(self, "u_dut")
        mod.con("main_i", "create(main_s)")


class GenTbMod(u.AGenericTbMod):
    """A Testbench Module."""

    dut_modclss: u.ClassVar[u.ModClss] = {DutMod, TopMod}

    @classmethod
    def build_dut(cls, **kwargs) -> u.BaseMod:
        """Build DUT."""
        return DutMod()  # type: ignore[call-arg]

    def _build(self):
        dut = self.dut
        dut.con("main_i", "create(main_s)")


class TopTbMod(u.ATbMod):
    """A Top Testbench Module."""

    dut_modclss: u.ClassVar[u.ModClss] = {TopMod}

    @classmethod
    def build_dut(cls, **kwargs) -> u.BaseMod:
        """Build DUT."""
        return TopMod()  # type: ignore[call-arg]

    def _build(self):
        pass


def test_basic():
    """Test Basics."""
    tb = TbMod()
    assert tb.modname == "tb"
    assert tb.topmodname == "tb"
    assert tb.libname == "tests"
    assert tb.is_tb is True
    assert repr(tb) == "<tests.test_modtb.TbMod(inst='tb', libname='tests', modname='tb')>"
    assert tb.get_modref() == u.ModRef("tests", "test_modtb", modclsname="TbMod")
    assert repr(tb.get_inst("u_dut")) == "<tests.test_modtb.DutMod(inst='tb/u_dut', libname='tests', modname='tb_dut')>"


def test_generic():
    """Test Basics."""
    tb = GenTbMod()
    dut = tb.dut
    assert isinstance(dut, DutMod)

    assert tb.modname == "gen_tb_dut"
    assert tb.topmodname == "gen_tb"
    assert tb.libname == "tests"
    assert tb.is_tb is True
    assert tuple(tb.get_tests()) == ()
    assert repr(tb) == (
        "<tests.test_modtb.GenTbMod(inst='gen_tb_dut', libname='tests', modname='gen_tb_dut', "
        "dut=<tests.test_modtb.DutMod(inst='dut', libname='tests', modname='dut')>)>"
    )
    assert tb.get_modref() == u.ModRef("tests", "test_modtb", modclsname="GenTbMod")

    assert dut.modname == "dut"
    assert dut.topmodname == "dut"
    assert dut.libname == "tests"
    assert dut.is_tb is False
    assert repr(dut) == "<tests.test_modtb.DutMod(inst='dut', libname='tests', modname='dut')>"
    assert dut.get_modref() == u.ModRef("tests", "test_modtb", modclsname="DutMod")


def test_wrong_mod():
    """Test Wrong Module."""
    msg = "<class 'tests.test_modtb.GenTbMod'> can only test"
    with raises(TypeError, match=re.escape(msg)):
        GenTbMod.build_tb(SubMod())
