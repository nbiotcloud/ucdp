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
Struct Type Testing.

"""
from pytest import raises

import ucdp

# ruff: noqa: PLR2004


def test_struct():
    """Struct."""

    class MyStructType(ucdp.StructType):
        """Struct."""

        def _build(self):
            self._add("data", ucdp.UintType(8), title="title")
            self._add("valid", ucdp.BitType(), descr="descr", ifdef="IFDEF")
            self._add("accept", ucdp.BitType(), ucdp.BWD, comment="comment")
            with raises(ValueError) as exception:
                self._add("valid", ucdp.BitType())
                assert str(exception.value) == "key 2 already exists in test_enum.<locals>.MyStructType()"

    struct = MyStructType()
    with raises(ucdp.LockError) as exception:
        struct._add("lock", ucdp.BitType())
        assert str(exception.value) == "key 2 already exists in test_enum.<locals>.MyStructType()"
    assert tuple(struct) == tuple(struct.keys())
    assert tuple(struct.keys()) == ("data", "valid", "accept")
    assert tuple(struct.values()) == (
        ucdp.StructItem("data", ucdp.UintType(8), doc=ucdp.Doc(title="title")),
        ucdp.StructItem("valid", ucdp.BitType(), doc=ucdp.Doc(descr="descr"), ifdef="IFDEF"),
        ucdp.StructItem("accept", ucdp.BitType(), orientation=ucdp.BWD, doc=ucdp.Doc(comment="comment")),
    )
    assert [(item.title, item.descr, item.comment) for item in struct.values()] == [
        ("title", None, None),
        (None, "descr", None),
        (None, None, "comment"),
    ]

    assert MyStructType() is MyStructType()
    assert MyStructType() == MyStructType()


def test_inherit_basestruct():
    """:any:`BaseStructType` must be inherited."""
    with raises(ucdp.MissingInheritanceError):
        ucdp.BaseStructType()


def test_inherit_struct():
    """:any:`StructType` must be inherited."""
    with raises(ucdp.MissingInheritanceError):
        ucdp.StructType()


def test_inherit_globalstruct():
    """:any:`GlobalStructType` must be inherited."""
    with raises(ucdp.MissingInheritanceError):
        ucdp.GlobalStructType()


def test_inherit_dynamicstruct():
    """:any:`DynamicStructType` must be inherited."""
    with raises(ucdp.MissingInheritanceError):
        ucdp.DynamicStructType()


def test_globalstruct():
    """Global Struct."""

    class BusType(ucdp.GlobalStructType):
        pass

    one = BusType()
    one.add("data", ucdp.UintType(8))
    one.add("valid", ucdp.BitType())
    assert tuple(one) == ("data", "valid")

    other = BusType()
    other.add("accept", ucdp.BitType(), orientation=ucdp.BWD)

    assert one is other
    assert one == other
    assert tuple(one) == ("data", "valid", "accept")
    assert tuple(other) == ("data", "valid", "accept")


def test_dynamicstruct():
    """Dynamic Struct."""

    class BusType(ucdp.DynamicStructType):
        pass

    assert BusType() is not BusType()
    assert BusType() == BusType()

    bus = BusType()
    bus.add("data", ucdp.UintType(8))
    bus.add("valid", ucdp.BitType())
    assert tuple(bus) == ("data", "valid")

    bus = BusType()
    bus.add("accept", ucdp.BitType(), orientation=ucdp.BWD)
    assert tuple(bus) == ("accept",)
