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

from click.testing import CliRunner
from pytest import fixture
from test2ref import assert_refdata
from ucdp.cli import ucdp


@fixture
def runner():
    """Click Runner for Testing."""
    yield CliRunner()


def _assert_output(result, lines):
    assert [line.rstrip() for line in result.output.splitlines()] == lines


def test_check(runner, example_simple):
    """Check Command."""
    result = runner.invoke(ucdp, ["check", "uart_lib.uart"])
    assert result.exit_code == 0
    _assert_output(
        result,
        [
            "'uart_lib.uart' checked.",
        ],
    )

    result = runner.invoke(ucdp, ["check", "uart_lib.uart2"])
    assert result.exit_code == 1
    assert result.output == ""

    result = runner.invoke(ucdp, ["check", "uart_lib.uart", "--stat"])
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

    result = runner.invoke(ucdp, ["gen", "uart_lib.uart", "hdl", "--maxworkers", "1"])
    assert result.exit_code == 0
    (prjroot / "gen.txt").write_text(result.output)

    assert uartfile.exists()

    result = runner.invoke(ucdp, ["cleangen", "uart_lib.uart", "hdl", "--maxworkers", "1"])
    assert result.exit_code == 0
    (prjroot / "cleangen.txt").write_text(result.output)

    assert not uartfile.exists()

    (prjroot / "console.txt").write_text(result.output)
    assert_refdata(test_gen, prjroot)


def test_filelist(runner, example_simple, prjroot):
    """Filelist Command."""
    result = runner.invoke(ucdp, ["filelist", "uart_lib.uart", "hdl"])
    assert result.exit_code == 0
    (prjroot / "console.txt").write_text(result.output)
    assert_refdata(test_filelist, prjroot)


def test_filelist_file(runner, example_simple, prjroot):
    """Filelist Command."""
    filepath = prjroot / "file.txt"
    result = runner.invoke(ucdp, ["filelist", "uart_lib.uart", "hdl", "--file", str(filepath)])
    assert result.exit_code == 0
    (prjroot / "console.txt").write_text(result.output)
    assert_refdata(test_filelist_file, prjroot)


def test_filelist_other(runner, prjroot, example_filelist):
    """Filelist Command."""
    result = runner.invoke(ucdp, ["filelist", "filelist_lib.filelist", "hdl"])
    assert result.exit_code == 0
    (prjroot / "console.txt").write_text(result.output)
    assert_refdata(test_filelist_other, prjroot)


def test_fileinfo(runner, example_simple, prjroot):
    """Fileinfo Command."""
    result = runner.invoke(ucdp, ["fileinfo", "uart_lib.uart", "hdl"])
    assert result.exit_code == 0
    (prjroot / "console.txt").write_text(result.output)
    assert_refdata(test_fileinfo, prjroot)


def test_fileinfo_maxlevel(runner, example_simple, prjroot):
    """Fileinfo Command with Maxlevel."""
    result = runner.invoke(ucdp, ["fileinfo", "uart_lib.uart", "hdl", "--maxlevel=1"])
    assert result.exit_code == 0
    (prjroot / "console.txt").write_text(result.output)
    assert_refdata(test_fileinfo_maxlevel, prjroot)


def test_fileinfo_file(runner, example_simple, prjroot):
    """Fileinfo Command with File."""
    filepath = prjroot / "file.txt"
    result = runner.invoke(ucdp, ["fileinfo", "uart_lib.uart", "hdl", "--file", str(filepath)])
    assert result.exit_code == 0
    (prjroot / "console.txt").write_text(result.output)
    assert_refdata(test_fileinfo_file, prjroot)


def test_overview(runner, example_simple, prjroot):
    """Overview Command."""
    result = runner.invoke(ucdp, ["overview", "uart_lib.uart"])
    assert result.exit_code == 0
    (prjroot / "console.txt").write_text(result.output)
    assert_refdata(test_overview, prjroot)


def test_overview_minimal(runner, example_simple, prjroot):
    """Overview Command - Minimal."""
    result = runner.invoke(ucdp, ["overview", "uart_lib.uart", "-m"])
    assert result.exit_code == 0
    (prjroot / "console.txt").write_text(result.output)
    assert_refdata(test_overview_minimal, prjroot)


def test_overview_file(runner, example_simple, prjroot):
    """Overview Command - Minimal."""
    filepath = prjroot / "file.txt"
    result = runner.invoke(ucdp, ["overview", "uart_lib.uart", "-o", str(filepath)])
    assert result.exit_code == 0
    (prjroot / "console.txt").write_text(result.output)
    assert_refdata(test_overview_file, prjroot)


def test_info_examples(runner, example_simple, prjroot):
    """Info Examples Command."""
    result = runner.invoke(ucdp, ["info", "examples"])
    assert result.exit_code == 0
    (prjroot / "console.txt").write_text(result.output)
    assert_refdata(test_info_examples, prjroot)


def test_info_templates(runner, example_simple, prjroot):
    """Info Templates Command."""
    result = runner.invoke(ucdp, ["info", "template-paths"])
    assert result.exit_code == 0
    (prjroot / "console.txt").write_text(result.output)
    assert_refdata(test_info_templates, prjroot)


def test_rendergen(runner, example_simple, prjroot, testdata):
    """Command rendergen."""
    template_filepath = testdata / "example.txt.mako"
    filepath = prjroot / "output.txt"
    result = runner.invoke(
        ucdp,
        [
            "rendergen",
            "uart_lib.uart",
            str(template_filepath),
            str(filepath),
        ],
    )
    assert result.exit_code == 0
    (prjroot / "console.txt").write_text(result.output)
    assert_refdata(test_rendergen, prjroot)


def test_rendergen_defines(runner, example_simple, prjroot, testdata):
    """Command rendergen."""
    template_filepath = testdata / "example.txt.mako"
    filepath = prjroot / "output.txt"
    result = runner.invoke(
        ucdp, ["rendergen", "uart_lib.uart", str(template_filepath), str(filepath), "-D", "one=1", "-D", "two"]
    )
    assert result.exit_code == 0
    (prjroot / "console.txt").write_text(result.output)
    assert_refdata(test_rendergen_defines, prjroot)


def test_renderinplace(runner, example_simple, prjroot, testdata):
    """Command renderinplace."""
    template_filepath = testdata / "example.txt.mako"
    filepath = prjroot / "output.txt"
    filepath.write_text("""
GENERATE INPLACE BEGIN content('test')
GENERATE INPLACE END content
""")
    result = runner.invoke(
        ucdp,
        [
            "renderinplace",
            "uart_lib.uart",
            str(template_filepath),
            str(filepath),
        ],
    )
    assert result.exit_code == 0
    (prjroot / "console.txt").write_text(result.output)
    assert_refdata(test_renderinplace, prjroot)
