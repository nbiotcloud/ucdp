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
"""Test Assigns."""

import ucdp as u
from pytest import fixture, raises


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
            u.Port(MyType(), "port_o"),
            u.Port(MyType(), "other_i"),
            u.Port(MyType(), "other_o"),
            u.Signal(MyType(), "sig_s"),
        ]
    )


@fixture
def sub() -> u.Idents:
    """Sub-Identifier."""
    return u.Idents(
        [
            u.Port(MyType(), "sub_i"),
            u.Port(MyType(), "sub_o"),
        ]
    )


# @fixture
# def some_ports():
#     """Some Ports."""
#     return u.Idents(
#         [
#             u.Port(u.ClkRstAnType(), "main_i"),
#             u.Port(u.UintType(8), "vec_a_i"),
#             u.Port(u.UintType(8), "vec_a_o"),
#             u.Port(MyType(), "my_a_i"),
#             u.Port(MyType(), "my_a_o"),
#             u.Port(ComplexType(), "comp_lex_i"),
#             u.Port(ComplexType(), "comp_lex_o"),
#         ]
#     )


# @fixture
# def some_ports_signals(ports):
#     """Some Signals."""
#     return u.Idents(
#         [
#             u.Signal(u.UintType(8), "vec_a_s"),
#             u.Signal(u.UintType(4), "vec_b_s"),
#             u.Signal(u.UintType(4), "vec_c_s"),
#             u.Signal(MyType(), "my_a_s"),
#             u.Signal(MyType(), "my_b_s"),
#             u.Signal(ComplexType(), "comp_lex_s"),
#             *ports,
#         ]
#     )


# @fixture
# def ports():
#     """Some Ports."""
#     return u.Idents(
#         [
#             u.Port(u.ClkRstAnType(), "main_i"),
#             u.Port(u.UintType(8), "vec_a_i"),
#             u.Port(u.UintType(8), "vec_a_o"),
#             u.Port(u.UintType(14), "vec_b_i"),
#             u.Port(u.UintType(14, default=0xFF), "vec_b_o"),
#             u.Port(u.UintType(4), "vec_c_i"),
#             u.Port(u.UintType(4), "vec_c_o"),
#             u.Port(u.UintType(8), "vec_d_i"),
#             u.Port(u.UintType(8), "vec_d_o"),
#             u.Port(MyType(), "my_a_i"),
#             u.Port(MyType(), "my_a_o"),
#             u.Port(MyType(), "my_b_i"),
#             u.Port(MyType(), "my_b_o"),
#             u.Port(ComplexType(), "comp_lex_i"),
#             u.Port(ComplexType(), "comp_lex_o"),
#         ]
#     )


# @fixture
# def ports_signals(ports):
#     """Some Signals."""
#     return u.Idents(
#         [
#             u.Signal(u.UintType(8), "vec_a_s"),
#             u.Signal(u.UintType(4), "vec_b_s"),
#             u.Signal(u.UintType(4), "vec_c_s"),
#             u.Signal(MyType(), "my_a_s"),
#             u.Signal(MyType(), "my_b_s"),
#             u.Signal(ComplexType(), "comp_lex_s"),
#             *ports,
#         ]
#     )


# @fixture
# def othersignals():
#     """Other Signals."""
#     return u.Idents(
#         [
#             u.Signal(u.UintType(8), "ovec_a_s"),
#             u.Signal(u.UintType(4), "ovec_b_s"),
#             u.Signal(u.UintType(4), "ovec_c_s"),
#             u.Signal(MyType(), "omy_a_s"),
#             u.Signal(MyType(), "omy_b_s"),
#             u.Signal(ComplexType(), "ocomp_lex_s"),
#         ]
#     )


# @fixture
# def params():
#     """Other Signals."""
#     return u.Idents(
#         [
#             u.Param(u.UintType(8), "a_p"),
#             u.Param(u.UintType(4), "b_p"),
#         ]
#     )


def test_assign_empty(top):
    """Empty Assigns."""
    assigns = u.Assigns(targets=top, sources=top)
    assert [str(assign) for assign in assigns] == []


def test_assign_empty_all(top):
    """Empty Assigns for all."""
    assigns = u.Assigns(targets=top, sources=top, all=True)
    assert [str(assign) for assign in assigns] == [
        "port_i  ---->  None",
        "port_my0_i  ---->  None",
        "port_my0_mode_i  ---->  None",
        "port_my0_send_i  ---->  None",
        "port_my0_return_o  <----  None",
        "port_my1_o  <----  None",
        "port_my1_mode_o  <----  None",
        "port_my1_send_o  <----  None",
        "port_my1_return_i  ---->  None",
        "port_uint_i  ---->  None",
        "port_o  <----  None",
        "port_my0_o  <----  None",
        "port_my0_mode_o  <----  None",
        "port_my0_send_o  <----  None",
        "port_my0_return_i  ---->  None",
        "port_my1_i  ---->  None",
        "port_my1_mode_i  ---->  None",
        "port_my1_send_i  ---->  None",
        "port_my1_return_o  <----  None",
        "port_uint_o  <----  None",
        "other_i  ---->  None",
        "other_my0_i  ---->  None",
        "other_my0_mode_i  ---->  None",
        "other_my0_send_i  ---->  None",
        "other_my0_return_o  <----  None",
        "other_my1_o  <----  None",
        "other_my1_mode_o  <----  None",
        "other_my1_send_o  <----  None",
        "other_my1_return_i  ---->  None",
        "other_uint_i  ---->  None",
        "other_o  <----  None",
        "other_my0_o  <----  None",
        "other_my0_mode_o  <----  None",
        "other_my0_send_o  <----  None",
        "other_my0_return_i  ---->  None",
        "other_my1_i  ---->  None",
        "other_my1_mode_i  ---->  None",
        "other_my1_send_i  ---->  None",
        "other_my1_return_o  <----  None",
        "other_uint_o  <----  None",
        "sig_s  ---->  None",
        "sig_my0_s  ---->  None",
        "sig_my0_mode_s  ---->  None",
        "sig_my0_send_s  ---->  None",
        "sig_my0_return_s  <----  None",
        "sig_my1_s  <----  None",
        "sig_my1_mode_s  <----  None",
        "sig_my1_send_s  <----  None",
        "sig_my1_return_s  ---->  None",
        "sig_uint_s  ---->  None",
    ]


# # def test_assign(tmp_path, ports, signals):
# #     """Test Assigns"""
# #     assigns = u.Assigns(ports, signals, drivers={})

# #     # valid assignment
# #     assigns.set(ports["vec_a_o"], ports["vec_a_i"])

# #     # re-assignement
# #     with raises(ValueError) as raised:
# #         assigns.set(ports["vec_a_o"], ports["vec_d_i"])
# #     assert (
# #         str(raised.value)
# #         == "'Port(UintType(8), name='vec_a_o')' already assigned to 'Port(UintType(8), name='vec_a_i')'"
# #     )

# #     # assign type mismatch
# #     # with raises(TypeError) as raised:
# #     #     assigns.set(ports["vec_c_o"], ports["vec_b_i"])
# #     # assert str(raised.value) == "Cannot assign 'vec_b_i' of UintType(14) to 'vec_c_o' of UintType(4)"
# #     # with raises(TypeError) as raised:
# #     #     assigns.set(ports["vec_c_o"], ports["vec_b_i"][12:2])
# #     # assert str(raised.value) == "Cannot assign 'vec_b_i[12:2]' of UintType(11) to 'vec_c_o' of UintType(4)"

# #     # assign
# #     assigns.set(ports["vec_c_o"], ports["vec_b_i"][12:9])

# #     # assign Concat
# #     assigns.set(ports["vec_d_o"], u.concat((ports["vec_c_i"], ports["vec_c_i"])))

# #     # # no target
# #     # with raises(ValueError) as raised:
# #     #     assigns.set(signals["my_b_s"], signals["my_a_s"])
# #     # assert str(raised.value) == "'my_b_s' is not available within target namespace"

# #     assigns.set(ports["my_a_o"], ports["my_a_i"])
# #     assigns.set(ports["my_b_o"], signals["my_a_s"])

# #     assert_assigns(tmp_path, "test_assign", assigns)


# # def test_assign_inst(tmp_path, ports, signals):
# #     """Test Assign with complete=True."""
# #     assigns = u.Assigns(ports, signals, inst=True)
# #     assert_assigns(tmp_path, "test_assign_inst", assigns)


# # def test_assign_slice(tmp_path, ports, signals):
# #     """Test Assign slice."""
# #     assigns = u.Assigns(ports, signals)
# #     assigns.set_default(ports["vec_a_o"], ports["vec_a_i"])
# #     assigns.set(ports["vec_a_o"][4:3], ports["vec_d_i"][3:2])
# #     assigns.set(ports["vec_b_o"][6:3], ports["vec_c_i"])
# #     assigns.set(ports["vec_b_o"][12:9], ports["vec_c_i"])
# #     assert_assigns(tmp_path, "test_assign_slice", assigns)


# # def test_assign_slice_inst(tmp_path, ports, signals):
# #     """Test Assign slice at inst."""
# #     assigns = u.Assigns(ports, signals, inst=True)
# #     assigns.set(ports["vec_a_i"][4:3], ports["vec_d_o"][3:2])
# #     assigns.set(ports["vec_b_o"][6:3], ports["vec_c_o"])
# #     assigns.set(ports["vec_b_o"][12:9], ports["vec_c_o"])
# #     assert_assigns(tmp_path, "test_assign_inst", assigns)


def test_top_dir_err(top):
    """Top - Direction Error."""
    drivers = u.Drivers()
    assigns = u.Assigns(targets=top, sources=top, drivers=drivers)

    # top-input MUST NOT drive from top-input
    with raises(u.DirectionError) as exc:
        assigns.set(top["port_i"], top["other_i"])
    assert str(exc.value) == "Cannot connect IN 'port_i' and IN 'other_i'"

    # top-output MUST NOT drive output top-output
    with raises(u.DirectionError) as exc:
        assigns.set(top["port_o"], top["other_o"])
    assert str(exc.value) == "Cannot connect OUT 'port_o' and OUT 'other_o'"

    # Drivers not modified
    assert tuple(drivers) == ()


def test_top_in(top):
    """Top - Input."""
    drivers = u.Drivers()
    assigns = u.Assigns(targets=top, sources=top, drivers=drivers)
    assigns.set(top["port_i"], top["port_o"])
    assert [str(assign) for assign in assigns] == [
        "port_i  ---->  port_o",
        "port_my0_i  ---->  port_my0_o",
        "port_my0_mode_i  ---->  port_my0_mode_o",
        "port_my0_send_i  ---->  port_my0_send_o",
        "port_my0_return_o  <----  port_my0_return_i",
        "port_my1_o  <----  port_my1_i",
        "port_my1_mode_o  <----  port_my1_mode_i",
        "port_my1_send_o  <----  port_my1_send_i",
        "port_my1_return_i  ---->  port_my1_return_o",
        "port_uint_i  ---->  port_uint_o",
    ]
    assert tuple(f"{name}: {driver}" for name, driver in drivers) == (
        "port_my0_return_o: port_my0_return_i",
        "port_my1_o: port_my1_i",
        "port_my1_mode_o: port_my1_mode_i",
        "port_my1_send_o: port_my1_send_i",
    )


def test_top_out(top):
    """Top - Output."""
    drivers = u.Drivers()
    assigns = u.Assigns(targets=top, sources=top, drivers=drivers)
    assigns.set(top["port_o"], top["port_i"])
    assert [str(assign) for assign in assigns] == [
        "port_o  <----  port_i",
        "port_my0_o  <----  port_my0_i",
        "port_my0_mode_o  <----  port_my0_mode_i",
        "port_my0_send_o  <----  port_my0_send_i",
        "port_my0_return_i  ---->  port_my0_return_o",
        "port_my1_i  ---->  port_my1_o",
        "port_my1_mode_i  ---->  port_my1_mode_o",
        "port_my1_send_i  ---->  port_my1_send_o",
        "port_my1_return_o  <----  port_my1_return_i",
        "port_uint_o  <----  port_uint_i",
    ]
    assert tuple(f"{name}: {driver}" for name, driver in drivers) == (
        "port_o: port_i",
        "port_my0_o: port_my0_i",
        "port_my0_mode_o: port_my0_mode_i",
        "port_my0_send_o: port_my0_send_i",
        "port_my1_return_o: port_my1_return_i",
        "port_uint_o: port_uint_i",
    )


def test_top_sub_dir_err(top, sub):
    """Top with Sub - Direction Error."""
    drivers = u.Drivers()
    assigns = u.Assigns(targets=sub, sources=top, sub=True, drivers=drivers)

    # sub-output MUST NOT drive against top-input
    with raises(u.DirectionError) as exc:
        assigns.set(sub["sub_o"], top["port_i"])
    assert str(exc.value) == "Cannot connect sub-level OUT 'sub_o' and IN 'port_i'"

    # sub-input MUST NOT drive from top-output
    with raises(u.DirectionError) as exc:
        assigns.set(sub["sub_i"], top["port_o"])
    assert str(exc.value) == "Cannot connect sub-level IN 'sub_i' and OUT 'port_o'"

    assert [str(assign) for assign in assigns] == []
    assert tuple(f"{name}: {driver}" for name, driver in drivers) == ()


def test_top_sub_in(top, sub):
    """Top with Sub - Input."""
    drivers = u.Drivers()
    assigns = u.Assigns(targets=sub, sources=top, sub=True, drivers=drivers)
    assigns.set(sub["sub_i"], top["port_i"])
    assert [str(assign) for assign in assigns] == [
        "sub_i  ---->  port_i",
        "sub_my0_i  ---->  port_my0_i",
        "sub_my0_mode_i  ---->  port_my0_mode_i",
        "sub_my0_send_i  ---->  port_my0_send_i",
        "sub_my0_return_o  <----  port_my0_return_o",
        "sub_my1_o  <----  port_my1_o",
        "sub_my1_mode_o  <----  port_my1_mode_o",
        "sub_my1_send_o  <----  port_my1_send_o",
        "sub_my1_return_i  ---->  port_my1_return_i",
        "sub_uint_i  ---->  port_uint_i",
    ]
    assert tuple(f"{name}: {driver}" for name, driver in drivers) == (
        "sub_i: port_i",
        "sub_my0_i: port_my0_i",
        "sub_my0_mode_i: port_my0_mode_i",
        "sub_my0_send_i: port_my0_send_i",
        "sub_my1_return_i: port_my1_return_i",
        "sub_uint_i: port_uint_i",
    )


def test_top_sub_out(top, sub):
    """Top with Sub - Output."""
    drivers = u.Drivers()
    assigns = u.Assigns(targets=sub, sources=top, sub=True, drivers=drivers)
    assigns.set(sub["sub_o"], top["port_o"])
    assert [str(assign) for assign in assigns] == [
        "sub_o  <----  port_o",
        "sub_my0_o  <----  port_my0_o",
        "sub_my0_mode_o  <----  port_my0_mode_o",
        "sub_my0_send_o  <----  port_my0_send_o",
        "sub_my0_return_i  ---->  port_my0_return_i",
        "sub_my1_i  ---->  port_my1_i",
        "sub_my1_mode_i  ---->  port_my1_mode_i",
        "sub_my1_send_i  ---->  port_my1_send_i",
        "sub_my1_return_o  <----  port_my1_return_o",
        "sub_uint_o  <----  port_uint_o",
    ]
    assert tuple(f"{name}: {driver}" for name, driver in drivers) == (
        "sub_my0_return_i: port_my0_return_i",
        "sub_my1_i: port_my1_i",
        "sub_my1_mode_i: port_my1_mode_i",
        "sub_my1_send_i: port_my1_send_i",
    )


def test_top_sub_in_note(top, sub):
    """Top with Sub - Input."""
    drivers = u.Drivers()
    assigns = u.Assigns(targets=sub, sources=top, sub=True, drivers=drivers)
    assigns.set(sub["sub_my1_i"], u.TODO)
    assert [str(assign) for assign in assigns] == [
        "sub_my1_i  ---->  TODO",
        "sub_my1_mode_i  ---->  TODO",
        "sub_my1_send_i  ---->  TODO",
        "sub_my1_return_o  <----  TODO",
    ]
    assert [f"{name}: {driver}" for name, driver in drivers] == []


def test_top_sub_in_const(top, sub):
    """Top with Sub - Input."""
    drivers = u.Drivers()
    assigns = u.Assigns(targets=sub, sources=top, sub=True, drivers=drivers)
    assigns.set(sub["sub_my1_mode_i"], u.const("2h2"))
    assert [str(assign) for assign in assigns] == [
        "sub_my1_mode_i  ---->  ConstExpr(UintType(2, default=2))",
    ]
    assert [f"{name}: {driver}" for name, driver in drivers] == [
        "sub_my1_mode_i: ConstExpr(UintType(2, default=2))",
    ]


def test_top_sub_in_type_err(top, sub):
    """Top with Sub - Type Error."""
    drivers = u.Drivers()
    assigns = u.Assigns(targets=sub, sources=top, sub=True, drivers=drivers)
    with raises(TypeError) as exc:
        assigns.set(sub["sub_my1_mode_i"], u.const("3h2"))
    assert (
        str(exc.value) == "Cannot assign 'ConstExpr(UintType(3, default=2))' "
        "of UintType(3, default=2) to sub-level 'sub_my1_mode_i' of ModeType()"
    )
