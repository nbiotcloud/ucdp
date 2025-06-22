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
"""Test :any:`LightObject`."""

import re

from hypothesis import assume, given
from hypothesis import strategies as st
from pydantic import ValidationError
from pytest import raises

import ucdp as u


class MyLightObject(u.LightObject):
    """Example LightObject."""

    arg1: int


class MyMyLightObject(MyLightObject):
    """Example Sub-LightObject."""

    arg2: int


class MyTuplingLightObject(u.LightObject):
    """Example LightObject with Tuple."""

    arg1: tuple[int, ...] = u.Field(default_factory=tuple)


class MyListingLightObject(u.LightObject):
    """Example LightObject with List."""

    arg1: list[int] = u.Field(default_factory=list)


@given(int1=st.integers(max_value=100), int2=st.integers(max_value=100), str1=st.text(max_size=10))
def test_light_object_basics(int1, int2, str1):
    """:any:`LightObject` Basic Testing."""
    inst = MyLightObject(arg1=int1)
    assert inst.arg1 == int1

    # compare
    assert MyLightObject(arg1=int1) == MyLightObject(arg1=int1)

    # caching
    assert MyLightObject(arg1=int1) is MyLightObject(arg1=int1)

    assert str(MyLightObject(arg1=int1)) == f"MyLightObject(arg1={int1!r})"
    assert repr(MyLightObject(arg1=int1)) == f"MyLightObject(arg1={int1!r})"

    # immutable
    with raises(ValidationError):
        inst.arg1 = int2

    # no extra
    with raises(ValidationError):
        MyLightObject(arg1=int1, arg2=int2)

    # validate
    with raises(ValidationError):
        MyLightObject(arg1=str1)

    assert hash(inst) is not None


@given(
    int1=st.integers(max_value=100),
    int2=st.integers(max_value=100),
    int3=st.integers(max_value=100),
    str1=st.text(max_size=10),
)
def test_sub_light_object(int1, int2, int3, str1):
    """Sub :any:`LightObject` Testing."""
    inst = MyMyLightObject(arg1=int1, arg2=int2)
    assert inst.arg1 == int1
    assert inst.arg2 == int2

    with raises(ValidationError):
        inst.arg1 = int3

    with raises(ValidationError):
        MyMyLightObject(arg1=int1, arg2=str1)

    assume(int2 != int3)

    # caching
    assert MyMyLightObject(arg1=int1, arg2=int2) is MyMyLightObject(arg1=int1, arg2=int2)
    assert MyMyLightObject(arg1=int1, arg2=int2) is MyMyLightObject(arg2=int2, arg1=int1)
    assert MyMyLightObject(arg1=int1, arg2=int2) is not MyMyLightObject(arg1=int1, arg2=int3)
    assert MyMyLightObject(arg1=int1, arg2=int3) is MyMyLightObject(arg1=int1, arg2=int3)


@given(int1=st.integers(max_value=100), int2=st.integers(max_value=100), tuple1=st.tuples(st.integers(max_value=100)))
def test_tupling_light_object(int1, int2, tuple1):
    """:any:`LightObject` With Tuple Testing."""
    assert MyTuplingLightObject().arg1 == ()

    with raises(ValidationError):
        MyTuplingLightObject(arg1=int1)

    inst = MyTuplingLightObject(arg1=tuple1)
    assert inst.arg1 == tuple1

    assert hash(inst) is not None


@given(int1=st.integers(max_value=100), list1=st.lists(st.integers(max_value=100)))
def test_listing_light_object(int1, list1):
    """:any:`LightObject` With List Testing."""
    with raises(TypeError):
        hash(MyListingLightObject())

    with raises(TypeError):
        MyListingLightObject(arg1=list1)

    with raises(ValidationError):
        MyListingLightObject(arg1=int1)


class NotHashableArg(u.LightObject):
    """Example."""

    arg: list[str]

    _posargs: u.PosArgs = ("arg",)

    def __init__(self, arg: list[str]):
        super().__init__(arg=arg)  # type: ignore[call-arg]


def test_not_hashable_arg():
    """Test Error Message on Non-Hashable Arg."""
    # TESTME

    #    NotHashableArg(["a", "b"])


class NotHashableKwarg(u.LightObject):
    """Example."""

    arg: list[str]


def test_not_hashable_kwarg():
    """Test Error Message on Non-Hashable Kwarg."""
    # TESTME

    #    NotHashableKwarg(["a", "b"])


class NoHashLightObject(u.LightObject):
    """Example LightObject."""

    arg1: list[int]

    def __init__(self, arg1):
        super().__init__(arg1=arg1)


def test_no_hash():
    """Not Hashable."""
    msg = "<class 'tests.test_light_object.NoHashLightObject'>: 0 argument [1, 2, 3] is not constant."
    with raises(TypeError, match=re.escape(msg)):
        NoHashLightObject([1, 2, 3])

    msg = "<class 'tests.test_light_object.NoHashLightObject'>: 'arg1' argument [1, 2, 3] is not constant."
    with raises(TypeError, match=re.escape(msg)):
        NoHashLightObject(arg1=[1, 2, 3])
