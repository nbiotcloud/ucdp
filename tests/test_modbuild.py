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
"""Test Module Building."""
import ucdp

TRACKER = []


class MyMod(ucdp.AMod):
    """MyMod."""

    def _build(self):
        TRACKER.append(f"{self}")

    def _buildpost(self):
        TRACKER.append(f"{self}post")


class MyImportedMod(ucdp.AImportedMod):
    """MyImportedMod."""

    def _build(self):
        TRACKER.append(f"{self}")

    def _buildpost(self):
        TRACKER.append(f"{self}post")


class MyTailoredMod(ucdp.ATailoredMod):
    """MyTailoredMod."""

    def _build(self):
        TRACKER.append(f"{self}")

    def _builddep(self):
        TRACKER.append(f"{self}dep")

    def _buildpost(self):
        TRACKER.append(f"{self}post")


class MyCoreMod(ucdp.CoreMod):
    """MyCoreMod."""

    def _build(self):
        TRACKER.append(f"{self}")

    def _buildpost(self):
        TRACKER.append(f"{self}post")


class MyConfigurableMod(ucdp.AConfigurableMod):
    """MyConfigurableMod."""

    def _build(self):
        TRACKER.append(f"{self}")

    def _buildpost(self):
        TRACKER.append(f"{self}post")


def test_flat():
    """Flat Hierarchy."""

    TRACKER.clear()

    mods = [
        MyMod(),
        MyImportedMod(),
        MyTailoredMod(),
        MyConfigurableMod(config=MyConfig("configname")),
    ]
    coremod = MyCoreMod(modname="mycore", libname="mylib")
    assert TRACKER == [
        "MyMod('my')",
        "MyMod('my')post",
        "MyImportedMod('my_imported')",
        "MyImportedMod('my_imported')post",
        "MyTailoredMod('my_tailored')",
        "MyTailoredMod('my_tailored')dep",
        "MyTailoredMod('my_tailored')post",
        "MyConfigurableMod('my_configurable', config=MyConfig('configname'))",
        "MyConfigurableMod('my_configurable', config=MyConfig('configname'))post",
    ]
    locks = [mod.is_locked for mod in mods]
    assert all(locks)
    assert not coremod.is_locked


class MyLeafMod(ucdp.AMod):
    """MyLeafMod."""

    def _build(self):
        TRACKER.append(f"{self}")

    def _buildpost(self):
        TRACKER.append(f"{self}post")


class MyImpLeafMod(ucdp.AImportedMod):
    """MyImpLeafMod."""

    def _build(self):
        TRACKER.append(f"{self}")

    def _buildpost(self):
        TRACKER.append(f"{self}post")


class MyTailored0Mod(ucdp.ATailoredMod):
    """MyTailored0Mod."""

    def _build(self):
        TRACKER.append(f"{self}")
        MyLeafMod(self, "u_leaf0")
        MyImpLeafMod(self, "u_imp0")

    def _builddep(self):
        TRACKER.append(f"{self}dep")
        MyLeafMod(self, "u_leaf0_dep")
        MyImpLeafMod(self, "u_imp0_dep")

    def _buildpost(self):
        TRACKER.append(f"{self}post")


class MyTailored1Mod(ucdp.ATailoredMod):
    """MyTailored1Mod."""

    def _build(self):
        TRACKER.append(f"{self}")
        MyLeafMod(self, "u_leaf0")
        MyImpLeafMod(self, "u_imp0")
        MyTailored0Mod(self, "u_tail0")
        ucdp.CoreMod(self, "u_core0")
        ucdp.CoreMod(self, "u_core1")

    def _builddep(self):
        TRACKER.append(f"{self}dep")
        MyLeafMod(self, "u_leaf0_dep")
        MyImpLeafMod(self, "u_imp0_dep")
        MyTailored0Mod(self, "u_tail0_dep")
        ucdp.CoreMod(self, "u_core0_dep")
        ucdp.CoreMod(self, "u_core1_dep")

    def _buildpost(self):
        TRACKER.append(f"{self}post")


class MyTailored2Mod(ucdp.ATailoredMod):
    """MyTailored2Mod."""

    def _build(self):
        TRACKER.append(f"{self}")
        MyLeafMod(self, "u_leaf0")
        MyImpLeafMod(self, "u_imp0")
        MyTailored0Mod(self, "u_tail0")
        MyTailored1Mod(self, "u_tail1")

    def _builddep(self):
        TRACKER.append(f"{self}dep")
        MyLeafMod(self, "u_leaf0_dep")
        MyImpLeafMod(self, "u_imp0_dep")
        MyTailored0Mod(self, "u_tail0_dep")
        MyTailored1Mod(self, "u_tail1_dep")

    def _buildpost(self):
        TRACKER.append(f"{self}post")


class MyTop0Mod(ucdp.AMod):
    """MyTop0Mod."""

    def _build(self):
        TRACKER.append(f"{self}")
        MyLeafMod(self, "u_leaf0")
        MyImpLeafMod(self, "u_imp0")
        MyTailored0Mod(self, "u_tail0")
        ucdp.CoreMod(self, "u_core0")
        ucdp.CoreMod(self, "u_core1")

    def _buildpost(self):
        TRACKER.append(f"{self}post")


class MyTop1Mod(ucdp.AMod):
    """MyTop1Mod."""

    def _build(self):
        TRACKER.append(f"{self}")
        MyLeafMod(self, "u_leaf1")
        MyImpLeafMod(self, "u_imp1")
        MyTailored1Mod(self, "u_tail1")

    def _buildpost(self):
        TRACKER.append(f"{self}post")


class MyTop2Mod(ucdp.AConfigurableMod):
    """MyTop2Mod."""

    def _build(self):
        TRACKER.append(f"{self}")
        assert self.config
        MyLeafMod(self, "u_leaf2")
        MyImpLeafMod(self, "u_imp2")
        MyTailored2Mod(self, "u_tail2")

    def _buildpost(self):
        TRACKER.append(f"{self}post")


class MyConfig(ucdp.AConfig):
    """MyConfig."""


def test_hier0():
    """Real Hierarchy."""
    TRACKER.clear()
    mytop0 = MyTop0Mod()
    assert all(mod.is_locked for mod in ucdp.ModPreIter(mytop0))
    assert TRACKER == [
        "MyTop0Mod('my_top0')",
        "MyLeafMod('my_top0/u_leaf0')",
        "MyLeafMod('my_top0/u_leaf0')post",
        "MyImpLeafMod('my_top0/u_imp0')",
        "MyImpLeafMod('my_top0/u_imp0')post",
        "MyTailored0Mod('my_top0/u_tail0')",
        "MyLeafMod('my_top0/u_tail0/u_leaf0')",
        "MyLeafMod('my_top0/u_tail0/u_leaf0')post",
        "MyImpLeafMod('my_top0/u_tail0/u_imp0')",
        "MyImpLeafMod('my_top0/u_tail0/u_imp0')post",
        "MyTailored0Mod('my_top0/u_tail0')dep",
        "MyLeafMod('my_top0/u_tail0/u_leaf0_dep')",
        "MyLeafMod('my_top0/u_tail0/u_leaf0_dep')post",
        "MyImpLeafMod('my_top0/u_tail0/u_imp0_dep')",
        "MyImpLeafMod('my_top0/u_tail0/u_imp0_dep')post",
        "MyTailored0Mod('my_top0/u_tail0')post",
        "MyTop0Mod('my_top0')post",
    ]
    assert [mod.pathstr for mod in ucdp.ModPreIter(mytop0)] == [
        "my_top0",
        "my_top0/u_leaf0",
        "my_top0/u_imp0",
        "my_top0/u_tail0",
        "my_top0/u_tail0/u_leaf0",
        "my_top0/u_tail0/u_imp0",
        "my_top0/u_tail0/u_leaf0_dep",
        "my_top0/u_tail0/u_imp0_dep",
        "my_top0/u_core0",
        "my_top0/u_core1",
    ]
    assert [mod.hiername for mod in ucdp.ModPreIter(mytop0)] == [
        "my_top0",
        "my_top0_leaf0",
        "my_top0_imp0",
        "my_top0_tail0",
        "my_top0_tail0_leaf0",
        "my_top0_tail0_imp0",
        "my_top0_tail0_leaf0_dep",
        "my_top0_tail0_imp0_dep",
        "my_top0_core0",
        "my_top0_core1",
    ]


def test_hier1():
    """Real Hierarchy."""
    TRACKER.clear()
    mytop1 = MyTop1Mod()
    assert all(mod.is_locked for mod in ucdp.ModPreIter(mytop1))
    assert TRACKER == [
        "MyTop1Mod('my_top1')",
        "MyLeafMod('my_top1/u_leaf1')",
        "MyLeafMod('my_top1/u_leaf1')post",
        "MyImpLeafMod('my_top1/u_imp1')",
        "MyImpLeafMod('my_top1/u_imp1')post",
        "MyTailored1Mod('my_top1/u_tail1')",
        "MyLeafMod('my_top1/u_tail1/u_leaf0')",
        "MyLeafMod('my_top1/u_tail1/u_leaf0')post",
        "MyImpLeafMod('my_top1/u_tail1/u_imp0')",
        "MyImpLeafMod('my_top1/u_tail1/u_imp0')post",
        "MyTailored0Mod('my_top1/u_tail1/u_tail0')",
        "MyLeafMod('my_top1/u_tail1/u_tail0/u_leaf0')",
        "MyLeafMod('my_top1/u_tail1/u_tail0/u_leaf0')post",
        "MyImpLeafMod('my_top1/u_tail1/u_tail0/u_imp0')",
        "MyImpLeafMod('my_top1/u_tail1/u_tail0/u_imp0')post",
        "MyTailored1Mod('my_top1/u_tail1')dep",
        "MyLeafMod('my_top1/u_tail1/u_leaf0_dep')",
        "MyLeafMod('my_top1/u_tail1/u_leaf0_dep')post",
        "MyImpLeafMod('my_top1/u_tail1/u_imp0_dep')",
        "MyImpLeafMod('my_top1/u_tail1/u_imp0_dep')post",
        "MyTailored0Mod('my_top1/u_tail1/u_tail0_dep')",
        "MyLeafMod('my_top1/u_tail1/u_tail0_dep/u_leaf0')",
        "MyLeafMod('my_top1/u_tail1/u_tail0_dep/u_leaf0')post",
        "MyImpLeafMod('my_top1/u_tail1/u_tail0_dep/u_imp0')",
        "MyImpLeafMod('my_top1/u_tail1/u_tail0_dep/u_imp0')post",
        "MyTailored0Mod('my_top1/u_tail1/u_tail0')dep",
        "MyLeafMod('my_top1/u_tail1/u_tail0/u_leaf0_dep')",
        "MyLeafMod('my_top1/u_tail1/u_tail0/u_leaf0_dep')post",
        "MyImpLeafMod('my_top1/u_tail1/u_tail0/u_imp0_dep')",
        "MyImpLeafMod('my_top1/u_tail1/u_tail0/u_imp0_dep')post",
        "MyTailored0Mod('my_top1/u_tail1/u_tail0_dep')dep",
        "MyLeafMod('my_top1/u_tail1/u_tail0_dep/u_leaf0_dep')",
        "MyLeafMod('my_top1/u_tail1/u_tail0_dep/u_leaf0_dep')post",
        "MyImpLeafMod('my_top1/u_tail1/u_tail0_dep/u_imp0_dep')",
        "MyImpLeafMod('my_top1/u_tail1/u_tail0_dep/u_imp0_dep')post",
        "MyTailored0Mod('my_top1/u_tail1/u_tail0')post",
        "MyTailored0Mod('my_top1/u_tail1/u_tail0_dep')post",
        "MyTailored1Mod('my_top1/u_tail1')post",
        "MyTop1Mod('my_top1')post",
    ]
    assert [mod.pathstr for mod in ucdp.ModPreIter(mytop1)] == [
        "my_top1",
        "my_top1/u_leaf1",
        "my_top1/u_imp1",
        "my_top1/u_tail1",
        "my_top1/u_tail1/u_leaf0",
        "my_top1/u_tail1/u_imp0",
        "my_top1/u_tail1/u_tail0",
        "my_top1/u_tail1/u_tail0/u_leaf0",
        "my_top1/u_tail1/u_tail0/u_imp0",
        "my_top1/u_tail1/u_tail0/u_leaf0_dep",
        "my_top1/u_tail1/u_tail0/u_imp0_dep",
        "my_top1/u_tail1/u_core0",
        "my_top1/u_tail1/u_core1",
        "my_top1/u_tail1/u_leaf0_dep",
        "my_top1/u_tail1/u_imp0_dep",
        "my_top1/u_tail1/u_tail0_dep",
        "my_top1/u_tail1/u_tail0_dep/u_leaf0",
        "my_top1/u_tail1/u_tail0_dep/u_imp0",
        "my_top1/u_tail1/u_tail0_dep/u_leaf0_dep",
        "my_top1/u_tail1/u_tail0_dep/u_imp0_dep",
        "my_top1/u_tail1/u_core0_dep",
        "my_top1/u_tail1/u_core1_dep",
    ]
    assert [mod.hiername for mod in ucdp.ModPreIter(mytop1)] == [
        "my_top1",
        "my_top1_leaf1",
        "my_top1_imp1",
        "my_top1_tail1",
        "my_top1_tail1_leaf0",
        "my_top1_tail1_imp0",
        "my_top1_tail1_tail0",
        "my_top1_tail1_tail0_leaf0",
        "my_top1_tail1_tail0_imp0",
        "my_top1_tail1_tail0_leaf0_dep",
        "my_top1_tail1_tail0_imp0_dep",
        "my_top1_tail1_core0",
        "my_top1_tail1_core1",
        "my_top1_tail1_leaf0_dep",
        "my_top1_tail1_imp0_dep",
        "my_top1_tail1_tail0_dep",
        "my_top1_tail1_tail0_dep_leaf0",
        "my_top1_tail1_tail0_dep_imp0",
        "my_top1_tail1_tail0_dep_leaf0_dep",
        "my_top1_tail1_tail0_dep_imp0_dep",
        "my_top1_tail1_core0_dep",
        "my_top1_tail1_core1_dep",
    ]


def test_hier2():
    """Real Hierarchy."""
    TRACKER.clear()
    mytop2 = MyTop2Mod(config=MyConfig("configname"))
    assert all(mod.is_locked for mod in ucdp.ModPreIter(mytop2))
    assert TRACKER == [
        "MyTop2Mod('my_top2', config=MyConfig('configname'))",
        "MyLeafMod('my_top2/u_leaf2')",
        "MyLeafMod('my_top2/u_leaf2')post",
        "MyImpLeafMod('my_top2/u_imp2')",
        "MyImpLeafMod('my_top2/u_imp2')post",
        "MyTailored2Mod('my_top2/u_tail2')",
        "MyLeafMod('my_top2/u_tail2/u_leaf0')",
        "MyLeafMod('my_top2/u_tail2/u_leaf0')post",
        "MyImpLeafMod('my_top2/u_tail2/u_imp0')",
        "MyImpLeafMod('my_top2/u_tail2/u_imp0')post",
        "MyTailored0Mod('my_top2/u_tail2/u_tail0')",
        "MyLeafMod('my_top2/u_tail2/u_tail0/u_leaf0')",
        "MyLeafMod('my_top2/u_tail2/u_tail0/u_leaf0')post",
        "MyImpLeafMod('my_top2/u_tail2/u_tail0/u_imp0')",
        "MyImpLeafMod('my_top2/u_tail2/u_tail0/u_imp0')post",
        "MyTailored1Mod('my_top2/u_tail2/u_tail1')",
        "MyLeafMod('my_top2/u_tail2/u_tail1/u_leaf0')",
        "MyLeafMod('my_top2/u_tail2/u_tail1/u_leaf0')post",
        "MyImpLeafMod('my_top2/u_tail2/u_tail1/u_imp0')",
        "MyImpLeafMod('my_top2/u_tail2/u_tail1/u_imp0')post",
        "MyTailored0Mod('my_top2/u_tail2/u_tail1/u_tail0')",
        "MyLeafMod('my_top2/u_tail2/u_tail1/u_tail0/u_leaf0')",
        "MyLeafMod('my_top2/u_tail2/u_tail1/u_tail0/u_leaf0')post",
        "MyImpLeafMod('my_top2/u_tail2/u_tail1/u_tail0/u_imp0')",
        "MyImpLeafMod('my_top2/u_tail2/u_tail1/u_tail0/u_imp0')post",
        "MyTailored2Mod('my_top2/u_tail2')dep",
        "MyLeafMod('my_top2/u_tail2/u_leaf0_dep')",
        "MyLeafMod('my_top2/u_tail2/u_leaf0_dep')post",
        "MyImpLeafMod('my_top2/u_tail2/u_imp0_dep')",
        "MyImpLeafMod('my_top2/u_tail2/u_imp0_dep')post",
        "MyTailored0Mod('my_top2/u_tail2/u_tail0_dep')",
        "MyLeafMod('my_top2/u_tail2/u_tail0_dep/u_leaf0')",
        "MyLeafMod('my_top2/u_tail2/u_tail0_dep/u_leaf0')post",
        "MyImpLeafMod('my_top2/u_tail2/u_tail0_dep/u_imp0')",
        "MyImpLeafMod('my_top2/u_tail2/u_tail0_dep/u_imp0')post",
        "MyTailored1Mod('my_top2/u_tail2/u_tail1_dep')",
        "MyLeafMod('my_top2/u_tail2/u_tail1_dep/u_leaf0')",
        "MyLeafMod('my_top2/u_tail2/u_tail1_dep/u_leaf0')post",
        "MyImpLeafMod('my_top2/u_tail2/u_tail1_dep/u_imp0')",
        "MyImpLeafMod('my_top2/u_tail2/u_tail1_dep/u_imp0')post",
        "MyTailored0Mod('my_top2/u_tail2/u_tail1_dep/u_tail0')",
        "MyLeafMod('my_top2/u_tail2/u_tail1_dep/u_tail0/u_leaf0')",
        "MyLeafMod('my_top2/u_tail2/u_tail1_dep/u_tail0/u_leaf0')post",
        "MyImpLeafMod('my_top2/u_tail2/u_tail1_dep/u_tail0/u_imp0')",
        "MyImpLeafMod('my_top2/u_tail2/u_tail1_dep/u_tail0/u_imp0')post",
        "MyTailored0Mod('my_top2/u_tail2/u_tail0')dep",
        "MyLeafMod('my_top2/u_tail2/u_tail0/u_leaf0_dep')",
        "MyLeafMod('my_top2/u_tail2/u_tail0/u_leaf0_dep')post",
        "MyImpLeafMod('my_top2/u_tail2/u_tail0/u_imp0_dep')",
        "MyImpLeafMod('my_top2/u_tail2/u_tail0/u_imp0_dep')post",
        "MyTailored1Mod('my_top2/u_tail2/u_tail1')dep",
        "MyLeafMod('my_top2/u_tail2/u_tail1/u_leaf0_dep')",
        "MyLeafMod('my_top2/u_tail2/u_tail1/u_leaf0_dep')post",
        "MyImpLeafMod('my_top2/u_tail2/u_tail1/u_imp0_dep')",
        "MyImpLeafMod('my_top2/u_tail2/u_tail1/u_imp0_dep')post",
        "MyTailored0Mod('my_top2/u_tail2/u_tail1/u_tail0_dep')",
        "MyLeafMod('my_top2/u_tail2/u_tail1/u_tail0_dep/u_leaf0')",
        "MyLeafMod('my_top2/u_tail2/u_tail1/u_tail0_dep/u_leaf0')post",
        "MyImpLeafMod('my_top2/u_tail2/u_tail1/u_tail0_dep/u_imp0')",
        "MyImpLeafMod('my_top2/u_tail2/u_tail1/u_tail0_dep/u_imp0')post",
        "MyTailored0Mod('my_top2/u_tail2/u_tail1/u_tail0')dep",
        "MyLeafMod('my_top2/u_tail2/u_tail1/u_tail0/u_leaf0_dep')",
        "MyLeafMod('my_top2/u_tail2/u_tail1/u_tail0/u_leaf0_dep')post",
        "MyImpLeafMod('my_top2/u_tail2/u_tail1/u_tail0/u_imp0_dep')",
        "MyImpLeafMod('my_top2/u_tail2/u_tail1/u_tail0/u_imp0_dep')post",
        "MyTailored0Mod('my_top2/u_tail2/u_tail1/u_tail0_dep')dep",
        "MyLeafMod('my_top2/u_tail2/u_tail1/u_tail0_dep/u_leaf0_dep')",
        "MyLeafMod('my_top2/u_tail2/u_tail1/u_tail0_dep/u_leaf0_dep')post",
        "MyImpLeafMod('my_top2/u_tail2/u_tail1/u_tail0_dep/u_imp0_dep')",
        "MyImpLeafMod('my_top2/u_tail2/u_tail1/u_tail0_dep/u_imp0_dep')post",
        "MyTailored0Mod('my_top2/u_tail2/u_tail0_dep')dep",
        "MyLeafMod('my_top2/u_tail2/u_tail0_dep/u_leaf0_dep')",
        "MyLeafMod('my_top2/u_tail2/u_tail0_dep/u_leaf0_dep')post",
        "MyImpLeafMod('my_top2/u_tail2/u_tail0_dep/u_imp0_dep')",
        "MyImpLeafMod('my_top2/u_tail2/u_tail0_dep/u_imp0_dep')post",
        "MyTailored1Mod('my_top2/u_tail2/u_tail1_dep')dep",
        "MyLeafMod('my_top2/u_tail2/u_tail1_dep/u_leaf0_dep')",
        "MyLeafMod('my_top2/u_tail2/u_tail1_dep/u_leaf0_dep')post",
        "MyImpLeafMod('my_top2/u_tail2/u_tail1_dep/u_imp0_dep')",
        "MyImpLeafMod('my_top2/u_tail2/u_tail1_dep/u_imp0_dep')post",
        "MyTailored0Mod('my_top2/u_tail2/u_tail1_dep/u_tail0_dep')",
        "MyLeafMod('my_top2/u_tail2/u_tail1_dep/u_tail0_dep/u_leaf0')",
        "MyLeafMod('my_top2/u_tail2/u_tail1_dep/u_tail0_dep/u_leaf0')post",
        "MyImpLeafMod('my_top2/u_tail2/u_tail1_dep/u_tail0_dep/u_imp0')",
        "MyImpLeafMod('my_top2/u_tail2/u_tail1_dep/u_tail0_dep/u_imp0')post",
        "MyTailored0Mod('my_top2/u_tail2/u_tail1_dep/u_tail0')dep",
        "MyLeafMod('my_top2/u_tail2/u_tail1_dep/u_tail0/u_leaf0_dep')",
        "MyLeafMod('my_top2/u_tail2/u_tail1_dep/u_tail0/u_leaf0_dep')post",
        "MyImpLeafMod('my_top2/u_tail2/u_tail1_dep/u_tail0/u_imp0_dep')",
        "MyImpLeafMod('my_top2/u_tail2/u_tail1_dep/u_tail0/u_imp0_dep')post",
        "MyTailored0Mod('my_top2/u_tail2/u_tail1_dep/u_tail0_dep')dep",
        "MyLeafMod('my_top2/u_tail2/u_tail1_dep/u_tail0_dep/u_leaf0_dep')",
        "MyLeafMod('my_top2/u_tail2/u_tail1_dep/u_tail0_dep/u_leaf0_dep')post",
        "MyImpLeafMod('my_top2/u_tail2/u_tail1_dep/u_tail0_dep/u_imp0_dep')",
        "MyImpLeafMod('my_top2/u_tail2/u_tail1_dep/u_tail0_dep/u_imp0_dep')post",
        "MyTailored0Mod('my_top2/u_tail2/u_tail0')post",
        "MyTailored0Mod('my_top2/u_tail2/u_tail1/u_tail0')post",
        "MyTailored0Mod('my_top2/u_tail2/u_tail1/u_tail0_dep')post",
        "MyTailored1Mod('my_top2/u_tail2/u_tail1')post",
        "MyTailored0Mod('my_top2/u_tail2/u_tail0_dep')post",
        "MyTailored0Mod('my_top2/u_tail2/u_tail1_dep/u_tail0')post",
        "MyTailored0Mod('my_top2/u_tail2/u_tail1_dep/u_tail0_dep')post",
        "MyTailored1Mod('my_top2/u_tail2/u_tail1_dep')post",
        "MyTailored2Mod('my_top2/u_tail2')post",
        "MyTop2Mod('my_top2', config=MyConfig('configname'))post",
    ]
    assert [mod.pathstr for mod in ucdp.ModPreIter(mytop2)] == [
        "my_top2",
        "my_top2/u_leaf2",
        "my_top2/u_imp2",
        "my_top2/u_tail2",
        "my_top2/u_tail2/u_leaf0",
        "my_top2/u_tail2/u_imp0",
        "my_top2/u_tail2/u_tail0",
        "my_top2/u_tail2/u_tail0/u_leaf0",
        "my_top2/u_tail2/u_tail0/u_imp0",
        "my_top2/u_tail2/u_tail0/u_leaf0_dep",
        "my_top2/u_tail2/u_tail0/u_imp0_dep",
        "my_top2/u_tail2/u_tail1",
        "my_top2/u_tail2/u_tail1/u_leaf0",
        "my_top2/u_tail2/u_tail1/u_imp0",
        "my_top2/u_tail2/u_tail1/u_tail0",
        "my_top2/u_tail2/u_tail1/u_tail0/u_leaf0",
        "my_top2/u_tail2/u_tail1/u_tail0/u_imp0",
        "my_top2/u_tail2/u_tail1/u_tail0/u_leaf0_dep",
        "my_top2/u_tail2/u_tail1/u_tail0/u_imp0_dep",
        "my_top2/u_tail2/u_tail1/u_core0",
        "my_top2/u_tail2/u_tail1/u_core1",
        "my_top2/u_tail2/u_tail1/u_leaf0_dep",
        "my_top2/u_tail2/u_tail1/u_imp0_dep",
        "my_top2/u_tail2/u_tail1/u_tail0_dep",
        "my_top2/u_tail2/u_tail1/u_tail0_dep/u_leaf0",
        "my_top2/u_tail2/u_tail1/u_tail0_dep/u_imp0",
        "my_top2/u_tail2/u_tail1/u_tail0_dep/u_leaf0_dep",
        "my_top2/u_tail2/u_tail1/u_tail0_dep/u_imp0_dep",
        "my_top2/u_tail2/u_tail1/u_core0_dep",
        "my_top2/u_tail2/u_tail1/u_core1_dep",
        "my_top2/u_tail2/u_leaf0_dep",
        "my_top2/u_tail2/u_imp0_dep",
        "my_top2/u_tail2/u_tail0_dep",
        "my_top2/u_tail2/u_tail0_dep/u_leaf0",
        "my_top2/u_tail2/u_tail0_dep/u_imp0",
        "my_top2/u_tail2/u_tail0_dep/u_leaf0_dep",
        "my_top2/u_tail2/u_tail0_dep/u_imp0_dep",
        "my_top2/u_tail2/u_tail1_dep",
        "my_top2/u_tail2/u_tail1_dep/u_leaf0",
        "my_top2/u_tail2/u_tail1_dep/u_imp0",
        "my_top2/u_tail2/u_tail1_dep/u_tail0",
        "my_top2/u_tail2/u_tail1_dep/u_tail0/u_leaf0",
        "my_top2/u_tail2/u_tail1_dep/u_tail0/u_imp0",
        "my_top2/u_tail2/u_tail1_dep/u_tail0/u_leaf0_dep",
        "my_top2/u_tail2/u_tail1_dep/u_tail0/u_imp0_dep",
        "my_top2/u_tail2/u_tail1_dep/u_core0",
        "my_top2/u_tail2/u_tail1_dep/u_core1",
        "my_top2/u_tail2/u_tail1_dep/u_leaf0_dep",
        "my_top2/u_tail2/u_tail1_dep/u_imp0_dep",
        "my_top2/u_tail2/u_tail1_dep/u_tail0_dep",
        "my_top2/u_tail2/u_tail1_dep/u_tail0_dep/u_leaf0",
        "my_top2/u_tail2/u_tail1_dep/u_tail0_dep/u_imp0",
        "my_top2/u_tail2/u_tail1_dep/u_tail0_dep/u_leaf0_dep",
        "my_top2/u_tail2/u_tail1_dep/u_tail0_dep/u_imp0_dep",
        "my_top2/u_tail2/u_tail1_dep/u_core0_dep",
        "my_top2/u_tail2/u_tail1_dep/u_core1_dep",
    ]
    assert [mod.hiername for mod in ucdp.ModPreIter(mytop2)] == [
        "my_top2",
        "my_top2_leaf2",
        "my_top2_imp2",
        "my_top2_tail2",
        "my_top2_tail2_leaf0",
        "my_top2_tail2_imp0",
        "my_top2_tail2_tail0",
        "my_top2_tail2_tail0_leaf0",
        "my_top2_tail2_tail0_imp0",
        "my_top2_tail2_tail0_leaf0_dep",
        "my_top2_tail2_tail0_imp0_dep",
        "my_top2_tail2_tail1",
        "my_top2_tail2_tail1_leaf0",
        "my_top2_tail2_tail1_imp0",
        "my_top2_tail2_tail1_tail0",
        "my_top2_tail2_tail1_tail0_leaf0",
        "my_top2_tail2_tail1_tail0_imp0",
        "my_top2_tail2_tail1_tail0_leaf0_dep",
        "my_top2_tail2_tail1_tail0_imp0_dep",
        "my_top2_tail2_tail1_core0",
        "my_top2_tail2_tail1_core1",
        "my_top2_tail2_tail1_leaf0_dep",
        "my_top2_tail2_tail1_imp0_dep",
        "my_top2_tail2_tail1_tail0_dep",
        "my_top2_tail2_tail1_tail0_dep_leaf0",
        "my_top2_tail2_tail1_tail0_dep_imp0",
        "my_top2_tail2_tail1_tail0_dep_leaf0_dep",
        "my_top2_tail2_tail1_tail0_dep_imp0_dep",
        "my_top2_tail2_tail1_core0_dep",
        "my_top2_tail2_tail1_core1_dep",
        "my_top2_tail2_leaf0_dep",
        "my_top2_tail2_imp0_dep",
        "my_top2_tail2_tail0_dep",
        "my_top2_tail2_tail0_dep_leaf0",
        "my_top2_tail2_tail0_dep_imp0",
        "my_top2_tail2_tail0_dep_leaf0_dep",
        "my_top2_tail2_tail0_dep_imp0_dep",
        "my_top2_tail2_tail1_dep",
        "my_top2_tail2_tail1_dep_leaf0",
        "my_top2_tail2_tail1_dep_imp0",
        "my_top2_tail2_tail1_dep_tail0",
        "my_top2_tail2_tail1_dep_tail0_leaf0",
        "my_top2_tail2_tail1_dep_tail0_imp0",
        "my_top2_tail2_tail1_dep_tail0_leaf0_dep",
        "my_top2_tail2_tail1_dep_tail0_imp0_dep",
        "my_top2_tail2_tail1_dep_core0",
        "my_top2_tail2_tail1_dep_core1",
        "my_top2_tail2_tail1_dep_leaf0_dep",
        "my_top2_tail2_tail1_dep_imp0_dep",
        "my_top2_tail2_tail1_dep_tail0_dep",
        "my_top2_tail2_tail1_dep_tail0_dep_leaf0",
        "my_top2_tail2_tail1_dep_tail0_dep_imp0",
        "my_top2_tail2_tail1_dep_tail0_dep_leaf0_dep",
        "my_top2_tail2_tail1_dep_tail0_dep_imp0_dep",
        "my_top2_tail2_tail1_dep_core0_dep",
        "my_top2_tail2_tail1_dep_core1_dep",
    ]
