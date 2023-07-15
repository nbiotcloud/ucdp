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

"""Signal Testing."""
from attr.exceptions import FrozenInstanceError
from pytest import raises

import ucdp


def test_signal():
    """Signal."""
    count = ucdp.Signal(ucdp.UintType(6), "count_s")
    assert repr(count) == "Signal(UintType(6), 'count_s')"
    assert count.type_ is ucdp.UintType(6)
    assert count.name == "count_s"
    assert count.basename == "count"
    assert count.suffix == "_s"
    assert count.direction == ucdp.FWD
    assert count.doc is ucdp.Doc()
    assert count.title is None
    assert count.descr is None
    assert count.comment is None
    assert tuple(count) == (count,)

    with raises(FrozenInstanceError):
        count.something = 1


def test_signal_doc():
    """Test Complex Signal with Doc."""

    class MyType(ucdp.AStructType):
        """My Type."""

        comment = "Mode"

        def _build(self):
            self._add("send", ucdp.ArrayType(ucdp.UintType(8), 3))
            self._add("return", ucdp.UintType(4), ucdp.BWD)

    doc = ucdp.Doc(title="title", descr="descr", comment="a input")
    count = ucdp.Signal(MyType(), "count_s", doc=doc)
    assert count.type_ is MyType()
    assert count.name == "count_s"
    assert count.basename == "count"
    assert count.suffix == "_s"
    assert count.direction == ucdp.FWD
    assert count.doc is doc
    assert count.title == "title"
    assert count.descr == "descr"
    assert count.comment == "a input"
    assert tuple(count) == (
        ucdp.Signal(MyType(), "count_s", doc=doc),
        ucdp.Signal(ucdp.UintType(8), "count_send_s", level=1, dims=(ucdp.Slice("0:2"),)),
        ucdp.Signal(ucdp.UintType(4), "count_return_s", level=1, direction=ucdp.BWD),
    )


def test_port():
    """Port."""
    count = ucdp.Port(ucdp.UintType(6), "count_o")
    assert repr(count) == "Port(UintType(6), name='count_o')"
    assert count.type_ is ucdp.UintType(6)
    assert count.name == "count_o"
    assert count.basename == "count"
    assert count.suffix == "_o"
    assert count.direction == ucdp.OUT
    assert count.doc is ucdp.Doc()
    assert count.title is None
    assert count.descr is None
    assert count.comment is None
    assert tuple(count) == (count,)

    with raises(FrozenInstanceError):
        count.something = 1


def test_port_direction():
    """Port."""
    count = ucdp.Port(ucdp.UintType(6), "count_o", direction=ucdp.IN)
    assert repr(count) == "Port(UintType(6), name='count_o', direction=IN)"
    assert count.type_ is ucdp.UintType(6)
    assert count.name == "count_o"
    assert count.basename == "count"
    assert count.suffix == "_o"
    assert count.direction == ucdp.IN
    assert count.doc is ucdp.Doc()


def test_port_doc():
    """Test Complex Port with Doc."""

    class MyType(ucdp.AStructType):
        """My Type."""

        comment = "Mode"

        def _build(self):
            self._add("send", ucdp.ArrayType(ucdp.UintType(8), 3))
            self._add("return", ucdp.UintType(4), ucdp.BWD)

    doc = ucdp.Doc(title="title", descr="descr", comment="a input")
    count = ucdp.Port(MyType(), "count_i", doc=doc)
    assert count.type_ is MyType()
    assert count.name == "count_i"
    assert count.basename == "count"
    assert count.suffix == "_i"
    assert count.direction == ucdp.IN
    assert count.doc is doc
    assert count.title == "title"
    assert count.descr == "descr"
    assert count.comment == "a input"
    assert tuple(count) == (
        ucdp.Port(MyType(), "count_i", doc=doc),
        ucdp.Port(ucdp.UintType(8), "count.send_i", level=1, dims=(ucdp.Slice("0:2"),)),
        ucdp.Port(ucdp.UintType(4), "count.return_o", level=1),
    )


def test_port_shortname():
    """port With Short Name."""
    port = ucdp.Port(ucdp.UintType(6), "a_i")
    assert port.basename == "a"
    assert port.suffix == "_i"
    assert port.direction == ucdp.IN
