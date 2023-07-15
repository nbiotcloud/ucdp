#
# MIT License
#
# Copyright (c) 2023 nbiotcloud
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
"""Test Module Building."""
import datetime
import re

from pytest import raises

import ucdp
from ucdp import Assign, BitType, ClkRstAnType, Doc, Port, Signal, Slice, SliceOp, UintType


class Ip0Mod(ucdp.AImportedMod):
    """Ip0Mod."""


class Ip1Mod(ucdp.AImportedMod):
    """Ip1Mod."""

    modname = "othermodname"


class LeafMod(ucdp.AMod):
    """Leaf Module."""

    libname = "some"

    def _build(self):
        pass


class Tailored0Mod(ucdp.ATailoredMod):
    """Tailored0Mod."""

    def _build(self):
        LeafMod(self, "u_leaf")


class Tailored1Mod(ucdp.ATailoredMod):
    """Tailored1Mod."""

    libname = "foo"
    copyright_start_year = 2016
    copyright_end_year = 2018

    def _build(self):
        Tailored0Mod(self, "u_tail0")
        ucdp.CoreMod(self, "u_core0")
        LeafMod(self, "u_leaf")

    def _builddep(self):
        Tailored0Mod(self, "u_tail0dep")
        ucdp.CoreMod(self, "u_core1")


class TopMod(ucdp.AMod):
    """Top Module."""

    libname = "mylib"

    def _build(self):
        Tailored0Mod(self, "u_tail0")
        ucdp.CoreMod(self, "u_core0")
        LeafMod(self, "u_leaf")


@ucdp.config()
class MyConfig(ucdp.AConfig):
    """MyConfig."""

    opt = ucdp.field()


@ucdp.config()
class MyVersionConfig(ucdp.AVersionConfig):
    """MyVersionConfig."""

    opt = ucdp.field()


class AFooMod(ucdp.AConfigurableMod):
    """MyConfiguarable."""

    libname = "mylib"

    def _build(self):
        Tailored0Mod(self, "u_tail0")
        ucdp.CoreMod(self, "u_core0")


class MyConfigurableMod(AFooMod):

    """MyConfiguarable."""

    libname = "mylib"


class MyCoreMod(ucdp.CoreMod):

    """My Core."""

    libname = "mylib"


class MyCore2Mod(ucdp.CoreMod):

    """My Core 2."""

    libname = "mylib"
    modname = "my_core2_foo"


class MyTbMod(ucdp.ATbMod):
    """My Testbench."""

    def _build(self):
        pass

    @staticmethod
    def build_dut(**kwargs):
        return TopMod()


def test_impmod0():
    """IP0."""
    ip0 = Ip0Mod()
    assert ip0.modname == "ip0"


def test_impmod1():
    """IP1."""
    ip1 = Ip1Mod()
    assert ip1.modname == "othermodname"


def test_tailored0():
    """Tail."""
    tail1 = Tailored1Mod(modname="tailored1")
    tail0 = tail1.get_inst("u_tail0")
    tail0dep = tail1.get_inst("u_tail0dep")
    core0 = tail1.get_inst("u_core0")
    core1 = tail1.get_inst("u_core1")
    assert tail0.get_inst("..") is tail1
    assert tail1.modname == "tailored1"
    assert tail0.modname == "tailored1_tail0"
    assert tail0dep.modname == "tailored1_tail0dep"
    assert core0.modname == "tailored1_core0"
    assert core1.modname == "tailored1_core1"

    assert tail1.libname == "foo"
    assert tail0.libname == "foo"
    assert tail0dep.libname == "foo"
    assert core0.libname == "foo"
    assert core1.libname == "foo"

    assert tail1.modbasenames == ("tailored1",)
    assert tail0.modbasenames == ("tailored0",)
    assert tail0dep.modbasenames == ("tailored0",)
    assert core0.modbasenames == ("tailored1_core0",)
    assert core1.modbasenames == ("tailored1_core1",)

    assert tail1.copyright_start_year == 2016
    assert tail0.copyright_start_year is None
    assert tail0dep.copyright_start_year is None
    assert core0.copyright_start_year == 2016
    assert core1.copyright_start_year == 2016

    assert tail1.copyright_end_year == 2018
    assert tail0.copyright_end_year == 2018
    assert tail0dep.copyright_end_year == 2018
    assert core0.copyright_end_year == 2018
    assert core1.copyright_end_year == 2018


def test_tailored1():
    """Tail."""
    tail1 = Tailored1Mod(None, "u_topname")
    tail0 = tail1.get_inst("u_tail0")
    tail0dep = tail1.get_inst("u_tail0dep")
    core0 = tail1.get_inst("u_core0")
    core1 = tail1.get_inst("u_core1")
    assert tail1.modname == "topname"
    assert tail0.modname == "topname_tail0"
    assert tail0dep.modname == "topname_tail0dep"
    assert core0.modname == "topname_core0"
    assert core1.modname == "topname_core1"


def test_tailored0_top():
    """Tailored with Top."""
    tail0 = Tailored0Mod()
    assert tail0.copyright_start_year is None
    assert tail0.copyright_end_year is None
    assert tail0.is_tb is False


def test_configurable_defaultconfig():
    """Default Configuration Handling."""
    with raises(ValueError) as raised:
        MyConfigurableMod()
    assert str(raised.value) == "'config' is required if no 'default_config' is provided."

    config = MyConfig("config1", "optB")

    class BlaMod(ucdp.AConfigurableMod):
        """A Configurable Module."""

        default_config = config

        def _build(self):
            pass

    bla = BlaMod()
    assert bla.modname == "bla_config1"
    assert bla.config == config
    assert bla.copyright_start_year is None
    assert bla.copyright_end_year is None


def test_configurable_versionconfig():
    """Version Configuration Handling."""
    config = MyVersionConfig(
        "config1",
        title="Title",
        timestamp=datetime.datetime(2020, 10, 17, 23, 42),
        version="version",
        rand=0x65DDB0631,
        file=__file__,
        opt="optB",
    )

    bla = MyConfigurableMod(config=config)
    assert bla.modname == "my_configurable_config1"
    assert bla.config == config
    assert bla.copyright_start_year is None
    assert bla.copyright_end_year == 2020


def test_top():
    """Top Mod."""
    mod = TopMod()
    tail0 = mod.get_inst("u_tail0")
    leaf = mod.get_inst("u_leaf")

    assert mod.modname == "top"
    assert tail0.modname == "top_tail0"
    assert leaf.modname == "leaf"

    assert mod.libname == "mylib"
    assert tail0.libname == "mylib"
    assert leaf.libname == "some"

    assert mod.modbasenames == ("top",)
    assert tail0.modbasenames == ("tailored0",)
    assert leaf.modbasenames == ("leaf",)


def test_configurable0():
    """Configurable."""
    config = MyConfig("config0", "optA")
    mod = MyConfigurableMod(config=config)
    core0 = mod.get_inst("u_core0")

    assert mod.modname == "my_configurable_config0"
    assert core0.modname == "my_configurable_config0_core0"

    assert mod.libname == "mylib"
    assert core0.libname == "mylib"

    assert mod.modbasenames == ("my_configurable", "afoo")
    assert core0.modbasenames == ("my_configurable_core0", "afoo_core0")


def test_configurable1():
    """Configurable."""
    config = MyConfig("configurable", "optB")
    mod = MyConfigurableMod(config=config)
    core0 = mod.get_inst("u_core0")

    assert mod.modname == "my_configurable"
    assert core0.modname == "my_configurable_core0"

    assert mod.libname == "mylib"
    assert core0.libname == "mylib"

    assert mod.modbasenames == ("my_configurable", "afoo")
    assert core0.modbasenames == ("my_configurable_core0", "afoo_core0")


def test_configurable2():
    """Configurable."""
    with raises(ValueError, match=re.escape("Invalid identifier ''")):
        MyConfig("", "optC")


def test_mycore():
    """My Core."""
    with raises(ValueError):
        MyCoreMod()
    mod = MyCoreMod(modname="my_core")
    assert mod.libname == "mylib"
    assert mod.modname == "my_core"
    assert mod.modbasenames == ("my_core",)
    assert mod.copyright_start_year is None
    assert mod.copyright_end_year is None
    assert mod.is_tb is None

    with raises(ValueError) as raised:
        ucdp.CoreMod()
    assert str(raised.value) == "Please either set 'modname' or 'parent'"
    with raises(ValueError) as raised:
        ucdp.CoreMod(None, "u_foo")
    assert str(raised.value) == "Please either set 'modname' or 'parent'"

    mod = MyCoreMod(modname="core")
    assert mod.libname == "mylib"
    assert mod.modname == "core"
    assert mod.modbasenames == ("my_core",)

    mod = ucdp.CoreMod(None, "u_foo", modname="foo", libname="mylib")
    assert mod.libname == "mylib"
    assert mod.modname == "foo"
    assert mod.modbasenames == ("foo",)

    assert MyCore2Mod().modname == "my_core2_foo"


def test_tb():
    """Test Testbench."""
    top = TopMod()
    tbench = MyTbMod.build_top()

    # assert tb.dut == top  # TODO: #10
    assert tbench.dut.__class__ is top.__class__
    assert tbench.dut.modname == top.modname
    assert tbench.pathstr == "my_tb_top"

    class AllTbMod(ucdp.AMod):
        """Collection of Testbenches."""

        def _build(self):
            tb0 = MyTbMod.build_top()
            tb1 = MyTbMod(Ip0Mod())
            self.add_inst(tb0)
            self.add_inst(tb1)

    alltb = AllTbMod()
    mytbtop = alltb.get_inst("my_tb_top")
    assert mytbtop.pathstr == "my_tb_top"
    mytbip0 = alltb.get_inst("my_tb_ip0")
    assert mytbip0.pathstr == "my_tb_ip0"


def test_tb_nobuild_dut():
    """Testbench module without build_dut."""

    # pylint: disable=abstract-method
    class OneTbMod(ucdp.ATbMod):

        """A Testbench Module"""

    with raises(NotImplementedError) as raised:
        OneTbMod.build_top()
    assert str(raised.value) == (
        "<class 'tests.test_mods.test_tb_nobuild_dut.<locals>.OneTbMod'> "
        "requires implementation of 'def build_dut(self):' or specify dut i.e. 'my_tb#my_mod'"
    )


def test_get_relpath():
    """Test get_relpath."""
    top = TopMod()
    item = top.get_inst("u_tail0/u_leaf")
    assert ucdp.get_relpath(item, top) == ("u_tail0", "u_leaf")
    assert ucdp.get_relpath(top, top) == tuple()
    with raises(ValueError):
        assert ucdp.get_relpath(top, item)


def test_get_relpath_tb():
    """Test get_relpath on Testbench."""

    class TopTbMod(ucdp.ATbMod):
        """Top Testbench."""

        @staticmethod
        def build_dut(**kwargs):
            return TopMod()

        def _build(self):
            pass

    tbench = TopTbMod()
    top = tbench.get_inst("top")
    assert isinstance(top, TopMod)
    item = top.get_inst("u_tail0/u_leaf")
    assert ucdp.get_relpath(top, tbench) == ("top",)
    assert ucdp.get_relpath(item, top) == ("u_tail0", "u_leaf")
    assert ucdp.get_relpath(top, top) == tuple()
    with raises(ValueError):
        assert ucdp.get_relpath(top, item)


def test_get_relpath_sub_tb():
    """Test get_relpath on Sub Testbench."""

    class TopTbMod(ucdp.ATbMod):
        """Top Testbench."""

        @staticmethod
        def build_dut(**kwargs):
            return TopMod().get_inst("u_tail0")

        def _build(self):
            pass

    tbench = TopTbMod()
    tail0 = tbench.get_inst("u_tail0")
    assert isinstance(tail0, Tailored0Mod)
    item = tail0.get_inst("u_leaf")
    assert ucdp.get_relpath(tail0, tbench) == ("u_tail0",)
    assert ucdp.get_relpath(item, tail0) == ("u_leaf",)
    assert ucdp.get_relpath(tail0, tail0) == tuple()
    with raises(ValueError):
        ucdp.get_relpath(tail0, item)


def test_mod_doc():
    """Module Doc."""

    class MyMod(ucdp.AMod):
        """My Module."""

        def _build(self):
            pass

    inst = MyMod()
    assert inst.doc.title is None
    assert inst.doc.descr is None
    assert inst.doc.comment is None

    inst = MyMod(title="mytitle", descr="mydescr", comment="mycomment")
    assert inst.doc.title == "mytitle"
    assert inst.doc.descr == "mydescr"
    assert inst.doc.comment == "mycomment"


def test_mod_doc_cls():
    """Module Doc from Class."""

    class MyMod(ucdp.AMod):
        """My Module."""

        title = "default title"
        descr = "default descr"
        comment = "default comment"

        def _build(self):
            pass

    inst = MyMod()
    assert inst.doc.title == "default title"
    assert inst.doc.descr == "default descr"
    assert inst.doc.comment == "default comment"

    inst = MyMod(title="mytitle", descr="mydescr", comment="mycomment")
    assert inst.doc.title == "mytitle"
    assert inst.doc.descr == "mydescr"
    assert inst.doc.comment == "mycomment"


def test_add_port_or_signal():
    """Test add_port_or_signal."""

    class MyMod(ucdp.AMod):
        """My Module."""

        def _build(self):
            self.add_port_or_signal(ucdp.UintType(8), "foo_i")
            self.add_port_or_signal(ucdp.UintType(8), "foo_o")
            self.add_port_or_signal(ucdp.UintType(8), "foo")

    mod = MyMod()
    assert list(mod.portssignals) == [
        Port(UintType(8), name="foo_i"),
        Port(UintType(8), name="foo_o"),
        Signal(UintType(8), "foo"),
    ]


def _assert_flipflop(bank, clk, rst_an, rst, ena, assigns):
    # pylint: disable=too-many-arguments
    assert bank.clk.name == clk
    assert bank.rst_an.name == rst_an
    assert bank.rst is rst or str(bank.rst.left) == rst
    assert bank.ena is ena or str(bank.ena.left) == ena
    assert list(bank) == assigns


def test_flip_flop():
    """Test add_port_or_signal."""

    class MyMod(ucdp.AMod):
        """My Module."""

        def _build(self):
            self.add_port(ucdp.ClkRstAnType(), "")
            self.add_port(ucdp.UintType(8), "d_i")
            self.add_port(ucdp.UintType(8), "d0_o")
            self.add_port(ucdp.UintType(8), "d1_o")
            self.add_port(ucdp.UintType(5), "g_i")
            self.add_port(ucdp.UintType(3), "g0_o")
            self.add_port(ucdp.UintType(3), "g1_o")
            self.add_port(ucdp.BitType(), "ctrl_i")

            self.add_flipflop(ucdp.UintType(8), "d0_r", nxt="d_i", route="d0_o")
            self.add_flipflop(ucdp.UintType(8), "d1_r", nxt="d_i", route="d1_o", ena="~ctrl_i")
            self.add_flipflop(ucdp.UintType(3), "g0_r", nxt="g_i[3:1]", route="g0_o")
            self.add_flipflop(ucdp.UintType(3), "g1_r", nxt="g_i[3:1]", route="g1_o", ena="ctrl_i", rst="~ctrl_i")
            self.add_flipflop(ucdp.UintType(5), "i_r")

    mod = MyMod()
    assert list(mod.portssignals) == [
        Port(ClkRstAnType(), doc=Doc(title="Clock and Reset")),
        Port(UintType(8), name="d_i"),
        Port(UintType(8), name="d0_o"),
        Port(UintType(8), name="d1_o"),
        Port(UintType(5), name="g_i"),
        Port(UintType(3), name="g0_o"),
        Port(UintType(3), name="g1_o"),
        Port(BitType(), name="ctrl_i"),
        Signal(UintType(8), "d0_r"),
        Signal(UintType(8), "d1_r"),
        Signal(UintType(3), "g0_r"),
        Signal(UintType(3), "g1_r"),
        Signal(UintType(5), "i_r"),
        Signal(UintType(5), "i_nxt_s"),
    ]
    banks = tuple(mod.flipflops)
    assert len(banks) == 3
    _assert_flipflop(
        banks[0],
        "clk_i",
        "rst_an_i",
        None,
        None,
        [
            Assign(Signal(UintType(8), "d0_r"), expr=Port(UintType(8), name="d_i")),
            Assign(Signal(UintType(3), "g0_r"), expr=SliceOp(Port(UintType(5), name="g_i"), Slice("3:1"))),
            Assign(Signal(UintType(5), "i_r"), expr=Signal(UintType(5), "i_nxt_s")),
        ],
    )
    _assert_flipflop(
        banks[1],
        "clk_i",
        "rst_an_i",
        None,
        "SOp('~', Port(BitType(), name='ctrl_i'))",
        [
            Assign(Signal(UintType(8), "d1_r"), expr=Port(UintType(8), name="d_i")),
        ],
    )
    _assert_flipflop(
        banks[2],
        "clk_i",
        "rst_an_i",
        "SOp('~', Port(BitType(), name='ctrl_i'))",
        "Port(BitType(), name='ctrl_i')",
        [Assign(Signal(UintType(3), "g1_r"), expr=SliceOp(Port(UintType(5), name="g_i"), Slice("3:1")))],
    )
