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


class MyConfig(u.AConfig):
    """My Configuration."""

    mem_baseaddr: u.Hex
    ram_size: u.Bytes
    rom_size: u.Bytes = 0
    feature: bool = False


def test_config():
    """Example."""
    # Missing Arguments
    with raises(u.ValidationError):
        MyConfig(name="myconfig")

    config = MyConfig("myconfig", mem_baseaddr=0xF100, ram_size="16 kB")
    assert str(config) == "MyConfig('myconfig', mem_baseaddr=Hex('0xF100'), ram_size=Bytes('16 KB'))"
    assert dict(config) == {
        "feature": False,
        "mem_baseaddr": u.Hex("0xF100"),
        "name": "myconfig",
        "ram_size": u.Bytes("16 KB"),
        "rom_size": u.Bytes("0 bytes"),
    }

    assert config.hash == "db829f1d9872ab0e"
    assert config.is_default is False


class OtherConfig(u.AConfig):
    """Other Configuration."""

    ram_size: u.Bytes = 0x100
    rom_size: u.Bytes = 0
    feature: bool = False


def test_default_config():
    """Default Configuration."""
    config = OtherConfig()
    assert config.hash == "180b3344e5934705"
    assert config.is_default is True

    config = OtherConfig(name="abc")
    assert config.hash == "06449e0c672f3868"
    assert config.is_default is False
