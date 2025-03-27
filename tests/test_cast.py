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
"""Test Assigns."""

from pytest import fixture

import ucdp as u


def _check_assigns(assigns, pairs):
    """Check Assignments."""
    assert tuple((assign.target, assign.source) for assign in assigns) == pairs


def _check(idents, dest, src, error=None):
    assigns = u.Assigns(targets=idents)
    if not error:
        assigns.set(dest, src)
        if dest.direction != u.IN:
            _check_assigns(assigns, ((dest, src),))
        else:
            _check_assigns(assigns, ((src, dest),))


class MstType(u.AStructType):
    """Mst."""

    def _build(self):
        self._add("trans", u.UintType(2))
        self._add("wdata", u.UintType(8))
        self._add("rdata", u.UintType(8), u.BWD)
        self._add("ready", u.BitType(), u.BWD)

    @staticmethod
    def cast(other):
        """
        How to cast an input of type `self` from a value of type `other`.

        `self = cast(other)`
        """
        if isinstance(other, SlvType):
            # Drive a Mst input with Slv signals
            yield "", ""
            yield "trans", "trans"
            yield "wdata", "wdata"
            yield "rdata", "rdata"
            yield "ready", "readyout"
        return NotImplemented


class SlvType(u.AStructType):
    """Slave."""

    def _build(self):
        self._add("trans", u.UintType(2))
        self._add("wdata", u.UintType(8))
        self._add("rdata", u.UintType(8), u.BWD)
        self._add("readyout", u.BitType(), u.BWD)
        self._add("ready", u.BitType())
        self._add("sel", u.BitType())

    @staticmethod
    def cast(other):
        """
        How to cast an input of type `self` from a value of type `other`.

        `self = cast(other)`
        """
        if isinstance(other, MstType):
            # Drive a Slv input with Mst signals
            yield "", ""
            yield "trans", "trans"
            yield "wdata", "wdata"
            yield "rdata", "rdata"  # BWD
            yield "readyout", "ready"  # BWD
            yield "ready", u.const("1b1")
            yield "sel", "ternary(trans > const('1b0'), const('1b1'), const('1b0'))"
        return NotImplemented


@fixture
def idents():
    """Idents For Testing."""
    return u.Idents(
        [
            # vectors
            u.Port(u.UintType(8), "uint_src_i"),
            u.Port(u.UintType(8), "uint_src_o"),
            u.Port(u.UintType(8), "uint_src_io"),
            u.Signal(u.UintType(8), "uint_src_s"),
            u.Port(u.UintType(8), "uint_dest_i"),
            u.Port(u.UintType(8), "uint_dest_o"),
            u.Port(u.UintType(8), "uint_dest_io"),
            u.Signal(u.UintType(8), "uint_dest_s"),
            # master
            u.Port(MstType(), "mst_src_i"),
            u.Port(MstType(), "mst_src_o"),
            u.Port(MstType(), "mst_src_io"),
            u.Signal(MstType(), "mst_src_s"),
            u.Port(MstType(), "mst_dest_i"),
            u.Port(MstType(), "mst_dest_o"),
            u.Port(MstType(), "mst_dest_io"),
            u.Signal(MstType(), "mst_dest_s"),
            # slave
            u.Port(SlvType(), "slv_src_i"),
            u.Port(SlvType(), "slv_src_o"),
            u.Port(SlvType(), "slv_src_io"),
            u.Signal(SlvType(), "slv_src_s"),
            u.Port(SlvType(), "slv_dest_i"),
            u.Port(SlvType(), "slv_dest_o"),
            u.Port(SlvType(), "slv_dest_io"),
            u.Signal(SlvType(), "slv_dest_s"),
        ]
    )


@fixture
def intidents():
    """Idents For Testing."""
    return u.Idents(
        [
            # vectors
            u.Port(u.UintType(8), "uint_src_i"),
            u.Port(u.UintType(8), "uint_src_o"),
            u.Port(u.UintType(8), "uint_src_io"),
            u.Signal(u.UintType(8), "uint_src_s"),
            u.Port(u.UintType(8), "uint_dest_i"),
            u.Port(u.UintType(8), "uint_dest_o"),
            u.Port(u.UintType(8), "uint_dest_io"),
            u.Signal(u.UintType(8), "uint_dest_s"),
            u.Port(u.SintType(8), "sint_src_i"),
            u.Port(u.SintType(8), "sint_src_o"),
            u.Port(u.SintType(8), "sint_src_io"),
            u.Signal(u.SintType(8), "sint_src_s"),
            u.Port(u.SintType(8), "sint_dest_i"),
            u.Port(u.SintType(8), "sint_dest_o"),
            u.Port(u.SintType(8), "sint_dest_io"),
            u.Signal(u.SintType(8), "sint_dest_s"),
        ]
    )


def test_fwd(idents):
    """Forward."""
    expr = u.const("8'hfc")

    # src=signal
    _check(idents, idents["uint_dest_s"], idents["uint_src_s"])
    _check(idents, idents["uint_dest_i"], idents["uint_src_s"])
    _check(idents, idents["uint_dest_o"], idents["uint_src_s"])
    _check(idents, idents["uint_dest_io"], idents["uint_src_s"])
    _check(idents, expr, idents["uint_src_s"], error="expression")
    # src=IN
    _check(idents, idents["uint_dest_s"], idents["uint_src_i"])
    _check(idents, idents["uint_dest_i"], idents["uint_src_i"], error="direction")
    _check(idents, idents["uint_dest_o"], idents["uint_src_i"])
    _check(idents, idents["uint_dest_io"], idents["uint_src_i"])
    _check(idents, expr, idents["uint_src_i"], error="expression")
    # src=OUT
    _check(idents, idents["uint_dest_s"], idents["uint_src_o"])
    _check(idents, idents["uint_dest_i"], idents["uint_src_o"])
    _check(idents, idents["uint_dest_o"], idents["uint_src_o"])
    _check(idents, idents["uint_dest_io"], idents["uint_src_o"])
    _check(idents, expr, idents["uint_src_o"], error="expression")
    # src=INOUT
    _check(idents, idents["uint_dest_s"], idents["uint_src_io"])
    _check(idents, idents["uint_dest_i"], idents["uint_src_io"])
    _check(idents, idents["uint_dest_o"], idents["uint_src_io"])
    _check(idents, idents["uint_dest_io"], idents["uint_src_io"])
    _check(idents, expr, idents["uint_src_io"], error="expression")
    # src=expr
    _check(idents, idents["uint_dest_s"], expr)
    _check(idents, idents["uint_dest_i"], expr, error="expression")
    _check(idents, idents["uint_dest_o"], expr)
    _check(idents, idents["uint_dest_io"], expr)
    _check(idents, expr, expr, error="expression")


def test_modassign_slv2mst_cast(idents):
    """Test Bi-Directional Assignments within module (assign statements) and casting."""
    assigns = u.Assigns(targets=idents)
    # Mst = cast(Slv)
    assigns.set(idents["mst_dest_o"], idents["slv_src_i"], cast=True)
    _check_assigns(
        assigns,
        (
            (idents["mst_dest_o"], idents["slv_src_i"]),
            (idents["mst_dest_trans_o"], idents["slv_src_trans_i"]),
            (idents["mst_dest_wdata_o"], idents["slv_src_wdata_i"]),
            (idents["slv_src_rdata_o"], idents["mst_dest_rdata_i"]),
            (idents["slv_src_readyout_o"], idents["mst_dest_ready_i"]),
        ),
    )


def test_modassign_mst2slv_cast(idents):
    """Test Bi-Directional Assignments within module (assign statements) and casting."""
    assigns = u.Assigns(targets=idents)
    # Mst = cast(Slv)
    assigns.set(idents["slv_dest_o"], idents["mst_src_i"], cast=True)
    _check_assigns(
        assigns,
        (
            (idents["mst_src_rdata_o"], idents["slv_dest_rdata_i"]),
            (idents["mst_src_ready_o"], idents["slv_dest_readyout_i"]),
            (idents["slv_dest_o"], idents["mst_src_i"]),
            (idents["slv_dest_trans_o"], idents["mst_src_trans_i"]),
            (idents["slv_dest_wdata_o"], idents["mst_src_wdata_i"]),
            (idents["slv_dest_ready_o"], u.ConstExpr(u.BitType(default=1))),
            (
                idents["slv_dest_sel_o"],
                u.TernaryExpr(
                    u.BoolOp(u.Port(u.UintType(2), "mst_src_trans_i", direction=u.IN), ">", u.ConstExpr(u.BitType())),
                    u.ConstExpr(u.BitType(default=1)),
                    u.ConstExpr(u.BitType()),
                ),
            ),
        ),
    )
