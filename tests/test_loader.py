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
"""Loader Testing."""
import re

from pytest import raises

import ucdp

# pylint: disable=unused-import
from .fixtures import example_simple

# pylint: disable=redefined-outer-name,unused-argument


def _tolist(items):
    return [str(item) for item in items]


def test_load(example_simple):
    """Load."""
    top = ucdp.load("uart.uart")
    assert isinstance(top, ucdp.Top)
    assert str(top.mod) == "UartMod('uart')"
    assert top.mod.modname == "uart"
    assert top.mod.qualname == "uart.uart"
    assert top.mod.parent is None

    assert _tolist(top.iter()) == [
        "UartMod('uart')",
        "ClkGateMod('uart/u_clkgate')",
        "RegfMod('uart/u_regf')",
        "ClkGateMod('uart/u_regf/u_clk_gate')",
        "CoreMod('uart/u_core')",
    ]
    assert _tolist(top.iter(post=True)) == [
        "ClkGateMod('uart/u_clkgate')",
        "ClkGateMod('uart/u_regf/u_clk_gate')",
        "RegfMod('uart/u_regf')",
        "CoreMod('uart/u_core')",
        "UartMod('uart')",
    ]
    assert _tolist(top.iter(unique=True)) == [
        "UartMod('uart')",
        "ClkGateMod('uart/u_clkgate')",
        "RegfMod('uart/u_regf')",
        "CoreMod('uart/u_core')",
    ]

    assert _tolist(top.get_mods()) == [
        "ClkGateMod('uart/u_clkgate')",
        "ClkGateMod('uart/u_regf/u_clk_gate')",
        "RegfMod('uart/u_regf')",
        "CoreMod('uart/u_core')",
        "UartMod('uart')",
    ]

    assert _tolist(top.get_mods("uart*")) == [
        "RegfMod('uart/u_regf')",
        "CoreMod('uart/u_core')",
        "UartMod('uart')",
    ]

    assert str(top.get_mod("uart")) == "UartMod('uart')"


def test_load_sub(example_simple):
    """Load Sub."""
    top = ucdp.load("uart.uart-regf")
    assert str(top.mod) == "RegfMod('uart/u_regf')"
    assert top.mod.modname == "uart_regf"
    assert top.mod.qualname == "uart.uart_regf"
    assert str(top.mod.parent) == "UartMod('uart')"


def test_load_tb(example_simple):
    """Load Testbench."""
    top = ucdp.load("glbl.regf_tb#uart.uart-regf")
    assert str(top.mod) == "RegfTbMod(RegfMod('uart/u_regf'))"
    assert top.mod.modname == "regf_tb_uart_regf"
    assert top.mod.qualname == "glbl.regf_tb_uart_regf"
    assert str(top.mod.dut) == "RegfMod('uart/u_regf')"


def test_load_no_tb(example_simple):
    """Load Non Testbench."""
    with raises(ValueError, match=re.escape("<class 'glbl.regf.RegfMod'> is not a testbench module")):
        ucdp.load("glbl.regf#uart.uart-regf")
