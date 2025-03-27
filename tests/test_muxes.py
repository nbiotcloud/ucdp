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


class MuxMod(u.AMod):
    """Module using Multiplexer."""

    def _build(self):
        sel = self.add_signal(u.UintType(3), "sel_s")
        self.add_port(u.UintType(4), "a0_i")
        b0 = self.add_port(u.UintType(4), "b0_i")
        self.add_port(u.UintType(4), "c0_i")
        q0 = self.add_port(u.UintType(4), "q0_o")

        self.add_port(u.UintType(8), "a1_i")
        self.add_port(u.UintType(8), "b1_i")
        self.add_port(u.UintType(8), "c1_i")
        self.add_port(u.UintType(8), "q1_o")

        self.add_port(u.UintType(8), "q2_o")

        mux = self.add_mux("main", title="title", descr="descr", comment="comment")

        mux.set_default("q0_o", u.UintType(4, default=8))
        mux.set("sel_s", "3h1", "q0_o", "a0_i")
        mux.set(sel, "3h2", q0, b0)
        mux.set(sel, "3h4", q0, "c0_i")

        mux.set("sel_s", "3h0", "q1_o", "a1_i")
        mux.set("sel_s", "3h1", "q1_o", "b1_i")
        mux.set_default("q1_o", "c1_i")

        mux = self.add_mux("slim")
        mux.set("sel_s", "3h1", "q2_o", "a1_i")

        mux = self.add_mux("empty")


def test_mux(tmp_path, capsys):
    """Multiplexer."""
    mod = MuxMod()

    mainmux = mod.get_mux("main")
    assert mainmux.name == "main"
    assert mainmux.doc == u.Doc(title="title", descr="descr", comment="comment")
    assert mod.get_mux(mainmux) is mainmux

    emptymux = mod.get_mux("empty")
    assert emptymux.name == "empty"
    assert emptymux.doc == u.Doc()

    msg = "'missing'. Known are 'main', 'slim' and 'empty'."
    with raises(ValueError, match=re.escape(msg)):
        mod.get_mux("missing")

    _print_muxes(mod)
    assert_refdata(test_mux, tmp_path, capsys=capsys)


def _print_muxes(mod: u.BaseMod):
    rslvr = u.ExprResolver()
    for mux in mod.muxes:
        for selexpr, conds in mux:
            print(mux.name, mux.sels)
            sel = rslvr(selexpr)
            for default in mux.defaults():
                print(default)
            for condexpr, assigns in conds.items():
                cond = rslvr(condexpr)
                print(f"  {sel}=={cond}:")
                for assign in assigns:
                    print(f"    {assign}")
        for name, driver in mux.drivers:
            print(f"  {name}: {driver}")
