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
"""Test Loader and Top."""

import ucdp as u


def test_load_simple(example_simple):
    """Simple Module."""
    top = u.load("glbl_lib.clk_gate", paths=None)
    assert u.TopModRef.from_mod(top.mod) == top.ref


def test_load_complex(example_simple):
    """Complexer Module."""
    top = u.load("uart_lib.uart", paths=None)
    assert u.TopModRef.from_mod(top.mod) == top.ref
    assert u.TopModRef.from_mod(top.mod.get_inst("u_clk_gate")) == u.TopModRef(u.ModRef("glbl_lib", "clk_gate"))
    assert u.TopModRef.from_mod(top.mod.get_inst("u_core")) == u.TopModRef(
        u.ModRef("uart_lib", "uart"), sub="uart_lib.uart_core"
    )
    assert u.TopModRef.from_mod(top.mod.get_inst("u_regf")) == u.TopModRef(
        u.ModRef("uart_lib", "uart"), sub="uart_lib.uart_regf"
    )


def test_tb(example_simple):
    """Testbench."""
    top = u.load("glbl_lib.regf_tb#uart_lib.uart-uart_lib.uart_regf", paths=None)
    assert u.TopModRef.from_mod(top.mod) == top.ref
