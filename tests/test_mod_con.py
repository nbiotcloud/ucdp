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


class SubMod(u.AMod):
    """Sub."""

    def _build(self):
        self.add_port(u.UintType(4), "in_i")
        self.add_port(u.UintType(4), "out_o")


class TopMod(u.AMod):
    """Top."""

    def _build(self):
        sub = SubMod(self, "u_sub0")
        sub.con("in_i", "4'h4")
        sub.con("out_o", u.OPEN)


def test_top():
    """Top Module."""
    top = TopMod()
    assert tuple(top.get_instcons("u_sub0").iter()) == (
        u.Assign(target=u.Port(u.UintType(4), "in_i", direction=u.IN), source=u.ConstExpr(u.UintType(4, default=4))),
        u.Assign(target=u.Port(u.UintType(4), "out_o", direction=u.OUT), source=u.Note(note="OPEN")),
    )
