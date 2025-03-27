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

from pathlib import Path

import ucdp as u


def test_basic(example_simple):
    """Basic Testing."""
    from uart_lib.uart import UartMod

    mod = UartMod()

    info = u.FileSet.from_mod(mod, "hdl")
    prjroot = Path("$PRJROOT")
    assert info.target is None
    assert info.filepaths == (
        u.LibPath(libname="glbl_lib", path=prjroot / "glbl_lib" / "clk_gate" / "rtl" / "clk_gate.sv"),
        u.LibPath(libname="uart_lib", path=prjroot / "uart_lib" / "uart" / "rtl" / "uart_regf.sv"),
        u.LibPath(libname="uart_lib", path=prjroot / "uart_lib" / "uart" / "rtl" / "uart_core.sv"),
        u.LibPath(libname="uart_lib", path=prjroot / "uart_lib" / "uart" / "rtl" / "uart.sv"),
    )
    assert info.inc_dirs == ()

    info = u.FileSet.from_mod(mod, "systemc")
    assert info.target is None
    assert info.filepaths == ()
    assert info.inc_dirs == ()
