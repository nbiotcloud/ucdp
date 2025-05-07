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
from ucdp import IN, OUT, Assign, ConstExpr, Default, Note, Port, UintType


class SubMod(u.AMod):
    """Sub."""

    def _build(self):
        self.add_port(u.UintType(4), "in_i")
        self.add_port(u.UintType(4), "open_i")
        self.add_port(u.UintType(4), "open_o")
        self.add_port(u.UintType(4), "note_i")
        self.add_port(u.UintType(4), "note_o")
        self.add_port(u.UintType(4), "default_i")
        self.add_port(u.UintType(4), "default_o")


class TopMod(u.AMod):
    """Top."""

    def _build(self):
        sub = SubMod(self, "u_sub0")
        sub.con("in_i", "4'h4")
        sub.con("open_i", u.OPEN)
        sub.con("open_o", u.OPEN)
        sub.con("note_i", u.note("my note"))
        sub.con("note_o", u.note("other note"))
        sub.con("default_i", u.DEFAULT)
        sub.con("default_o", u.DEFAULT)


def test_top():
    """Top Module."""
    top = TopMod()
    assert tuple(top.get_instcons("u_sub0").iter()) == (
        Assign(target=Port(UintType(4), "in_i", direction=IN), source=ConstExpr(UintType(4, default=4))),
        Assign(target=Port(UintType(4), "open_i", direction=IN), source=Note(note="OPEN")),
        Assign(target=Port(UintType(4), "open_o", direction=OUT), source=Note(note="OPEN")),
        Assign(target=Port(UintType(4), "note_i", direction=IN), source=Note(note="my note")),
        Assign(target=Port(UintType(4), "note_o", direction=OUT), source=Note(note="other note")),
        Assign(target=Port(UintType(4), "default_i", direction=IN), source=Default(note="DEFAULT")),
        Assign(target=Port(UintType(4), "default_o", direction=OUT), source=Default(note="DEFAULT")),
    )
