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
"""Test Configuration."""

import ucdp as u
from pytest import raises


def test_config():
    """Example."""

    class MyConfig(u.AConfig):
        """My Configuration."""

        mem_baseaddr: u.Hex
        ram_size: u.Bytes
        rom_size: u.Bytes = 0
        feature: bool = False

    # Missing Arguments
    with raises(u.ValidationError):
        MyConfig(name="myconfig")

    config = MyConfig("myconfig", mem_baseaddr=0xF100, ram_size="16 kB")
    assert (
        str(config) == "test_config.<locals>.MyConfig('myconfig', mem_baseaddr=Hex('0xF100'), ram_size=Bytes('16 KB'))"
    )
    assert dict(config) == {
        "feature": False,
        "mem_baseaddr": u.Hex("0xF100"),
        "name": "myconfig",
        "ram_size": u.Bytes("16 KB"),
        "rom_size": u.Bytes("0 bytes"),
    }
