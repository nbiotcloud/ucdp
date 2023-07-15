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
"""Expression Testing."""
from pytest import fixture, raises

import ucdp


@fixture
def names():
    """Names."""
    return ucdp.Idents(
        [
            ucdp.Signal(ucdp.UintType(3), "data3_s"),
            ucdp.Signal(ucdp.UintType(3), "uint3_s"),
        ]
    )


# pylint: disable=redefined-outer-name
def test_ident(names):
    """Identifier Parsing."""
    assert ucdp.parse("data3_s", namespace=names) == names["data3_s"]
    assert ucdp.parse("data3_s[2]", namespace=names) == names["data3_s"][2]
    with raises(NameError):
        ucdp.parse("data3_s")
    with raises(NameError):
        ucdp.parse("unknown_s", namespace=names)
    assert ucdp.parse("ConstExpr(IntegerType(default=10))") is ucdp.ConstExpr(ucdp.IntegerType(default=10))
    # assert ucdp.parse('const("3\'d4")') is ucdp.ConstExpr(ucdp.UintType(3, default=4))


def test_constparse(names):
    """Constant Parsing."""
    assert repr(ucdp.parse("3b001", namespace=names)) == "ConstExpr(UintType(3, default=1))"


def test_constinexpr(names):
    """Constant in Expression Parsing."""
    assert (
        repr(ucdp.parse("data3_s > '3d2'", namespace=names))
        == "BoolOp(Signal(UintType(3), 'data3_s'), '>', ConstExpr(UintType(3, default=2)))"
    )


def _test_op(expr, intvalue, type_):
    assert isinstance(expr, ucdp.Op)
    assert int(expr) == intvalue
    assert expr.type_ is type_


def _test_sop(expr, intvalue, type_):
    assert isinstance(expr, ucdp.SOp)
    assert int(expr) == intvalue
    assert expr.type_ is type_


def _test_expr(expr, intvalue, type_, cls):
    assert isinstance(expr, cls)
    assert int(expr) == intvalue
    assert expr.type_ is type_


def test_const_const():
    """Const op Const."""
    one = ucdp.const("16'd10")
    other = ucdp.const("16'd5")
    _test_op(one + other, 15, ucdp.UintType(16, default=10))
    _test_op(one - other, 5, ucdp.UintType(16, default=10))
    _test_op(one * other, 50, ucdp.UintType(16, default=10))
    _test_op(one // other, 2, ucdp.UintType(16, default=10))
    _test_op(one % other, 0, ucdp.UintType(16, default=10))
    _test_op(one**other, 100000, ucdp.UintType(16, default=10))
    _test_op(one > other, 1, ucdp.BoolType())
    _test_op(one >= other, 1, ucdp.BoolType())
    _test_op(one == other, 0, ucdp.BoolType())
    _test_op(one != other, 1, ucdp.BoolType())
    _test_op(one <= other, 0, ucdp.BoolType())
    _test_op(one < other, 0, ucdp.BoolType())
    _test_op(one << other, 320, ucdp.UintType(16, default=10))
    _test_op(one >> other, 0, ucdp.UintType(16, default=10))
    _test_op(one & other, 0, ucdp.UintType(16, default=10))
    _test_op(one | other, 15, ucdp.UintType(16, default=10))
    _test_op(one ^ other, 15, ucdp.UintType(16, default=10))
    _test_sop(~one, -11, ucdp.UintType(16, default=10))
    _test_sop(-one, -10, ucdp.UintType(16, default=10))
    _test_sop(abs(one), 10, ucdp.UintType(16, default=10))
    _test_sop(abs(-one), 10, ucdp.UintType(16, default=10))


def test_const_str():
    """Const op String."""
    one = ucdp.const("16'd10")
    other = "16'd5"
    _test_op(one + other, 15, ucdp.UintType(16, default=10))
    _test_op(one - other, 5, ucdp.UintType(16, default=10))
    _test_op(one * other, 50, ucdp.UintType(16, default=10))
    _test_op(one // other, 2, ucdp.UintType(16, default=10))
    _test_op(one % other, 0, ucdp.UintType(16, default=10))
    _test_op(one**other, 100000, ucdp.UintType(16, default=10))
    _test_op(one > other, 1, ucdp.BoolType())
    _test_op(one >= other, 1, ucdp.BoolType())
    _test_op(one == other, 0, ucdp.BoolType())
    _test_op(one != other, 1, ucdp.BoolType())
    _test_op(one <= other, 0, ucdp.BoolType())
    _test_op(one < other, 0, ucdp.BoolType())
    _test_op(one << other, 320, ucdp.UintType(16, default=10))
    _test_op(one >> other, 0, ucdp.UintType(16, default=10))
    _test_op(one & other, 0, ucdp.UintType(16, default=10))
    _test_op(one | other, 15, ucdp.UintType(16, default=10))
    _test_op(one ^ other, 15, ucdp.UintType(16, default=10))
    _test_sop(~one, -11, ucdp.UintType(16, default=10))
    _test_sop(-one, -10, ucdp.UintType(16, default=10))
    _test_sop(abs(one), 10, ucdp.UintType(16, default=10))
    _test_sop(abs(-one), 10, ucdp.UintType(16, default=10))


def test_const_int():
    """Const op Int."""
    one = ucdp.const("16'd10")
    other = 5
    _test_op(one + other, 15, ucdp.UintType(16, default=10))
    _test_op(one - other, 5, ucdp.UintType(16, default=10))
    _test_op(one * other, 50, ucdp.UintType(16, default=10))
    _test_op(one // other, 2, ucdp.UintType(16, default=10))
    _test_op(one % other, 0, ucdp.UintType(16, default=10))
    _test_op(one**other, 100000, ucdp.UintType(16, default=10))
    _test_op(one > other, 1, ucdp.BoolType())
    _test_op(one >= other, 1, ucdp.BoolType())
    _test_op(one == other, 0, ucdp.BoolType())
    _test_op(one != other, 1, ucdp.BoolType())
    _test_op(one <= other, 0, ucdp.BoolType())
    _test_op(one < other, 0, ucdp.BoolType())
    _test_op(one << other, 320, ucdp.UintType(16, default=10))
    _test_op(one >> other, 0, ucdp.UintType(16, default=10))
    _test_op(one & other, 0, ucdp.UintType(16, default=10))
    _test_op(one | other, 15, ucdp.UintType(16, default=10))
    _test_op(one ^ other, 15, ucdp.UintType(16, default=10))
    _test_sop(~one, -11, ucdp.UintType(16, default=10))
    _test_sop(-one, -10, ucdp.UintType(16, default=10))
    _test_sop(abs(one), 10, ucdp.UintType(16, default=10))
    _test_sop(abs(-one), 10, ucdp.UintType(16, default=10))


def test_str_const():
    """String op Const."""
    one = "16'd10"
    other = ucdp.const("16'd5")
    _test_op(one + other, 15, ucdp.UintType(16, default=10))
    _test_op(one - other, 5, ucdp.UintType(16, default=10))
    _test_op(one * other, 50, ucdp.UintType(16, default=10))
    _test_op(one // other, 2, ucdp.UintType(16, default=10))
    _test_op(one**other, 100000, ucdp.UintType(16, default=10))
    _test_op(one > other, 1, ucdp.BoolType())
    _test_op(one >= other, 1, ucdp.BoolType())
    _test_op(one == other, 0, ucdp.BoolType())
    _test_op(one != other, 1, ucdp.BoolType())
    _test_op(one <= other, 0, ucdp.BoolType())
    _test_op(one < other, 0, ucdp.BoolType())
    _test_op(one << other, 320, ucdp.UintType(16, default=10))
    _test_op(one >> other, 0, ucdp.UintType(16, default=10))
    _test_op(one & other, 0, ucdp.UintType(16, default=10))
    _test_op(one | other, 15, ucdp.UintType(16, default=10))
    _test_op(one ^ other, 15, ucdp.UintType(16, default=10))


def test_int_const():
    """Int op Const."""
    one = 10
    other = ucdp.const("16'd5")
    _test_op(one + other, 15, ucdp.UintType(16, default=5))
    _test_op(one - other, 5, ucdp.UintType(16, default=5))
    _test_op(one * other, 50, ucdp.UintType(16, default=5))
    _test_op(one // other, 2, ucdp.UintType(16, default=5))
    _test_op(one % other, 0, ucdp.UintType(16, default=5))
    _test_op(one**other, 100000, ucdp.UintType(16, default=5))
    _test_op(one > other, 1, ucdp.BoolType())
    _test_op(one >= other, 1, ucdp.BoolType())
    _test_op(one == other, 0, ucdp.BoolType())
    _test_op(one != other, 1, ucdp.BoolType())
    _test_op(one <= other, 0, ucdp.BoolType())
    _test_op(one < other, 0, ucdp.BoolType())
    _test_op(one << other, 320, ucdp.UintType(16, default=5))
    _test_op(one >> other, 0, ucdp.UintType(16, default=5))
    _test_op(one & other, 0, ucdp.UintType(16, default=5))
    _test_op(one | other, 15, ucdp.UintType(16, default=5))
    _test_op(one ^ other, 15, ucdp.UintType(16, default=5))


def test_const_expr():
    """Const op String."""
    one = ucdp.const("16'd10")
    other = ucdp.const("16'd10") - ucdp.const("16'd5")
    _test_op(one + other, 15, ucdp.UintType(16, default=10))
    _test_op(one - other, 5, ucdp.UintType(16, default=10))
    _test_op(one * other, 50, ucdp.UintType(16, default=10))
    _test_op(one // other, 2, ucdp.UintType(16, default=10))
    _test_op(one % other, 0, ucdp.UintType(16, default=10))
    _test_op(one**other, 100000, ucdp.UintType(16, default=10))
    _test_op(one > other, 1, ucdp.BoolType())
    _test_op(one >= other, 1, ucdp.BoolType())
    _test_op(one == other, 0, ucdp.BoolType())
    _test_op(one != other, 1, ucdp.BoolType())
    _test_op(one <= other, 0, ucdp.BoolType())
    _test_op(one < other, 0, ucdp.BoolType())
    _test_op(one << other, 320, ucdp.UintType(16, default=10))
    _test_op(one >> other, 0, ucdp.UintType(16, default=10))
    _test_op(one & other, 0, ucdp.UintType(16, default=10))
    _test_op(one | other, 15, ucdp.UintType(16, default=10))
    _test_op(one ^ other, 15, ucdp.UintType(16, default=10))


def test_ident_const():
    """Identifier op Const."""
    ones = [
        ucdp.Ident(ucdp.UintType(16, default=10), "name"),
        ucdp.Param(ucdp.UintType(16, default=10), "name"),
        ucdp.Const(ucdp.UintType(16, default=10), "name"),
        ucdp.Port(ucdp.UintType(16, default=10), "name", direction=ucdp.IN),
        ucdp.Signal(ucdp.UintType(16, default=10), "name"),
        # ucdp.FlipFlop(ucdp.UintType(16, default=10), "name"),
    ]
    other = ucdp.const("16'd5")
    for one in ones:
        _test_op(one + other, 15, ucdp.UintType(16, default=10))
        _test_op(one - other, 5, ucdp.UintType(16, default=10))
        _test_op(one * other, 50, ucdp.UintType(16, default=10))
        _test_op(one // other, 2, ucdp.UintType(16, default=10))
        _test_op(one % other, 0, ucdp.UintType(16, default=10))
        _test_op(one**other, 100000, ucdp.UintType(16, default=10))
        _test_op(one > other, 1, ucdp.BoolType())
        _test_op(one >= other, 1, ucdp.BoolType())
        _test_op(one == other, 0, ucdp.BoolType())
        _test_op(one != other, 1, ucdp.BoolType())
        _test_op(one <= other, 0, ucdp.BoolType())
        _test_op(one < other, 0, ucdp.BoolType())
        _test_op(one << other, 320, ucdp.UintType(16, default=10))
        _test_op(one >> other, 0, ucdp.UintType(16, default=10))
        _test_op(one & other, 0, ucdp.UintType(16, default=10))
        _test_op(one | other, 15, ucdp.UintType(16, default=10))
        _test_op(one ^ other, 15, ucdp.UintType(16, default=10))
        _test_sop(~one, -11, ucdp.UintType(16, default=10))
        _test_sop(-one, -10, ucdp.UintType(16, default=10))
        _test_sop(abs(one), 10, ucdp.UintType(16, default=10))
        _test_sop(abs(-one), 10, ucdp.UintType(16, default=10))


def test_ident_int():
    """Identifier op int."""
    ones = [
        ucdp.Ident(ucdp.UintType(16, default=10), "name"),
        ucdp.Param(ucdp.UintType(16, default=10), "name"),
        ucdp.Const(ucdp.UintType(16, default=10), "name"),
        ucdp.Port(ucdp.UintType(16, default=10), "name", direction=ucdp.IN),
        ucdp.Signal(ucdp.UintType(16, default=10), "name"),
        # ucdp.FlipFlop(ucdp.UintType(16, default=10), "name"),
    ]
    other = 5
    for one in ones:
        _test_op(one + other, 15, ucdp.UintType(16, default=10))
        _test_op(one - other, 5, ucdp.UintType(16, default=10))
        _test_op(one * other, 50, ucdp.UintType(16, default=10))
        _test_op(one // other, 2, ucdp.UintType(16, default=10))
        _test_op(one % other, 0, ucdp.UintType(16, default=10))
        _test_op(one**other, 100000, ucdp.UintType(16, default=10))
        _test_op(one > other, 1, ucdp.BoolType())
        _test_op(one >= other, 1, ucdp.BoolType())
        _test_op(one != other, 1, ucdp.BoolType())
        _test_op(one == other, 0, ucdp.BoolType())
        _test_op(one <= other, 0, ucdp.BoolType())
        _test_op(one < other, 0, ucdp.BoolType())
        _test_op(one << other, 320, ucdp.UintType(16, default=10))
        _test_op(one >> other, 0, ucdp.UintType(16, default=10))
        _test_op(one & other, 0, ucdp.UintType(16, default=10))
        _test_op(one | other, 15, ucdp.UintType(16, default=10))
        _test_op(one ^ other, 15, ucdp.UintType(16, default=10))
        _test_sop(~one, -11, ucdp.UintType(16, default=10))
        _test_sop(-one, -10, ucdp.UintType(16, default=10))
        _test_sop(abs(one), 10, ucdp.UintType(16, default=10))
        _test_sop(abs(-one), 10, ucdp.UintType(16, default=10))


def test_ternary():
    """Ternary."""
    cond = ucdp.Signal(ucdp.BitType(), "if_s")
    one = ucdp.Signal(ucdp.UintType(16, default=10), "one_s")
    other = ucdp.Signal(ucdp.UintType(16, default=20), "other_s")
    expr = ucdp.ternary(cond, one, other)
    _test_expr(expr, 20, ucdp.UintType(16, default=10), ucdp.TernaryExpr)
    assert int(expr) == 20


def test_ternary_true():
    """Ternary."""
    cond = ucdp.Signal(ucdp.BitType(default=1), "if_s")
    one = ucdp.Signal(ucdp.UintType(16, default=10), "one_s")
    other = ucdp.Signal(ucdp.UintType(16, default=20), "other_s")
    expr = ucdp.ternary(cond, one, other)
    _test_expr(expr, 10, ucdp.UintType(16, default=10), ucdp.TernaryExpr)
    assert int(expr) == 10


def test_ternary_expr():
    """Ternary."""
    cond = ucdp.Signal(ucdp.BitType(), "if_s") * 2
    one = ucdp.Signal(ucdp.UintType(16, default=10), "one_s") * 2
    other = ucdp.Signal(ucdp.UintType(16, default=20), "other_s") * 2
    assert int(cond) == 0
    assert int(one) == 20
    assert int(other) == 40
    _test_expr(ucdp.ternary(cond, one, other), 40, ucdp.UintType(16, default=10), ucdp.TernaryExpr)


def test_slice_param():
    """Test Slicing of Param."""
    param_p = ucdp.Param(ucdp.UintType(8, default=5), "param_p")
    _test_expr(param_p[2:1], 2, ucdp.UintType(2, default=2), ucdp.SliceOp)


def test_slice_concat():
    """Test Slicing of Concat."""
    expr = ucdp.concat(("10'd2", 10))
    _test_expr(expr[2:1], 1, ucdp.UintType(2, default=1), ucdp.SliceOp)


def test_min():
    """Minimum."""
    param0_p = ucdp.Param(ucdp.UintType(8, default=5), "param0_p")
    param1_p = ucdp.Param(ucdp.UintType(8, default=8), "param1_p")
    expr = ucdp.minimum(param0_p, param1_p)
    _test_expr(expr, 5, ucdp.UintType(8, default=5), ucdp.MinimumFunc)
    expr = ucdp.minimum(param1_p, param0_p)
    _test_expr(expr, 5, ucdp.UintType(8, default=8), ucdp.MinimumFunc)


def test_max():
    """Maximum."""
    param0_p = ucdp.Param(ucdp.UintType(8, default=5), "param0_p")
    param1_p = ucdp.Param(ucdp.UintType(8, default=8), "param1_p")
    expr = ucdp.maximum(param0_p, param1_p)
    _test_expr(expr, 8, ucdp.UintType(8, default=5), ucdp.MaximumFunc)
    expr = ucdp.maximum(param1_p, param0_p)
    _test_expr(expr, 8, ucdp.UintType(8, default=8), ucdp.MaximumFunc)


def test_log2():
    """Log to base 2."""
    param_p = ucdp.Param(ucdp.UintType(8, default=5), "param_p")
    expr = ucdp.log2(param_p)
    _test_expr(expr, 2, ucdp.UintType(8, default=5), ucdp.Log2Func)


def test_comment():
    """Comment"""
    comment = ucdp.CommentExpr("mycomment")
    assert str(comment) == "CommentExpr('mycomment')"
    assert comment.type_ is None
