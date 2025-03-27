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
"""Test :any:`Object`."""

import re

from pytest import fixture, raises

import ucdp as u


@fixture
def namespace() -> u.Namespace:
    """Example Namespace."""
    return u.Namespace(
        [
            u.Param(u.IntegerType(default=8), "param"),
            u.Param(u.IntegerType(default=1), "param1"),
            u.Signal(u.UintType(16, default=15), "uint_s"),
            u.Ident(u.UintType(10), "ident0"),
            u.Ident(u.UintType(10), "ident1"),
        ]
    )


class MyExprResolver(u.ExprResolver):
    """Resolver with Array Implementation."""

    def _get_array_value(self, itemvalue: str, slice_: u.Slice) -> str:
        width = self._resolve(slice_.width, brackets=True)
        return f"{width}#{itemvalue}"


@fixture
def rslvr(namespace) -> u.ExprResolver:
    """Expression Resolver."""
    return MyExprResolver(namespace=namespace)


class MyEnumType(u.AEnumType):
    """Example Enumeration."""

    keytype: u.UintType = u.UintType(4)

    def _build(self):
        self._add(0, "a")


class MyStructType(u.AStructType):
    """Example Struct."""

    def _build(self):
        self._add("a", u.UintType(4))


def test_op(rslvr):
    """Bool Op."""
    a = u.const("2")
    b = u.const("3")

    assert rslvr.resolve(a + b) == "2 + 3"
    assert rslvr.resolve(a == b) == "2 == 3"
    assert rslvr.resolve(-a) == "-2"
    assert rslvr.resolve(abs(-a)) == "abs(-2)"


def test_slice(rslvr):
    """Resolver."""
    param = rslvr.namespace["param"]
    param1 = rslvr.namespace["param1"]
    signal = rslvr.namespace["uint_s"]

    assert rslvr.resolve(signal[2]) == "uint_s[2]"
    assert rslvr.resolve(signal[2:1]) == "uint_s[2:1]"
    assert rslvr.resolve(signal[2:0]) == "uint_s[2:0]"

    assert rslvr.resolve(signal[param]) == "uint_s[param]"
    assert rslvr.resolve(signal[param:1]) == "uint_s[param:1]"
    assert rslvr.resolve(signal[param:0]) == "uint_s[param:0]"
    assert rslvr.resolve(signal[14:param]) == "uint_s[14:param]"

    assert rslvr.resolve_slice(u.Slice(left=param)) == "[param]"

    assert rslvr.resolve(signal[param1:1]) == "uint_s[param1:1]"


def test_values(rslvr):
    """Values."""
    param = u.Param(u.BitType(), "param")
    assert rslvr.resolve(u.ConstExpr(u.BitType())) == "0"
    assert rslvr.resolve(u.ConstExpr(u.BitType(default=1))) == "1"
    assert rslvr.resolve(u.ConstExpr(u.BitType(default=param))) == "param"

    param = u.Param(u.RailType(), "param")
    assert rslvr.resolve(u.ConstExpr(u.RailType())) == ""
    assert rslvr.resolve(u.ConstExpr(u.RailType(default=0))) == "0"
    assert rslvr.resolve(u.ConstExpr(u.RailType(default=1))) == "1"
    assert rslvr.resolve(u.ConstExpr(u.RailType(default=param))) == "param"

    param = u.Param(u.BoolType(), "param")
    assert rslvr.resolve(u.ConstExpr(u.BoolType())) == "False"
    assert rslvr.resolve(u.ConstExpr(u.BoolType(default=True))) == "True"
    assert rslvr.resolve(u.ConstExpr(u.BoolType(default=param))) == "param"

    param = u.Param(u.UintType(8), "param")
    assert rslvr.resolve(u.ConstExpr(u.UintType(8))) == "0x0"
    assert rslvr.resolve(u.ConstExpr(u.UintType(8, default=1))) == "0x1"
    assert rslvr.resolve(u.ConstExpr(u.UintType(8, default=param))) == "param"

    param = u.Param(u.UintType(8), "param")
    assert rslvr.resolve(u.ConstExpr(u.UintType(8))) == "0x0"
    assert rslvr.resolve(u.ConstExpr(u.UintType(8, default=1))) == "0x1"
    assert rslvr.resolve(u.ConstExpr(u.UintType(8, default=param))) == "param"

    with raises(ValueError):
        rslvr.resolve(u.ConstExpr(u.UintType(-8)))

    param = u.Param(u.SintType(8), "param")
    assert rslvr.resolve(u.ConstExpr(u.SintType(8))) == "0x0"
    assert rslvr.resolve(u.ConstExpr(u.SintType(8, default=1))) == "0x1"
    assert rslvr.resolve(u.ConstExpr(u.SintType(8, default=-2))) == "-0x2"
    assert rslvr.resolve(u.ConstExpr(u.SintType(8, default=param))) == "param"

    param = u.Param(u.IntegerType(), "param")
    assert rslvr.resolve(u.ConstExpr(u.IntegerType())) == "0"
    assert rslvr.resolve(u.ConstExpr(u.IntegerType(default=1))) == "1"
    assert rslvr.resolve(u.ConstExpr(u.IntegerType(default=-2))) == "-2"
    assert rslvr.resolve(u.ConstExpr(u.IntegerType(default=param))) == "param"

    with raises(ValueError):
        rslvr.resolve(u.ConstExpr(u.SintType(-8)))

    param = u.Param(MyEnumType(), "param")
    assert rslvr.resolve(u.ConstExpr(MyEnumType())) == "0x0"
    assert rslvr.resolve(u.ConstExpr(MyEnumType(default=1))) == "0x1"
    assert rslvr.resolve(u.ConstExpr(MyEnumType(default=param))) == "param"

    assert rslvr.resolve(u.ConstExpr(u.StringType())) == "''"
    assert rslvr.resolve(u.ConstExpr(u.StringType(default="foo"))) == "'foo'"

    assert rslvr.resolve(u.ConstExpr(u.FloatType())) == "0.0"
    assert rslvr.resolve(u.ConstExpr(u.FloatType(default=1.2))) == "1.2"

    assert rslvr.resolve(u.ConstExpr(u.DoubleType())) == "0.0"
    assert rslvr.resolve(u.ConstExpr(u.DoubleType(default=1.2))) == "1.2"

    assert rslvr.resolve(u.TODO) == "'TODO'"

    with raises(ValueError):
        rslvr.resolve(u.ConstExpr(MyStructType()))


def test_resolve_value(rslvr):
    """Resolver."""
    assert rslvr.resolve_value(u.StringType()) == "''"
    assert rslvr.resolve_value(u.StringType(default="foo")) == "'foo'"


def test_missing(rslvr):
    """Missing Name."""
    msg = "'unknown' is not a valid expression."
    with raises(ValueError, match=re.escape(msg)):
        rslvr.resolve("unknown")

    msg = "Ident(UintType(6), 'ident') not known within current namespace."
    with raises(ValueError, match=re.escape(msg)):
        rslvr.resolve(u.Ident(u.UintType(6), "ident"))


def test_concat(rslvr):
    """Concat."""
    expr = u.ConcatExpr(
        (
            u.ConstExpr(u.UintType(5, default=5)),
            u.ConstExpr(u.UintType(10, default=0x123))[4:1],
            u.ConstExpr(u.UintType(16, default=3)),
        )
    )
    assert rslvr.resolve(expr) == "{0x5, 0x1, 0x3}"


def test_ternary(rslvr):
    """Concat."""
    param = rslvr.namespace["param"]
    ident0 = rslvr.namespace["ident0"]
    ident1 = rslvr.namespace["ident1"]
    expr = u.TernaryExpr(param == 5, ident0, ident1)
    assert rslvr.resolve(expr) == "(param == 5) ? ident0 : ident1"


def test_remap():
    """Remap."""
    param = u.Param(u.IntegerType(default=8), "param")
    width = u.Param(u.IntegerType(default=u.Log2Expr(param)), "width")
    namespace = u.Namespace(
        [
            param,
            width,
            u.Port(u.UintType(param), "data_i"),
            u.Port(u.UintType(param), "cnt_o"),
        ]
    )

    rslvr = u.ExprResolver(namespace=namespace)
    assert rslvr(param) == "param"

    remap = u.Idents([param])
    rslvr = u.ExprResolver(namespace=namespace, remap=remap)
    assert rslvr(param) == "8"
    assert rslvr(width) == "width"


def test_log2(rslvr):
    """Log2."""
    expr = u.Log2Expr(u.ConstExpr(u.UintType(8, default=8)))
    with raises(NotImplementedError):
        rslvr(expr)


def test_min(rslvr):
    """Minimum."""
    expr = u.MinimumExpr(
        (
            u.ConstExpr(u.UintType(5, default=5)),
            u.ConstExpr(u.UintType(16, default=3)),
        )
    )
    with raises(NotImplementedError):
        rslvr(expr)


def test_max(rslvr):
    """Maximum."""
    expr = u.MaximumExpr(
        (
            u.ConstExpr(u.UintType(5, default=5)),
            u.ConstExpr(u.UintType(16, default=3)),
        )
    )
    with raises(NotImplementedError):
        rslvr(expr)


def test_range(rslvr):
    """Range."""
    expr = u.RangeExpr(type_=u.UintType(4), range_=range(2, 9))
    with raises(NotImplementedError):
        rslvr(expr)


def test_array(rslvr, namespace):
    """Array."""
    param = namespace["param"]
    expr = u.ConstExpr(u.ArrayType(u.UintType(8, default=4), param))
    assert rslvr(expr) == "param#0x4"

    expr = u.ConstExpr(u.ArrayType(u.UintType(8, default=2), param * 2))
    assert rslvr(expr) == "(param * 2)#0x2"

    expr = u.ConstExpr(u.ArrayType(u.UintType(8, default=2), param * 2, left=3))
    assert rslvr(expr) == "(param * 2)#0x2"
