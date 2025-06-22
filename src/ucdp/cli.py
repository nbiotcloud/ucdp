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

"""Command Line Interface."""

import logging
import sys
from collections import defaultdict
from collections.abc import Iterable
from logging import StreamHandler
from pathlib import Path
from typing import Literal

import click
from click_bash42_completion import patch
from pydantic import BaseModel, ConfigDict
from rich import box
from rich.console import Console
from rich.logging import RichHandler
from rich.pretty import pprint
from rich.table import Table

from ._cligroup import MainGroup
from ._logging import HasErrorHandler
from .cache import CACHE
from .cliutil import (
    PathType,
    arg_template_filepaths,
    arg_top,
    arg_tops,
    auto_path,
    defines2data,
    opt_check,
    opt_create,
    opt_defines,
    opt_dry_run,
    opt_file,
    opt_filelist,
    opt_filepath,
    opt_local,
    opt_maxlevel,
    opt_maxworkers,
    opt_path,
    opt_show_diff,
    opt_tag,
    opt_target,
    opt_topsfile,
    read_file,
)
from .consts import PATH
from .create import TB_MAP, TYPE_CHOICES, CreateInfo
from .create import create as create_
from .fileset import FileSet
from .finder import find
from .generate import Generator, clean, get_makolator, render_generate, render_inplace
from .iterutil import namefilter
from .loader import load
from .modfilelist import iter_modfilelists
from .modtopref import PAT_TOPMODREF, TopModRef
from .pathutil import relative
from .top import Top
from .util import LOGGER, guess_path

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
    has_error_handler: HasErrorHandler | None = None

    verbose: int = 0
    no_cache: bool = False
    no_color: bool | None = None

    @staticmethod
    def create(no_color: bool | None = None, **kwargs) -> "Ctx":
        """Create."""
        console = Console(log_time=False, log_path=False, no_color=no_color)
        has_error_handler = HasErrorHandler()
        return Ctx(console=console, has_error_handler=has_error_handler, no_color=no_color, **kwargs)

    def __enter__(self):
        # Logging
        level = _LOGLEVELMAP.get(self.verbose, logging.DEBUG)
        if not self.no_color:
            handler = RichHandler(
                show_time=False,
                show_path=False,
                rich_tracebacks=True,
                console=Console(stderr=True, no_color=self.no_color),
            )
            format_ = "%(message)s"
        else:
            handler = StreamHandler(stream=sys.stderr)
            format_ = "%(levelname)s %(message)s"
        handlers = [handler, self.has_error_handler]
        logging.basicConfig(level=level, format=format_, handlers=handlers)

        # Cache
        if self.no_cache:
            CACHE.disable()

        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type or self.has_error_handler.has_errors:
            if exc_type is KeyboardInterrupt:
                self.console.print("[red]Aborted.")
            else:
                self.console.print("[red][bold]Failed.")
            sys.exit(1)


@click.group(cls=MainGroup, context_settings={"help_option_names": ["-h", "--help"]})
@click.option("-v", "--verbose", count=True, help="Increase Verbosity.")
@click.option("-C", "--no-cache", is_flag=True, help="Disable Caching.")
@click.option("--no-color", is_flag=True, help="Disable Coloring.", envvar="UCDP_NO_COLOR")
@click.version_option()
@click.pass_context
def ucdp(ctx, verbose=0, no_cache=False, no_color=False):
    """Unified Chip Design Platform."""
    ctx.obj = ctx.with_resource(Ctx.create(verbose=verbose, no_cache=no_cache, no_color=no_color))


pass_ctx = click.make_pass_decorator(Ctx)


def get_group(help=None):  # pragma: no cover
    """Create Command Group."""

    @click.group(help=help)
    @click.pass_context
    def group(ctx):
        ctx.obj = Ctx(console=Console(log_time=False, log_path=False))

    return group


def load_top(ctx: Ctx, top: str | TopModRef, paths: Iterable[str | Path], quiet: bool = False) -> Top:
    """Load Top Module."""
    lpaths = [Path(path) for path in paths]
    # Check if top seems to be some kind of file path
    topmodref = TopModRef.cast(guess_path(top) or top) if isinstance(top, str) else top
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
"""
)
@arg_tops
@opt_path
@opt_filelist
@opt_target
@opt_show_diff
@opt_maxworkers
@opt_defines
@opt_local
@opt_topsfile
@opt_check
@opt_create
@pass_ctx
def gen(
    ctx,
    tops,
    path,
    filelist,
    target=None,
    show_diff=False,
    maxworkers=None,
    define=None,
    local=None,
    check=False,
    create=False,
    tops_file=None,
):
    """Generate."""
    tops = list(tops)
    for filepath in tops_file or []:
        tops.extend(read_file(filepath))
    makolator = get_makolator(show_diff=show_diff, paths=path, create=create)
    data = defines2data(define)
    filelist = filelist or ["*"]
    with Generator(makolator=makolator, maxworkers=maxworkers, check=check) as generator:
        for info in find(path, patterns=tuple(tops), local=local, is_top=True):
            try:
                top = load_top(ctx, info.topmodref, path)
            except Exception as exc:
                LOGGER.warning(f"Cannot load '{info.topmodref}'")
                LOGGER.warning(str(exc))
                LOGGER.warning(f"Debug with 'ucdp check {info.topmodref}'")
                continue
            for item in filelist:
                generator.generate(top, item, target=target, data=data)


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
@opt_create
@pass_ctx
def rendergen(ctx, top, path, template_filepaths, genfile, show_diff=False, define=None, create=False):
    """Render Generate."""
    top = load_top(ctx, top, path)
    makolator = get_makolator(show_diff=show_diff, paths=path, create=create)
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
@opt_create
@click.option("--ignore_unknown", "-i", default=False, is_flag=True, help="Ignore Unknown Placeholder.")
@pass_ctx
def renderinplace(
    ctx, top, path, template_filepaths, inplacefile, show_diff=False, define=None, ignore_unknown=False, create=False
):
    """Render Inplace."""
    top = load_top(ctx, top, path)
    makolator = get_makolator(show_diff=show_diff, paths=path, create=create)
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
"""
)
@arg_top
@opt_path
@opt_filelist
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
"""
)
@arg_top
@opt_path
@opt_filelist
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
"""
)
@arg_top
@opt_path
@opt_filelist
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
@arg_tops
@opt_path
@click.option("--names", "-n", default=False, is_flag=True, help="Just print names")
@click.option("--top/--no-top", "-t/-T", default=None, is_flag=True, help="List loadable top modules only.")
@click.option("--tb/--no-tb", "-b/-B", default=None, is_flag=True, help="List testbench modules only.")
@click.option("--generic-tb", "-g", default=False, is_flag=True, help="List Generic Testbench modules only.")
@opt_local
@click.option("--base", "-A", default=False, is_flag=True, help="Show Base Classes.")
@click.option("--filepath", "-f", default=False, is_flag=True, help="Show File Path.")
@click.option("--abs-filepath", "-F", default=False, is_flag=True, help="Show Absolute File Path.")
@opt_tag
@pass_ctx
def ls(  # noqa: C901
    ctx,
    path=None,
    tops=None,
    names=False,
    top=None,
    tb=None,
    local=None,
    generic_tb=False,
    tag=None,
    base=False,
    filepath=False,
    abs_filepath=False,
):
    """List Modules."""
    with ctx.console.status("Searching"):
        infos = find(path, patterns=tops or ["*"], local=local)
    if top is not None:
        infos = [info for info in infos if info.is_top == top]
    if tb is not None:
        infos = [info for info in infos if bool(info.tb) == tb]
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
        table = Table(expand=filepath or abs_filepath, box=box.MARKDOWN)
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
Load Data Model and Module Information.

TOP: Top Module. {PAT_TOPMODREF}. Environment Variable 'UCDP_TOP'
"""
)
@arg_tops
@opt_path
@opt_local
@click.option("--top", "-t", default=None, is_flag=True, help="List loadable top modules only.")
@click.option("--sub", "-S", default=False, is_flag=True, help="Show Submodules.")
@pass_ctx
def modinfo(ctx, tops, path, local, top, sub):
    """Module Information."""
    sep = ""
    for info in find(path, patterns=tops, local=local, is_top=top):
        try:
            top = load_top(ctx, info.topmodref, path, quiet=True)
        except Exception as exc:
            LOGGER.warning(str(exc))
            continue
        print(sep + top.mod.get_info(sub=sub))
        sep = "\n\n"


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


@ucdp.command(
    help="""
Create Datamodel Skeleton.
"""
)
@click.option("--module", "-m", prompt=True, help="Name of the Module")
@click.option("--library", "-l", default=Path().resolve().name, prompt=True, help="Name of the Library")
@click.option("--regf/--no-regf", "-r/-R", default=True, help="Make use of a Register File")
@click.option("--descr", "-d", default="", help="Description")
@click.option("--flavour", "-F", type=click.Choice(TYPE_CHOICES, case_sensitive=False), help="Choose a Module Flavour")
@click.option("--tb/--no-tb", "-t/-T", default=None, help="Create testbench for design module")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing files")
@pass_ctx
def create(
    ctx,
    module,
    library,
    regf,
    descr,
    flavour,
    tb,
    force,
):
    """Let The User Type In The Name And Library Of The File."""
    if flavour is None:
        flavour = prompt_flavour()
        ctx.console.print(f"\nYou choose the flavour [bold blue]{flavour}[/bold blue].\n")

    info = CreateInfo(module=module, library=library, regf=regf, descr=descr, flavour=flavour)

    if info.is_tb:
        if not module.endswith("_tb"):
            LOGGER.warning(f"Your testbench module name {module!r} does not end with '_tb'")

    else:
        if module.endswith("_tb"):
            LOGGER.warning(f"Your design module name {module!r} ends with '_tb'")
        if tb is None:
            answer = click.prompt(
                "Do you want to create a corresponding testbench? (y)es. (n)o.",
                type=click.Choice(["y", "n"]),
                default="y",
            )
            tb = answer == "y"
            ctx.console.print("")
        if tb:
            tbinfo = CreateInfo(module=f"{module}_tb", library=library, regf=regf, descr=descr, flavour=TB_MAP[flavour])
            create_(tbinfo, force)
    create_(info, force)


Type = Literal["AConfigurableMod", "AConfigurableTbMod", "AGenericTbMod", "AMod", "ATailoredMod", "ATbMod"]


def prompt_flavour() -> Type:
    """Let The User Choose The Type Of The File."""
    answer = click.prompt("Do you want to build a (d)esign or (t)estbench?", type=click.Choice(["d", "t"]), default="d")
    if answer == "d":
        answer = click.prompt(
            "Does your design vary more than what `parameter` can cover? (y)es. (n)o.", type=click.Choice(["y", "n"])
        )
        if answer == "y":
            answer = click.prompt(
                "Do you want to use a (c)onfig or (t) shall the parent module tailor the functionality?",
                type=click.Choice(["c", "t"]),
            )
            if answer == "c":
                flavour_ = "AConfigurableMod"

            else:
                flavour_ = "ATailoredMod"

        else:
            flavour_ = "AMod"

    else:
        answer = click.prompt(
            "Do you want to build a generic testbench which tests similar modules? (y)es. (n)o.",
            type=click.Choice(["y", "n"]),
        )
        if answer == "y":
            answer = click.prompt(
                "Do you want to automatically adapt your testbench to your (g) dut or use a (c)onfig?",
                type=click.Choice(["g", "c"]),
            )
            if answer == "c":
                flavour_ = "AConfigurableTbMod"

            else:
                flavour_ = "AGenericTbMod"

        else:
            flavour_ = "ATbMod"

    return flavour_
