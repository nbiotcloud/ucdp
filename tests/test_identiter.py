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

"""Test Ident Iteration."""
from pytest import fixture, raises

import ucdp


class AType(ucdp.AStructType):
    """AType."""

    def _build(self):
        self._add("req", ucdp.BitType())
        self._add("data", ucdp.ArrayType(ucdp.UintType(16), 5))
        self._add("ack", ucdp.BitType(), ucdp.BWD)
        self._add("error", ucdp.BitType(), ucdp.BIDIR)


class MType(ucdp.AEnumType):
    """MType."""

    keytype = ucdp.UintType(2)

    def _build(self):
        self._add(0, "Linear")
        self._add(1, "Cyclic")


class BType(ucdp.AStructType):
    """BType."""

    def _build(self):
        self._add("foo", AType())
        self._add("mode", MType())
        self._add("bar", ucdp.ArrayType(AType(), 3), ucdp.BWD)


class MyType(ucdp.AStructType):
    """My."""

    comment = "Mode"

    def _build(self):
        self._add("mode", SelType())
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
    """Some Ports."""
    return ucdp.Idents(
        [
            ucdp.Port(ucdp.ClkRstAnType()),
            ucdp.Port(ucdp.UintType(8), "vec_a_i"),
            ucdp.Port(ucdp.UintType(8), "vec_a_o"),
            ucdp.Port(ucdp.UintType(14), "vec_b_i"),
            ucdp.Port(ucdp.UintType(14), "vec_b_o"),
            ucdp.Port(ucdp.UintType(4), "vec_c_i"),
            ucdp.Port(ucdp.UintType(4), "vec_c_o"),
            ucdp.Port(ucdp.UintType(8), "vec_d_i"),
            ucdp.Port(ucdp.UintType(8), "vec_d_o"),
            ucdp.Port(MyType(), "my_a_i"),
            ucdp.Port(MyType(), "my_a_o"),
            ucdp.Port(MyType(), "my_b_i"),
            ucdp.Port(MyType(), "my_b_o"),
            ucdp.Port(ComplexType(), "comp_lex_i"),
            ucdp.Port(ComplexType(), "comp_lex_o"),
        ]
    )


def _test(idents):
    return tuple(repr(ident) for ident in idents)


def test_iter():
    """Default."""
    assert _test(ucdp.Signal(BType(), "name_s").iter()) == (
        "Signal(BType(), 'name_s')",
        "Signal(AType(), 'name_foo_s', level=1)",
        "Signal(BitType(), 'name_foo_req_s', level=2)",
        "Signal(UintType(16), 'name_foo_data_s', level=2, dims=(Slice('0:4'),))",
        "Signal(BitType(), 'name_foo_ack_s', level=2, direction=BWD)",
        "Signal(BitType(), 'name_foo_error_s', level=2, direction=BIDIR)",
        "Signal(MType(), 'name_mode_s', level=1)",
        "Signal(AType(), 'name_bar_s', level=1, direction=BWD, dims=(Slice('0:2'),))",
        "Signal(BitType(), 'name_bar_req_s', level=2, direction=BWD, dims=(Slice('0:2'),))",
        "Signal(UintType(16), 'name_bar_data_s', level=2, direction=BWD, dims=(Slice('0:2'), Slice('0:4')))",
        "Signal(BitType(), 'name_bar_ack_s', level=2, dims=(Slice('0:2'),))",
        "Signal(BitType(), 'name_bar_error_s', level=2, direction=BIDIR, dims=(Slice('0:2'),))",
    )


def test_iter_maxlevel():
    """Maxlevel."""
    assert _test(ucdp.Signal(BType(), "name_s").iter(maxlevel=0)) == ("Signal(BType(), 'name_s')",)
    assert _test(ucdp.Signal(BType(), "name_s").iter(maxlevel=1)) == (
        "Signal(BType(), 'name_s')",
        "Signal(AType(), 'name_foo_s', level=1)",
        "Signal(MType(), 'name_mode_s', level=1)",
        "Signal(AType(), 'name_bar_s', level=1, direction=BWD, dims=(Slice('0:2'),))",
    )
    assert _test(ucdp.Signal(BType(), "name_s").iter(maxlevel=2)) == (
        "Signal(BType(), 'name_s')",
        "Signal(AType(), 'name_foo_s', level=1)",
        "Signal(BitType(), 'name_foo_req_s', level=2)",
        "Signal(UintType(16), 'name_foo_data_s', level=2, dims=(Slice('0:4'),))",
        "Signal(BitType(), 'name_foo_ack_s', level=2, direction=BWD)",
        "Signal(BitType(), 'name_foo_error_s', level=2, direction=BIDIR)",
        "Signal(MType(), 'name_mode_s', level=1)",
        "Signal(AType(), 'name_bar_s', level=1, direction=BWD, dims=(Slice('0:2'),))",
        "Signal(BitType(), 'name_bar_req_s', level=2, direction=BWD, dims=(Slice('0:2'),))",
        "Signal(UintType(16), 'name_bar_data_s', level=2, direction=BWD, dims=(Slice('0:2'), Slice('0:4')))",
        "Signal(BitType(), 'name_bar_ack_s', level=2, dims=(Slice('0:2'),))",
        "Signal(BitType(), 'name_bar_error_s', level=2, direction=BIDIR, dims=(Slice('0:2'),))",
    )


def test_iter_filter():
    """Filter."""

    def filter_(ident):
        return ident.name.startswith("name_bar")

    assert _test(ucdp.Signal(BType(), "name_s").iter(filter_=filter_)) == (
        "Signal(AType(), 'name_bar_s', level=1, direction=BWD, dims=(Slice('0:2'),))",
        "Signal(BitType(), 'name_bar_req_s', level=2, direction=BWD, dims=(Slice('0:2'),))",
        "Signal(UintType(16), 'name_bar_data_s', level=2, direction=BWD, dims=(Slice('0:2'), Slice('0:4')))",
        "Signal(BitType(), 'name_bar_ack_s', level=2, dims=(Slice('0:2'),))",
        "Signal(BitType(), 'name_bar_error_s', level=2, direction=BIDIR, dims=(Slice('0:2'),))",
    )


def test_iter_stop():
    """Stop."""

    def stop(ident):
        return ident.name == "name_foo_s"

    assert _test(ucdp.Signal(BType(), "name_s").iter(stop=stop)) == (
        "Signal(BType(), 'name_s')",
        "Signal(MType(), 'name_mode_s', level=1)",
        "Signal(AType(), 'name_bar_s', level=1, direction=BWD, dims=(Slice('0:2'),))",
        "Signal(BitType(), 'name_bar_req_s', level=2, direction=BWD, dims=(Slice('0:2'),))",
        "Signal(UintType(16), 'name_bar_data_s', level=2, direction=BWD, dims=(Slice('0:2'), Slice('0:4')))",
        "Signal(BitType(), 'name_bar_ack_s', level=2, dims=(Slice('0:2'),))",
        "Signal(BitType(), 'name_bar_error_s', level=2, direction=BIDIR, dims=(Slice('0:2'),))",
    )


def test_iter_stop_early():
    """Stop early."""

    def stop(ident):
        return ident.name != "name_foo_s"

    assert _test(ucdp.Signal(BType(), "name_s").iter(stop=stop)) == tuple()


def test_iter_stop_array():
    """Stop arry."""

    def stop(ident):
        return isinstance(ident.type_, ucdp.UintType)

    assert _test(ucdp.Signal(BType(), "name_s").iter(stop=stop)) == (
        "Signal(BType(), 'name_s')",
        "Signal(AType(), 'name_foo_s', level=1)",
        "Signal(BitType(), 'name_foo_req_s', level=2)",
        "Signal(BitType(), 'name_foo_ack_s', level=2, direction=BWD)",
        "Signal(BitType(), 'name_foo_error_s', level=2, direction=BIDIR)",
        "Signal(MType(), 'name_mode_s', level=1)",
        "Signal(AType(), 'name_bar_s', level=1, direction=BWD, dims=(Slice('0:2'),))",
        "Signal(BitType(), 'name_bar_req_s', level=2, direction=BWD, dims=(Slice('0:2'),))",
        "Signal(BitType(), 'name_bar_ack_s', level=2, dims=(Slice('0:2'),))",
        "Signal(BitType(), 'name_bar_error_s', level=2, direction=BIDIR, dims=(Slice('0:2'),))",
    )


def test_get_ident():
    """get_ident."""
    ident = ucdp.ident.Ident(BType(), "name_s")
    subidents = tuple(ident.iter())
    assert len(subidents) == 12
    for subident in subidents:
        assert ident.get(subident.name) is subident
    with raises(ValueError):
        ident.get("name")


# pylint: disable=redefined-outer-name
def test_get_ident_ports(ports):
    """get_ident on ports."""
    for ident in ports:
        for subident in ident.iter():
            assert ports[subident.name] is subident


def test_typeiter():
    """Default."""
    assert tuple(ucdp.typeiter("", BType())) == (
        ("", BType(), ucdp.FWD),
        ("foo", AType(), ucdp.FWD),
        ("foo_req", ucdp.BitType(), ucdp.FWD),
        ("foo_data", ucdp.UintType(16), ucdp.FWD),
        ("foo_ack", ucdp.BitType(), ucdp.BWD),
        ("foo_error", ucdp.BitType(), ucdp.BIDIR),
        ("mode", MType(), ucdp.FWD),
        ("bar", AType(), ucdp.BWD),
        ("bar_req", ucdp.BitType(), ucdp.BWD),
        ("bar_data", ucdp.UintType(16), ucdp.BWD),
        ("bar_ack", ucdp.BitType(), ucdp.FWD),
        ("bar_error", ucdp.BitType(), ucdp.BIDIR),
    )
