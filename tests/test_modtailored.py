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

import ucdp as u


class TailMod(u.ATailoredMod):
    """Example Tailored Module."""

    def _build(self):
        self.add_port(u.ClkRstAnType(), "main_i")
        self.add_port(u.UintType(8), "data_i")
        self.add_port(u.UintType(8), "data_o")


class TopMod(u.AMod):
    """Top Module."""

    def _build(self):
        TailMod(self, "u_sub0")
        TailMod(self, "u_sub1")


def test_noparent():
    """Without Parent."""
    mod = TailMod()
    assert mod.modname == "tail"
    assert mod.topmodname == "tail"
    assert mod.libname == "tests"


def test_parent():
    """With Parent."""
    top = TopMod()
    sub0 = top.get_inst("u_sub0")
    assert sub0.modname == "top_sub0"
    assert sub0.topmodname == "top"
    assert sub0.libname == "tests"
    sub1 = top.get_inst("u_sub1")
    assert sub1.modname == "top_sub1"
    assert sub1.topmodname == "top"
    assert sub1.libname == "tests"
