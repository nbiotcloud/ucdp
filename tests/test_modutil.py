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
"""Test Module Utilities."""
import ucdp


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
        Tailored0Mod(self, "u_tail0", is_hull=True)
        ucdp.CoreMod(self, "u_core0")
        LeafMod(self, "u_leaf")

    def _builddep(self):
        Tailored0Mod(self, "u_tail0dep")
        ucdp.CoreMod(self, "u_core1", is_hull=True)


class TopMod(ucdp.AMod):
    """Top Module."""

    libname = "mylib"

    def _build(self):
        Tailored0Mod(self, "u_tail0")
        ucdp.CoreMod(self, "u_core0")
        LeafMod(self, "u_leaf")


def test_gettopmod():
    """Test get_topmod."""
    topmod = TopMod()
    for mod in ucdp.ModPreIter(topmod):
        assert ucdp.get_topmod(mod) is topmod
