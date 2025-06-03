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
"""Identifier."""

from pytest import fixture

import ucdp as u


class ModeType(u.AEnumType):
    """Mode."""

    keytype: u.UintType = u.UintType(2)

    def _build(self):
        self._add(0, "add")
        self._add(1, "sub")
        self._add(2, "max")


class StructType(u.AStructType):
    """My."""

    comment: str = "Mode"

    def _build(self):
        self._add("mode", ModeType())
        self._add("send", u.ArrayType(u.UintType(8), 3))
        self._add("return", u.UintType(4), u.BWD)


class MyType(u.AStructType):
    """A Complex Type."""

    def _build(self):
        self._add("my0", StructType())
        self._add("my1", StructType(), u.BWD)
        self._add("uint", u.UintType(3))


@fixture
def top() -> u.Idents:
    """Top-Identifier."""
    return u.Idents(
        [
            u.Port(MyType(), "port_i"),
            u.Port(MyType(), "other_o"),
            u.Port(StructType(), "struct_i"),
            u.Port(StructType(), "struct_o"),
            u.Signal(StructType(), "struct_s"),
            u.Signal(MyType(), "sig_s"),
            u.Port(u.UintType(8), "data_i"),
        ]
    )


def test_expridents():
    """Expression Identifier Resolve."""
    ident0 = u.Ident(u.UintType(8), "ident0")
    ident1 = u.Ident(u.UintType(8), "ident1")
    ident2 = u.Ident(u.UintType(8), "ident2")

    assert u.get_expridents(ident0 + -ident1) == (ident0, ident1)
    assert u.get_expridents(ident0 + 5) == (ident0,)
    assert u.get_expridents(ident0 + 5) == (ident0,)
    assert u.get_expridents(u.ConcatExpr((ident0, ident1))) == (ident0, ident1)
    assert u.get_expridents(u.Log2Expr(ident0)) == (ident0,)

    assert u.get_expridents(u.TernaryExpr(ident2 == 5, ident1, ident0)) == (ident2, ident1, ident0)


def test_idents():
    """Idents."""
    port = u.Port(u.ClkRstAnType(), "main_i")
    idents = u.Idents([port])
    assert idents["main_i"] is port
    assert idents["main_i"] == port
    assert "main_clk_i" in idents
    assert idents["main_clk_i"] == u.Port(u.ClkType(), "main_clk_i", direction=u.IN, doc=u.Doc(title="Clock"))


def test_leveliter(top):
    """Top."""
    assert tuple(f"{idx}: {name}" for idx, name in top.leveliter()) == (
        "0: port_i",
        "1: port_my0_i",
        "2: port_my0_mode_i",
        "2: port_my0_send_i",
        "2: port_my0_return_o",
        "1: port_my1_o",
        "2: port_my1_mode_o",
        "2: port_my1_send_o",
        "2: port_my1_return_i",
        "1: port_uint_i",
        "0: other_o",
        "1: other_my0_o",
        "2: other_my0_mode_o",
        "2: other_my0_send_o",
        "2: other_my0_return_i",
        "1: other_my1_i",
        "2: other_my1_mode_i",
        "2: other_my1_send_i",
        "2: other_my1_return_o",
        "1: other_uint_o",
        "0: struct_i",
        "1: struct_mode_i",
        "1: struct_send_i",
        "1: struct_return_o",
        "0: struct_o",
        "1: struct_mode_o",
        "1: struct_send_o",
        "1: struct_return_i",
        "0: struct_s",
        "1: struct_mode_s",
        "1: struct_send_s",
        "1: struct_return_s",
        "0: sig_s",
        "1: sig_my0_s",
        "2: sig_my0_mode_s",
        "2: sig_my0_send_s",
        "2: sig_my0_return_s",
        "1: sig_my1_s",
        "2: sig_my1_mode_s",
        "2: sig_my1_send_s",
        "2: sig_my1_return_s",
        "1: sig_uint_s",
        "0: data_i",
    )


def test_port_iter():
    """Port Iteration."""
    assert tuple(sub.name for sub in u.Port(MyType(), "port_i").iter()) == (
        "port_i",
        "port_my0_i",
        "port_my0_mode_i",
        "port_my0_send_i",
        "port_my0_return_o",
        "port_my1_o",
        "port_my1_mode_o",
        "port_my1_send_o",
        "port_my1_return_i",
        "port_uint_i",
    )
    assert tuple(sub.name for sub in u.Port(MyType(), "port", direction=u.IN).iter()) == (
        "port",
        "port_my0",
        "port_my0_mode",
        "port_my0_send",
        "port_my0_return",
        "port_my1",
        "port_my1_mode",
        "port_my1_send",
        "port_my1_return",
        "port_uint",
    )
    assert tuple(sub.name for sub in u.Port(MyType(), "po_t", direction=u.IN).iter()) == (
        "po_t",
        "po_t_my0",
        "po_t_my0_mode",
        "po_t_my0_send",
        "po_t_my0_return",
        "po_t_my1",
        "po_t_my1_mode",
        "po_t_my1_send",
        "po_t_my1_return",
        "po_t_uint",
    )
