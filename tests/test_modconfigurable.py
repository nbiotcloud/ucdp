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
"""Test Module File Information."""

import re

from pytest import raises

import ucdp as u


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
        SubMod(self, "u_inst0", config=SubConfig())
        SubMod(self, "u_inst1", config=SubConfig(baseaddr=0x1000))
        SubMod(self, "u_inst2", config=SubConfig(baseaddr=0x2000))
        SubMod(self, "u_inst3", config=SubConfig(name="one", baseaddr=0x2000))


def test_sub():
    """Sub."""
    mod = RootMod()
    inst0 = mod.get_inst("u_inst0")
    assert inst0.modname == "sub"
    assert inst0.topmodname == "sub"

    inst1 = mod.get_inst("u_inst1")
    assert inst1.modname == "sub"
    assert inst1.topmodname == "sub"

    inst2 = mod.get_inst("u_inst2")
    assert inst2.modname == "sub_8a5068b003412f45"
    assert inst2.topmodname == "sub"

    inst3 = mod.get_inst("u_inst3")
    assert inst3.modname == "sub_one"
    assert inst3.topmodname == "sub"


class UniqueConfig(u.AConfig):
    """Configuration."""

    baseaddr: u.Hex = 0x1000

    @property
    def unique_name(self):
        """Unique Name."""
        return f"b{self.baseaddr!s}"


class UniqueMod(u.AConfigurableMod):
    """Example Configurable Module."""

    config: UniqueConfig = UniqueConfig()

    def _build(self):
        pass


def test_unique():
    """Unique Name."""
    mod = UniqueMod()
    assert mod.modname == "unique"

    mod = UniqueMod(config=UniqueConfig())
    assert mod.modname == "unique"

    mod = UniqueMod(config=UniqueConfig(baseaddr=0x2000))
    assert mod.modname == "unique_b0x2000"


def test_missing_config():
    """Missing Configuration."""
    with raises(u.ValidationError):
        MyMod()


class DefaultMod(u.AConfigurableMod):
    """Example Configurable Module."""

    config: UniqueConfig

    def _build(self):
        pass

    def get_default_config(self) -> UniqueConfig:
        """Calculate Config."""
        return UniqueConfig(baseaddr=0xCAFE)


def test_default_config():
    """Default Configuration."""
    mod = DefaultMod()
    assert mod.modname == "default"


def test_config_modname():
    """Modname from config."""
    config = MyConfig(modname="forced_name")
    mod = MyMod(config=config)
    assert mod.modname == "forced_name"
