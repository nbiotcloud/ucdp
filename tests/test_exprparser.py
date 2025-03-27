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
def idents() -> u.Idents:
    """Some Identifier."""
    return u.Idents(
        [
            u.Signal(u.UintType(16, default=15), "uint_s"),
            u.Signal(u.SintType(16, default=-15), "sint_s"),
        ]
    )


@fixture
def parser(idents) -> u.ExprParser:
    """Some Identifier."""
    return u.ExprParser(namespace=idents)


def test_parse(parser):
    """Parse."""
    signal = u.Signal(u.UintType(16, default=15), "uint_s")
    expr = parser.parse("uint_s[2]")
    assert expr == u.SliceOp(signal, u.Slice("2"))

    with raises(NameError):
        parser.parse(u.TODO)
    assert parser.parse(2) == u.ConstExpr(u.IntegerType(default=2))
    assert parser.parse(u.IntegerType(default=2)) == u.ConstExpr(u.IntegerType(default=2))

    assert parser.parse("uint_s", only=u.Signal) is signal

    msg = (
        "Signal(UintType(16, default=15), 'uint_s') is not a <class 'ucdp.signal.Port'>. "
        "It is a <class 'ucdp.signal.Signal'>"
    )
    with raises(ValueError, match=re.escape(msg)):
        parser.parse("uint_s", only=u.Port)

    msg = (
        "Signal(UintType(16, default=15), 'uint_s') requires type_ <class 'ucdp.typescalar.SintType'>. "
        "It is a UintType(16, default=15)"
    )
    with raises(ValueError, match=re.escape(msg)):
        parser.parse("uint_s", types=u.SintType)

    msg = "'uint_s *** uint_s': invalid syntax (<string>, line 1)"
    with raises(u.InvalidExpr, match=re.escape(msg)):
        parser.parse("uint_s *** uint_s")


def test_parse_undefined(parser):
    """Undefined names."""
    with raises(NameError, match=re.escape("None: 'uint' is not known.")):
        parser.parse("uint")


# def test_parse_nostrict(idents):
#    """Some Identifier."""
#     parser = u.ExprParser(namespace=idents, strict=False)

#     expr = parser.parse("uint_s[2]")
#     assert expr == u.SliceOp(u.Signal(u.UintType(16, default=15), "uint_s"), u.Slice("2"))

#     assert parser.parse("uint") == "uint"


# def test_parse_empty_nostrict():
#    """Some Identifier."""
#     parser = u.ExprParser(strict=False)

#     expr = parser.parse("uint_s[2]")
#     assert expr == 2
#     assert parser.parse("uint") == "uint"


def test_int():
    """Test Integer."""
    signal = u.Signal(u.UintType(16, default=15), "uint_s")

    expr = signal // 2
    assert expr == u.Op(signal, "//", u.ConstExpr(u.UintType(16, default=2)))

    expr = signal // -2
    assert expr == u.Op(signal, "//", u.ConstExpr(u.SintType(2, default=-2)))


def test_const():
    """Test Constants."""
    assert u.const("0") is u.ConstExpr(u.IntegerType())
    assert u.const("2'b10") is u.ConstExpr(u.UintType(2, default=2))
    assert u.const("-2'sb10") is u.ConstExpr(u.SintType(2, default=-2))

    assert u.const("1'b0") is u.ConstExpr(u.BitType())
    assert u.const("1'b1") is u.ConstExpr(u.BitType(default=1))

    assert u.const("1'h0") is u.ConstExpr(u.UintType(1))
    assert u.const("1'h1") is u.ConstExpr(u.UintType(1, default=1))

    assert u.const(0) is u.ConstExpr(u.IntegerType())
    assert u.const(1) is u.ConstExpr(u.IntegerType(default=1))
    assert u.const(-1) is u.ConstExpr(u.IntegerType(default=-1))

    assert u.const(u.IntegerType.min_) is u.ConstExpr(u.IntegerType(default=u.IntegerType.min_))
    assert u.const(u.IntegerType.max_) is u.ConstExpr(u.IntegerType(default=u.IntegerType.max_))

    assert u.const(u.IntegerType.min_ - 1) is u.ConstExpr(u.SintType(33, default=u.IntegerType.min_ - 1))
    assert u.const(u.IntegerType.max_ + 1) is u.ConstExpr(u.UintType(32, default=u.IntegerType.max_ + 1))

    assert u.const(4) == u.ConstExpr(u.IntegerType(default=4))


def test_concat(parser):
    """Test Concat."""
    expr = parser.parse(("10'd2", 10))
    assert expr == u.ConcatExpr((u.ConstExpr(u.UintType(10, default=2)), u.ConstExpr(u.IntegerType(default=10))))
    assert expr is parser.parse(expr)
    assert expr is parser.concat(expr)
    assert expr[2:1] == u.SliceOp(
        u.ConcatExpr((u.ConstExpr(u.UintType(10, default=2)), u.ConstExpr(u.IntegerType(default=10)))), u.Slice("2:1")
    )
    assert int(expr) == 10242
    assert expr.type_ == u.UintType(
        42,
        default=u.Op(
            u.Op(
                u.Op(
                    u.ConstExpr(u.UintType(10)),
                    "+",
                    u.Op(u.ConstExpr(u.UintType(10, default=2)), "<<", u.ConstExpr(u.UintType(10))),
                ),
                "+",
                u.Op(u.ConstExpr(u.IntegerType(default=10)), "<<", u.ConstExpr(u.IntegerType(default=10))),
            ),
            "+",
            u.ConstExpr(u.UintType(10)),
        ),
    )

    assert u.concat((4, 3, 4)) == u.ConcatExpr(
        (
            u.ConstExpr(u.IntegerType(default=4)),
            u.ConstExpr(u.IntegerType(default=3)),
            u.ConstExpr(u.IntegerType(default=4)),
        )
    )


def test_ternary(parser):
    """Ternary."""
    cond0 = u.Signal(u.BitType(), "if_s") == 0
    cond1 = u.Signal(u.BitType(), "if_s") == 1
    one = u.Signal(u.UintType(16, default=10), "one_s")
    other = u.Signal(u.UintType(16, default=20), "other_s")

    expr = parser.ternary(cond0, one, other)
    assert expr == u.TernaryExpr(
        u.BoolOp(u.Signal(u.BitType(), "if_s"), "==", u.ConstExpr(u.BitType())),
        u.Signal(u.UintType(16, default=10), "one_s"),
        u.Signal(u.UintType(16, default=20), "other_s"),
    )
    assert int(expr) == 10

    expr = parser.ternary(cond1, one, other)
    assert expr == u.TernaryExpr(
        u.BoolOp(u.Signal(u.BitType(), "if_s"), "==", u.ConstExpr(u.BitType(default=1))),
        u.Signal(u.UintType(16, default=10), "one_s"),
        u.Signal(u.UintType(16, default=20), "other_s"),
    )
    assert int(expr) == 20

    a = u.const(4)
    b = u.const(5)
    assert u.ternary(a == b, 4, 5) == u.TernaryExpr(u.BoolOp(a, "==", b), a, b)


def test_note(parser):
    """Note."""
    assert parser.parse_note(u.TODO) is u.TODO
    assert parser.parse_note(2) == u.ConstExpr(u.IntegerType(default=2))
    assert parser.parse_note(u.IntegerType(default=2)) == u.ConstExpr(u.IntegerType(default=2))

    msg = "Note(note='TODO') is not a <class 'ucdp.signal.Signal'>. It is a <class 'ucdp.note.Note'>"
    with raises(ValueError, match=re.escape(msg)):
        parser.parse_note(u.TODO, only=u.Signal)

    msg = "Note(note='TODO') does not meet type_ <class 'ucdp.typescalar.BoolType'>."
    with raises(ValueError, match=re.escape(msg)):
        parser.parse_note(u.TODO, types=u.BoolType)


def test_castbooltype():
    """Cast BoolType."""
    value2 = u.const("2b10")
    boolop = u.BoolOp(value2, "==", value2)
    assert u.cast_booltype(boolop) is boolop

    msg = "ConstExpr(UintType(2, default=2)) does not result in bool"
    with raises(ValueError, match=re.escape(msg)):
        u.cast_booltype(value2)

    boolopuint = u.BoolOp(u.ConstExpr(u.UintType(1, default=1)), "==", u.ConstExpr(u.BitType(default=1)))
    assert u.cast_booltype(u.const("1h1")) == boolopuint

    boolopuint = u.BoolOp(u.ConstExpr(u.UintType(1)), "==", u.ConstExpr(u.UintType(1, default=1)))
    assert u.cast_booltype(u.const("1h0")) == boolopuint


def test_unknown():
    """Unknown."""
    parser = u.ExprParser()
    parser("unknown")


def test_type_error():
    """Type Error."""
    parser = u.ExprParser()
    msg = "'faf' / 5"
    with raises(u.InvalidExpr, match=re.escape(msg)):
        parser("'faf' / 5")


def test_log2():
    """Log 2."""
    a = u.const(67)
    assert u.log2(a) == u.Log2Expr(a)
