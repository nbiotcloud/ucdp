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

"""Command Line Interface - Utilities."""

from collections.abc import Iterator
from logging import FATAL, getLogger
from pathlib import Path

import click

from ucdp.finder import find
from ucdp.pathutil import improved_glob

PathType = click.Path(path_type=Path)


def auto_top(ctx, param, incomplete):
    """Autocompletion for TOP."""
    getLogger().setLevel(FATAL)
    infos = find(patterns=[f"{incomplete}*"], glob=True)
    return [str(info.topmodref) for info in infos]


def auto_path(ctr, param, incomplete):
    """Autocompletion for Paths."""
    return [str(path) for path in improved_glob(Path(f"{incomplete}*"))]


arg_top = click.argument("top", envvar="UCDP_TOP", shell_complete=auto_top)
arg_tops = click.argument("tops", nargs=-1, envvar="UCDP_TOP", shell_complete=auto_top)
opt_topsfile = click.option(
    "--tops-file",
    type=click.Path(path_type=Path),
    default=[],
    multiple=True,
    help="File with Top Module References",
)

opt_path = click.option(
    "--path",
    "-p",
    default=[],
    multiple=True,
    envvar="UCDP_PATH",
    shell_complete=auto_path,
    help="""
Search Path For Data Model And Template Files.
This option can be specified multiple times.
Environment Variable 'UCDP_PATH'.
""",
)
opt_filelist = click.option(
    "--filelist",
    "-f",
    multiple=True,
    help="Filelist Names. Environment Variable 'UCDP_FILELIST'.",
    envvar="UCDP_FILELIST",
)
opt_target = click.option(
    "--target",
    "-t",
    help="Filter File List for Target. Environment Variable 'UCDP_TARGET'.",
    envvar="UCDP_TARGET",
)
opt_show_diff = click.option(
    "--show-diff",
    "-s",
    default=False,
    is_flag=True,
    help="Show What Changed. Environment Variable 'UCDP_SHOW_DIFF'.",
    envvar="UCDP_SHOW_DIFF",
)
opt_maxlevel = click.option("--maxlevel", "-L", type=int, help="Limit to maximum number of hierarchy levels.")
opt_dry_run = click.option("--dry-run", default=False, is_flag=True, help="Do nothing.")
opt_maxworkers = click.option(
    "--maxworkers",
    "-J",
    type=int,
    help="Maximum Number of Processes.",
    envvar="UCDP_MAXWORKERS",
)
opt_defines = click.option(
    "--define",
    "-D",
    multiple=True,
    type=str,
    help="Defines set on the datamodel. Environment Variable 'UCDP_DEFINES'",
    envvar="UCDP_DEFINES",
)
opt_file = click.option(
    "--file",
    "-o",
    type=click.File("w"),
    shell_complete=auto_path,
    help="Output to file instead of STDOUT",
)
opt_filepath = click.option(
    "--file",
    "-o",
    type=click.Path(path_type=Path),
    shell_complete=auto_path,
    help="Output to file instead of STDOUT",
)
opt_tag = click.option(
    "--tag",
    "-G",
    default=[],
    multiple=True,
    help="Filter Modules by Tag Name or Wildcard.",
)
arg_template_filepaths = click.argument(
    "template_filepaths",
    type=PathType,
    shell_complete=auto_path,
    nargs=-1,
    envvar="UCDP_TEMPLATE_FILEPATHS",
)
opt_local = click.option(
    "--local/--no-local",
    "-l/-L",
    default=None,
    is_flag=True,
    help="List local/non-local modules only.",
)
opt_check = click.option(
    "--check",
    default=False,
    is_flag=True,
    help="Report an error if any file changes.",
)
opt_create = click.option(
    "--create",
    "-c",
    default=False,
    is_flag=True,
    help="Create missing inplace files.",
)


def defines2data(defines: list[str]) -> dict[str, str]:
    """Convert defines to data."""
    return dict(define.split("=", 1) if "=" in define else (define, None) for define in defines)


def read_file(filepath: Path) -> Iterator[str]:
    """Read File."""
    with filepath.open() as file:
        for line in file:
            line = line.strip()  # noqa: PLW2901
            if line.startswith("#"):
                continue
            if line:
                yield line
