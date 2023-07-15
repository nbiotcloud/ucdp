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
"""Test Module Building."""
from attrs.exceptions import FrozenInstanceError
from pytest import raises

import ucdp
from ucdp import (
    Assign,
    BitType,
    ClkRstAnType,
    ClkType,
    Const,
    DescriptiveStructType,
    Doc,
    IntegerType,
    Param,
    Port,
    RstAnType,
    Signal,
    Slice,
    SliceOp,
    UintType,
)

# pylint: disable=attribute-defined-outside-init


def test_add_port_or_signal():
    """Test add_port_or_signal."""

    class MyMod(ucdp.AMod):
        """My Module."""

        def _build(self):
            self.add_port_or_signal(ucdp.UintType(8), "foo_i")
            self.add_port_or_signal(ucdp.UintType(8), "foo_o")
            self.add_port_or_signal(ucdp.UintType(8), "foo")

    mod = MyMod()
    assert list(mod.portssignals) == [
        Port(UintType(8), name="foo_i"),
        Port(UintType(8), name="foo_o"),
        Signal(UintType(8), "foo"),
    ]


def _assert_flipflop(bank, clk, rst_an, rst, ena, assigns):
    # pylint: disable=too-many-arguments
    assert bank.clk.name == clk
    assert bank.rst_an.name == rst_an
    assert bank.rst is rst or str(bank.rst.left) == rst
    assert bank.ena is ena or str(bank.ena.left) == ena
    assert list(bank) == assigns


def test_flip_flop():
    """Test add_port_or_signal."""

    class MyMod(ucdp.AMod):
        """My Module."""

        def _build(self):
            self.add_port(ucdp.ClkRstAnType(), "")
            self.add_port(ucdp.UintType(8), "d_i")
            self.add_port(ucdp.UintType(8), "d0_o")
            self.add_port(ucdp.UintType(8), "d1_o")
            self.add_port(ucdp.UintType(5), "g_i")
            self.add_port(ucdp.UintType(3), "g0_o")
            self.add_port(ucdp.UintType(3), "g1_o")
            self.add_port(ucdp.BitType(), "ctrl_i")

            self.add_flipflop(ucdp.UintType(8), "d0_r", nxt="d_i", route="d0_o")
            self.add_flipflop(ucdp.UintType(8), "d1_r", nxt="d_i", route="d1_o", ena="~ctrl_i")
            self.add_flipflop(ucdp.UintType(3), "g0_r", nxt="g_i[3:1]", route="g0_o")
            self.add_flipflop(ucdp.UintType(3), "g1_r", nxt="g_i[3:1]", route="g1_o", ena="ctrl_i", rst="~ctrl_i")
            self.add_flipflop(ucdp.UintType(5), "i_r")

    mod = MyMod()
    assert list(mod.portssignals) == [
        Port(ClkRstAnType(), doc=Doc(title="Clock and Reset")),
        Port(UintType(8), name="d_i"),
        Port(UintType(8), name="d0_o"),
        Port(UintType(8), name="d1_o"),
        Port(UintType(5), name="g_i"),
        Port(UintType(3), name="g0_o"),
        Port(UintType(3), name="g1_o"),
        Port(BitType(), name="ctrl_i"),
        Signal(UintType(8), "d0_r"),
        Signal(UintType(8), "d1_r"),
        Signal(UintType(3), "g0_r"),
        Signal(UintType(3), "g1_r"),
        Signal(UintType(5), "i_r"),
        Signal(UintType(5), "i_nxt_s"),
    ]
    banks = tuple(mod.flipflops)
    assert len(banks) == 3
    _assert_flipflop(
        banks[0],
        "clk_i",
        "rst_an_i",
        None,
        None,
        [
            Assign(Signal(UintType(8), "d0_r"), expr=Port(UintType(8), name="d_i")),
            Assign(Signal(UintType(3), "g0_r"), expr=SliceOp(Port(UintType(5), name="g_i"), Slice("3:1"))),
            Assign(Signal(UintType(5), "i_r"), expr=Signal(UintType(5), "i_nxt_s")),
        ],
    )
    _assert_flipflop(
        banks[1],
        "clk_i",
        "rst_an_i",
        None,
        "SOp('~', Port(BitType(), name='ctrl_i'))",
        [
            Assign(Signal(UintType(8), "d1_r"), expr=Port(UintType(8), name="d_i")),
        ],
    )
    _assert_flipflop(
        banks[2],
        "clk_i",
        "rst_an_i",
        "SOp('~', Port(BitType(), name='ctrl_i'))",
        "Port(BitType(), name='ctrl_i')",
        [Assign(Signal(UintType(3), "g1_r"), expr=SliceOp(Port(UintType(5), name="g_i"), Slice("3:1")))],
    )


def test_param():
    """Test Param."""

    class MyMod(ucdp.AMod):
        """My Module."""

        def _build(self):
            self.add_port(ucdp.ClkRstAnType(), "")
            self.add_port(ucdp.UintType(8), "d_i")

            param = self.add_param(ucdp.UintType(4), "param_p")

            core = ucdp.CoreMod(self, "u_core")
            param = core.add_param(param)

    mod = MyMod()
    assert tuple(mod.namespace.values()) == (
        Port(ClkRstAnType(), doc=Doc(title="Clock and Reset")),
        Port(UintType(8), name="d_i"),
        Param(UintType(4), "param_p"),
    )


def test_const():
    """Test Const."""

    class MyMod(ucdp.AMod):
        """My Module."""

        def _build(self):
            self.add_port(ucdp.ClkRstAnType(), "")
            self.add_port(ucdp.UintType(8), "d_i")

            const = self.add_const(ucdp.UintType(4), "const_p")

            core = ucdp.CoreMod(self, "u_core")
            const = core.add_const(const)

    mod = MyMod()
    assert tuple(mod.namespace.values()) == (
        Port(ClkRstAnType(), doc=Doc(title="Clock and Reset")),
        Port(UintType(8), name="d_i"),
        Const(UintType(4), "const_p"),
    )


def test_immutable():
    """Immutable."""

    class MyMod(ucdp.AMod):
        """Test Module."""

        def _build(self):
            self.add_port(ucdp.ClkRstAnType(), "")
            self.add_port(ucdp.UintType(8), "d_i")

    mod = MyMod()
    with raises(FrozenInstanceError):
        mod.something = 4


def test_immutable_decorated():
    """Immutable."""

    @ucdp.mod
    class MyMod(ucdp.AMod):
        """Test Module."""

        def _build(self):
            self.add_port(ucdp.ClkRstAnType(), "")
            self.add_port(ucdp.UintType(8), "d_i")

    mod = MyMod()
    with raises(FrozenInstanceError):
        mod.something = 4


def test_mutable():
    """Mutable."""

    @ucdp.mod(mutable=("something",))
    class MyMod(ucdp.AMod):
        """Test Module."""

        def _build(self):
            self.add_port(ucdp.ClkRstAnType(), "")
            self.add_port(ucdp.UintType(8), "d_i")

    mod = MyMod()
    mod.something = 4
    with raises(FrozenInstanceError):
        mod.other = 4


def test_descr_type():
    """Type as Constant."""

    class SubStructType(ucdp.AStructType):
        """Struct."""

        def _build(self):
            self._add("a", ucdp.UintType(2))
            self._add("b", ucdp.UintType(3), ucdp.BWD)
            self._add("c", ucdp.UintType(4), ucdp.BIDIR)

    class MyStructType(ucdp.AStructType):
        """Another Struct."""

        def _build(self):
            self._add("ctrl", ucdp.UintType(4), title="Control")
            self._add("data", ucdp.ArrayType(ucdp.SintType(16, default=5), 8), ucdp.FWD, descr="Data to be handled")
            self._add("resp", ucdp.BitType(), ucdp.BWD, comment="Sink response")
            self._add("bi", ucdp.UintType(5), ucdp.BIDIR)
            self._add("sub", SubStructType(), ucdp.BWD)

    class MyMod(ucdp.AMod):
        """Test Module."""

        def _build(self):
            self.add_port(ucdp.ClkRstAnType(), "")
            self.add_port(ucdp.UintType(8), "d_i")

            self.add_type_consts(MyStructType())

    mod = MyMod()
    assert tuple(mod.namespace.iter()) == (
        Port(ClkRstAnType(), doc=Doc(title="Clock and Reset")),
        Port(ClkType(), name="clk_i", level=1, doc=Doc(title="Clock")),
        Port(
            RstAnType(),
            name="rst_an_i",
            level=1,
            doc=Doc(title="Async Reset", descr="Low-Active", comment="Async Reset (Low-Active)"),
        ),
        Port(UintType(8), name="d_i"),
        Const(DescriptiveStructType(MyStructType()), "my_struct"),
        Const(IntegerType(default=147), "my_struct_bits_p", level=1, doc=Doc(title="Size in Bits")),
        Const(IntegerType(default=135), "my_struct_fwdbits_p", level=1, doc=Doc(title="Forward Size in Bits")),
        Const(IntegerType(default=3), "my_struct_bwdbits_p", level=1, doc=Doc(title="Backward Size in Bits")),
        Const(IntegerType(default=9), "my_struct_bibits_p", level=1, doc=Doc(title="Bi-Directional Size in Bits")),
    )


def test_lock():
    """Lock Testing."""

    class MyMod(ucdp.AMod):
        """Test Module."""

        def _build(self):
            self.add_port(ucdp.ClkRstAnType(), "")
            self.add_port(ucdp.UintType(8), "d_i")

    mod = MyMod()
    with raises(ucdp.LockError):
        mod.add_port(ucdp.UintType(4), "q_o")
    with raises(ucdp.LockError):
        mod.add_param(ucdp.UintType(4), "param_c")
    with raises(ucdp.LockError):
        mod.add_const(ucdp.UintType(4), "const_c")
    with raises(ucdp.LockError):
        ucdp.CoreMod(mod, "u_core")
    with raises(ucdp.LockError):
        mod.add_mux("main")
