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
"""Test Module File Information."""

import re

import ucdp as u
from pytest import raises


class MyConfig(u.AConfig):
    """A Configuration."""

    feature: bool = False
    size: int = 0


class MyMod(u.AConfigurableMod):
    """Example Configurable Module."""

    config: MyConfig

    def _build(self):
        config = self.config
        self.add_port(u.ClkRstAnType(), "main_i")
        self.add_port(u.UintType(8), "data_i")
        self.add_port(u.UintType(8), "data_o")
        if config.feature:
            self.add_port(u.UintType(8), "feat_i")
            self.add_port(u.UintType(8), "feat_o")


class MyOtherMod(MyMod):
    """Configurable Module with Other Config."""

    config: MyConfig = MyConfig(feature=True)


class AnotherMod(MyMod):
    """Configurable Module with Other Config."""

    config: MyConfig = MyConfig("foo")


def test_noconfig():
    """Configurable Module."""
    with raises(ValueError):
        MyMod()


def test_config():
    """Configurable Module."""
    mod = MyMod(config=MyConfig())
    assert mod.modname == "my"
    assert mod.topmodname == "my"

    config = mod.config
    assert config == MyConfig("")
    assert config.feature is False
    assert config.size == 0


class TopMod(u.AMod):
    """Instance without Config."""

    def _build(self) -> None:
        MyOtherMod(self, "u_inst")


def test_no_inst_config():
    """Config is required on Instance Creation."""
    msg = "'config' is required if 'parent' is given"
    with raises(ValueError, match=re.escape(msg)):
        TopMod()


def test_no_default_config():
    """Configurable Module."""
    mod = MyMod(config=MyConfig("name"))
    assert mod.modname == "my_name"
    assert mod.topmodname == "my"

    config = mod.config
    assert config == MyConfig("name")
    assert config.feature is False
    assert config.size == 0


def test_other():
    """Other Configurable Module."""
    mod = MyOtherMod()
    assert mod.modname == "my_other"
    assert mod.topmodname == "my"

    config = mod.config
    assert config == MyConfig(feature=True)
    assert config.feature is True
    assert config.size == 0


def test_another():
    """Another Configurable Module."""
    mod = AnotherMod()
    assert mod.modname == "another_foo"
    assert mod.topmodname == "my"


class SubConfig(u.AConfig):
    """Sub Configuration."""

    baseaddr: u.Hex = 0x1000


class SubMod(u.AConfigurableMod):
    """Sub Module."""

    def _build(self):
        pass


class RootMod(u.AMod):
    """Parent Module."""

    def _build(self):
        SubMod(self, "u_inst", config=SubConfig())


def test_sub():
    """Sub."""
    mod = RootMod()
    sub = mod.get_inst("u_inst")
    assert sub.modname == "inst"
    assert sub.topmodname == "sub"
