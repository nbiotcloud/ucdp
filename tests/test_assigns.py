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

import re
from pathlib import Path

from pytest import fixture, raises
from test2ref import assert_refdata

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
            u.Port(MyType(), "port_o"),
            u.Port(MyType(), "other_i"),
            u.Port(MyType(), "other_o"),
            u.Port(StructType(), "struct_i"),
            u.Port(StructType(), "struct_o"),
            u.Signal(StructType(), "struct_s"),
            u.Signal(MyType(), "sig_s"),
            u.Port(u.UintType(8), "data_i"),
            u.Port(u.UintType(8), "data_o"),
            u.Signal(u.UintType(8), "data0_s"),
            u.Signal(u.UintType(8), "data1_s"),
        ]
    )


@fixture
def sub() -> u.Idents:
    """Sub-Identifier."""
    return u.Idents(
        [
            u.Port(MyType(), "sub_i"),
            u.Port(MyType(), "sub_o"),
            u.Port(u.UintType(8), "data_i"),
            u.Port(u.UintType(8), "data_o"),
        ]
    )


def _dump_assigns(assigns: u.Assigns, path: Path, name: str = "assigns", full: bool = False):
    filepath = path / f"{name}.txt"
    with filepath.open("w") as file:
        if not full:
            file.write("SET-ONLY\n")
        for assign in assigns:
            if full or assign.source is not None:
                file.write(f"ASSIGN: {assign}\n")
        if assigns.drivers:
            for dname, value in assigns.drivers:
                file.write(f"DRIVER: {dname}: {value}\n")


def test_basic(top):
    """Assign Basics."""
    doc = u.Doc(title="title", descr="descr", comment="comment")
    target = u.Port(u.UintType(8), "a_i", doc=doc, ifdef="IFDEF")
    source = u.Signal(u.UintType(8), "b_s")
    assign = u.Assign(target=target, source=source)

    assert assign.name == "a_i"
    assert assign.type_ == u.UintType(8)
    assert assign.doc is doc
    assert assign.direction == u.IN
    assert assign.ifdef == "IFDEF"


def test_assign_empty(top, tmp_path):
    """Empty Assigns."""
    assigns = u.Assigns(targets=top, sources=top)
    _dump_assigns(assigns, tmp_path, full=True)
    assert_refdata(test_assign_empty, tmp_path)


def test_assign_empty_inst(top, tmp_path):
    """Empty Assigns for inst."""
    assigns = u.Assigns(targets=top, sources=top, inst=True)
    _dump_assigns(assigns, tmp_path, full=True)
    assert_refdata(test_assign_empty_inst, tmp_path)


def test_reassign(top, tmp_path):
    """Assigns."""
    assigns = u.Assigns(targets=top, sources=top)
    assigns.set(top["port_o"], top["other_i"])

    msg = "'port_o' already assigned to 'other_i'"
    with raises(ValueError, match=re.escape(msg)):
        assigns.set(top["port_o"], top["port_i"])

    _dump_assigns(assigns, tmp_path)
    assert_refdata(test_reassign, tmp_path)


def test_direction_error(top, tmp_path):
    """Assigns."""
    assigns = u.Assigns(targets=top, sources=top)

    msg = "Cannot drive 'other_i' by 'port_i'"
    with raises(ValueError, match=re.escape(msg)):
        assigns.set(top["other_i"], top["port_i"])

    assigns.set(top["other_o"], top["port_o"])
    assigns.set(top["port_i"], top["port_o"])
    assigns.set(top["data0_s"], top["data1_s"])

    _dump_assigns(assigns, tmp_path)
    assert_refdata(test_direction_error, tmp_path)


def test_inst_direction_error(top, tmp_path):
    """Assigns."""
    assigns = u.Assigns(targets=top, inst=True)

    msg = "Cannot drive 'other_o' by 'port_i'"
    with raises(ValueError, match=re.escape(msg)):
        assigns.set(top["other_o"], top["port_i"])

    assigns.set(top["other_o"], top["port_o"])
    assigns.set(top["other_i"], top["port_o"])
    assigns.set(top["data0_s"], top["data1_s"])

    _dump_assigns(assigns, tmp_path)
    assert_refdata(test_inst_direction_error, tmp_path)


def test_drivers(top, tmp_path):
    """Multiple Drivers."""
    drivers = u.Drivers()
    assigns0 = u.Assigns(targets=top, sources=top, drivers=drivers)
    assigns0.set(top["port_o"], top["other_i"])
    assigns1 = u.Assigns(targets=top, sources=top, drivers=drivers)

    msg = "'other_i' already driven by 'other_i'"
    with raises(u.MultipleDriverError, match=re.escape(msg)):
        assigns1.set(top["port_o"], top["other_i"])

    _dump_assigns(assigns0, tmp_path, name="assign0")
    _dump_assigns(assigns1, tmp_path, name="assign1")
    assert_refdata(test_drivers, tmp_path)


def test_lock(top, tmp_path):
    """Lock."""
    assigns = u.Assigns(targets=top, sources=top)
    assert assigns.is_locked is False

    assigns.lock()

    assert assigns.is_locked is True

    msg = "Cannot set 'other_i' to 'port_o'"
    with raises(u.LockError, match=re.escape(msg)):
        assigns.set(top["port_o"], top["other_i"])

    msg = "Cannot set default 'other_i' to 'port_o'"
    with raises(u.LockError, match=re.escape(msg)):
        assigns.set_default(top["port_o"], top["other_i"])

    msg = "Assigns are already locked. Cannot lock again."
    with raises(u.LockError, match=re.escape(msg)):
        assigns.lock()

    _dump_assigns(assigns, tmp_path)
    assert_refdata(test_lock, tmp_path)


def test_assign(top, tmp_path):
    """Test Assigns."""
    assigns = u.Assigns(targets=top)

    # valid assignment
    assigns.set(top["port_o"], top["port_i"])

    # re-assignement
    msg = "'port_o' already assigned to 'port_i'"
    with raises(ValueError, match=re.escape(msg)):
        assigns.set(top["port_o"], top["other_i"])

    # assign
    msg = "Cannot assign 'data_o' of type UintType(8) to 'port_i' of type MyType()."
    with raises(TypeError, match=re.escape(msg)):
        assigns.set(top["port_i"], top["data_o"])

    _dump_assigns(assigns, tmp_path)
    assert_refdata(test_assign, tmp_path)


def test_concat(tmp_path):
    """Test Concatenation."""
    a_i = u.Port(u.UintType(4), "a_i")
    b_i = u.Port(u.UintType(4), "b_i")
    c_o = u.Port(u.UintType(8), "c_o")
    idents = u.Idents([a_i, b_i, c_o])
    assigns = u.Assigns(targets=idents)

    assigns.set(c_o, u.ConcatExpr((a_i, b_i)))
    _dump_assigns(assigns, tmp_path)
    assert_refdata(test_concat, tmp_path)


def test_const(top, tmp_path):
    """Type Error."""
    assigns = u.Assigns(targets=top)
    constscal = u.Const(u.UintType(8), "scal")
    myconst = u.Const(MyType(), "const_c")

    msg = "Target const_c is not a Signal, Port or Slice of them"
    with raises(ValueError, match=re.escape(msg)):
        assigns.set(myconst, top["port_i"])

    assigns.set(top["data_o"], constscal)

    msg = "Target const_my0_return_c is not a Signal or Port"
    with raises(ValueError, match=re.escape(msg)):
        assigns.set(top["port_o"], myconst)

    _dump_assigns(assigns, tmp_path)
    assert_refdata(test_const, tmp_path)


def test_assign_slice(tmp_path):
    """Test Assign slice."""
    a_i = u.Port(u.UintType(4), "a_i")
    b_i = u.Port(u.UintType(4), "b_i")
    c_i = u.Port(u.UintType(4), "c_i")
    c_o = u.Port(u.UintType(10, default=0x1A1), "c_o")
    idents = u.Idents([a_i, b_i, c_o])
    drivers = u.Drivers()
    assigns = u.Assigns(targets=idents, drivers=drivers)

    assigns.set(c_o[3:1], a_i[2:0])
    assigns.set(c_o[6:5], b_i[2:1])

    msg = "Slice 6:5 is already taken by SliceOp(Port(UintType(4), 'b_i', direction=IN), Slice('2:1'))"
    with raises(ValueError, match=re.escape(msg)):
        assigns.set(c_o[6:5], c_i[2:1])

    msg = "Cannot slice bit(s) 11 from UintType(10, default=417)"
    with raises(ValueError, match=re.escape(msg)):
        assigns.set(c_o[11], b_i[3])

    _dump_assigns(assigns, tmp_path)
    assert_refdata(test_assign_slice, tmp_path)


def test_assign_slice_inst(tmp_path):
    """Test Assign slice."""
    a_i = u.Port(u.UintType(4), "a_i")
    b_i = u.Port(u.UintType(4), "b_i")
    c_i = u.Port(u.UintType(4), "c_i")
    c_o = u.Port(u.UintType(10, default=0x1A1), "c_o")
    idents = u.Idents([a_i, b_i, c_i, c_o])
    drivers = u.Drivers()
    assigns = u.Assigns(targets=idents, drivers=drivers, inst=True)

    assigns.set(c_o[3:1], a_i[2:0])
    assigns.set(c_o[6:5], b_i[2:1])

    msg = "Slice 6:5 is already taken by SliceOp(Port(UintType(4), 'b_i', direction=IN), Slice('2:1'))"
    with raises(ValueError, match=re.escape(msg)):
        assigns.set(c_o[6:5], c_i[2:1])

    msg = "Cannot slice bit(s) 11 from UintType(10, default=417)"
    with raises(ValueError, match=re.escape(msg)):
        assigns.set(c_o[11], b_i[3])

    _dump_assigns(assigns, tmp_path)
    assert_refdata(test_assign_slice_inst, tmp_path)


def test_top_in(top, tmp_path):
    """Top - Input."""
    drivers = u.Drivers()
    assigns = u.Assigns(targets=top, drivers=drivers)
    assigns.set(top["port_i"], top["port_o"])
    _dump_assigns(assigns, tmp_path)
    assert_refdata(test_top_in, tmp_path)


def test_top_out(top, tmp_path):
    """Top - Output."""
    drivers = u.Drivers()
    assigns = u.Assigns(targets=top, drivers=drivers)
    assigns.set(top["port_o"], top["port_i"])
    _dump_assigns(assigns, tmp_path)
    assert_refdata(test_top_out, tmp_path)


def test_top_inst_in(top, sub, tmp_path):
    """Top with Sub - Input."""
    drivers = u.Drivers()
    assigns = u.Assigns(targets=sub, sources=top, inst=True, drivers=drivers)
    assigns.set(sub["sub_i"], top["port_i"])
    _dump_assigns(assigns, tmp_path)
    assert_refdata(test_top_inst_in, tmp_path)


def test_top_inst_out(top, sub, tmp_path):
    """Top with Sub - Output."""
    drivers = u.Drivers()
    assigns = u.Assigns(targets=sub, sources=top, inst=True, drivers=drivers)
    assigns.set(sub["sub_o"], top["port_o"])
    _dump_assigns(assigns, tmp_path)
    assert_refdata(test_top_inst_out, tmp_path)


def test_top_inst_in_note(top, sub, tmp_path):
    """Top with Sub - Input."""
    drivers = u.Drivers()
    assigns = u.Assigns(targets=sub, sources=top, inst=True, drivers=drivers)
    assigns.set(sub["sub_my1_i"], u.TODO)
    _dump_assigns(assigns, tmp_path)
    assert_refdata(test_top_inst_in_note, tmp_path)


def test_top_inst_in_const(top, sub, tmp_path):
    """Top with Sub - Input."""
    drivers = u.Drivers()
    assigns = u.Assigns(targets=sub, sources=top, inst=True, drivers=drivers)
    assigns.set(sub["data_i"], u.const("8h2"))

    _dump_assigns(assigns, tmp_path)
    assert_refdata(test_top_inst_in_const, tmp_path)


def test_assign_cast(tmp_path):
    """Test Casting."""

    class MyEnumType(u.AEnumType):
        keytype: u.UintType = u.UintType(4)

        def _build(self):
            self._add(u.AUTO, "a")
            self._add(u.AUTO, "b")
            self._add(u.AUTO, "c")

    targets = u.Idents(
        [
            u.Port(u.UintType(4), "data_i"),
            u.Port(MyEnumType(), "a_o"),
            u.Port(MyEnumType(), "b_o"),
            u.Port(MyEnumType(), "c_o"),
        ]
    )
    assigns = u.Assigns(targets=targets)

    msg = "MyEnumType(). Try to cast."
    with raises(TypeError, match=re.escape(msg)):
        assigns.set(targets["a_o"], targets["data_i"])

    assigns.set(targets["b_o"], targets["data_i"], cast=None)

    _dump_assigns(assigns, tmp_path)
    assert_refdata(test_assign_cast, tmp_path)
