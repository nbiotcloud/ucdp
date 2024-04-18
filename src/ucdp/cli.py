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

"""Command Line Interface."""

import logging
from pathlib import Path

import click
from anytree import Node, RenderTree
from pydantic import BaseModel, ConfigDict
from rich.console import Console
from rich.logging import RichHandler

from .fileset import FileSet
from .generate import generate
from .loader import load
from .moditer import ModPreIter
from .modtopref import PAT_TOPMODREF
from .top import Top
from .util import extend_sys_path

_LOGLEVELMAP = {
    0: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG,
}


class Ctx(BaseModel):
    """Command Line Context."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    console: Console


pass_ctx = click.make_pass_decorator(Ctx)
arg_top = click.argument("top", envvar="UCDP_TOP")
opt_path = click.option(
    "--path",
    "-p",
    default=[],
    multiple=True,
    envvar="UCDP_PATH",
    help="""
Search Path For Data Model Files.
This option can be specified multiple times.
Environment Variable 'UCDP_PATH'.
""",
)
arg_filelist = click.argument("filelist", envvar="UCDP_FILELIST")
opt_target = click.option("--target", "-t", help="Filter File List for Target", envvar="UCDP_TARGET")


def _load_top(ctx, top, path) -> Top:
    with ctx.console.status(f"Loading {top!r}"):
        with extend_sys_path(path):
            return load(top)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("-v", "--verbose", count=True, help="Increase Verbosity.")
@click.version_option()
@click.pass_context
def ucdp(ctx, verbose=0):
    """Unified Chip Design Platform."""
    level = _LOGLEVELMAP.get(verbose, logging.DEBUG)
    handler = RichHandler(show_time=False, show_path=False, rich_tracebacks=True, tracebacks_suppress=("click",))
    logging.basicConfig(level=level, format="%(message)s", handlers=[handler])
    ctx.obj = Ctx(
        console=Console(log_time=False, log_path=False),
    )


@ucdp.command(
    help=f"""
Load Data Model and Check.

TOP: Top Module. {PAT_TOPMODREF}. Environment Variable 'UCDP_TOP'
"""
)
@arg_top
@opt_path
@pass_ctx
def check(ctx, top, path):
    """Check."""
    top = _load_top(ctx, top, path)

    instcnt = len(top.get_mods())
    modcnt = len(top.get_mods(unique=True))
    ctx.console.log(f"{str(top.ref)!r} checked ({instcnt} instances of {modcnt} modules).")


@ucdp.command(
    help=f"""
Load Data Model and Generate Files.

TOP: Top Module. {PAT_TOPMODREF}. Environment Variable 'UCDP_TOP'

FILELIST: Filelist name to render. Environment Variable 'UCDP_FILELIST'
"""
)
@arg_top
@opt_path
@arg_filelist
@opt_target
@pass_ctx
def gen(ctx, top, path, filelist, target=None):
    """Generate."""
    top = _load_top(ctx, top, path)
    generate(top.mod, filelist, target=target)


@ucdp.command(
    help=f"""
Load Data Model and Generate File List.

TOP: Top Module. {PAT_TOPMODREF}. Environment Variable 'UCDP_TOP'

FILELIST: Filelist name to render. Environment Variable 'UCDP_FILELIST'
"""
)
@arg_top
@opt_path
@arg_filelist
@opt_target
@pass_ctx
def filelist(ctx, top, path, filelist, target=None):
    """File List."""
    top = _load_top(ctx, top, path)

    fileset = FileSet.from_mod(top.mod, filelist, target=target)
    for incdir in fileset.incdirs:
        print(f"-incdir {incdir}")
    for libfilepath in fileset.filepaths:
        print(str(libfilepath.path))


@ucdp.command(
    help=f"""
Load Data Model and Show Module Overview.

TOP: Top Module. {PAT_TOPMODREF}. Environment Variable 'UCDP_TOP'
"""
)
@arg_top
@opt_path
@pass_ctx
def overview(ctx, top, path):
    """Overview."""
    top = _load_top(ctx, top, path)
    nodes = {}
    for inst in ModPreIter(top.mod):
        parent = nodes.get(inst.parent.inst, None) if inst.parent else None
        nodes[inst.inst] = Node(name=inst.inst, inst=inst, overview=inst.get_overview() or None, parent=parent)
    root = nodes[top.mod.inst]
    for pre, fill, node in RenderTree(root):
        mod = node.inst
        print(f"{pre}{mod.name}  {mod!r}")
        if node.overview:
            print(fill)
            for line in node.overview.splitlines():
                print(f"{fill}    {line}")
            print(fill)


@ucdp.group(context_settings={"help_option_names": ["-h", "--help"]})
def info():
    """Information."""


@info.command()
@pass_ctx
def examples(ctx):
    """Path to Examples."""
    examples_path = Path(__file__).parent / "examples"
    print(str(examples_path))
