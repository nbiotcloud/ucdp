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
"""Test :any:`Object`."""

import ucdp as u
from pytest import fixture


@fixture
def parser() -> u.ExprParser:
    """Some Identifier."""
    namespace = u.Idents(
        [
            u.Signal(u.UintType(16, default=15), "uint_s"),
            u.Signal(u.SintType(16, default=-15), "sint_s"),
        ]
    )
    return u.ExprParser(namespace=namespace)


def test_parse(parser):
    """Parse."""
    expr = parser.parse("uint_s[2]")
    assert expr == u.SliceOp(u.Signal(u.UintType(16, default=15), "uint_s"), u.Slice("2"))
