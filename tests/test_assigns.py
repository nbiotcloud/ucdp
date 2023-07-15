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
"""Test Assigns."""
from pytest import fixture, raises

import ucdp

from .util import TESTDATA, assert_gen


class ModeType(ucdp.AEnumType):
    """Mode."""

    keytype = ucdp.UintType(2)

    def _build(self):
        self._add(0, "add")
        self._add(1, "sub")
        self._add(2, "max")


class MyType(ucdp.AStructType):
    """My."""

    comment = "Mode"

    def _build(self):
        self._add("mode", ModeType())
        self._add("send", ucdp.ArrayType(ucdp.UintType(8), 3))
        self._add("return", ucdp.UintType(4), ucdp.BWD)


class SelType(ucdp.AEnumType):
    """Sel."""

    keytype = ucdp.UintType(2, default=2)

    def _build(self):
        self._add(0, "my_a")
        self._add(1, "my_b")
        self._add(2, "my_c")


class ComplexType(ucdp.AStructType):
    """A Complex Type."""

    def _build(self):
        self._add("my0", ucdp.ArrayType(MyType(), 8))
        self._add("my1", ucdp.ArrayType(MyType(), 8), ucdp.BWD)
        self._add("bi", ucdp.SintType(9), ucdp.BIDIR)
        self._add("sel", SelType())
        self._add("uint", ucdp.UintType(3))


@fixture
def ports():
    """Some Ports."""
    return ucdp.Idents(
        [
            ucdp.Port(ucdp.ClkRstAnType()),
            ucdp.Port(ucdp.UintType(8), "vec_a_i"),
            ucdp.Port(ucdp.UintType(8), "vec_a_o"),
            ucdp.Port(ucdp.UintType(14), "vec_b_i"),
            ucdp.Port(ucdp.UintType(14, default=0xFF), "vec_b_o"),
            ucdp.Port(ucdp.UintType(4), "vec_c_i"),
            ucdp.Port(ucdp.UintType(4), "vec_c_o"),
            ucdp.Port(ucdp.UintType(8), "vec_d_i"),
            ucdp.Port(ucdp.UintType(8), "vec_d_o"),
            ucdp.Port(MyType(), "my_a_i"),
            ucdp.Port(MyType(), "my_a_o"),
            ucdp.Port(MyType(), "my_b_i"),
            ucdp.Port(MyType(), "my_b_o"),
            ucdp.Port(ComplexType(), "comp_lex_i"),
            ucdp.Port(ComplexType(), "comp_lex_o"),
        ]
    )


@fixture
def signals():
    """Some Signals."""
    return ucdp.Idents(
        [
            ucdp.Port(ucdp.ClkRstAnType()),
            ucdp.Port(ucdp.UintType(8), "vec_a_i"),
            ucdp.Port(ucdp.UintType(8), "vec_a_o"),
            ucdp.Port(ucdp.UintType(14), "vec_b_i"),
            ucdp.Port(ucdp.UintType(14, default=0xFF), "vec_b_o"),
            ucdp.Port(ucdp.UintType(4), "vec_c_i"),
            ucdp.Port(ucdp.UintType(4), "vec_c_o"),
            ucdp.Port(ucdp.UintType(8), "vec_d_i"),
            ucdp.Port(ucdp.UintType(8), "vec_d_o"),
            ucdp.Port(MyType(), "my_a_i"),
            ucdp.Port(MyType(), "my_a_o"),
            ucdp.Port(MyType(), "my_b_i"),
            ucdp.Port(MyType(), "my_b_o"),
            ucdp.Port(ComplexType(), "comp_lex_i"),
            ucdp.Port(ComplexType(), "comp_lex_o"),
            ucdp.Signal(ucdp.UintType(8), "vec_a_s"),
            ucdp.Signal(ucdp.UintType(4), "vec_b_s"),
            ucdp.Signal(ucdp.UintType(4), "vec_c_s"),
            ucdp.Signal(MyType(), "my_a_s"),
            ucdp.Signal(MyType(), "my_b_s"),
            ucdp.Signal(ComplexType(), "comp_lex_s"),
        ]
    )


@fixture
def othersignals():
    """Other Signals."""
    return ucdp.Idents(
        [
            ucdp.Signal(ucdp.UintType(8), "ovec_a_s"),
            ucdp.Signal(ucdp.UintType(4), "ovec_b_s"),
            ucdp.Signal(ucdp.UintType(4), "ovec_c_s"),
            ucdp.Signal(MyType(), "omy_a_s"),
            ucdp.Signal(MyType(), "omy_b_s"),
            ucdp.Signal(ComplexType(), "ocomp_lex_s"),
        ]
    )


def assert_assigns(tmp_path, name, assigns):
    """Assert Assigns for Compare."""
    with open(tmp_path / "assigns.txt", "w", encoding="utf-8") as file:
        for assign in assigns:
            file.write(f"{assign.target.name}: {assign.expr}\n")
    refpath = TESTDATA / "test_assigns" / name
    assert_gen(tmp_path, refpath)


@fixture
def params():
    """Other Signals."""
    return ucdp.Idents(
        [
            ucdp.Param(ucdp.UintType(8), "a_p"),
            ucdp.Param(ucdp.UintType(4), "b_p"),
        ]
    )


# pylint: disable=redefined-outer-name
def test_assign_empty(ports, signals):
    """Test Assign."""
    assigns = ucdp.Assigns(ports, signals, drivers={})
    assert tuple(repr(assign) for assign in assigns) == tuple()


# pylint: disable=redefined-outer-name
def test_assign(tmp_path, ports, signals):
    """Test Assigns"""
    assigns = ucdp.Assigns(ports, signals, drivers={})

    # valid assignment
    assigns.set(ports["vec_a_o"], ports["vec_a_i"])

    # re-assignement
    with raises(ValueError) as raised:
        assigns.set(ports["vec_a_o"], ports["vec_d_i"])
    assert (
        str(raised.value)
        == "'Port(UintType(8), name='vec_a_o')' already assigned to 'Port(UintType(8), name='vec_a_i')'"
    )

    # assign type mismatch
    # with raises(TypeError) as raised:
    #     assigns.set(ports["vec_c_o"], ports["vec_b_i"])
    # assert str(raised.value) == "Cannot assign 'vec_b_i' of UintType(14) to 'vec_c_o' of UintType(4)"
    # with raises(TypeError) as raised:
    #     assigns.set(ports["vec_c_o"], ports["vec_b_i"][12:2])
    # assert str(raised.value) == "Cannot assign 'vec_b_i[12:2]' of UintType(11) to 'vec_c_o' of UintType(4)"

    # assign
    assigns.set(ports["vec_c_o"], ports["vec_b_i"][12:9])

    # assign Concat
    assigns.set(ports["vec_d_o"], ucdp.concat((ports["vec_c_i"], ports["vec_c_i"])))

    # # no target
    # with raises(ValueError) as raised:
    #     assigns.set(signals["my_b_s"], signals["my_a_s"])
    # assert str(raised.value) == "'my_b_s' is not available within target namespace"

    assigns.set(ports["my_a_o"], ports["my_a_i"])
    assigns.set(ports["my_b_o"], signals["my_a_s"])

    assert_assigns(tmp_path, "test_assign", assigns)


# pylint: disable=redefined-outer-name
def test_assign_inst(tmp_path, ports, signals):
    """Test Assign with complete=True."""
    assigns = ucdp.Assigns(ports, signals, inst=True)
    assert_assigns(tmp_path, "test_assign_inst", assigns)


# pylint: disable=redefined-outer-name
def test_assign_slice(tmp_path, ports, signals):
    """Test Assign slice."""
    assigns = ucdp.Assigns(ports, signals)
    assigns.set_default(ports["vec_a_o"], ports["vec_a_i"])
    assigns.set(ports["vec_a_o"][4:3], ports["vec_d_i"][3:2])
    assigns.set(ports["vec_b_o"][6:3], ports["vec_c_i"])
    assigns.set(ports["vec_b_o"][12:9], ports["vec_c_i"])
    assert_assigns(tmp_path, "test_assign_slice", assigns)


# pylint: disable=redefined-outer-name
def test_assign_slice_inst(tmp_path, ports, signals):
    """Test Assign slice at inst."""
    assigns = ucdp.Assigns(ports, signals, inst=True)
    assigns.set(ports["vec_a_i"][4:3], ports["vec_d_o"][3:2])
    assigns.set(ports["vec_b_o"][6:3], ports["vec_c_o"])
    assigns.set(ports["vec_b_o"][12:9], ports["vec_c_o"])
    assert_assigns(tmp_path, "test_assign_inst", assigns)
