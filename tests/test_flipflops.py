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
from test2ref import assert_refdata

import ucdp as u


class FlipFlopMod(u.AMod):
    """Module using FlipFlop."""

    def _build(self):
        self.add_port(u.ClkRstAnType(), "main_i")
        self.add_port(u.UintType(2), "ctrl_i")
        self.add_port(u.UintType(8), "data_i")
        self.add_port(u.UintType(8), "data_o")

        self.add_flipflop(u.UintType(8), "data_r", "main_clk_i", "main_rst_an_i", nxt="data_i")
        self.add_flipflop(u.UintType(8), "other_r", "main_clk_i", "main_rst_an_i", ena="ctrl_i == 1", rst="ctrl_i == 0")

        msg = "clk is not of ClkType"
        with raises(ValueError, match=re.escape(msg)):
            self.add_flipflop(u.UintType(8), "noclk_r", "ctrl_i", "main_rst_an_i")

        msg = "rst_an is not of RstAnType"
        with raises(ValueError, match=re.escape(msg)):
            self.add_flipflop(u.UintType(8), "norst_r", "main_clk_i", "ctrl_i")


def test_flipflop(tmp_path, capsys):
    """FlipFlop."""
    mod = FlipFlopMod()

    _print_flipflops(mod)
    assert_refdata(test_flipflop, tmp_path, capsys=capsys)


def _print_flipflops(mod: u.BaseMod):
    rslvr = u.ExprResolver()
    for flipflop in mod.flipflops:
        print("clk", rslvr(flipflop.clk))
        print("rst_an", rslvr(flipflop.rst_an))
        print("rst", rslvr(flipflop.rst) if flipflop.rst else "-")
        print("ena", rslvr(flipflop.ena) if flipflop.ena else "-")
        for item in flipflop:
            print(f"  {item}")
