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
"""Test Command-Line-Interface."""

import subprocess
from pathlib import Path

from click.testing import CliRunner
from contextlib_chdir import chdir
from pydantic import BaseModel
from pytest import mark
from test2ref import assert_refdata, configure

import ucdp as u

from .conftest import TESTDATA_PATH

configure(ignore_spaces=True)

REPLACEMENTS = ((Path("$PRJROOT"), "$PRJROOT"),)


class Result(BaseModel):
    """Result."""

    exit_code: int
    stdout: str
    stderr: str


def run(*cmd, exit_code: int = 0) -> Result:
    """Run."""
    result = subprocess.run(("ucdp", *cmd), check=False, capture_output=True, text=True)  # noqa: S603
    assert result.returncode == exit_code
    stdout = result.stdout
    stderr = result.stderr
    return Result(exit_code=result.returncode, stdout=stdout, stderr=stderr)


def run2console(prjroot: Path, *cmd, exit_code: int = 0, output="console.txt") -> None:
    """Run And Capture Console."""
    result = run(*cmd, exit_code=exit_code)
    if result.stdout:
        (prjroot / output).write_text(result.stdout)
    if result.stderr:
        (prjroot / output).with_suffix(".err.txt").write_text(result.stderr)


def test_check(prjroot, example_simple):
    """Check Command."""
    run2console(prjroot, "check", "uart_lib.uart", output="check-uart.txt")

    run("check", "uart_lib.uart2", exit_code=1)

    run2console(prjroot, "check", "uart_lib.uart", "--stat", output="check-stat.txt")

    assert_refdata(test_check, prjroot)


def test_gen(prjroot, example_simple, uartcorefile):
    """Generate and Clean Command."""
    uartfile = prjroot / "uart_lib" / "uart" / "rtl" / "uart.sv"

    assert not uartfile.exists()

    run2console(prjroot, "gen", "uart_lib.uart", "-f", "hdl", output="gen.txt")

    assert uartfile.exists()

    run2console(prjroot, "cleangen", "uart_lib.uart", "-f", "hdl", output="cleangen.txt")

    assert not uartfile.exists()

    assert_refdata(test_gen, prjroot)


def test_gen_check(prjroot, example_simple, uartcorefile):
    """Generate with Check."""
    uartfile = prjroot / "uart_lib" / "uart" / "rtl" / "uart.sv"

    run2console(prjroot, "gen", "uart_lib.uart", "--check", exit_code=1, output="check.txt")

    assert uartfile.exists()

    run2console(prjroot, "gen", "uart_lib.uart", "--check", output="re-check.txt")

    assert_refdata(test_gen_check, prjroot)


def test_gen_tb(prjroot, example_simple):
    """Generate with Check."""
    run2console(prjroot, "gen", "glbl_lib.regf_tb#uart_lib.uart-uart_lib.uart_regf", output="gen.txt")
    assert_refdata(test_gen_tb, prjroot)


def test_gen_topsfile(prjroot, example_simple, uartcorefile):
    """Generate with --tops-file."""
    topfile = prjroot / "tops.txt"
    topfile.write_text("""
# comment
  uart_lib.uart

""")

    run2console(prjroot, "gen", "--tops-file", str(topfile))

    assert_refdata(test_gen_topsfile, prjroot)


def test_gen_default(prjroot, example_simple, uartcorefile):
    """Generate and Clean Command."""
    run2console(prjroot, "gen", "uart_lib.uart", output="gen.txt")

    run2console(prjroot, "cleangen", "uart_lib.uart", output="cleangen.txt")

    assert_refdata(test_gen_default, prjroot)


def test_filelist(prjroot, example_simple):
    """Filelist Command."""
    run2console(prjroot, "filelist", "uart_lib.uart", "-f", "hdl")
    assert_refdata(test_filelist, prjroot, replacements=REPLACEMENTS)


def test_filelist_default(prjroot, example_simple):
    """Filelist Command with Default."""
    run2console(prjroot, "filelist", "uart_lib.uart")
    assert_refdata(test_filelist_default, prjroot, replacements=REPLACEMENTS)


def test_filelist_file(prjroot, example_simple):
    """Filelist Command."""
    filepath = prjroot / "file.txt"
    run2console(prjroot, "filelist", "uart_lib.uart", "-f", "hdl", "--file", str(filepath))
    assert_refdata(test_filelist_file, prjroot, replacements=REPLACEMENTS)


def test_filelist_other(prjroot, example_filelist):
    """Filelist Command."""
    run2console(prjroot, "filelist", "filelist_lib.filelist", "-f", "hdl")
    assert_refdata(test_filelist_other, prjroot, replacements=REPLACEMENTS)


def test_fileinfo(prjroot, example_simple):
    """Fileinfo Command."""
    run2console(prjroot, "fileinfo", "uart_lib.uart", "-f", "hdl")
    assert_refdata(test_fileinfo, prjroot, replacements=REPLACEMENTS)


def test_fileinfo_default(prjroot, example_simple):
    """Fileinfo Command."""
    run2console(prjroot, "fileinfo", "uart_lib.uart")
    assert_refdata(test_fileinfo_default, prjroot, replacements=REPLACEMENTS)


def test_fileinfo_minimal(prjroot, example_simple):
    """Fileinfo Command Minimal."""
    run2console(prjroot, "fileinfo", "uart_lib.uart", "-m")
    assert_refdata(test_fileinfo_minimal, prjroot, replacements=REPLACEMENTS)


def test_fileinfo_maxlevel(prjroot, example_simple):
    """Fileinfo Command with Maxlevel."""
    run2console(prjroot, "fileinfo", "uart_lib.uart", "-f", "hdl", "--maxlevel=1")
    assert_refdata(test_fileinfo_maxlevel, prjroot, replacements=REPLACEMENTS)


def test_fileinfo_file(prjroot, example_simple):
    """Fileinfo Command with File."""
    filepath = prjroot / "file.txt"
    run2console(prjroot, "fileinfo", "uart_lib.uart", "-f", "hdl", "--file", str(filepath))
    assert_refdata(test_fileinfo_file, prjroot, replacements=REPLACEMENTS)


def test_overview(prjroot, example_simple):
    """Overview Command."""
    run2console(prjroot, "overview", "uart_lib.uart")
    assert_refdata(test_overview, prjroot)


def test_overview_minimal(prjroot, example_simple):
    """Overview Command - Minimal."""
    run2console(prjroot, "overview", "uart_lib.uart", "-m")
    assert_refdata(test_overview_minimal, prjroot)


def test_overview_file(prjroot, example_simple):
    """Overview Command - Minimal."""
    filepath = prjroot / "file.txt"
    run2console(prjroot, "overview", "uart_lib.uart", "-o", str(filepath))
    assert_refdata(test_overview_file, prjroot)


def test_overview_tags(prjroot, example_simple):
    """Overview Command."""
    run2console(prjroot, "overview", "uart_lib.uart", "--tag", "intf")
    assert_refdata(test_overview_tags, prjroot)


def test_info_examples(prjroot, example_simple):
    """Info Examples Command."""
    run2console(prjroot, "info", "examples")
    assert_refdata(test_info_examples, prjroot)


def test_info_templates(prjroot, example_simple):
    """Info Templates Command."""
    run2console(prjroot, "info", "template-paths")
    assert_refdata(test_info_templates, prjroot)


def test_rendergen(prjroot, example_simple):
    """Command rendergen."""
    template_filepath = TESTDATA_PATH / "example.txt.mako"
    filepath = prjroot / "output.txt"
    run2console(prjroot, "rendergen", "uart_lib.uart", str(template_filepath), str(filepath))
    assert_refdata(test_rendergen, prjroot)


def test_rendergen_defines(prjroot, example_simple):
    """Command rendergen."""
    template_filepath = TESTDATA_PATH / "example.txt.mako"
    filepath = prjroot / "output.txt"
    run2console(
        prjroot, "rendergen", "uart_lib.uart", str(template_filepath), str(filepath), "-D", "one=1", "-D", "two"
    )
    assert_refdata(test_rendergen_defines, prjroot)


def test_renderinplace(prjroot, example_simple):
    """Command renderinplace."""
    template_filepath = TESTDATA_PATH / "example.txt.mako"
    filepath = prjroot / "output.txt"
    filepath.write_text("""
GENERATE INPLACE BEGIN content('test')
GENERATE INPLACE END content
""")
    run2console(prjroot, "renderinplace", "uart_lib.uart", str(template_filepath), str(filepath))
    assert_refdata(test_renderinplace, prjroot)


def test_ls(prjroot, example_simple):
    """List Command."""
    run2console(prjroot, "ls")
    assert_refdata(test_ls, prjroot)


def test_ls_base(prjroot, example_simple):
    """List Command."""
    run2console(prjroot, "ls", "-A")
    assert_refdata(test_ls_base, prjroot)


def test_ls_local(prjroot, example_simple):
    """List Command - Local Only."""
    run2console(prjroot, "ls", "--local")
    assert_refdata(test_ls_local, prjroot)


def test_ls_nonlocal(prjroot, example_simple):
    """List Command - Non-Local Only."""
    run2console(prjroot, "ls", "--no-local", exit_code=1)
    assert_refdata(test_ls_nonlocal, prjroot)


def test_ls_filepath(prjroot, tests):
    """List Command With Filepath."""
    run2console(prjroot, "ls", "-fn")
    assert_refdata(test_ls_filepath, prjroot, replacements=((Path("tests"), "tests"),))


def test_ls_filepath_abs(prjroot, tests):
    """List Command With Filepath."""
    run2console(prjroot, "ls", "-Fn")
    assert_refdata(test_ls_filepath_abs, prjroot)


def test_ls_names(prjroot, tests):
    """List with Names Only."""
    run2console(prjroot, "ls", "-n")
    assert_refdata(test_ls_names, prjroot)


def test_ls_top(prjroot, tests):
    """List Top Modules Only."""
    run2console(prjroot, "ls", "-t")
    assert_refdata(test_ls_top, prjroot)


def test_ls_notop(prjroot, tests):
    """List No Top Modules Only."""
    run2console(prjroot, "ls", "-T")
    assert_refdata(test_ls_notop, prjroot)


def test_ls_tb(prjroot, tests):
    """List Testbenches Only."""
    run2console(prjroot, "ls", "-b")
    assert_refdata(test_ls_tb, prjroot)


def test_ls_notb(prjroot, tests):
    """List Testbenches Only."""
    run2console(prjroot, "ls", "-B")
    assert_refdata(test_ls_notb, prjroot)


def test_ls_gentb(prjroot, tests):
    """List Generic Testbenches Only."""
    run2console(prjroot, "ls", "-g")
    assert_refdata(test_ls_gentb, prjroot)


def test_ls_pat(prjroot, tests):
    """List Command with Pattern."""
    run2console(prjroot, "ls", "*SomeMod")
    assert_refdata(test_ls_pat, prjroot)


def test_ls_tags(prjroot, tests):
    """List Command with Tags."""
    run2console(prjroot, "ls", "--tag", "intf", "--tag", "ip*")
    assert_refdata(test_ls_tags, prjroot)


def test_ls_tb_dut(prjroot, tests):
    """List Testbenches DUTs."""
    run2console(prjroot, "ls", "tests.*", "-n")
    assert_refdata(test_ls_tb_dut, prjroot)


def test_ls_tb_dut_sub(prjroot, example_simple):
    """List Testbenches DUT with Subs."""
    run2console(prjroot, "ls", "glbl_lib.regf_tb#uart_lib.uart-*", "-n")
    assert_refdata(test_ls_tb_dut_sub, prjroot)


def test_ls_tb_dut_sub_all(prjroot, tests):
    """List Testbenches DUT with Subs, glob."""
    run2console(prjroot, "ls", "*#*-*", "-n")
    assert_refdata(test_ls_tb_dut_sub_all, prjroot)


def test_ls_none(prjroot, tests):
    """List Testbenches DUT with Subs, glob."""
    run2console(prjroot, "ls", "#", exit_code=1)
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


def test_autocomplete_path(prjroot):
    """Autocompletion for Path."""
    with chdir(prjroot):
        Path("aaa.txt").touch()
        Path("aab.txt").touch()
        Path("ac.txt").touch()

        assert u.cliutil.auto_path(None, None, "a") == ["aaa.txt", "aab.txt", "ac.txt"]
        assert u.cliutil.auto_path(None, None, "aa") == ["aaa.txt", "aab.txt"]
        assert u.cliutil.auto_path(None, None, "b") == []


def test_toppath(prjroot, example_simple):
    """Check Command."""
    run2console(prjroot, "check", str(example_simple / "uart_lib" / "uart.py"))
    assert_refdata(test_toppath, prjroot)


def test_modinfo(prjroot, example_simple):
    """Modinfo Command."""
    run2console(prjroot, "modinfo", "uart_lib.uart")
    assert_refdata(test_modinfo, prjroot)


def test_modinfos(prjroot, example_simple):
    """Modinfo Command."""
    run2console(prjroot, "modinfo", "*_lib.*", "-S")
    assert_refdata(test_modinfos, prjroot)


def test_modinfos_param(example_param, prjroot):
    """Modinfo Command."""
    run2console(prjroot, "modinfo", "*_lib.*")
    assert_refdata(test_modinfos_param, prjroot)


def test_create(tmp_path):
    """Test Command For The Create Function."""
    with chdir(tmp_path):
        run("create", "-T", "--module", "my_name", "--library", "my_library", "--flavour", "AMod")
    assert_refdata(test_create, tmp_path, replacements=((Path("my_library"), "my_library"),))


def test_create_numbers(tmp_path):
    """Test Create Command With Specified With Numbers."""
    with chdir(tmp_path):
        run("create", "-T", "-m", "my_name2", "-l", "my_library_2", "-F", "AMod")
    assert_refdata(test_create_numbers, tmp_path, replacements=((Path("my_library_2"), "my_library"),))


def test_create_invalid_name(tmp_path):
    """Test Command For The Create Function But To Test Where The Maximum Is."""
    with chdir(tmp_path):
        run(
            "create",
            "-T",
            "--module",
            "my_name_2_previus",
            "--library",
            "my_library_2_previus.py",
            "--flavour",
            "AMod",
            exit_code=1,
        )
    # Check that no file is generated
    assert tuple(tmp_path.glob("*")) == ()


def test_create_regf(tmp_path):
    """Test Create Command With Specified With Numbers."""
    with chdir(tmp_path):
        run("create", "-T", "--module", "my_name_regf", "--library", "my_library", "--regf", "--flavour", "AMod")
    assert_refdata(test_create_regf, tmp_path, replacements=((Path("my_library"), "my_library"),))


def test_create_no_regf(tmp_path):
    """Test Create Command With Specified With Numbers."""
    with chdir(tmp_path):
        run("create", "-T", "--module", "my_name_no_regf", "--library", "my_library", "--no-regf", "--flavour", "AMod")
    assert_refdata(test_create_no_regf, tmp_path, replacements=((Path("my_library"), "my_library"),))


def test_create_descr(tmp_path):
    """Test Create Command With Specified Description."""
    with chdir(tmp_path):
        run(
            "create",
            "-T",
            "--module",
            "my_name_descr",
            "--library",
            "my_library",
            "--descr",
            "My Fancy Module",
            "--flavour",
            "AMod",
        )
    assert_refdata(test_create_descr, tmp_path, replacements=((Path("my_library"), "my_library"),))


@mark.parametrize(
    "flavour",
    [
        "AConfigurableMod",
        "AConfigurableTbMod",
        "AGenericTbMod",
        "AMod",
        "ATailoredMod",
        "ATbMod",
    ],
)
def test_create_flavour(tmp_path, flavour):
    """Test Create Command Flavour."""
    runner = CliRunner()
    with chdir(tmp_path):
        runner.invoke(
            u.cli.ucdp,
            ["create", "-T", "--name", "my_name_flavour", "--library", "my_library", "--flavour", "{flavour}"],
            flavour="\n".join((*flavour, "")),
        )
    assert_refdata(
        test_create_flavour, tmp_path, flavor="-".join(flavour), replacements=((Path("my_library"), "my_library"),)
    )


@mark.parametrize(
    "input",
    [
        ("mod0", "lib_type", "d", "n"),
        ("mod1", "lib_type", "d", "y", "c"),
        ("mod2", "lib_type", "d", "y", "t"),
        ("mod3", "lib_type", "t", "y", "g"),
        ("mod4", "lib_type", "t", "y", "c"),
        ("mod5", "lib_type", "t", "n"),
        ("mod6_tb", "lib_type", "d", "n"),
        ("mod7_tb", "lib_type", "t", "n"),
    ],
)
def test_create_type_questions(tmp_path, input):
    """Test Type Questionnaire."""
    runner = CliRunner()
    with chdir(tmp_path):
        result = runner.invoke(u.cli.ucdp, ["create", "-T"], input="\n".join((*input, "")))
    assert not result.exception
    output_path = tmp_path / "output.txt"
    output_path.write_text(result.output)
    assert_refdata(
        test_create_type_questions, tmp_path, flavor="-".join(input), replacements=((Path("lib_type"), "lib_type"),)
    )


@mark.parametrize("input", [("mod0", "y"), ("mod1", "n")])
def test_create_tb_questions(tmp_path, input):
    """Test tb Questionnaire."""
    runner = CliRunner()
    with chdir(tmp_path):
        result = runner.invoke(
            u.cli.ucdp, ["create", "--library", "lib_tb", "--flavour", "amod"], input="\n".join((*input, ""))
        )
    assert not result.exception
    assert_refdata(
        test_create_tb_questions, tmp_path, flavor="-".join(input), replacements=((Path("lib_tb"), "lib_tb"),)
    )
