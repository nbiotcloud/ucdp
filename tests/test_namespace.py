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
"""Test Configuration."""

import re

from hypothesis import assume, given
from hypothesis import strategies as st
from pytest import raises

import ucdp


class MyObject(ucdp.NamedObject):
    """Example Object."""

    arg1: int
    arg2: int


def test_default():
    """Basic Testing."""
    # Create empty Namespace
    namespace = ucdp.Namespace()
    # test basic properties: len(), tuple(), lock(), repr()
    assert len(namespace) == 0
    assert repr(namespace) == "Namespace([])"
    assert tuple(namespace) == ()
    assert namespace.is_locked is False
    namespace.lock()
    assert namespace.is_locked is True


@given(
    int1=st.integers(),
    int2=st.integers(),
    int3=st.integers(),
    int4=st.integers(),
    int5=st.integers(),
    int6=st.integers(),
    str1=st.text(),
    str2=st.text(),
    str3=st.text(),
)
def test_init(int1, int2, int3, int4, int5, int6, str1, str2, str3):
    """Namespace with Initialization Items."""
    assume(str1 != str2)
    assume(str2 != str3)
    assume(str1 != str3)

    myobject1 = MyObject(name=str1, arg1=int1, arg2=int2)
    myobject2 = MyObject(name=str2, arg1=int3, arg2=int4)
    myobject3 = MyObject(name=str3, arg1=int5, arg2=int6)
    assert myobject1.name == str1
    assert myobject1.arg1 == int1
    assert myobject1.arg2 == int2
    assert myobject2.name == str2
    assert myobject2.arg1 == int3
    assert myobject2.arg2 == int4
    assert myobject3.name == str3
    assert myobject3.arg1 == int5
    assert myobject3.arg2 == int6

    # Create Namespace with Elements in Constructor
    namespace = ucdp.Namespace([myobject1, myobject2, myobject3])
    # test basic properties: len(), tuple(), lock(), repr()
    assert namespace[str1] == myobject1
    assert namespace[str2] == myobject2
    assert namespace[str3] == myobject3
    assert len(namespace) == 3
    assert repr(namespace) == f"Namespace([{myobject1!r}, {myobject2!r}, {myobject3!r}])"
    assert tuple(namespace) == (myobject1, myobject2, myobject3)
    assert namespace.is_locked is False
    namespace.lock()
    assert namespace.is_locked is True


@given(
    int1=st.integers(),
    int2=st.integers(),
    int3=st.integers(),
    int4=st.integers(),
    int5=st.integers(),
    int6=st.integers(),
    str1=st.text(),
    str2=st.text(),
)
def test_add(int1, int2, int3, int4, int5, int6, str1, str2):
    """Namespace add() Method."""
    assume(str1 != str2)

    myobject1 = MyObject(name=str1, arg1=int1, arg2=int2)
    myobject2 = MyObject(name=str2, arg1=int3, arg2=int4)
    myobject3 = MyObject(name=str1, arg1=int5, arg2=int6)

    # Create empty Namespace
    namespace = ucdp.Namespace([])
    assert len(namespace) == 0

    # Add new Object
    namespace.add(myobject1)
    assert namespace[str1] == myobject1
    assert len(namespace) == 1
    assert repr(namespace) == f"Namespace([{myobject1!r}])"
    assert tuple(namespace) == (myobject1,)

    # Add 2nd Object
    namespace.add(myobject2)
    assert namespace[str1] == myobject1
    assert namespace[str2] == myobject2
    assert len(namespace) == 2
    assert repr(namespace) == f"Namespace([{myobject1!r}, {myobject2!r}])"
    assert tuple(namespace) == (myobject1, myobject2)

    # Try to add Object with same name
    with raises(ucdp.exceptions.DuplicateError) as excep:
        namespace.add(myobject3)
    assert str(excep.value) == f"Name '{str1}' already taken by {namespace[str1]!r}"
    assert namespace[str1] == myobject1
    assert namespace[str2] == myobject2
    assert len(namespace) == 2
    assert repr(namespace) == f"Namespace([{myobject1!r}, {myobject2!r}])"
    assert tuple(namespace) == (myobject1, myobject2)


@given(
    int1=st.integers(),
    int2=st.integers(),
    int3=st.integers(),
    int4=st.integers(),
    str1=st.text(),
    str2=st.text(),
    str3=st.text(),
)
def test_get(int1, int2, int3, int4, str1, str2, str3):
    """Namespace get() Method."""
    assume(str1 != str2)
    assume(str2 != str3)
    assume(str1 != str3)

    myobject1 = MyObject(name=str1, arg1=int1, arg2=int2)
    myobject2 = MyObject(name=str2, arg1=int3, arg2=int4)

    # Create Namespace with Elements in Constructor
    namespace = ucdp.Namespace([myobject1, myobject2])
    assert namespace[myobject1.name] == myobject1
    assert namespace[myobject2.name] == myobject2
    with raises(KeyError) as excep:
        namespace[str3]
    assert str(excep.value) == f"{str3!r}"


@given(
    int1=st.integers(),
    int2=st.integers(),
    int3=st.integers(),
    int4=st.integers(),
    str1=st.text(),
    str2=st.text(),
    str3=st.text(),
)
def test_get_dym(int1, int2, int3, int4, str1, str2, str3):
    """Namespace get_dym() Method."""
    assume(str1 != str2)
    assume(str2 != str3)
    assume(str1 != str3)

    myobject1 = MyObject(name=str1, arg1=int1, arg2=int2)
    myobject2 = MyObject(name=str2, arg1=int3, arg2=int4)

    # Create Namespace with Elements in Constructor
    namespace = ucdp.Namespace([myobject1, myobject2])
    assert namespace.get_dym(myobject1.name) == myobject1
    assert namespace.get_dym(myobject2.name) == myobject2
    with raises(ValueError) as excep:
        namespace.get_dym(str3)

    tmp_dict = {myobject1.name: myobject1, myobject2.name: myobject2}
    dym = ucdp.nameutil.didyoumean(str3, tmp_dict.keys(), known=True)
    assert str(excep.value) == f"{str3!r}.{dym}"


@given(
    int1=st.integers(),
    int2=st.integers(),
    int3=st.integers(),
    int4=st.integers(),
    str1=st.text(),
    str2=st.text(),
    str3=st.text(),
)
def test_getitem(int1, int2, int3, int4, str1, str2, str3):
    """Namespace set item Method."""
    assume(str1 != str2)
    assume(str2 != str3)
    assume(str1 != str3)

    myobject1 = MyObject(name=str1, arg1=int1, arg2=int2)
    myobject2 = MyObject(name=str2, arg1=int3, arg2=int4)

    # Create Namespace with Elements in Constructor
    namespace = ucdp.Namespace([myobject1, myobject2])
    assert namespace[myobject1.name] == myobject1
    assert namespace[myobject2.name] == myobject2
    tmp_dict = {myobject1.name: myobject1, myobject2.name: myobject2}
    assert namespace.items() == tmp_dict.items()
    assert namespace.keys() == tmp_dict.keys()
    assert repr(namespace.values()) == repr(tmp_dict.values())


@given(
    int1=st.integers(),
    int2=st.integers(),
    int3=st.integers(),
    int4=st.integers(),
    int5=st.integers(),
    int6=st.integers(),
    str1=st.text(),
    str2=st.text(),
    str3=st.text(),
)
def test_setitem(int1, int2, int3, int4, int5, int6, str1, str2, str3):
    """Namespace set item Method."""
    assume(str1 != str2)
    assume(str1 != str3)
    assume(str2 != str3)

    myobject1 = MyObject(name=str1, arg1=int1, arg2=int2)
    myobject2 = MyObject(name=str2, arg1=int3, arg2=int4)
    myobject3 = MyObject(name=str1, arg1=int5, arg2=int6)

    # Create empty Namespace
    namespace = ucdp.Namespace([])
    assert len(namespace) == 0

    # Add new Object
    namespace[myobject1.name] = myobject1
    assert namespace[str1] == myobject1
    assert len(namespace) == 1
    assert repr(namespace) == f"Namespace([{myobject1!r}])"
    assert tuple(namespace) == (myobject1,)

    # Try to add same Object
    with raises(ucdp.exceptions.DuplicateError) as excep:
        namespace[myobject1.name] = myobject1
    assert str(excep.value) == f"{myobject1!r} already exists"

    # Try to add 2nd Object with not matching name
    with raises(ValueError) as excep:
        namespace[str3] = myobject2
    assert str(excep.value) == f"{myobject2} with must be stored at name '{myobject2.name}' not at '{str3}'"

    # Add 2nd Object
    namespace[myobject2.name] = myobject2
    assert namespace[str1] == myobject1
    assert namespace[str2] == myobject2
    assert len(namespace) == 2
    assert repr(namespace) == f"Namespace([{myobject1!r}, {myobject2!r}])"
    assert tuple(namespace) == (myobject1, myobject2)

    # Try to add Object with same name
    with raises(ucdp.exceptions.DuplicateError) as excep:
        namespace[myobject3.name] = myobject3
    assert str(excep.value) == f"Name '{str1}' already taken by {namespace[str1]!r}"
    assert namespace[str1] == myobject1
    assert namespace[str2] == myobject2
    assert len(namespace) == 2
    assert repr(namespace) == f"Namespace([{myobject1!r}, {myobject2!r}])"
    assert tuple(namespace) == (myobject1, myobject2)

    # Try to add Object with same name with update()
    with raises(ucdp.exceptions.DuplicateError) as excep:
        namespace.update({myobject3.name: myobject3})
    assert str(excep.value) == f"Name '{str1}' already taken by {namespace[str1]!r}"
    assert namespace[str1] == myobject1
    assert namespace[str2] == myobject2
    assert len(namespace) == 2
    assert repr(namespace) == f"Namespace([{myobject1!r}, {myobject2!r}])"
    assert tuple(namespace) == (myobject1, myobject2)

    # Add Object with update()
    myobject3 = MyObject(name=str3, arg1=int5, arg2=int6)
    namespace.update({myobject3.name: myobject3})
    assert namespace[str1] == myobject1
    assert namespace[str2] == myobject2
    assert namespace[str3] == myobject3
    assert len(namespace) == 3
    assert repr(namespace) == f"Namespace([{myobject1!r}, {myobject2!r}, {myobject3!r}])"
    assert tuple(namespace) == (myobject1, myobject2, myobject3)


@given(int1=st.integers(), int2=st.integers(), str1=st.text())
def test_delitem(int1, int2, str1):
    """Namespace set item Method."""
    # Create Namespace with Elements in Constructor
    namespace = ucdp.Namespace([MyObject(name=str1, arg1=int1, arg2=int2)])

    assert len(namespace) == 1

    with raises(TypeError) as excep:
        del namespace[str1]
    assert str(excep.value) == f"It is forbidden to remove {str1!r}."

    with raises(TypeError) as excep:
        namespace.pop(str1)
    assert str(excep.value) == "It is forbidden to remove any item."

    with raises(TypeError) as excep:
        namespace.popitem()
    assert str(excep.value) == "It is forbidden to remove any item."

    assert len(namespace) == 1


@given(
    int1=st.integers(),
    int2=st.integers(),
    int3=st.integers(),
    int4=st.integers(),
    str1=st.text(),
    str2=st.text(),
)
def test_lock(int1, int2, int3, int4, str1, str2):
    """Namespace lock Method."""
    assume(str1 != str2)

    myobject1 = MyObject(name=str1, arg1=int1, arg2=int2)
    myobject2 = MyObject(name=str2, arg1=int3, arg2=int4)

    # Create empty Namespace
    namespace = ucdp.Namespace([])
    assert len(namespace) == 0

    # Add new Object
    namespace.add(myobject1)
    assert len(namespace) == 1
    assert namespace.is_locked is False
    namespace.lock()
    assert namespace.is_locked is True

    msg = "Namespace is already locked. Cannot lock again."
    with raises(ucdp.LockError, match=re.escape(msg)):
        namespace.lock()

    msg = "Namespace is already locked. Cannot add items anymore."
    with raises(ucdp.LockError, match=re.escape(msg)):
        namespace.add(myobject2)

    msg = "Namespace is already locked. Cannot add items anymore."
    with raises(ucdp.LockError, match=re.escape(msg)):
        namespace.update({myobject2.name: myobject2})

    assert len(namespace) == 1


def test_ior():
    """Namespace IOR-Operator."""
    myobject1 = ucdp.NamedObject(name="str1")
    myobject2 = ucdp.NamedObject(name="str2")
    myobject3 = ucdp.NamedObject(name="str3")
    namespace = ucdp.Namespace()
    namespace.add(myobject1)
    assert tuple(namespace) == (myobject1,)

    namespace |= {"str2": myobject2}
    assert tuple(namespace) == (myobject1, myobject2)

    namespace.lock()
    assert tuple(namespace) == (myobject1, myobject2)

    msg = "Namespace is already locked. Cannot add items anymore."
    with raises(ucdp.LockError, match=re.escape(msg)):
        namespace |= {"str3": myobject3}

    assert tuple(namespace) == (myobject1, myobject2)


def test_or():
    """Namespace IOR-Operator."""
    myobject1 = ucdp.NamedObject(name="str1")
    myobject2 = ucdp.NamedObject(name="str2")
    myobject3 = ucdp.NamedObject(name="str3")
    namespace = ucdp.Namespace()
    namespace.add(myobject1)
    assert tuple(namespace) == (myobject1,)

    namespace2 = namespace | {"str2": myobject2}
    assert tuple(namespace) == (myobject1,)
    assert tuple(namespace2) == (myobject1, myobject2)

    namespace2.lock()
    assert tuple(namespace2) == (myobject1, myobject2)

    msg = "Namespace is already locked. Cannot add items anymore."
    with raises(ucdp.LockError, match=re.escape(msg)):
        namespace2 | {"str3": myobject3}

    assert tuple(namespace2) == (myobject1, myobject2)


def test_set_default():
    """Namespace IOR-Operator."""
    myobject1 = ucdp.NamedObject(name="str1")
    myobject2 = ucdp.NamedObject(name="str2")
    myobject3 = ucdp.NamedObject(name="str3")
    namespace = ucdp.Namespace()
    assert namespace.set_default("str1", myobject1) is myobject1
    assert tuple(namespace) == (myobject1,)
    assert namespace.set_default("str1", myobject1) is myobject1
    assert tuple(namespace) == (myobject1,)

    msg = "NamedObject(name='str3') with must be stored at name 'str3' not at 'str2'"
    with raises(ValueError, match=re.escape(msg)):
        namespace.set_default("str2", myobject3)

    assert tuple(namespace) == (myobject1,)

    namespace.lock()

    msg = "Namespace is already locked. Cannot add items anymore."
    with raises(ValueError, match=re.escape(msg)):
        namespace.set_default("str2", myobject2)

    assert tuple(namespace) == (myobject1,)
