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
"""Test :any:`Object`."""

from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError
from pytest import raises

import ucdp as u


class MyObject(u.Object):
    """Example Object."""

    arg1: int


class MyMyObject(MyObject):
    """Example Sub-Object."""

    arg2: int


class MyTuplingObject(u.Object):
    """Example Object with Tuple."""

    arg1: tuple[int, ...] = u.Field(default_factory=tuple)


class MyListingObject(u.Object):
    """Example Object with List."""

    arg1: list[int] = u.Field(default_factory=list)


@given(int1=st.integers(), int2=st.integers(), str1=st.text())
def test_object_basics(int1, int2, str1):
    """:any:`Object` Basic Testing."""
    inst = MyObject(arg1=int1)
    assert inst.arg1 == int1

    # compare
    assert MyObject(arg1=int1) == MyObject(arg1=int1)

    # no caching
    assert MyObject(arg1=int1) is not MyObject(arg1=int1)

    assert str(MyObject(arg1=int1)) == f"MyObject(arg1={int1!r})"
    assert repr(MyObject(arg1=int1)) == f"MyObject(arg1={int1!r})"

    # immutable
    with raises(ValidationError):
        inst.arg1 = int2

    # no extra
    with raises(ValidationError):
        MyObject(arg1=int1, arg2=int2)

    # validate
    with raises(ValidationError):
        MyObject(arg1=str1)

    assert hash(inst) is not None


@given(int1=st.integers(), int2=st.integers(), int3=st.integers(), str1=st.text())
def test_sub_object(int1, int2, int3, str1):
    """Sub :any:`Object` Testing."""
    inst = MyMyObject(arg1=int1, arg2=int2)
    assert inst.arg1 == int1
    assert inst.arg2 == int2

    with raises(ValidationError):
        inst.arg1 = int3

    with raises(ValidationError):
        MyMyObject(arg1=int1, arg2=str1)

    # no caching
    assert MyMyObject(arg1=int1, arg2=int2) is not MyMyObject(arg1=int1, arg2=int2)
    assert MyMyObject(arg1=int1, arg2=int2) is not MyMyObject(arg2=int2, arg1=int1)
    assert MyMyObject(arg1=int1, arg2=int2) is not MyMyObject(arg1=int1, arg2=int3)
    assert MyMyObject(arg1=int1, arg2=int3) is not MyMyObject(arg1=int1, arg2=int3)


@given(int1=st.integers(), int2=st.integers(), tuple1=st.tuples(st.integers()))
def test_tupling_object(int1, int2, tuple1):
    """:any:`Object` With Tuple Testing."""
    assert MyTuplingObject().arg1 == ()

    with raises(ValidationError):
        MyTuplingObject(arg1=int1)

    inst = MyTuplingObject(arg1=tuple1)
    assert inst.arg1 == tuple1

    assert hash(inst) is not None


@given(int1=st.integers(), int2=st.integers(), list1=st.lists(st.integers()))
def test_listing_object(int1, int2, list1):
    """:any:`Object` With List Testing."""
    assert MyListingObject().arg1 == []

    with raises(ValidationError):
        MyListingObject(arg1=int1)

    inst = MyListingObject(arg1=list1)
    assert inst.arg1 == list1

    inst.arg1.append(int2)

    assert inst.arg1[-1] == int2

    with raises(TypeError):
        hash(inst)


class OneObject(u.Object):
    """Example Object."""

    arg1: int


class ParentObject(u.Object):
    """Example Object."""

    arg1: int
    arg2: OneObject
    arg3: tuple[OneObject, ...]


@given(int1=st.integers(), int2=st.integers(), int3=st.integers(), int4=st.integers())
def test_nested(int1, int2, int3, int4):
    """Nested Types."""
    one2 = OneObject(arg1=int2)
    one3 = OneObject(arg1=int3)
    one4 = OneObject(arg1=int4)
    parent = ParentObject(arg1=int1, arg2=one2, arg3=(one3, one4))
    assert parent.arg1 == int1
    assert parent.arg2 == one2
    assert parent.arg3 == (one3, one4)
