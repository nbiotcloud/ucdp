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
"""Test Name Utilities."""
import ucdp


def test_split_prefix():
    """Split Prefix."""
    assert ucdp.split_prefix("a_name", prefixes=("a_", "b_")) == ("a_", "name")
    assert ucdp.split_prefix("b_name", prefixes=("a_", "b_")) == ("b_", "name")
    assert ucdp.split_prefix("c_name", prefixes=("a_", "b_")) == ("", "c_name")


def test_split_suffix():
    """Split Suffix."""
    assert ucdp.split_suffix("name_a", suffixes=("_a", "_b")) == ("name", "_a")
    assert ucdp.split_suffix("name_b", suffixes=("_a", "_b")) == ("name", "_b")
    assert ucdp.split_suffix("name_c", suffixes=("_a", "_b")) == ("name_c", "")
