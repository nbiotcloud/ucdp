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

"""Command Line Interface - Utilities."""

from pathlib import Path

import click

arg_top = click.argument("top", envvar="UCDP_TOP")
opt_path = click.option(
    "--path",
    "-p",
    default=[],
    multiple=True,
    envvar="UCDP_PATH",
    help="""
Search Path For Data Model And Template Files.
This option can be specified multiple times.
Environment Variable 'UCDP_PATH'.
""",
)
arg_filelist = click.argument("filelist", nargs=-1, required=True, envvar="UCDP_FILELIST")
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
opt_maxworkers = click.option("--maxworkers", "-J", type=int, help="Maximum Number of Processes.")
opt_defines = click.option(
    "--define",
    "-D",
    multiple=True,
    type=str,
    help="Defines set on the datamodel. Environment Variable 'UCDP_DEFINES'",
    envvar="UCDP_DEFINES",
)
opt_file = click.option("--file", "-o", type=click.File("w"), help="Output to file instead of STDOUT")
opt_filepath = click.option("--file", "-o", type=click.Path(path_type=Path), help="Output to file instead of STDOUT")


def defines2data(defines: list[str]) -> dict[str, str]:
    """Convert defines to data."""
    return dict(define.split("=", 1) if "=" in define else (define, None) for define in defines)
