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

"""Type Testing."""
from attrs.exceptions import FrozenInstanceError
from pytest import raises

import ucdp


def test_integer():
    """Integer."""
    # pylint: disable=too-many-statements
    var0 = ucdp.IntegerType()
    assert var0.default == 0
    assert var0.width == 32
    assert repr(var0) == "IntegerType()"
    with raises(FrozenInstanceError):
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

    with raises(TypeError):
        ucdp.IntegerType(width=4)

    assert var0 is not var1
    assert var0 is var2
    assert var0 != var1
    assert var0 == var2

    with raises(ValueError):
        ucdp.IntegerType(default="afe")


def test_uint():
    """Integer."""
    var0 = ucdp.UintType(12)
    assert var0.default == 0
    assert var0.width == 12
    assert repr(var0) == "UintType(12)"

    assert -1 not in var0
    assert 1 in var0
    assert 2**12 not in var0

    var1 = ucdp.UintType(12, default=8)
    assert var1.default == 8
    assert var1.width == 12
    assert repr(var1) == "UintType(12, default=8)"

    with raises(FrozenInstanceError):
        var1.default = 1

    assert var0 is not var1
    assert var0 != var1

    with raises(ValueError):
        ucdp.UintType(12, default="abc")


def test_enum():
    """Enumeration."""

    class ModeType(ucdp.AEnumType):
        """Mode."""

        keytype = ucdp.UintType(2)

        def _build(self):
            self._add(0, "linear")
            self._add(1, "cyclic")
            self._add(2, "loop", title="Run in a Loop")
            with raises(ValueError) as exception:
                self._add(2, "double")
            assert str(exception.value) == f"key 2 already exists in {self}"

    mode = ModeType()
    assert tuple(mode) == tuple(mode.values())

    assert "linear" in mode
    assert "notlinear" not in mode


def test_enum_auto():
    """Enumeration."""

    class AutoType(ucdp.AEnumType):
        """Auto."""

        keytype = ucdp.UintType(2)

        def _build(self):
            self._add(ucdp.AUTO, "linear")
            self._add(2, "cyclic")
            self._add(ucdp.AUTO, "auto")

    auto = AutoType()
    assert tuple(auto) == (ucdp.EnumItem(0, "linear"), ucdp.EnumItem(2, "cyclic"), ucdp.EnumItem(3, "auto"))


def test_struct():
    """Struct."""

    class StructType(ucdp.AStructType):
        """Struct."""

        def _build(self):
            self._add("data", ucdp.UintType(8))
            self._add("valid", ucdp.BitType())
            self._add("accept", ucdp.BitType(), ucdp.BWD)
            with raises(ValueError) as exception:
                self._add("valid", ucdp.BitType())
                assert str(exception.value) == "key 2 already exists in test_enum.<locals>.StructType()"

    struct = StructType()
    assert tuple(struct) == tuple(struct.values())
    assert tuple(struct.keys()) == ("data", "valid", "accept")


# def test_tailtype():
#     """Test Tailoring."""

#     @ucdp.tailoredtype()
#     class MonSelType(ucdp.DynamicEnumType):

#         """Monitoring."""

#         size = ucdp.field()
#         keytype = ucdp.field(kw_only=True, init=False)

#         @keytype.default
#         def _keytype_default(self):
#             width = calc_unsigned_width(self.size - 1)
#             return ucdp.UintType(width)

#     type0 = MonSelType(6)
#     assert type0.width == 3
#     assert type0.default == 0

#     type1 = MonSelType(6)

#     assert type0 is not type1
#     assert type0 != type1


def test_alias():
    """Test Aliased Types."""

    @ucdp.tailoredtype
    class MyUintType(ucdp.UintType):
        """My Type."""

        no_codecov = True
        title = "Title"

        width = ucdp.field(default=4, init=False)

    myt = MyUintType()
    assert myt.width == 4
    assert myt.default == 0
    assert myt.title == "Title"

    @ucdp.tailoredtype
    class MyIntegerType(ucdp.IntegerType):
        """My Type."""

        no_codecov = True
        title = "Title"

        default = ucdp.field(default=4, init=False)

    myt = MyIntegerType()
    assert myt.width == 32
    assert myt.default == 4
    assert myt.title == "Title"
