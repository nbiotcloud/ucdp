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
"""Test Multiplexer."""

import re

from pytest import raises

from ucdp import DOWN, UP, Const, Slice, UintType


def test_str():
    """Slice from String."""
    assert Slice(left="5").bits == "5"
    assert Slice(left="[5:7]").bits == "5:7"
    assert Slice(left="[7:5]").bits == "7:5"
    with raises(ValueError, match=re.escape("'right' must be None")):
        Slice(left="6", right=4)
    with raises(ValueError, match=re.escape("'width' must be None")):
        Slice(left="6", width=4)
    with raises(ValueError, match=re.escape("Invalid Slice Specification ''")):
        Slice(left="")


def test_width():
    """Slice with Width."""
    assert Slice(width=2).bits == "1:0"
    assert Slice(left=4, width=2).bits == "4:3"
    assert Slice(right=4, width=2).bits == "5:4"
    with raises(ValueError, match=re.escape("'left', 'right' AND 'width' given, this is one too much")):
        Slice(left=1, right=2, width=3)


def test_up():
    """Slice Upwards."""
    assert Slice(width=2, direction=UP).bits == "0:1"
    assert Slice(width=2, left=2, direction=UP).bits == "2:3"
    assert Slice(width=2, right=2, direction=UP).bits == "1:2"


def test_down():
    """Slice Downwards."""
    assert Slice(width=2, direction=DOWN).bits == "1:0"
    assert Slice(width=2, left=2, direction=DOWN).bits == "2:1"
    assert Slice(width=2, right=2, direction=DOWN).bits == "3:2"


def test_const():
    """Const."""
    const4 = Const(UintType(8, default=4), "const4")

    assert (
        Slice(width=const4).bits
        == "Op(Const(UintType(8, default=4), 'const4'), '-', ConstExpr(UintType(8, default=1))):0"
    )
    assert (
        Slice(width=const4, right=0).bits
        == "Op(Const(UintType(8, default=4), 'const4'), '-', ConstExpr(UintType(8, default=1))):0"
    )
    assert (
        Slice(width=const4, right=2).bits
        == "Op(Op(Const(UintType(8, default=4), 'const4'), '-', ConstExpr(UintType(8, default=1))), '+', "
        "ConstExpr(UintType(8, default=2))):2"
    )

    assert Slice(right=const4).bits == "const4"
    assert Slice(right=const4, width=1).bits == "const4"
    assert (
        Slice(right=const4, width=3).bits
        == "Op(ConstExpr(UintType(8, default=2)), '+', Const(UintType(8, default=4), 'const4')):const4"
    )

    assert Slice(left=const4).bits == "const4"
    assert Slice(left=const4, width=1).bits == "const4"
    assert (
        Slice(left=const4, width=3).bits
        == "const4:Op(Const(UintType(8, default=4), 'const4'), '-', ConstExpr(UintType(8, default=2)))"
    )
