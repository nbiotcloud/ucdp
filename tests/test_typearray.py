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

import ucdp as u


def test_array_up():
    """Array - upwards."""
    type_ = u.ArrayType(u.UintType(16), 10)
    assert repr(type_) == "ArrayType(UintType(16), 10)"
    assert type_.slice_ == u.Slice("0:9")

    type_ = u.ArrayType(u.UintType(16), 10, right=20)
    assert repr(type_) == "ArrayType(UintType(16), 10, right=20)"
    assert type_.slice_ == u.Slice("11:20")

    type_ = u.ArrayType(u.UintType(16), 10, left=20)
    assert repr(type_) == "ArrayType(UintType(16), 10, left=20)"
    assert type_.slice_ == u.Slice("20:29")


def test_array_down():
    """Array - downwards."""
    type_ = u.ArrayType(u.UintType(16), 10, direction=u.DOWN)
    assert repr(type_) == "ArrayType(UintType(16), 10, direction=DOWN)"
    assert type_.slice_ == u.Slice("9:0")

    type_ = u.ArrayType(u.UintType(16), 10, right=20, direction=u.DOWN)
    assert repr(type_) == "ArrayType(UintType(16), 10, right=20, direction=DOWN)"
    assert type_.slice_ == u.Slice("29:20")

    type_ = u.ArrayType(u.UintType(16), 10, left=20, direction=u.DOWN)
    assert repr(type_) == "ArrayType(UintType(16), 10, left=20, direction=DOWN)"
    assert type_.slice_ == u.Slice("20:11")
