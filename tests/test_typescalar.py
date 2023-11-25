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

"""
Scalar Type Testing.

* :any:`IntegerType`
* :any:`BitType`
* :any:`BoolType`
* :any:`RailType`
* :any:`UintType`
* :any:`SintType`

"""
from icdutil.slices import Slice
from pytest import raises

import ucdp

# ruff: noqa: PLR2004


def test_bit():
    """Bit."""
    assert ucdp.BitType() is ucdp.BitType()
    assert ucdp.BitType() is not ucdp.BitType(default=0)
    assert ucdp.BitType() is not ucdp.BitType(default=1)
    with raises(ucdp.ValidationError):
        ucdp.BitType(width=3)


def test_integer():
    """Integer."""
    var0 = ucdp.IntegerType()
    assert var0.default == 0
    assert var0.width == 32
    assert repr(var0) == "IntegerType()"
    with raises(ucdp.ValidationError):
        var0.default = 0xF
    assert var0.default == 0

    assert 1 in var0

    var1 = ucdp.IntegerType(default=8)
    assert var1.default == 8
    assert var1.width == 32
    assert repr(var1) == "IntegerType(default=8)"

    var2 = ucdp.IntegerType()
    assert var2.default == 0
    assert var2.width == 32
    assert repr(var2) == "IntegerType()"

    with raises(ucdp.ValidationError):
        ucdp.IntegerType(width=4)

    assert var0 is not var1
    assert var0 is var2
    assert var0 != var1
    assert var0 == var2

    with raises(ValueError):
        ucdp.IntegerType(default="safe")

    assert ucdp.IntegerType() is ucdp.IntegerType()
    assert ucdp.IntegerType() is not ucdp.IntegerType(default=0)
    assert ucdp.IntegerType() is not ucdp.IntegerType(default=1)


def test_rail():
    """Rail."""
    var0 = ucdp.RailType()
    assert var0.default is None
    assert var0.width == 1
    assert repr(var0) == "RailType()"
    with raises(ucdp.ValidationError):
        var0.default = 0xF
    assert var0.default is None

    assert 1 in var0

    var1 = ucdp.RailType(default=1)
    assert var1.default == 1
    assert var1.width == 1
    assert repr(var1) == "RailType(default=1)"

    var2 = ucdp.RailType()
    assert var2.default is None
    assert var2.width == 1
    assert repr(var2) == "RailType()"

    with raises(ucdp.ValidationError):
        ucdp.RailType(width=4)

    assert var0 is not var1
    assert var0 is var2
    assert var0 != var1
    assert var0 == var2

    with raises(ValueError):
        ucdp.RailType(default="safe")

    assert ucdp.RailType() is ucdp.RailType()
    assert ucdp.RailType() is not ucdp.RailType(default=0)
    assert ucdp.RailType() is not ucdp.RailType(default=1)


def test_uint():
    """Uint Vector."""
    var0 = ucdp.UintType(12)
    assert var0.default == 0
    assert var0.width == 12
    assert var0.bits == 12
    assert repr(var0) == "UintType(12)"

    assert -1 not in var0
    assert 1 in var0
    assert 2**12 not in var0

    var1 = ucdp.UintType(12, default=8)
    assert var1.default == 8
    assert var1.width == 12
    assert var1.right == 0
    assert var1.slice_ == Slice("11:0")
    assert repr(var1) == "UintType(12, default=8)"

    assert repr(var1.new(width=4)) == "UintType(4, default=8)"

    with raises(ucdp.ValidationError):
        var1.default = 1

    assert var0 is not var1
    assert var0 != var1

    with raises(ValueError):
        ucdp.UintType(12, default="abc")

    var1 = ucdp.UintType(12, default=8, right=4)
    assert var1.default == 8
    assert var1.width == 12
    assert var1.right == 4
    assert var1.slice_ == Slice("15:4")
    assert repr(var1) == "UintType(12, default=8, right=4)"


def test_sint():
    """Sint Vector."""
    var0 = ucdp.SintType(12)
    assert var0.default == 0
    assert var0.width == 12
    assert var0.bits == 12
    assert repr(var0) == "SintType(12)"

    assert -1 in var0
    assert 1 in var0
    assert -(2**11) in var0
    assert 2**11 - 1 in var0
    assert 2**11 not in var0

    var1 = ucdp.SintType(12, default=8)
    assert var1.default == 8
    assert var1.width == 12
    assert var1.right == 0
    assert var1.slice_ == Slice("11:0")
    assert repr(var1) == "SintType(12, default=8)"

    assert repr(var1.new(width=5)) == "SintType(5, default=8)"
    with raises(ucdp.ValidationError):
        var1.new(width=4)

    with raises(ucdp.ValidationError):
        var1.default = 1

    assert var0 is not var1
    assert var0 != var1

    with raises(ValueError):
        ucdp.SintType(12, default="abc")

    var1 = ucdp.SintType(12, default=8, right=4)
    assert var1.default == 8
    assert var1.width == 12
    assert var1.right == 4
    assert var1.slice_ == Slice("15:4")
    assert repr(var1) == "SintType(12, default=8, right=4)"
