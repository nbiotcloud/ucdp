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
"""Test Configuration."""

from pytest import raises
from uniquer import uniquelist

import ucdp as u


class MyConfig(u.AConfig):
    """My Configuration."""

    _hash_excludes: u.ClassVar[set[str]] = {
        "ignored",
    }

    mem_baseaddr: u.Hex
    ram_size: u.Bytesize
    rom_size: u.Bytesize = 0
    feature: bool = False

    ignored: int = 0


def test_config():
    """Example."""
    # Missing Arguments
    with raises(u.ValidationError):
        MyConfig(name="myconfig")

    config = MyConfig("myconfig", mem_baseaddr=0xF100, ram_size="16 kB")
    assert str(config) == "MyConfig('myconfig', mem_baseaddr=Hex('0xF100'), ram_size=Bytesize('16 KB'))"
    assert dict(config) == {
        "feature": False,
        "ignored": 0,
        "mem_baseaddr": u.Hex("0xF100"),
        "modname": "",
        "name": "myconfig",
        "ram_size": u.Bytesize("16 KB"),
        "rom_size": u.Bytesize("0 bytes"),
    }

    assert config.hash == "5f9de9502e167f99"
    assert config.is_default is False


class OtherConfig(u.AConfig):
    """Other Configuration."""

    ram_size: u.Bytesize = 0x100
    rom_size: u.Bytesize = 0
    feature: bool = False


def test_default_config():
    """Default Configuration."""
    config = OtherConfig()
    assert config.hash == "286f2a5127a1bd37"
    assert config.is_default is True

    config = OtherConfig(name="abc")
    assert config.hash == "619017c580520b19"
    assert config.is_default is False


class ParentConfig(u.AConfig):
    """My Configuration."""

    _hash_excludes: u.ClassVar[set[str]] = {
        "ignored",
    }

    mem_baseaddr: u.Hex
    sub: MyConfig
    subs: tuple[MyConfig, ...]

    ignored: int = 0


def assert_unique_hashes(*configs):
    """Check for unique hashes."""
    hashes = [config.hash for config in configs]
    assert hashes == uniquelist(hashes)


def test_hier_config():
    """Test hierarchical hashes."""
    my0 = MyConfig(mem_baseaddr=0x1000, ram_size=0x2000)
    my1 = MyConfig(mem_baseaddr=0x1000, ram_size=0x2001)
    my2 = MyConfig(mem_baseaddr=0x1000, ram_size=0x2001, ignored=1)
    assert my0.hash != my1.hash
    assert my1.hash == my2.hash

    # ignored in parent
    p0 = ParentConfig(mem_baseaddr=0x1000, sub=my0, subs=(my0, my0))
    p1 = ParentConfig(mem_baseaddr=0x1000, sub=my0, subs=(my0, my0), ignored=1)
    assert p0.hash == p1.hash

    # changed sub
    p2 = ParentConfig(mem_baseaddr=0x1000, sub=my1, subs=(my0, my0))
    assert p0.hash != p2.hash

    # ignored in sub
    p3 = ParentConfig(mem_baseaddr=0x1000, sub=my2, subs=(my0, my0))
    assert p2.hash == p3.hash

    # changed in subs
    assert_unique_hashes(
        ParentConfig(mem_baseaddr=0x1000, sub=my0, subs=(my0, my0)),
        ParentConfig(mem_baseaddr=0x1000, sub=my0, subs=(my1, my0)),
        ParentConfig(mem_baseaddr=0x1000, sub=my0, subs=(my0, my1)),
        ParentConfig(mem_baseaddr=0x1000, sub=my0, subs=(my1, my1)),
    )

    # ignored in subs
    p4 = ParentConfig(mem_baseaddr=0x1000, sub=my0, subs=(my1, my0))
    p5 = ParentConfig(mem_baseaddr=0x1000, sub=my0, subs=(my2, my0))
    assert p4.hash == p5.hash
