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
enum Type Testing.

"""
from pytest import raises

import ucdp

# ruff: noqa: PLR2004


def test_enum():
    """Enum."""

    class MyEnumType(ucdp.EnumType):
        """Enum."""

        keytype: ucdp.ScalarType = ucdp.UintType(4)

        def _build(self):
            self._add(ucdp.AUTO, "a", title="title")
            self._add(ucdp.AUTO, "b", descr="descr")
            self._add(4, "a")
            self._add(ucdp.AUTO, "d", comment="comment")
            with raises(ValueError):
                self._add(5, 8)

    enum = MyEnumType()
    with raises(ucdp.LockError):
        enum._add(ucdp.AUTO, 11)
    assert tuple(enum) == tuple(enum.keys())
    assert tuple(enum.keys()) == (0, 1, 4, 5)
    assert tuple(enum.values()) == (
        ucdp.EnumItem(0, "a", doc=ucdp.Doc(title="title")),
        ucdp.EnumItem(1, "b", doc=ucdp.Doc(descr="descr")),
        ucdp.EnumItem(4, "a"),
        ucdp.EnumItem(5, "d", doc=ucdp.Doc(comment="comment")),
    )
    assert [(item.title, item.descr, item.comment) for item in enum.values()] == [
        ("title", None, None),
        (None, "descr", None),
        (None, None, None),
        (None, None, "comment"),
    ]

    assert MyEnumType() is MyEnumType()
    assert MyEnumType() == MyEnumType()


def test_inherit_baseenum():
    """:any:`BaseEnumType` must be inherited."""
    with raises(ucdp.MissingInheritanceError):
        ucdp.BaseEnumType()


def test_inherit_enum():
    """:any:`EnumType` must be inherited."""
    with raises(ucdp.MissingInheritanceError):
        ucdp.EnumType()


def test_inherit_globalenum():
    """:any:`GlobalEnumType` must be inherited."""
    with raises(ucdp.MissingInheritanceError):
        ucdp.GlobalEnumType()


def test_inherit_dynamicenum():
    """:any:`DynamicEnumType` must be inherited."""
    with raises(ucdp.MissingInheritanceError):
        ucdp.DynamicEnumType()


# def test_globalenum():
#     """Global enum."""

#     class BusType(ucdp.GlobalEnumType):
#         pass

#     one = BusType()
#     one.add("data", ucdp.UintType(8))
#     one.add("valid", ucdp.BitType())
#     assert tuple(one) == ("data", "valid")

#     other = BusType()
#     other.add("accept", ucdp.BitType(), orientation=ucdp.BWD)

#     assert one is other
#     assert one == other
#     assert tuple(one) == ("data", "valid", "accept")
#     assert tuple(other) == ("data", "valid", "accept")


# def test_dynamicenum():
#     """Dynamic enum."""

#     class BusType(ucdp.DynamicEnumType):
#         pass

#     assert BusType() is not BusType()
#     assert BusType() == BusType()

#     bus = BusType()
#     bus.add("data", ucdp.UintType(8))
#     bus.add("valid", ucdp.BitType())
#     assert tuple(bus) == ("data", "valid")

#     bus = BusType()
#     bus.add("accept", ucdp.BitType(), orientation=ucdp.BWD)
#     assert tuple(bus) == ("accept",)
