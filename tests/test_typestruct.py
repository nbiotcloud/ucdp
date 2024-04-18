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

"""
Struct Type Testing.

"""

import ucdp as u
from pytest import raises


def test_struct():
    """Struct."""

    class MyStructType(u.AStructType):
        """Struct."""

        def _build(self) -> None:
            self._add("data", u.UintType(8), title="title")
            self._add("valid", u.BitType(), descr="descr", ifdef="IFDEF")
            self._add("accept", u.BitType(), u.BWD, comment="comment")
            with raises(ValueError) as exception:
                self._add("valid", u.BitType())
                assert str(exception.value) == "key 2 already exists in test_enum.<locals>.MyStructType()"

    struct = MyStructType()
    with raises(u.LockError) as exception:
        struct._add("lock", u.BitType())
        assert str(exception.value) == "key 2 already exists in test_enum.<locals>.MyStructType()"
    assert tuple(struct) == tuple(struct.keys())
    assert tuple(struct.keys()) == ("data", "valid", "accept")
    assert tuple(struct.values()) == (
        u.StructItem("data", u.UintType(8), doc=u.Doc(title="title")),
        u.StructItem("valid", u.BitType(), doc=u.Doc(descr="descr"), ifdef="IFDEF"),
        u.StructItem("accept", u.BitType(), orientation=u.BWD, doc=u.Doc(comment="comment")),
    )
    assert [item.doc for item in struct.values()] == [
        u.Doc(title="title"),
        u.Doc(descr="descr"),
        u.Doc(comment="comment"),
    ]

    assert MyStructType() is MyStructType()
    assert MyStructType() == MyStructType()


def test_inherit_basestruct():
    """:any:`BaseStructType` must be inherited."""
    with raises(TypeError):
        u.BaseStructType()


def test_inherit_struct():
    """:any:`StructType` must be inherited."""
    with raises(TypeError):
        u.AStructType()


def test_inherit_globalstruct():
    """:any:`AGlobalStructType` must be inherited."""
    with raises(TypeError):
        u.AGlobalStructType()


def test_inherit_dynamicstruct():
    """:any:`DynamicStructType` must be inherited."""
    u.DynamicStructType()


def test_globalstruct():
    """Global Struct."""

    class MyType(u.AGlobalStructType):
        pass

    one = MyType()
    one.add("data", u.UintType(8))
    one.add("valid", u.BitType())
    assert tuple(one) == ("data", "valid")

    other = MyType()
    other.add("accept", u.BitType(), orientation=u.BWD)

    assert one is other
    assert one == other
    assert tuple(one) == ("data", "valid", "accept")
    assert tuple(other) == ("data", "valid", "accept")


def test_dynamicstruct():
    """Dynamic Struct."""

    class MyType(u.DynamicStructType):
        pass

    one = MyType()
    one.add("data", u.UintType(8))
    one.add("valid", u.BitType())
    assert tuple(one) == ("data", "valid")

    other = MyType()
    other.add("accept", u.BitType(), orientation=u.BWD)

    assert one is not other
    assert one != other
    assert tuple(one) == ("data", "valid")
    assert tuple(other) == ("accept",)
