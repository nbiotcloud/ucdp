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
"""Test :any:`Object`."""

import ucdp as u
from pytest import fixture


@fixture
def idents() -> u.Idents:
    """Some Identifier."""
    return u.Idents(
        [
            u.Signal(u.UintType(16, default=15), "uint_s"),
            u.Signal(u.SintType(16, default=-15), "sint_s"),
        ]
    )


@fixture
def parser(idents) -> u.ExprParser:
    """Some Identifier."""
    return u.ExprParser(namespace=idents)


def test_parse(parser):
    """Parse."""
    expr = parser.parse("uint_s[2]")
    assert expr == u.SliceOp(u.Signal(u.UintType(16, default=15), "uint_s"), u.Slice("2"))


def test_int():
    """Test Integer."""
    signal = u.Signal(u.UintType(16, default=15), "uint_s")

    expr = signal // 2
    assert expr == u.Op(signal, "//", u.ConstExpr(u.UintType(16, default=2)))

    expr = signal // -2
    assert expr == u.Op(signal, "//", u.ConstExpr(u.SintType(2, default=-2)))


def test_const():
    """Test Constants."""
    assert u.const("0") is u.ConstExpr(u.IntegerType())
    assert u.const("2'b10") is u.ConstExpr(u.UintType(2, default=2))
    assert u.const("-2'sb10") is u.ConstExpr(u.SintType(2, default=-2))

    assert u.const("1'b0") is u.ConstExpr(u.BitType())
    assert u.const("1'b1") is u.ConstExpr(u.BitType(default=1))

    assert u.const("1'h0") is u.ConstExpr(u.UintType(1))
    assert u.const("1'h1") is u.ConstExpr(u.UintType(1, default=1))

    assert u.const(0) is u.ConstExpr(u.IntegerType())
    assert u.const(1) is u.ConstExpr(u.IntegerType(default=1))
    assert u.const(-1) is u.ConstExpr(u.IntegerType(default=-1))

    assert u.const(u.IntegerType.min_) is u.ConstExpr(u.IntegerType(default=u.IntegerType.min_))
    assert u.const(u.IntegerType.max_) is u.ConstExpr(u.IntegerType(default=u.IntegerType.max_))

    assert u.const(u.IntegerType.min_ - 1) is u.ConstExpr(u.SintType(33, default=u.IntegerType.min_ - 1))
    assert u.const(u.IntegerType.max_ + 1) is u.ConstExpr(u.UintType(32, default=u.IntegerType.max_ + 1))
