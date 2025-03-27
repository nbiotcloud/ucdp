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


class IpMod(u.AMod):
    """IP."""

    tags: u.ClassVar[u.ModTags] = {"ip"}

    def _build(self):
        pass


class SubMod(u.AMod):
    """Sub."""

    has_hiername: bool = False

    tags: u.ClassVar[u.ModTags] = {"ip"}

    def _build(self):
        IpMod(self, "u_ip0")
        IpMod(self, "u_ip1")


class TopMod(u.AMod):
    """Top."""

    tags: u.ClassVar[u.ModTags] = {"ippp"}

    def _build(self):
        SubMod(self, "u_sub0")
        SubMod(self, "u_sub1")


def test_hier():
    """Module Hierarchy."""
    top = TopMod()
    sub0 = top.get_inst("u_sub0")
    sub0ip0 = top.get_inst("u_sub0/u_ip0")
    sub0ip1 = top.get_inst("u_sub0/u_ip1")
    sub1 = top.get_inst("u_sub1")
    sub1ip0 = top.get_inst("u_sub1/u_ip0")
    sub1ip1 = top.get_inst("u_sub1/u_ip1")

    assert top.hiername == "top"
    assert sub0.hiername == "top"
    assert sub0ip0.hiername == "top_ip0"
    assert sub0ip1.hiername == "top_ip1"
    assert sub1.hiername == "top"
    assert sub1ip0.hiername == "top_ip0"
    assert sub1ip1.hiername == "top_ip1"

    assert top.path == (top,)
    assert sub0.path == (top, sub0)
    assert sub0ip0.path == (top, sub0, sub0ip0)
    assert sub0ip1.path == (top, sub0, sub0ip1)
    assert sub1.path == (top, sub1)
    assert sub1ip0.path == (top, sub1, sub1ip0)
    assert sub1ip1.path == (top, sub1, sub1ip1)

    assert top.get_inst(sub0) is sub0
    assert sub0.get_inst(sub0ip0) is sub0ip0

    assert top.parent is None
    assert sub0.parent is top
    assert sub0ip0.parent is sub0
    assert sub0ip1.parent is sub0
    assert sub1.parent is top
    assert sub1ip0.parent is sub1
    assert sub1ip1.parent is sub1

    assert top.parents == ()
    assert sub0.parents == (top,)
    assert sub0ip0.parents == (sub0,)
    assert sub0ip1.parents == (sub0,)
    assert sub1.parents == (top,)
    assert sub1ip0.parents == (sub1,)
    assert sub1ip1.parents == (sub1,)

    assert top.get_inst(sub0) is sub0

    msg = (
        "<tests.test_mods.IpMod(inst='top/u_sub0/u_ip0', libname='tests', modname='ip')> "
        "is not a sub-module of <tests.test_mods.TopMod(inst='top', libname='tests', modname='top')>"
    )
    with raises(ValueError, match=re.escape(msg)):
        top.get_inst(sub0ip0)

    assert sub0.get_inst("..") is top

    msg = (
        "<tests.test_mods.TopMod(inst='top', libname='tests', modname='top')>: "
        "<tests.test_mods.TopMod(inst='top', libname='tests', modname='top')> has no parent."
    )
    with raises(ValueError, match=re.escape(msg)):
        top.get_inst("..")


class ParamMod(u.AMod):
    """Parameterized Module."""

    def _build(self):
        self.add_param(u.IntegerType(), "param_p")
        width_p = u.Param(u.IntegerType(), "width_p")
        self.add_param(width_p)

        self.add_const(u.IntegerType(), "const_a")
        const_b = u.Const(u.IntegerType(), "const_b")
        self.add_const(const_b)


def test_param():
    """Parameter."""
    param_p = u.Param(u.IntegerType(), "param_p")
    width_p = u.Param(u.IntegerType(), "width_p")
    const_a = u.Const(u.IntegerType(), "const_a")
    const_b = u.Const(u.IntegerType(), "const_b")

    mod = ParamMod()
    assert mod.params == u.Idents([param_p, width_p])
    assert mod.namespace == u.Idents([param_p, width_p, const_a, const_b])


class DeclMod(u.AMod):
    """Declarative Struct Module."""

    def _build(self):
        # param_p = self.add_param(u.IntegerType(), "param_p")
        # default_p = self.add_param(u.IntegerType(), "default_p")
        self.add_type_consts(u.UintType(4, default=2), name="one")
        # self.add_type_consts(u.UintType(param_p, default=default_p), name="two")


def test_decl():
    """Declarative."""
    mod = DeclMod()

    assert tuple(repr(item) for item in mod.namespace.iter()) == (
        # "Param(IntegerType(), 'param_p')",
        # "Param(IntegerType(), 'default_p')",
        "Const(DescriptiveStructType(type_=UintType(4, default=2)), 'one')",
        "Const(IntegerType(default=4), 'one_width_p', doc=Doc(title='Width in Bits'))",
        "Const(UintType(4), 'one_min_p', doc=Doc(title='Minimal Value'))",
        "Const(UintType(4, default=15), 'one_max_p', doc=Doc(title='Maximal Value'))",
        "Const(UintType(4, default=2), 'one_default_p', doc=Doc(title='Default Value'))",
        # "Const(DescriptiveStructType(type_=UintType(Param(IntegerType(), 'param_p'))), 'two')",
        # "Const(IntegerType(), 'two_width_p', doc=Doc(title='Width in Bits'))",
        # "Const(UintType(Param(IntegerType(), 'param_p')), 'two_min_p', doc=Doc(title='Minimal Value'))",
        # "Const(UintType(Param(IntegerType(), 'param_p')), 'two_max_p', doc=Doc(title='Maximal Value'))",
        # "Const(UintType(Param(IntegerType(), 'param_p')), 'two_default_p', doc=Doc(title='Default Value'))",
    )


# class DeclFilterMod(u.AMod):
#    """Declarative Struct Module."""

#     def _build(self):
#         self.add_type_consts(u.UintType(4, default=2), name="one", only="*width*")


# def test_decl_filter():
#    """Declarative."""
#     mod = DeclFilterMod()

#     assert tuple(repr(item) for item in mod.namespace.iter()) == ()


class SomeMod(u.AMod):
    """A Module."""

    def _build(self):
        pass


class SomeSomeMod(SomeMod):
    """Module Derived from Another Module."""


def test_basequalnames():
    """Base Qual Names."""
    assert TopMod().basequalnames == ("tests.test_mods",)

    assert SomeMod().basequalnames == ("tests.test_mods",)

    assert SomeSomeMod().basequalnames == ("tests.test_mods",)


def test_modrefs():
    """ModRef."""
    assert TopMod().get_modref() == u.ModRef("tests", "test_mods", modclsname="TopMod")
    assert SomeMod().get_modref() == u.ModRef("tests", "test_mods", modclsname="SomeMod")
    assert SomeSomeMod().get_modref() == u.ModRef("tests", "test_mods", modclsname="SomeSomeMod")


def test_basemodrefs():
    """Base Mod Refs."""
    assert TopMod().get_basemodrefs() == (u.ModRef("tests", "test_mods", modclsname="TopMod"),)
    assert SomeMod().get_basemodrefs() == (u.ModRef("tests", "test_mods", modclsname="SomeMod"),)
    assert SomeSomeMod().get_basemodrefs() == (
        u.ModRef("tests", "test_mods", modclsname="SomeSomeMod"),
        u.ModRef("tests", "test_mods", modclsname="SomeMod"),
    )


class WrongName(u.AMod):
    """Example Module not ending with Mod."""

    def _build(self):
        pass


class NoBuildMod(u.AMod):
    """Example Module without _build method."""


def test_inherit():
    """Inherit Rules."""
    with raises(TypeError):
        u.BaseMod()

    msg = "Name of <class 'tests.test_mods.WrongName'> MUST end with 'Mod'"
    with raises(NameError, match=re.escape(msg)):
        WrongName()

    msg = "_build"
    with raises(TypeError, match=re.escape(msg)):
        NoBuildMod()


class NoNameMod(u.AMod):
    """Test Module with parent but without name."""

    def _build(self):
        TopMod(self)


def test_no_name():
    """Test Module with parent but without name."""
    with raises(u.ValidationError):
        NoNameMod()


class DocMod(u.AMod):
    """Test Module with some documentation."""

    title: str = "title"
    descr: str = "descr"
    comment: str = "comment"

    def _build(self):
        pass


def test_doc():
    """Documentation."""
    assert TopMod().doc == u.Doc()
    assert DocMod().doc == u.Doc(title="title", descr="descr", comment="comment")


def test_lock():
    """Lock."""
    top = TopMod()

    msg = "<tests.test_mods.TopMod(inst='top', libname='tests', modname='top')> is already locked. Cannot lock again."
    with raises(u.LockError, match=re.escape(msg)):
        top.lock()

    msg = "<tests.test_mods.TopMod(inst='top', libname='tests', modname='top')>: Cannot add port 'foo_i'."
    with raises(u.LockError, match=re.escape(msg)):
        top.add_port(u.UintType(7), "foo_i")

    msg = "<tests.test_mods.TopMod(inst='top', libname='tests', modname='top')>: Cannot add signal 'foo_s'."
    with raises(u.LockError, match=re.escape(msg)):
        top.add_signal(u.UintType(7), "foo_s")

    msg = "<tests.test_mods.TopMod(inst='top', libname='tests', modname='top')>: Cannot add parameter 'foo_p'."
    with raises(u.LockError, match=re.escape(msg)):
        top.add_param(u.UintType(7), "foo_p")

    msg = "<tests.test_mods.TopMod(inst='top', libname='tests', modname='top')>: Cannot add constant 'foo_c'."
    with raises(u.LockError, match=re.escape(msg)):
        top.add_const(u.UintType(7), "foo_c")

    msg = "<tests.test_mods.TopMod(inst='top', libname='tests', modname='top')>: Cannot add mux 'one'."
    with raises(u.LockError, match=re.escape(msg)):
        top.add_mux("one")

    msg = "<tests.test_mods.TopMod(inst='top', libname='tests', modname='top')>: Cannot add assign 'src' to 'dest'."
    with raises(u.LockError, match=re.escape(msg)):
        top.assign("dest", "src")

    msg = (
        "<tests.test_mods.TopMod(inst='top', libname='tests', modname='top')>: "
        "Cannot add instance '<tests.test_mods.IpMod(inst='ip', libname='tests', modname='ip')>'."
    )
    with raises(u.LockError, match=re.escape(msg)):
        top.add_inst(IpMod())

    msg = (
        "<tests.test_mods.TopMod(inst='top', libname='tests', modname='top')>: "
        "Cannot connect 'out_o' of'u_sub0' to 'out_o'."
    )
    with raises(u.LockError, match=re.escape(msg)):
        top.set_instcon("u_sub0", "out_o", "out_o")

    msg = "<tests.test_mods.TopMod(inst='top', libname='tests', modname='top')>: Cannot add flipflop 'data_r'."
    with raises(u.LockError, match=re.escape(msg)):
        top.add_flipflop(u.UintType(5), "data_r", "main_clk_i", "main_rst_an_i")


def test_get_inst():
    """Get Instance Errors."""
    top = TopMod()

    top.get_inst("u_sub0")

    msg = (
        "<tests.test_mods.TopMod(inst='top', libname='tests', modname='top')> has no sub-module 'u_foo'. "
        "Known are 'u_sub0' and 'u_sub1'."
    )
    with raises(ValueError, match=re.escape(msg)):
        top.get_inst("u_foo")

    msg = (
        "<tests.test_mods.TopMod(inst='top', libname='tests', modname='top')> has no sub-module 'u_sup0'. "
        "Known are 'u_sub0' and 'u_sub1'."
    )
    with raises(ValueError, match=re.escape(msg)):
        top.get_inst("u_sup0")
