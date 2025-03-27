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
Struct Type Testing.
"""

import re

from pytest import raises

import ucdp as u


def test_float():
    """Float."""
    float = u.FloatType()
    assert float is u.FloatType()
    assert float.is_connectable(float) is True
    assert float.is_connectable(u.DoubleType()) is False
    with raises(ValueError, match=re.escape("Slicing is not allowed floating point numbers")):
        float[2]


def test_double():
    """Double."""
    double = u.DoubleType()
    assert double is u.DoubleType()
    assert double.is_connectable(double) is True
    assert double.is_connectable(u.FloatType()) is False
    with raises(ValueError, match=re.escape("Slicing is not allowed on floating point numbers")):
        double[2]
