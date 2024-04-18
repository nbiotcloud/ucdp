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
"""Test Loader and Top."""

import ucdp as u
from pytest import raises


def test_load_simple(example_simple):
    """Simple Module."""
    top = u.load("glbl.clk_gate")
    assert top.ref == u.TopModRef(u.ModRef("glbl", "clk_gate"))
    assert top.mod.libname == "glbl"
    assert top.mod.modname == "clk_gate"
    assert [str(mod) for mod in top.iter()] == [
        "<glbl.clk_gate.ClkGateMod(inst='clk_gate', libname='glbl', modname='clk_gate')>"
    ]
    assert [str(mod) for mod in top.get_mods()] == [
        "<glbl.clk_gate.ClkGateMod(inst='clk_gate', libname='glbl', modname='clk_gate')>"
    ]
    assert (
        str(top.get_mod("glbl.clk_gate")) == "<glbl.clk_gate.ClkGateMod(inst='clk_gate', "
        "libname='glbl', modname='clk_gate')>"
    )


def test_load_non_mod(example_bad):
    """Simple Module."""
    with raises(ValueError) as exc:
        u.load("glbl_bad.regf.MyMod")
    assert str(exc.value) == "<class 'glbl_bad.regf.MyMod'> is not a module aka child of <class ucdp.BaseMod>."


def test_load_complex(example_simple):
    """Complexer Module."""
    top = u.load("uart.uart")
    assert top.ref == u.TopModRef(u.ModRef("uart", "uart"))
    assert top.mod.libname == "uart"
    assert top.mod.modname == "uart"
    assert [repr(mod) for mod in top.iter()] == [
        "<uart.uart.UartMod(inst='uart', libname='uart', modname='uart')>",
        "<glbl.clk_gate.ClkGateMod(inst='uart/u_clk_gate', libname='glbl', modname='clk_gate')>",
        "<glbl.regf.RegfMod(inst='uart/u_regf', libname='uart', modname='uart_regf')>",
        "<glbl.clk_gate.ClkGateMod(inst='uart/u_regf/u_clk_gate', libname='glbl', modname='clk_gate')>",
        "<ucdp.modcore.CoreMod(inst='uart/u_core', libname='uart', modname='uart_core')>",
    ]
    assert [repr(mod) for mod in top.iter(unique=True)] == [
        "<uart.uart.UartMod(inst='uart', libname='uart', modname='uart')>",
        "<glbl.clk_gate.ClkGateMod(inst='uart/u_clk_gate', libname='glbl', modname='clk_gate')>",
        "<glbl.regf.RegfMod(inst='uart/u_regf', libname='uart', modname='uart_regf')>",
        "<ucdp.modcore.CoreMod(inst='uart/u_core', libname='uart', modname='uart_core')>",
    ]
    assert [repr(mod) for mod in top.iter(post=True)] == [
        "<glbl.clk_gate.ClkGateMod(inst='uart/u_clk_gate', libname='glbl', modname='clk_gate')>",
        "<glbl.clk_gate.ClkGateMod(inst='uart/u_regf/u_clk_gate', libname='glbl', modname='clk_gate')>",
        "<glbl.regf.RegfMod(inst='uart/u_regf', libname='uart', modname='uart_regf')>",
        "<ucdp.modcore.CoreMod(inst='uart/u_core', libname='uart', modname='uart_core')>",
        "<uart.uart.UartMod(inst='uart', libname='uart', modname='uart')>",
    ]
    assert [repr(mod) for mod in top.iter(post=True, unique=True)] == [
        "<glbl.clk_gate.ClkGateMod(inst='uart/u_clk_gate', libname='glbl', modname='clk_gate')>",
        "<glbl.regf.RegfMod(inst='uart/u_regf', libname='uart', modname='uart_regf')>",
        "<ucdp.modcore.CoreMod(inst='uart/u_core', libname='uart', modname='uart_core')>",
        "<uart.uart.UartMod(inst='uart', libname='uart', modname='uart')>",
    ]
    assert [repr(mod) for mod in top.get_mods()] == [repr(mod) for mod in top.iter(post=True)]
    assert [repr(mod) for mod in top.get_mods("uart.uart*")] == [
        "<glbl.regf.RegfMod(inst='uart/u_regf', libname='uart', modname='uart_regf')>",
        "<ucdp.modcore.CoreMod(inst='uart/u_core', libname='uart', modname='uart_core')>",
        "<uart.uart.UartMod(inst='uart', libname='uart', modname='uart')>",
    ]
    assert (
        repr(top.get_mod("glbl.clk_gate"))
        == "<glbl.clk_gate.ClkGateMod(inst='uart/u_clk_gate', libname='glbl', modname='clk_gate')>"
    )


def test_load_complex_sub(example_simple):
    """Complexer Module with Sub module."""
    top = u.load("uart.uart-glbl.clk_gate")
    assert top.ref == u.TopModRef(u.ModRef("uart", "uart"), sub="glbl.clk_gate")
    assert repr(top.mod) == "<glbl.clk_gate.ClkGateMod(inst='uart/u_clk_gate', libname='glbl', modname='clk_gate')>"


def test_load_tb(example_simple):
    """Complexer Module with Testbench."""
    top = u.load("glbl.regf_tb#uart.uart-uart.uart_regf")
    assert top.ref == u.TopModRef(u.ModRef("uart", "uart"), sub="uart.uart_regf", tb=u.ModRef("glbl", "regf_tb"))
    assert repr(top.mod) == (
        "<glbl.regf_tb.RegfTbMod(inst='regf_tb_uart_regf', libname='glbl', modname='regf_tb_uart_regf', "
        "dut=<glbl.regf.RegfMod(inst='uart/u_regf', libname='uart', modname='uart_regf')>)>"
    )
    assert repr(top.mod.dut) == "<glbl.regf.RegfMod(inst='uart/u_regf', libname='uart', modname='uart_regf')>"


def test_load_non_tb(example_simple):
    """Complexer Module with Testbench - Non-TB."""
    with raises(ValueError) as exc:
        u.load("glbl.regf#uart.uart-uart.uart_regf")
    assert str(exc.value) == "<class 'glbl.regf.RegfMod'> is not a testbench module aka child of <class ucdp.ATbMod>."
