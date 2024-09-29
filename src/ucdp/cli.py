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
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path

import click
from click_bash42_completion import patch
from pydantic import BaseModel, ConfigDict
from rich.console import Console
from rich.logging import RichHandler
from rich.pretty import pprint
from rich.table import Table

from ._cligroup import MainGroup
from .cache import CACHE
from .cliutil import (
    PathType,
    arg_filelist,
    arg_template_filepaths,
    arg_top,
    auto_path,
    auto_top,
    defines2data,
    guess_path,
    opt_defines,
    opt_dry_run,
    opt_file,
    opt_filepath,
    opt_maxlevel,
    opt_maxworkers,
    opt_path,
    opt_show_diff,
    opt_tag,
    opt_target,
)
from .consts import PATH
from .fileset import FileSet
from .finder import find
from .generate import clean, generate, get_makolator, render_generate, render_inplace
from .iterutil import namefilter
from .loader import load
from .modfilelist import iter_modfilelists
from .modtopref import PAT_TOPMODREF, TopModRef
from .pathutil import relative
from .top import Top

patch()


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


@click.group(cls=MainGroup, context_settings={"help_option_names": ["-h", "--help"]})
@click.option("-v", "--verbose", count=True, help="Increase Verbosity.")
@click.option("-C", "--no-cache", is_flag=True, help="Disable Caching.")
@click.version_option()
@click.pass_context
def ucdp(ctx, verbose=0, no_cache=False):
    """Unified Chip Design Platform."""
    level = _LOGLEVELMAP.get(verbose, logging.DEBUG)
    handler = RichHandler(
        show_time=False,
        show_path=False,
        rich_tracebacks=True,
        tracebacks_suppress=("click",),
        console=Console(stderr=True),
    )
    logging.basicConfig(level=level, format="%(message)s", handlers=[handler])
    if no_cache:
        CACHE.disable()
    ctx.obj = Ctx(console=Console(log_time=False, log_path=False))


pass_ctx = click.make_pass_decorator(Ctx)


def get_group(help=None):  # pragma: no cover
    """Create Command Group."""

    @click.group(help=help)
    @click.pass_context
    def group(ctx):
        ctx.obj = Ctx(console=Console(log_time=False, log_path=False))

    return group


def load_top(ctx: Ctx, top: str, paths: Iterable[str | Path], quiet: bool = False) -> Top:
    """Load Top Module."""
    lpaths = [Path(path) for path in paths]
    # Check if top seems to be some kind of file path
    topmodref = TopModRef.cast(guess_path(top) or top)
    if quiet:
        return load(topmodref, paths=lpaths)
    with ctx.console.status(f"Loading '{topmodref!s}'"):
        result = load(topmodref, paths=lpaths)
    ctx.console.log(f"'{topmodref!s}' checked.")
    return result


@ucdp.command(
    help=f"""
Load Data Model and Check.

TOP: Top Module. {PAT_TOPMODREF}. Environment Variable 'UCDP_TOP'
"""
)
@arg_top
@opt_path
@click.option("--stat", default=False, is_flag=True, help="Show Statistics.")
@pass_ctx
def check(ctx, top, path, stat=False):
    """Check."""
    top = load_top(ctx, top, path)
    if stat:
        print("Statistics:")
        for name, value in top.get_stat().items():
            print(f"  {name}: {value}")


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
@opt_show_diff
@opt_maxworkers
@opt_defines
@pass_ctx
def gen(ctx, top, path, filelist, target=None, show_diff=False, maxworkers=None, define=None):
    """Generate."""
    top = load_top(ctx, top, path)
    makolator = get_makolator(show_diff=show_diff, paths=path)
    data = defines2data(define)
    for item in filelist or ["*"]:
        generate(top, item, target=target, makolator=makolator, maxworkers=maxworkers, data=data)


@ucdp.command(
    help=f"""
Load Data Model and Render Template and Create File.

TOP: Top Module. {PAT_TOPMODREF}. Environment Variable 'UCDP_TOP'

TEMPLATE_FILEPATHS: Templates to render. Environment Variable 'UCDP_TEMPLATE_FILEPATHS'
                    Templates in `templates` folders are found automatically.

GENFILE: Generated File.
"""
)
@arg_top
@opt_path
@arg_template_filepaths
@click.argument("genfile", type=PathType, shell_complete=auto_path, nargs=1)
@opt_show_diff
@opt_defines
@pass_ctx
def rendergen(ctx, top, path, template_filepaths, genfile, show_diff=False, define=None):
    """Render Generate."""
    top = load_top(ctx, top, path)
    makolator = get_makolator(show_diff=show_diff, paths=path)
    data = defines2data(define)
    render_generate(top, template_filepaths, genfile=genfile, makolator=makolator, data=data)


@ucdp.command(
    help=f"""
Load Data Model and Render Template and Update File.

TOP: Top Module. {PAT_TOPMODREF}. Environment Variable 'UCDP_TOP'

TEMPLATE_FILEPATHS: Templates to render. Environment Variable 'UCDP_TEMPLATE_FILEPATHS'
                    Templates in `templates` folders are found automatically.

INPLACEFILE: Inplace File.
"""
)
@arg_top
@opt_path
@arg_template_filepaths
@click.argument("inplacefile", type=PathType, shell_complete=auto_path, nargs=1)
@opt_show_diff
@opt_defines
@click.option("--ignore_unknown", "-i", default=False, is_flag=True, help="Ignore Unknown Placeholder.")
@pass_ctx
def renderinplace(ctx, top, path, template_filepaths, inplacefile, show_diff=False, define=None, ignore_unknown=False):
    """Render Inplace."""
    top = load_top(ctx, top, path)
    makolator = get_makolator(show_diff=show_diff, paths=path)
    data = defines2data(define)
    render_inplace(
        top,
        template_filepaths,
        inplacefile=inplacefile,
        makolator=makolator,
        data=data,
        ignore_unknown=ignore_unknown,
    )


@ucdp.command(
    help=f"""
Load Data Model and REMOVE Generated Files.

TOP: Top Module. {PAT_TOPMODREF}. Environment Variable 'UCDP_TOP'

FILELIST: Filelist name to render. Environment Variable 'UCDP_FILELIST'
"""
)
@arg_top
@opt_path
@arg_filelist
@opt_target
@opt_show_diff
@opt_dry_run
@opt_maxworkers
@pass_ctx
def cleangen(ctx, top, path, filelist, target=None, show_diff=False, maxworkers=None, dry_run=False):
    """Clean Generated Files."""
    top = load_top(ctx, top, path)
    makolator = get_makolator(show_diff=show_diff, paths=path)
    for item in filelist or ["*"]:
        clean(top, item, target=target, makolator=makolator, maxworkers=maxworkers, dry_run=dry_run)


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
@opt_file
@pass_ctx
def filelist(ctx, top, path, filelist, target=None, file=None):
    """File List."""
    # Load quiet, otherwise stdout is messed-up
    top = load_top(ctx, top, path, quiet=True)
    for item in filelist or ["*"]:
        fileset = FileSet.from_mod(top.mod, item, target=target)
        for line in fileset:
            print(line, file=file)


@ucdp.command(
    help=f"""
Load Data Model and Show File Information

TOP: Top Module. {PAT_TOPMODREF}. Environment Variable 'UCDP_TOP'

FILELIST: Filelist name to render. Environment Variable 'UCDP_FILELIST'
"""
)
@arg_top
@opt_path
@arg_filelist
@opt_target
@opt_maxlevel
@click.option("--minimal", "-m", default=False, is_flag=True, help="Skip defaults.")
@opt_file
@pass_ctx
def fileinfo(ctx, top, path, filelist, target=None, maxlevel=None, minimal=False, file=None):
    """File List."""
    # Load quiet, otherwise stdout is messed-up
    top = load_top(ctx, top, path, quiet=True)
    console = Console(file=file) if file else ctx.console
    for item in filelist or ["*"]:
        data = defaultdict(list)
        for mod, modfilelist in iter_modfilelists(top.mod, item, target=target, maxlevel=maxlevel):
            data[str(mod)].append(modfilelist.model_dump(exclude_defaults=minimal))
        pprint(dict(data), indent_guides=False, console=console)


@ucdp.command(
    help="""
              List Available Data Models.

              PATTERN: Limit list to these modules only.

              Examples:

                ucdp ls

                ucdp ls -n

                ucdp ls glbl_lib*
              """
)
@opt_path
@click.argument("pattern", nargs=-1, shell_complete=auto_top)
@click.option("--names", "-n", default=False, is_flag=True, help="Just print names")
@click.option("--top", "-t", default=False, is_flag=True, help="List loadable top modules only.")
@click.option("--tb", "-b", default=False, is_flag=True, help="List testbench modules only.")
@click.option("--generic-tb", "-g", default=False, is_flag=True, help="List Generic Testbench modules only.")
@click.option("--local/--no-local", "-l/-L", default=None, is_flag=True, help="List local/non-local modules only.")
@click.option("--base", "-B", default=False, is_flag=True, help="Show Base Classes.")
@click.option("--filepath", "-f", default=False, is_flag=True, help="Show File Path.")
@click.option("--abs-filepath", "-F", default=False, is_flag=True, help="Show Absolute File Path.")
@opt_tag
@pass_ctx
def ls(  # noqa: C901
    ctx,
    path,
    pattern=None,
    names=False,
    top=False,
    tb=False,
    local=None,
    generic_tb=False,
    tag=None,
    base=False,
    filepath=False,
    abs_filepath=False,
):
    """List Modules."""
    with ctx.console.status("Searching"):
        infos = find(path, patterns=pattern, local=local)
    if top:
        infos = [info for info in infos if info.is_top]
    if tb:
        infos = [info for info in infos if info.tb]
    if generic_tb:
        infos = [info for info in infos if info.tb == "Generic"]
    if tag:
        filter_ = namefilter(tag)
        infos = [info for info in infos if any(filter_(tag) for tag in info.tags)]

    def fill_row(row, info):
        if base:
            row.append(info.modbasecls.__name__)
        if filepath:
            row.append(str(relative(info.filepath)))
        if abs_filepath:
            row.append(str(info.filepath))

    if names:
        for info in infos:
            row = [info.topmodref]
            fill_row(row, info)
            print(*row)
    else:
        table = Table(expand=filepath or abs_filepath)
        table.add_column("Reference")
        table.add_column("Top", justify="center")
        table.add_column("Tb ", justify="center")
        table.add_column("Tags")
        if base:
            table.add_column("Bases on", justify="right")
        if filepath:
            table.add_column("Filepath")
        if abs_filepath:
            table.add_column("Absolute Filepath")
        for info in infos:
            row = [
                str(info.topmodref),
                "X" if info.is_top else "",
                "X" if info.tb else "",
                ",".join(sorted(info.tags)),
            ]
            fill_row(row, info)
            table.add_row(*row)
        ctx.console.print(table)


@ucdp.command(
    help=f"""
Load Data Model and Show Module Overview.

TOP: Top Module. {PAT_TOPMODREF}. Environment Variable 'UCDP_TOP'
"""
)
@arg_top
@opt_path
@click.option("--minimal", "-m", default=False, is_flag=True, help="Skip modules without specific details")
@opt_filepath
@opt_tag
@pass_ctx
def overview(ctx, top, path, minimal=False, file=None, tag=None):
    """Overview."""
    # Load quiet, otherwise stdout is messed-up
    top = load_top(ctx, top, path, quiet=True)
    data = {"minimal": minimal, "tags": tag}
    render_generate(top, [PATH / "ucdp-templates" / "overview.txt.mako"], genfile=file, data=data, no_stat=True)


@ucdp.group(context_settings={"help_option_names": ["-h", "--help"]})
def info():
    """Information."""


@info.command()
@pass_ctx
def examples(ctx):
    """Path to Examples."""
    examples_path = Path(__file__).parent / "examples"
    print(str(examples_path))


@info.command()
@opt_path
@pass_ctx
def template_paths(ctx, path):
    """Template Paths."""
    makolator = get_makolator(paths=path)
    for template_path in makolator.config.template_paths:
        print(str(template_path))
