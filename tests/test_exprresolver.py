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
def rslvr() -> u.ExprResolver:
    """Expression Resolver."""
    return u.ExprResolver()


def test_slice(rslvr):
    """Resolver."""
    param = u.Param(u.IntegerType(default=8), "param")
    signal = u.Signal(u.UintType(16, default=15), "uint_s")

    assert rslvr.resolve(signal[2]) == "uint_s[2]"
    assert rslvr.resolve(signal[2:1]) == "uint_s[2:1]"
    assert rslvr.resolve(signal[2:0]) == "uint_s[3-1:0]"

    assert rslvr.resolve(signal[param]) == "uint_s[param]"
    assert rslvr.resolve(signal[param:1]) == "uint_s[param:1]"
    assert rslvr.resolve(signal[param:0]) == "uint_s[param:0]"
    assert rslvr.resolve(signal[14:param]) == "uint_s[14:param]"
