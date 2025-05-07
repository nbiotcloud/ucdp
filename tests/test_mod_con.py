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
from logging import INFO, WARNING

from pytest import raises

import ucdp as u
from ucdp import IN, OUT, Assign, ConstExpr, Default, Note, Port, UintType


class SubMod(u.AMod):
    """Sub."""

    def _build(self):
        self.add_port(u.UintType(4), "in_i")
        self.add_port(u.UintType(4), "out_o")
        self.add_port(u.UintType(4), "open_i")
        self.add_port(u.UintType(4), "open_o")
        self.add_port(u.UintType(4), "note_i")
        self.add_port(u.UintType(4), "note_o")
        self.add_port(u.UintType(4), "default_i")
        self.add_port(u.UintType(4), "default_o")


class TopMod(u.AMod):
    """Top."""

    def _build(self):
        self.add_port(u.UintType(4), "in_i")
        self.add_port(u.UintType(4), "out_o")

        sub = SubMod(self, "u_sub0")
        sub.con("in_i", "4'h4")
        sub.con("out_o", "out_o")
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
        Assign(target=Port(UintType(4), "out_o", direction=OUT), source=Port(UintType(4), "out_o", direction=OUT)),
        Assign(target=Port(UintType(4), "open_i", direction=IN), source=Note(note="OPEN")),
        Assign(target=Port(UintType(4), "open_o", direction=OUT), source=Note(note="OPEN")),
        Assign(target=Port(UintType(4), "note_i", direction=IN), source=Note(note="my note")),
        Assign(target=Port(UintType(4), "note_o", direction=OUT), source=Note(note="other note")),
        Assign(target=Port(UintType(4), "default_i", direction=IN), source=Default(note="DEFAULT")),
        Assign(target=Port(UintType(4), "default_o", direction=OUT), source=Default(note="DEFAULT")),
    )


class TopErrMod(u.AMod):
    """Top Module with Routing Error."""

    def _build(self):
        self.add_port(u.UintType(4), "in_i")
        self.add_port(u.UintType(4), "out_o")

        sub = SubMod(self, "u_sub0")
        sub.con("in_i", "5'h4")
        sub.con("out_o", "out_o")


def test_top_err(caplog):
    """Top Module with Routing Error."""
    msg = (
        "<tests.test_mod_con.TopErrMod(inst='top_err', libname='tests', modname='top_err')>: "
        "Cannot assign 'ConstExpr(UintType(5, default=4))' of type UintType(5, default=4) to 'in_i' "
        "of type UintType(4)."
    )
    with raises(TypeError, match=re.escape(msg)):
        TopErrMod()


class TopWarnMod(u.AMod):
    """Top Module with Routing Warning."""

    def _build(self):
        self.add_port(u.UintType(4), "in_i")
        self.add_port(u.UintType(4), "out_o")

        sub = SubMod(self, "u_sub0")
        sub.con("in_i", "5'h4", on_error="warn")
        sub.con("out_o", "out_o")


def test_top_warn(caplog):
    """Top Module with Routing Error."""
    msg = (
        "<tests.test_mod_con.TopWarnMod(inst='top_warn', libname='tests', modname='top_warn')>: "
        "Cannot assign 'ConstExpr(UintType(5, default=4))' of type UintType(5, default=4) to 'in_i' "
        "of type UintType(4)."
    )
    top = TopWarnMod()
    assert tuple(top.get_instcons("u_sub0").iter()) == (
        Assign(target=Port(UintType(4), "in_i", direction=IN)),
        Assign(target=Port(UintType(4), "out_o", direction=OUT), source=Port(UintType(4), "out_o", direction=OUT)),
        Assign(target=Port(UintType(4), "open_i", direction=IN)),
        Assign(target=Port(UintType(4), "open_o", direction=OUT)),
        Assign(target=Port(UintType(4), "note_i", direction=IN)),
        Assign(target=Port(UintType(4), "note_o", direction=OUT)),
        Assign(target=Port(UintType(4), "default_i", direction=IN)),
        Assign(target=Port(UintType(4), "default_o", direction=OUT)),
    )
    assert caplog.record_tuples == [("ucdp", WARNING, msg)]


class TopIgnoreMod(u.AMod):
    """Top Module with ignored Routing Error."""

    def _build(self):
        self.add_port(u.UintType(4), "in_i")
        self.add_port(u.UintType(4), "out_o")

        sub = SubMod(self, "u_sub0")
        sub.con("in_i", "5'h4", on_error="ignore")
        sub.con("out_o", "out_o")


def test_top_ign(caplog):
    """Top Module with ignored Routing Error."""
    msg = (
        "Ignored: <tests.test_mod_con.TopIgnoreMod(inst='top_ignore', libname='tests', modname='top_ignore')>: "
        "Cannot assign 'ConstExpr(UintType(5, default=4))' of type UintType(5, default=4) to 'in_i' "
        "of type UintType(4)."
    )
    top = TopIgnoreMod()
    assert tuple(top.get_instcons("u_sub0").iter()) == (
        Assign(target=Port(UintType(4), "in_i", direction=IN)),
        Assign(target=Port(UintType(4), "out_o", direction=OUT), source=Port(UintType(4), "out_o", direction=OUT)),
        Assign(target=Port(UintType(4), "open_i", direction=IN)),
        Assign(target=Port(UintType(4), "open_o", direction=OUT)),
        Assign(target=Port(UintType(4), "note_i", direction=IN)),
        Assign(target=Port(UintType(4), "note_o", direction=OUT)),
        Assign(target=Port(UintType(4), "default_i", direction=IN)),
        Assign(target=Port(UintType(4), "default_o", direction=OUT)),
    )
    assert caplog.record_tuples == [("ucdp", INFO, msg)]
