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

"""Identifier Testing."""
from pytest import fixture, raises

import ucdp


class ModeType(ucdp.AEnumType):
    """Mode."""

    keytype = ucdp.UintType(2)

    def _build(self):
        self._add(0, "add")
        self._add(1, "sub")
        self._add(2, "max")


class MyType(ucdp.AStructType):
    """My."""

    comment = "Mode"

    def _build(self):
        self._add("mode", ModeType())
        self._add("send", ucdp.ArrayType(ucdp.UintType(8), 3))
        self._add("return", ucdp.UintType(4), ucdp.BWD)


class SelType(ucdp.AEnumType):
    """Sel."""

    keytype = ucdp.UintType(2, default=2)

    def _build(self):
        self._add(0, "my_a")
        self._add(1, "my_b")
        self._add(2, "my_c")


class ComplexType(ucdp.AStructType):
    """A Complex Type."""

    def _build(self):
        self._add("my0", ucdp.ArrayType(MyType(), 8))
        self._add("my1", ucdp.ArrayType(MyType(), 8), ucdp.BWD)
        self._add("bi", ucdp.SintType(9), ucdp.BIDIR)
        self._add("sel", SelType())


@fixture
def ports():
    """Ports."""
    return ucdp.Idents(
        [
            ucdp.Port(ucdp.ClkRstAnType(), ""),
            ucdp.Port(ucdp.ClkRstAnType(), "sys_i"),
            ucdp.Port(ucdp.UintType(8), "vec_a_i"),
            ucdp.Port(ucdp.UintType(8), "vec_a_o"),
            ucdp.Port(ucdp.UintType(4), "vec_b_i"),
            ucdp.Port(ucdp.UintType(4), "vec_b_o"),
            ucdp.Port(MyType(), "my_a_i"),
            ucdp.Port(MyType(), "my_a_o"),
            ucdp.Port(MyType(), "my_b_i"),
            ucdp.Port(MyType(), "my_b_o"),
            ucdp.Port(ComplexType(), "comp_lex_i"),
            ucdp.Port(ComplexType(), "comp_lex_o"),
        ]
    )


# pylint: disable=redefined-outer-name
def test_idents(ports):
    """Idents."""
    assert repr(ports["vec_a_i"]) == "Port(UintType(8), name='vec_a_i')"
    assert repr(ports["my_a_i"]) == "Port(MyType(), name='my_a_i')"
    assert repr(ports["my_a_mode_i"]) == "Port(ModeType(), name='my_a_mode_i', level=1)"
    assert repr(ports["my_a_mode_i"]) == "Port(ModeType(), name='my_a_mode_i', level=1)"
    assert ("my_a_i" in ports) is True
    assert ("my_t_i" in ports) is False
    assert ports["my_a_mode_i"] in ports
    assert (6 in ports) is False

    with raises(ValueError) as raised:
        ports.add(ucdp.Port(ucdp.UintType(4), "vec_b_o"))
    assert str(raised.value) == "Port(UintType(4), name='vec_b_o') already exists"

    with raises(ValueError) as raised:
        ports["foo"] = ucdp.Port(ucdp.UintType(4), "vec_x_o")
    assert str(raised.value) == "Port(UintType(4), name='vec_x_o') with must be stored at name 'vec_x_o' not at 'foo'"

    with raises(TypeError) as raised:
        del ports["foo"]
    assert str(raised.value) == "It is forbidden to remove 'foo'."

    assert ports.is_locked is False
    ports.lock()
    assert ports.is_locked is True
    with raises(ucdp.LockError) as raised:
        ports.add(ucdp.Port(ComplexType(), "another_o"))
    assert str(raised.value) == "Port(ComplexType(), name='another_o')"


def test_idents_conflict():
    """Idents with conflict."""
    with raises(ValueError) as raised:
        ucdp.Idents(
            [
                ucdp.Port(ucdp.UintType(8), "vec_a_i"),
                ucdp.Port(ucdp.UintType(8), "vec_a_i"),
            ]
        )
    assert str(raised.value) == "vec_a_i already exists (Port(UintType(8), name='vec_a_i'))"


def test_idents_empty():
    """Idents with conflict."""
    idents = ucdp.Idents()
    with raises(ValueError) as raised:
        assert idents["unknown"]
    assert str(raised.value) == "'unknown' is not known."


def test_idents_fuzzy():
    """Fussy Name Message."""
    idents = ucdp.Idents(
        [
            ucdp.Port(MyType(), "vec_a_i"),
            ucdp.Port(MyType(), "another_i"),
        ]
    )
    with raises(ValueError) as raised:
        assert idents.get("vec_a_sent_i")
    assert (
        str(raised.value)
        == """\
'vec_a_sent_i' is not known. Known are
'vec_a_i'            MyType()
  'vec_a_mode_i'     ModeType()
  'vec_a_send_i'     UintType(8)
  'vec_a_return_o'   UintType(4)
'another_i'          MyType()
  'another_mode_i'   ModeType()
  'another_send_i'   UintType(8)
  'another_return_o' UintType(4)

'vec_a_sent_i' is not known.

Did you mean 'vec_a_send_i'?"""
    )


# pylint: disable=redefined-outer-name
def test_findfirst(ports):
    """findfirst."""

    def filterclk(ident):
        return isinstance(ident.type_, ucdp.ClkType)

    assert repr(ports.findfirst(filter_=filterclk)) == "Port(ClkType(), name='clk_i', level=1, doc=Doc(title='Clock'))"


# pylint: disable=redefined-outer-name
def test_findfirst_none(ports):
    """findfirst."""

    def filternone(ident):
        return ident.name == "noname"

    assert ports.findfirst(filter_=filternone) is None


def test_identsingleton():
    """Singleton."""
    assert ucdp.Ident(ucdp.UintType(4), "a") is ucdp.Ident(ucdp.UintType(4), "a")
    assert ucdp.Ident(ucdp.UintType(4), "a") is not ucdp.Ident(ucdp.UintType(4), "b")

    # Non-Singleton Type
    dyn0 = ucdp.DynamicStructType()
    dyn1 = ucdp.DynamicStructType()
    assert dyn0 is not dyn1
    assert id(dyn0) != id(dyn1)
    assert hash(dyn0) != hash(dyn1)

    # Non-Singleton Ident
    assert ucdp.Ident(dyn0, "a") is not ucdp.Ident(dyn1, "a")
