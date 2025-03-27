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
"""Test Type Specific Casts."""

import ucdp as u


def test_bit():
    """Bit Casting."""
    type_ = u.BitType()

    assert type_.cast(u.UintType(1)) == [("", "")]
    assert type_.cast(u.UintType(1, default=1)) == [("", "")]
    assert type_.cast(u.UintType(2)) is None

    assert type_.cast(u.SintType(1)) == [("", "")]
    assert type_.cast(u.SintType(1, default=-1)) == [("", "")]
    assert type_.cast(u.SintType(2)) is None

    assert type_.cast(u.IntegerType()) is None

    class MyEnum1(u.AEnumType):
        keytype: u.UintType = u.UintType(1)

        def _build(self) -> None:
            pass

    assert type_.cast(MyEnum1()) == [("", "")]

    class MyEnum2(u.AEnumType):
        keytype: u.UintType = u.UintType(2)

        def _build(self) -> None:
            pass

    assert type_.cast(MyEnum2()) is None


def test_rail():
    """Rail Casting."""
    type_ = u.RailType()

    assert type_.cast(u.UintType(1)) == [("", "")]
    assert type_.cast(u.UintType(1, default=1)) == [("", "")]
    assert type_.cast(u.UintType(2)) is None

    assert type_.cast(u.SintType(1)) == [("", "")]
    assert type_.cast(u.SintType(1, default=-1)) == [("", "")]
    assert type_.cast(u.SintType(2)) is None

    assert type_.cast(u.IntegerType()) is None

    class MyEnum1(u.AEnumType):
        keytype: u.UintType = u.UintType(1)

        def _build(self) -> None:
            pass

    assert type_.cast(MyEnum1()) == [("", "")]

    class MyEnum2(u.AEnumType):
        keytype: u.UintType = u.UintType(2)

        def _build(self) -> None:
            pass

    assert type_.cast(MyEnum2()) is None


def test_uint():
    """Uint Casting."""
    type_ = u.UintType(3)

    assert type_.cast(u.BitType()) is None

    assert type_.cast(u.SintType(3)) == [("", "")]
    assert type_.cast(u.SintType(3, default=-1)) == [("", "")]
    assert type_.cast(u.SintType(2)) is None

    assert type_.cast(u.IntegerType()) is None
    assert u.UintType(32).cast(u.IntegerType()) == [("", "")]

    class MyEnum3(u.AEnumType):
        keytype: u.UintType = u.UintType(3)

        def _build(self) -> None:
            pass

    assert type_.cast(MyEnum3()) == [("", "")]

    class MyEnum2(u.AEnumType):
        keytype: u.UintType = u.UintType(2)

        def _build(self) -> None:
            pass

    assert type_.cast(MyEnum2()) is None


def test_sint():
    """Sint Casting."""
    type_ = u.SintType(3)

    assert type_.cast(u.BitType()) is None

    assert type_.cast(u.UintType(3)) == [("", "")]
    assert type_.cast(u.UintType(3, default=1)) == [("", "")]
    assert type_.cast(u.UintType(2)) is None

    assert type_.cast(u.IntegerType()) is None
    assert u.SintType(32).cast(u.IntegerType()) == [("", "")]

    class MyEnum3(u.AEnumType):
        keytype: u.UintType = u.UintType(3)

        def _build(self) -> None:
            pass

    assert type_.cast(MyEnum3()) == [("", "")]

    class MyEnum2(u.AEnumType):
        keytype: u.UintType = u.UintType(2)

        def _build(self) -> None:
            pass

    assert type_.cast(MyEnum2()) is None
