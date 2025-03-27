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

"""
Scalar Type Testing.

* :any:`IntegerType`
* :any:`BitType`
* :any:`BoolType`
* :any:`RailType`
* :any:`UintType`
* :any:`SintType`

"""

from pytest import raises

import ucdp as u


def test_bit():
    """Bit."""
    assert u.BitType() is u.BitType()
    assert u.BitType() is not u.BitType(default=0)
    assert u.BitType() is not u.BitType(default=1)
    with raises(u.ValidationError):
        u.BitType(width=3)


def test_integer():
    """Integer."""
    var0 = u.IntegerType()
    assert var0.default == 0
    assert var0.width == 32
    assert repr(var0) == "IntegerType()"
    with raises(u.ValidationError):
        var0.default = 0xF
    assert var0.default == 0

    assert 1 in var0

    var1 = u.IntegerType(default=8)
    assert var1.default == 8
    assert var1.width == 32
    assert repr(var1) == "IntegerType(default=8)"

    var2 = u.IntegerType()
    assert var2.default == 0
    assert var2.width == 32
    assert repr(var2) == "IntegerType()"

    with raises(u.ValidationError):
        u.IntegerType(width=4)

    assert var0 is not var1
    assert var0 is var2
    assert var0 != var1
    assert var0 == var2

    with raises(ValueError):
        u.IntegerType(default="safe")

    assert u.IntegerType() is u.IntegerType()
    assert u.IntegerType() is not u.IntegerType(default=0)
    assert u.IntegerType() is not u.IntegerType(default=1)


def test_rail():
    """Rail."""
    var0 = u.RailType()
    assert var0.default is None
    assert var0.width == 1
    assert repr(var0) == "RailType()"
    with raises(u.ValidationError):
        var0.default = 0xF
    assert var0.default is None

    assert 1 in var0

    var1 = u.RailType(default=1)
    assert var1.default == 1
    assert var1.width == 1
    assert repr(var1) == "RailType(default=1)"

    var2 = u.RailType()
    assert var2.default is None
    assert var2.width == 1
    assert repr(var2) == "RailType()"

    with raises(u.ValidationError):
        u.RailType(width=4)

    assert var0 is not var1
    assert var0 is var2
    assert var0 != var1
    assert var0 == var2

    with raises(ValueError):
        u.RailType(default="safe")

    assert u.RailType() is u.RailType()
    assert u.RailType() is not u.RailType(default=0)
    assert u.RailType() is not u.RailType(default=1)


def test_uint():
    """Uint Vector."""
    var0 = u.UintType(12)
    assert var0.default == 0
    assert var0.width == 12
    assert var0.bits == 12
    assert repr(var0) == "UintType(12)"

    assert -1 not in var0
    assert 1 in var0
    assert 2**12 not in var0

    var1 = u.UintType(12, default=8)
    assert var1.default == 8
    assert var1.width == 12
    assert var1.right == 0
    assert var1.slice_ == u.Slice("11:0")
    assert repr(var1) == "UintType(12, default=8)"

    assert repr(var1.new(width=4)) == "UintType(4, default=8)"

    with raises(u.ValidationError):
        var1.default = 1

    assert var0 is not var1
    assert var0 != var1

    with raises(ValueError):
        u.UintType(12, default="abc")

    var1 = u.UintType(12, default=8, right=4)
    assert var1.default == 8
    assert var1.width == 12
    assert var1.right == 4
    assert var1.slice_ == u.Slice("15:4")
    assert repr(var1) == "UintType(12, default=8, right=4)"


def test_sint():
    """Sint Vector."""
    var0 = u.SintType(12)
    assert var0.default == 0
    assert var0.width == 12
    assert var0.bits == 12
    assert repr(var0) == "SintType(12)"

    assert -1 in var0
    assert 1 in var0
    assert -(2**11) in var0
    assert 2**11 - 1 in var0
    assert 2**11 not in var0

    var1 = u.SintType(12, default=8)
    assert var1.default == 8
    assert var1.width == 12
    assert var1.right == 0
    assert var1.slice_ == u.Slice("11:0")
    assert repr(var1) == "SintType(12, default=8)"

    assert repr(var1.new(width=5)) == "SintType(5, default=8)"
    with raises(u.ValidationError):
        var1.new(width=4)

    with raises(u.ValidationError):
        var1.default = 1

    assert var0 is not var1
    assert var0 != var1

    with raises(ValueError):
        u.SintType(12, default="abc")

    var1 = u.SintType(12, default=8, right=4)
    assert var1.default == 8
    assert var1.width == 12
    assert var1.right == 4
    assert var1.slice_ == u.Slice("15:4")
    assert repr(var1) == "SintType(12, default=8, right=4)"


def test_doc():
    """Documentation."""
    assert u.UintType(8).doc == u.Doc()

    class MyUintType(u.UintType):
        title: str = "mytitle"
        descr: str = "mydescr"
        comment: str = "mycomment"

        def __init__(self):
            super().__init__(8)

    assert MyUintType().doc == u.Doc(title="mytitle", descr="mydescr", comment="mycomment")


class MyUintType(u.UintType):
    """Example Uint."""

    def __init__(self, width=42):
        super().__init__(width=width)


def test_fixed_vector_size():
    """Uint with fixed size."""
    assert MyUintType().width == 42
