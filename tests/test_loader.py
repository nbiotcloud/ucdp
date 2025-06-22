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
"""Test Loader and Top."""

import re
from pathlib import Path

from caseconverter import pascalcase
from contextlib_chdir import chdir
from pytest import raises

import ucdp as u


def test_load_simple(example_simple):
    """Simple Module."""
    top = u.load("glbl_lib.clk_gate", paths=None)
    assert top.ref == u.TopModRef(u.ModRef("glbl_lib", "clk_gate"))
    assert top.mod.libname == "glbl_lib"
    assert top.mod.modname == "clk_gate"
    assert [str(mod) for mod in top.iter()] == [
        "<glbl_lib.clk_gate.ClkGateMod(inst='clk_gate', libname='glbl_lib', modname='clk_gate')>"
    ]
    assert [str(mod) for mod in top.get_mods()] == [
        "<glbl_lib.clk_gate.ClkGateMod(inst='clk_gate', libname='glbl_lib', modname='clk_gate')>"
    ]
    assert (
        str(top.get_mod("glbl_lib.clk_gate")) == "<glbl_lib.clk_gate.ClkGateMod(inst='clk_gate', "
        "libname='glbl_lib', modname='clk_gate')>"
    )

    retop = u.Top.from_mod(top.mod)
    assert retop.mod == top.mod
    assert retop.ref == u.TopModRef(u.ModRef("glbl_lib", "clk_gate", modclsname="ClkGateMod"))


def test_load_non_mod(example_bad):
    """Load Non Module."""
    with raises(ValueError) as exc:
        u.load("glbl_bad_lib.regf.MyMod", paths=None)
    assert str(exc.value) == "<class 'glbl_bad_lib.regf.MyMod'> is not a module aka child of <class ucdp.BaseMod>."


def test_load_non_top(example_simple):
    """Load Non-Top Module."""
    msg = "uart_lib.uart.UartCoreMod is not a top module as it bases on <class 'ucdp.modcore.ACoreMod'>"
    with raises(ValueError, match=re.escape(msg)):
        u.load("uart_lib.uart.UartCoreMod")


def test_load_complex(example_simple):
    """Complexer Module."""
    top = u.load("uart_lib.uart", paths=None)
    assert top.ref == u.TopModRef(u.ModRef("uart_lib", "uart"))
    assert top.mod.libname == "uart_lib"
    assert top.mod.modname == "uart"
    assert [repr(mod) for mod in top.iter()] == [
        "<uart_lib.uart.UartMod(inst='uart', libname='uart_lib', modname='uart')>",
        "<glbl_lib.clk_gate.ClkGateMod(inst='uart/u_clk_gate', libname='glbl_lib', modname='clk_gate')>",
        "<glbl_lib.regf.RegfMod(inst='uart/u_regf', libname='uart_lib', modname='uart_regf')>",
        "<glbl_lib.clk_gate.ClkGateMod(inst='uart/u_regf/u_clk_gate', libname='glbl_lib', modname='clk_gate')>",
        "<uart_lib.uart.UartCoreMod(inst='uart/u_core', libname='uart_lib', modname='uart_core')>",
    ]
    assert [repr(mod) for mod in top.iter(unique=True)] == [
        "<uart_lib.uart.UartMod(inst='uart', libname='uart_lib', modname='uart')>",
        "<glbl_lib.clk_gate.ClkGateMod(inst='uart/u_clk_gate', libname='glbl_lib', modname='clk_gate')>",
        "<glbl_lib.regf.RegfMod(inst='uart/u_regf', libname='uart_lib', modname='uart_regf')>",
        "<uart_lib.uart.UartCoreMod(inst='uart/u_core', libname='uart_lib', modname='uart_core')>",
    ]
    assert [repr(mod) for mod in top.iter(post=True)] == [
        "<glbl_lib.clk_gate.ClkGateMod(inst='uart/u_clk_gate', libname='glbl_lib', modname='clk_gate')>",
        "<glbl_lib.clk_gate.ClkGateMod(inst='uart/u_regf/u_clk_gate', libname='glbl_lib', modname='clk_gate')>",
        "<glbl_lib.regf.RegfMod(inst='uart/u_regf', libname='uart_lib', modname='uart_regf')>",
        "<uart_lib.uart.UartCoreMod(inst='uart/u_core', libname='uart_lib', modname='uart_core')>",
        "<uart_lib.uart.UartMod(inst='uart', libname='uart_lib', modname='uart')>",
    ]
    assert [repr(mod) for mod in top.iter(post=True, unique=True)] == [
        "<glbl_lib.clk_gate.ClkGateMod(inst='uart/u_clk_gate', libname='glbl_lib', modname='clk_gate')>",
        "<glbl_lib.regf.RegfMod(inst='uart/u_regf', libname='uart_lib', modname='uart_regf')>",
        "<uart_lib.uart.UartCoreMod(inst='uart/u_core', libname='uart_lib', modname='uart_core')>",
        "<uart_lib.uart.UartMod(inst='uart', libname='uart_lib', modname='uart')>",
    ]
    assert [repr(mod) for mod in top.get_mods()] == [repr(mod) for mod in top.iter(post=True)]
    assert [repr(mod) for mod in top.get_mods("uart_lib.uart*")] == [
        "<glbl_lib.regf.RegfMod(inst='uart/u_regf', libname='uart_lib', modname='uart_regf')>",
        "<uart_lib.uart.UartCoreMod(inst='uart/u_core', libname='uart_lib', modname='uart_core')>",
        "<uart_lib.uart.UartMod(inst='uart', libname='uart_lib', modname='uart')>",
    ]
    assert (
        repr(top.get_mod("glbl_lib.clk_gate"))
        == "<glbl_lib.clk_gate.ClkGateMod(inst='uart/u_clk_gate', libname='glbl_lib', modname='clk_gate')>"
    )
    assert [repr(mod) for mod in top.get_mods("glbl_lib.clk_gate")] == [
        "<glbl_lib.clk_gate.ClkGateMod(inst='uart/u_clk_gate', libname='glbl_lib', modname='clk_gate')>",
        "<glbl_lib.clk_gate.ClkGateMod(inst='uart/u_regf/u_clk_gate', libname='glbl_lib', modname='clk_gate')>",
    ]
    assert [repr(mod) for mod in top.get_mods("glbl_lib.regf")] == []
    assert [repr(mod) for mod in top.get_mods("glbl_lib.regf", base=True)] == [
        "<glbl_lib.regf.RegfMod(inst='uart/u_regf', libname='uart_lib', modname='uart_regf')>",
    ]

    msg = (
        "'glbl_lib.regf' not found. Known are:\n  glbl_lib.clk_gate\n  uart_lib.uart\n  "
        "uart_lib.uart_core\n  uart_lib.uart_regf"
    )
    with raises(ValueError, match=re.escape(msg)):
        top.get_mod("glbl_lib.regf")

    assert (
        repr(top.get_mod("glbl_lib.regf", base=True))
        == "<glbl_lib.regf.RegfMod(inst='uart/u_regf', libname='uart_lib', modname='uart_regf')>"
    )

    msg = (
        "Found multiple hardware modules for 'uart_lib.*':\n  uart_lib.uart\n  uart_lib.uart_core\n  uart_lib.uart_regf"
    )
    with raises(ValueError, match=re.escape(msg)):
        top.get_mod("uart_lib.*")

    msg = "'glbl_lib.foo' not found. Known are:\n  glbl_lib.clk_gate\n  glbl_lib.regf\n  uart_lib.uart"
    with raises(ValueError, match=re.escape(msg)):
        top.get_mod("glbl_lib.foo", base=True)


def test_load_complex_sub(example_simple):
    """Complexer Module with Sub module."""
    top = u.load("uart_lib.uart-glbl_lib.clk_gate", paths=None)
    assert top.ref == u.TopModRef(u.ModRef("uart_lib", "uart"), sub="glbl_lib.clk_gate")
    assert (
        repr(top.mod)
        == "<glbl_lib.clk_gate.ClkGateMod(inst='uart/u_clk_gate', libname='glbl_lib', modname='clk_gate')>"
    )


def test_load_tb(example_simple):
    """Complexer Module with Testbench."""
    top = u.load("glbl_lib.regf_tb#uart_lib.uart-uart_lib.uart_regf", paths=None)
    assert top.ref == u.TopModRef(
        u.ModRef("uart_lib", "uart"), sub="uart_lib.uart_regf", tb=u.ModRef("glbl_lib", "regf_tb")
    )
    assert repr(top.mod) == (
        "<glbl_lib.regf_tb.RegfTbMod(inst='regf_tb_uart_regf', libname='glbl_lib', modname='regf_tb_uart_regf', "
        "dut=<glbl_lib.regf.RegfMod(inst='uart/u_regf', libname='uart_lib', modname='uart_regf')>)>"
    )
    assert repr(top.mod.dut) == "<glbl_lib.regf.RegfMod(inst='uart/u_regf', libname='uart_lib', modname='uart_regf')>"

    retop = u.Top.from_mod(top.mod)
    assert retop.mod == top.mod
    assert retop.ref == u.TopModRef(
        u.ModRef("glbl_lib", "regf", modclsname="RegfMod"), tb=u.ModRef("glbl_lib", "regf_tb", modclsname="RegfTbMod")
    )


def test_load_non_tb(example_simple):
    """Complexer Module with Testbench - Non-TB."""
    with raises(ValueError) as exc:
        u.load("glbl_lib.regf#uart_lib.uart-uart_lib.uart_regf", paths=None)
    assert (
        str(exc.value)
        == "<class 'glbl_lib.regf.RegfMod'> is not a testbench module aka child of <class ucdp.AGenericTbMod>."
    )


def test_imp_err(testdata):
    """Import Error."""
    msg = "'imp_err_lib.not_existing' not found."
    with raises(NameError, match=re.escape(msg)):
        u.load("imp_err_lib.not_existing", paths=None)


def test_imp_err_dep(testdata):
    """Broken Dependency."""
    msg = "No module named 'imp_err_lib.not_existing'"
    with raises(ModuleNotFoundError, match=re.escape(msg)):
        u.load("imp_err_lib.imp_err", paths=None)


def test_typo(example_simple):
    """Typos."""
    with raises(NameError, match=re.escape("'glbl_li.clk_gate' not found. Did you mean 'glbl_lib.clk_gate'")):
        u.load("glbl_li.clk_gate", paths=None)

    with raises(NameError, match=re.escape("'glbl_lib.clk_ate' not found. Did you mean 'glbl_lib.clk_gate'")):
        u.load("glbl_lib.clk_ate", paths=None)

    msg = "'glbl_lib.clk_gate' does not contain GateMod. Did you mean 'glbl_lib.clk_gate', '"
    with raises(NameError, match=re.escape(msg)):
        u.load("glbl_lib.clk_gate.GateMod", paths=None)


def test_paths(tmp_path):
    """Paths Argument."""
    for name in ("one", "two", "three", "four", "five"):
        one_path = tmp_path / name / f"{name}_lib"
        one_path.mkdir(parents=True)
        (one_path / f"{name}.py").write_text(f"""\
import ucdp as u

class {pascalcase(name)}Mod(u.AMod):
    def _build(self) -> None:
        pass
""")

    with raises(NameError):
        assert u.load("one_lib.one")

    # relative path
    with chdir(tmp_path):
        assert u.load("one_lib.one", paths=(Path("one"),)).mod.name == "one"

    with raises(NameError):
        assert u.load("two_lib.two")

    # absolute path
    with chdir(tmp_path):
        assert u.load("two_lib.two", paths=(tmp_path / "two",)).mod.name == "two"

    # glob
    with chdir(tmp_path):
        assert u.load("four_lib.four", paths=(tmp_path / "*",)).mod.name == "four"
