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

import ucdp as u


def test_basic(example_simple):
    """Basic Testing."""
    from fileliststandard import HdlFileList
    from uart.uart import UartMod

    mod = UartMod()

    filepath = example_simple / "src" / "uart" / "uart" / "rtl" / "uart.sv"
    modfilelist = u.resolve_modfilelist(mod, "hdl")
    assert modfilelist == HdlFileList(gen="full", filepaths=(filepath,))


# def test_target(example_simple):
#     """Basic Testing."""
#     from glbl.clk_gate import ClkGateMod

#     mod = ClkGateMod()

#     filepath = example_simple / "glbl" / "clk_gate.sv"
#     modfilelist = u.resolve_modfilelist(mod, "hdl")
#     assert modfilelist == u.ModFileList(name="hdl", gen="inplace", target="!asic", filepaths=(filepath,))

#     filepath = example_simple / "glbl" / "clk_gate_asic.sv"
#     modfilelist = u.resolve_modfilelist(mod, "hdl", target="asic")
#     assert modfilelist == u.ModFileList(name="hdl", gen="inplace", target="asic", filepaths=(filepath,))

#     filepath = example_simple / "glbl" / "clk_gate.sv"
#     modfilelist = u.resolve_modfilelist(mod, "hdl", target="fpga")
#     assert modfilelist == u.ModFileList(name="hdl", gen="inplace", target="!asic", filepaths=(filepath,))


def test_filelistparser(example_filelist):
    """File List."""
    from filelist_lib.filelist import FilelistMod

    mod = FilelistMod()
    assert u.resolve_modfilelist(mod, "hdl") == u.ModFileList(
        name="hdl",
        filepaths=(
            example_filelist / "filelist_lib" / "mod0.sv",
            example_filelist / "filelist_lib" / "sub" / "mod2.sv",
            example_filelist / "mod2.sv",
        ),
        incdirs=(example_filelist / "filelist_lib" / "inc",),
    )
