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
enum Type Testing.

"""

from pytest import raises

import ucdp as u


def test_enum():
    """Enum."""

    class MyEnumType(u.AEnumType):
        """Enum."""

        keytype: u.AScalarType = u.UintType(4)

        def _build(self) -> None:
            self._add(u.AUTO, "a", title="title")
            self._add(u.AUTO, "b", descr="descr")
            self._add(4, "a")
            self._add(u.AUTO, "d", comment="comment")
            with raises(ValueError):
                self._add(5, 8)

    enum = MyEnumType()
    with raises(u.LockError):
        enum._add(u.AUTO, 11)
    assert tuple(enum) == tuple(enum.keys())
    assert tuple(enum.keys()) == (0, 1, 4, 5)
    assert tuple(enum.values()) == (
        u.EnumItem(0, "a", doc=u.Doc(title="title")),
        u.EnumItem(1, "b", doc=u.Doc(descr="descr")),
        u.EnumItem(4, "a"),
        u.EnumItem(5, "d", doc=u.Doc(comment="comment")),
    )
    assert [item.doc for item in enum.values()] == [
        u.Doc(title="title"),
        u.Doc(descr="descr"),
        u.Doc(),
        u.Doc(comment="comment"),
    ]

    assert MyEnumType() is MyEnumType()
    assert MyEnumType() == MyEnumType()


def test_inherit_baseenum():
    """:any:`BaseEnumType` must be inherited."""
    with raises(TypeError):
        u.BaseEnumType()


def test_inherit_enum():
    """:any:`EnumType` must be inherited."""
    with raises(TypeError):
        u.AEnumType()


def test_inherit_globalenum():
    """:any:`AGlobalEnumType` must be inherited."""
    with raises(TypeError):
        u.AGlobalEnumType()


def test_inherit_dynamicenum():
    """:any:`DynamicEnumType` must be inherited."""
    u.DynamicEnumType()


def test_globalenum():
    """Global enum."""

    class MyType(u.AGlobalEnumType):
        pass

    one = MyType()
    one.add(0, "a")
    one.add(1, "b")
    assert tuple(one) == (0, 1)

    other = MyType()
    other.add(2, "c")

    assert one is other
    assert one == other
    assert tuple(one) == (0, 1, 2)
    assert tuple(other) == (0, 1, 2)


def test_dynamicenum():
    """Dynamic enum."""

    class MyType(u.DynamicEnumType):
        pass

    one = MyType()
    one.add(0, "a")
    one.add(1, "b")
    assert tuple(one) == (0, 1)

    other = MyType()
    other.add(2, "c")

    assert one is not other
    assert one != other
    assert tuple(one) == (0, 1)
    assert tuple(other) == (2,)


def test_cast():
    """Enum."""

    class OneType(u.AEnumType):
        """Enum."""

        keytype: u.AScalarType = u.UintType(4)

        def _build(self) -> None:
            self._add(u.AUTO, "a", title="title")

    class TwoType(u.AEnumType):
        """Enum."""

        keytype: u.AScalarType = u.UintType(4)

        def _build(self) -> None:
            self._add(u.AUTO, "a", title="title")

    class ThreeType(u.AEnumType):
        """Enum."""

        keytype: u.AScalarType = u.UintType(3)

        def _build(self) -> None:
            self._add(u.AUTO, "a", title="title")

    assert OneType().cast(TwoType()) == [
        (
            "",
            "",
        ),
    ]
    assert TwoType().cast(OneType()) == OneType().cast(TwoType())

    assert OneType().cast(ThreeType()) is None
    assert ThreeType().cast(OneType()) is None
