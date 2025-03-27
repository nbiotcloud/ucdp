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
"""Expression Testing."""

from test2ref import assert_refdata

import ucdp as u


def _test_op(file, expr):
    type_ = getattr(expr, "type_", "-")
    file.write(f"{expr!r} {int(expr)} {bool(expr)} {type_}\n")


def test_const_const(tmp_path):
    """Const op Const."""
    one = u.const("16'd10")
    other = u.const("16'd5")
    resultfile = tmp_path / "result.txt"
    with resultfile.open("w") as file:
        _test_op(file, one + other)
        _test_op(file, one - other)
        _test_op(file, one * other)
        _test_op(file, one // other)
        _test_op(file, one % other)
        _test_op(file, one**other)
        _test_op(file, one > other)
        _test_op(file, one >= other)
        _test_op(file, one >> other)
        _test_op(file, one < other)
        _test_op(file, one <= other)
        _test_op(file, one << other)
        _test_op(file, one == other)
        _test_op(file, one != other)
        _test_op(file, one & other)
        _test_op(file, one | other)
        _test_op(file, one ^ other)
        _test_op(file, ~one)
        _test_op(file, -one)
        _test_op(file, abs(one))
        _test_op(file, abs(-one))
    assert_refdata(test_const_const, tmp_path)


def test_const_int(tmp_path):
    """Const op int."""
    one = u.const("16'd10")
    other = 5
    resultfile = tmp_path / "result.txt"
    with resultfile.open("w") as file:
        _test_op(file, one + other)
        _test_op(file, one - other)
        _test_op(file, one * other)
        _test_op(file, one // other)
        _test_op(file, one % other)
        _test_op(file, one**other)
        _test_op(file, one > other)
        _test_op(file, one >= other)
        _test_op(file, one >> other)
        _test_op(file, one < other)
        _test_op(file, one <= other)
        _test_op(file, one << other)
        _test_op(file, one == other)
        _test_op(file, one != other)
        _test_op(file, one & other)
        _test_op(file, one | other)
        _test_op(file, one ^ other)
        _test_op(file, ~one)
        _test_op(file, -one)
        _test_op(file, abs(one))
        _test_op(file, abs(-one))
    assert_refdata(test_const_int, tmp_path)


def test_int_const(tmp_path):
    """Const op int."""
    one = 10
    other = u.const("16'd5")
    resultfile = tmp_path / "result.txt"
    with resultfile.open("w") as file:
        _test_op(file, one + other)
        _test_op(file, one - other)
        _test_op(file, one * other)
        _test_op(file, one // other)
        _test_op(file, one % other)
        _test_op(file, one**other)
        _test_op(file, one > other)
        _test_op(file, one >= other)
        _test_op(file, one >> other)
        _test_op(file, one < other)
        _test_op(file, one <= other)
        _test_op(file, one << other)
        _test_op(file, one == other)
        _test_op(file, one != other)
        _test_op(file, one & other)
        _test_op(file, one | other)
        _test_op(file, one ^ other)
        _test_op(file, ~one)
        _test_op(file, -one)
        _test_op(file, abs(one))
        _test_op(file, abs(-one))
    assert_refdata(test_int_const, tmp_path)


def test_slice_const():
    """Test Slicing of Const."""
    param_p = u.ConstExpr(u.UintType(8, default=5))
    expr = u.const(2)
    assert param_p[2:1] == u.SliceOp(u.Param(u.UintType(8, default=5), "param_p"), u.Slice("2:1"))
    assert param_p[2] == u.SliceOp(u.Param(u.UintType(8, default=5), "param_p"), u.Slice("2"))
    assert param_p[expr] == u.SliceOp(
        u.Param(u.UintType(8, default=5), "param_p"), u.Slice(u.ConstExpr(u.IntegerType(default=2)))
    )


def test_slice_param():
    """Test Slicing of Param."""
    param_p = u.Param(u.UintType(8, default=5), "param_p")
    expr = u.const(2)
    assert param_p[2:1] == u.SliceOp(u.Param(u.UintType(8, default=5), "param_p"), u.Slice("2:1"))
    assert param_p[2] == u.SliceOp(u.Param(u.UintType(8, default=5), "param_p"), u.Slice("2"))
    assert param_p[expr] == u.SliceOp(
        u.Param(u.UintType(8, default=5), "param_p"), u.Slice(u.ConstExpr(u.IntegerType(default=2)))
    )
