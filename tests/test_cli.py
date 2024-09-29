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
"""Test Command-Line-Interface."""

from pathlib import Path

import ucdp as u
from click.testing import CliRunner
from contextlib_chdir import chdir
from pytest import fixture
from test2ref import assert_refdata


@fixture
def runner():
    """Click Runner for Testing."""
    yield CliRunner()


def _assert_output(result, lines):
    assert [line.rstrip() for line in result.output.splitlines()] == lines


def _run(runner, prjroot, cmd):
    result = runner.invoke(u.cli.ucdp, cmd)
    assert result.exit_code == 0
    (prjroot / "console.txt").write_text(result.output)


def test_check(runner, example_simple):
    """Check Command."""
    result = runner.invoke(u.cli.ucdp, ["check", "uart_lib.uart"])
    assert result.exit_code == 0
    _assert_output(result, ["'uart_lib.uart' checked."])

    result = runner.invoke(u.cli.ucdp, ["check", "uart_lib.uart2"])
    assert result.exit_code == 1
    assert result.output == ""

    result = runner.invoke(u.cli.ucdp, ["check", "uart_lib.uart", "--stat"])
    assert result.exit_code == 0
    _assert_output(
        result,
        [
            "'uart_lib.uart' checked.",
            "Statistics:",
            "  Modules: 4",
            "  Module-Instances: 5",
            "  LightObjects: 10",
        ],
    )


def test_gen(runner, example_simple, prjroot):
    """Generate and Clean Command."""
    uartfile = prjroot / "uart_lib" / "uart" / "rtl" / "uart.sv"

    assert not uartfile.exists()

    result = runner.invoke(u.cli.ucdp, ["gen", "uart_lib.uart", "hdl", "--maxworkers", "1"])
    assert result.exit_code == 0
    (prjroot / "gen.txt").write_text(result.output)

    assert uartfile.exists()

    result = runner.invoke(u.cli.ucdp, ["cleangen", "uart_lib.uart", "hdl", "--maxworkers", "1"])
    assert result.exit_code == 0
    (prjroot / "cleangen.txt").write_text(result.output)

    assert not uartfile.exists()

    (prjroot / "console.txt").write_text(result.output)
    assert_refdata(test_gen, prjroot)


def test_gen_default(runner, example_simple, prjroot):
    """Generate and Clean Command."""
    result = runner.invoke(u.cli.ucdp, ["gen", "uart_lib.uart", "--maxworkers", "1"])
    assert result.exit_code == 0
    (prjroot / "gen.txt").write_text(result.output)

    result = runner.invoke(u.cli.ucdp, ["cleangen", "uart_lib.uart", "--maxworkers", "1"])
    assert result.exit_code == 0
    (prjroot / "cleangen.txt").write_text(result.output)
    assert_refdata(test_gen_default, prjroot)


def test_filelist(runner, example_simple, prjroot):
    """Filelist Command."""
    cmd = ["filelist", "uart_lib.uart", "hdl"]
    _run(runner, prjroot, cmd)
    assert_refdata(test_filelist, prjroot)


def test_filelist_default(runner, example_simple, prjroot):
    """Filelist Command with Default."""
    cmd = ["filelist", "uart_lib.uart"]
    _run(runner, prjroot, cmd)
    assert_refdata(test_filelist_default, prjroot)


def test_filelist_file(runner, example_simple, prjroot):
    """Filelist Command."""
    filepath = prjroot / "file.txt"
    cmd = ["filelist", "uart_lib.uart", "hdl", "--file", str(filepath)]
    _run(runner, prjroot, cmd)
    assert_refdata(test_filelist_file, prjroot)


def test_filelist_other(runner, prjroot, example_filelist):
    """Filelist Command."""
    cmd = ["filelist", "filelist_lib.filelist", "hdl"]
    _run(runner, prjroot, cmd)
    assert_refdata(test_filelist_other, prjroot)


def test_fileinfo(runner, example_simple, prjroot):
    """Fileinfo Command."""
    cmd = ["fileinfo", "uart_lib.uart", "hdl"]
    _run(runner, prjroot, cmd)
    assert_refdata(test_fileinfo, prjroot)


def test_fileinfo_default(runner, example_simple, prjroot):
    """Fileinfo Command."""
    cmd = ["fileinfo", "uart_lib.uart"]
    _run(runner, prjroot, cmd)
    assert_refdata(test_fileinfo_default, prjroot)


def test_fileinfo_minimal(runner, example_simple, prjroot):
    """Fileinfo Command Minimal."""
    cmd = ["fileinfo", "uart_lib.uart", "-m"]
    _run(runner, prjroot, cmd)
    assert_refdata(test_fileinfo_minimal, prjroot)


def test_fileinfo_maxlevel(runner, example_simple, prjroot):
    """Fileinfo Command with Maxlevel."""
    cmd = ["fileinfo", "uart_lib.uart", "hdl", "--maxlevel=1"]
    _run(runner, prjroot, cmd)
    assert_refdata(test_fileinfo_maxlevel, prjroot)


def test_fileinfo_file(runner, example_simple, prjroot):
    """Fileinfo Command with File."""
    filepath = prjroot / "file.txt"
    cmd = ["fileinfo", "uart_lib.uart", "hdl", "--file", str(filepath)]
    _run(runner, prjroot, cmd)
    assert_refdata(test_fileinfo_file, prjroot)


def test_overview(runner, example_simple, prjroot):
    """Overview Command."""
    cmd = ["overview", "uart_lib.uart"]
    _run(runner, prjroot, cmd)
    assert_refdata(test_overview, prjroot)


def test_overview_minimal(runner, example_simple, prjroot):
    """Overview Command - Minimal."""
    cmd = ["overview", "uart_lib.uart", "-m"]
    _run(runner, prjroot, cmd)
    assert_refdata(test_overview_minimal, prjroot)


def test_overview_file(runner, example_simple, prjroot):
    """Overview Command - Minimal."""
    filepath = prjroot / "file.txt"
    cmd = ["overview", "uart_lib.uart", "-o", str(filepath)]
    _run(runner, prjroot, cmd)
    assert_refdata(test_overview_file, prjroot)


def test_overview_tags(runner, example_simple, prjroot):
    """Overview Command."""
    cmd = ["overview", "uart_lib.uart", "-T", "intf"]
    _run(runner, prjroot, cmd)
    assert_refdata(test_overview_tags, prjroot)


def test_info_examples(runner, example_simple, prjroot):
    """Info Examples Command."""
    _run(runner, prjroot, ["info", "examples"])
    assert_refdata(test_info_examples, prjroot)


def test_info_templates(runner, example_simple, prjroot):
    """Info Templates Command."""
    _run(runner, prjroot, ["info", "template-paths"])
    assert_refdata(test_info_templates, prjroot)


def test_rendergen(runner, example_simple, prjroot, testdata):
    """Command rendergen."""
    template_filepath = testdata / "example.txt.mako"
    filepath = prjroot / "output.txt"
    cmd = ["rendergen", "uart_lib.uart", str(template_filepath), str(filepath)]
    _run(runner, prjroot, cmd)

    assert_refdata(test_rendergen, prjroot)


def test_rendergen_defines(runner, example_simple, prjroot, testdata):
    """Command rendergen."""
    template_filepath = testdata / "example.txt.mako"
    filepath = prjroot / "output.txt"
    cmd = ["rendergen", "uart_lib.uart", str(template_filepath), str(filepath), "-D", "one=1", "-D", "two"]
    _run(runner, prjroot, cmd)
    assert_refdata(test_rendergen_defines, prjroot)


def test_renderinplace(runner, example_simple, prjroot, testdata):
    """Command renderinplace."""
    template_filepath = testdata / "example.txt.mako"
    filepath = prjroot / "output.txt"
    filepath.write_text("""
GENERATE INPLACE BEGIN content('test')
GENERATE INPLACE END content
""")
    cmd = ["renderinplace", "uart_lib.uart", str(template_filepath), str(filepath)]
    _run(runner, prjroot, cmd)
    assert_refdata(test_renderinplace, prjroot)


def test_ls(runner, example_simple, testdata, prjroot):
    """List Command."""
    _run(runner, prjroot, ["ls"])
    assert_refdata(test_ls, prjroot)


def test_ls_base(runner, example_simple, testdata, prjroot):
    """List Command with Base."""
    _run(runner, prjroot, ["ls", "-B"])
    assert_refdata(test_ls_base, prjroot)


def test_ls_local(runner, example_simple, testdata, prjroot):
    """List Command - Local Only."""
    _run(runner, prjroot, ["ls", "--local"])
    assert_refdata(test_ls_local, prjroot)


def test_ls_nonlocal(runner, example_simple, testdata, prjroot):
    """List Command - Non-Local Only."""
    _run(runner, prjroot, ["ls", "--no-local"])
    assert_refdata(test_ls_nonlocal, prjroot)


def test_ls_filepath(runner, example_simple, testdata, prjroot):
    """List Command With Filepath."""
    _run(runner, prjroot, ["ls", "-fn"])
    assert_refdata(test_ls_filepath, prjroot)


def test_ls_filepath_abs(runner, example_simple, testdata, prjroot):
    """List Command With Filepath."""
    _run(runner, prjroot, ["ls", "-Fn"])
    assert_refdata(test_ls_filepath_abs, prjroot)


def test_ls_names(runner, example_simple, testdata, prjroot):
    """List with Names Only."""
    _run(runner, prjroot, ["ls", "-n"])
    assert_refdata(test_ls_names, prjroot)


def test_ls_top(runner, example_simple, testdata, prjroot):
    """List Top Modules Only."""
    _run(runner, prjroot, ["ls", "-t"])
    assert_refdata(test_ls_top, prjroot)


def test_ls_tb(runner, example_simple, testdata, prjroot):
    """List Testbenches Only."""
    _run(runner, prjroot, ["ls", "-b"])
    assert_refdata(test_ls_tb, prjroot)


def test_ls_gentb(runner, example_simple, testdata, prjroot):
    """List Generic Testbenches Only."""
    _run(runner, prjroot, ["ls", "-g"])
    assert_refdata(test_ls_gentb, prjroot)


def test_ls_pat(runner, example_simple, testdata, prjroot):
    """List Command with Pattern."""
    _run(runner, prjroot, ["ls", "glbl_lib*", "*SomeMod"])
    assert_refdata(test_ls_pat, prjroot)


def test_ls_tags(runner, example_simple, testdata, prjroot):
    """List Command with Tags."""
    _run(runner, prjroot, ["ls", "-T", "intf", "-T", "ip*"])
    assert_refdata(test_ls_tags, prjroot)


def test_ls_tb_dut(runner, example_simple, testdata, prjroot):
    """List Testbenches DUTs."""
    _run(runner, prjroot, ["ls", "tests.test_modtb.GenTbMod#*", "-n"])
    assert_refdata(test_ls_tb_dut, prjroot)


def test_ls_tb_dut_sub(runner, example_simple, testdata, prjroot):
    """List Testbenches DUT with Subs."""
    _run(runner, prjroot, ["ls", "glbl_lib.regf_tb#uart_lib.uart-*", "-n"])
    assert_refdata(test_ls_tb_dut_sub, prjroot)


def test_ls_tb_dut_sub_all(runner, example_simple, testdata, prjroot):
    """List Testbenches DUT with Subs, glob."""
    _run(runner, prjroot, ["ls", "*#*-*", "-n"])
    assert_refdata(test_ls_tb_dut_sub_all, prjroot)


def test_ls_none(runner, example_simple, testdata, prjroot):
    """List Testbenches DUT with Subs, glob."""
    _run(runner, prjroot, ["ls", "#"])
    assert_refdata(test_ls_none, prjroot)


def test_autocomplete_top(example_simple):
    """Autocompletion for Top."""
    assert len(u.cliutil.auto_top(None, None, "")) > 20
    assert u.cliutil.auto_top(None, None, "gl") == [
        "glbl_lib.clk_gate",
        "glbl_lib.regf",
        "glbl_lib.regf_tb",
    ]
    assert u.cliutil.auto_top(None, None, "glbl_lib.r") == [
        "glbl_lib.regf",
        "glbl_lib.regf_tb",
    ]


def test_autocomplete_path(tmp_path):
    """Autocompletion for Path."""
    with chdir(tmp_path):
        Path("aaa.txt").touch()
        Path("aab.txt").touch()
        Path("ac.txt").touch()

        assert u.cliutil.auto_path(None, None, "a") == ["aaa.txt", "aab.txt", "ac.txt"]
        assert u.cliutil.auto_path(None, None, "aa") == ["aaa.txt", "aab.txt"]
        assert u.cliutil.auto_path(None, None, "b") == []


def test_toppath(runner, example_simple):
    """Check Command."""
    result = runner.invoke(u.cli.ucdp, ["check", str(example_simple / "uart_lib" / "uart.py")])
    assert result.exit_code == 0
    _assert_output(result, ["'uart_lib.uart' checked."])
