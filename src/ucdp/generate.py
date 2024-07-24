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

"""Code Generator based of FileLists."""

import sys
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from makolator import Config, Datamodel, Makolator
from uniquer import uniquelist

from .filelistparser import FileListParser
from .logging import LOGGER
from .modbase import BaseMod
from .modfilelist import iter_modfilelists
from .top import Top
from .util import extend_sys_path

Paths = Path | Iterable[Path]
Data = dict[str, Any]


def get_template_paths(paths: Iterable[Path] | None = None) -> list[Path]:
    """
    Determine Template Paths.

    Keyword Args:
        paths: Search Path For Data Model And Template Files.
    """
    template_paths: list[Path] = []
    with extend_sys_path(paths):
        for path in sys.path:
            template_paths.extend(Path(path).glob("*/ucdp-templates/"))
    return uniquelist(template_paths)


def get_makolator(show_diff: bool = False, verbose=True, paths: Iterable[Path] | None = None) -> Makolator:
    """
    Create Makolator.

    Keyword Args:
        show_diff: Show Changes.
        verbose: Display updated files.
        paths: Search Path For Data Model And Template Files.
    """
    diffout = print if show_diff else None
    template_paths = get_template_paths(paths=paths)
    config = Config(template_paths=template_paths, marker_linelength=80, diffout=diffout, verbose=verbose)
    return Makolator(config=config)


def generate(
    top: Top | BaseMod,
    name: str,
    target: str | None = None,
    filelistparser: FileListParser | None = None,
    makolator: Makolator | None = None,
    maxlevel: int | None = None,
    maxworkers: int | None = None,
    paths: Iterable[Path] | None = None,
    data: Data | None = None,
):
    """
    Generate for Top-Module.

    Args:
        top: Top
        name: Filelist Name

    Keyword Args:
        target: Target Filter
        filelistparser: Specific File List Parser
        makolator: Specific Makolator
        maxlevel: Stop Generation on given hierarchy level.
        maxworkers: Maximal Parallelism.
        paths: Search Path For Data Model And Template Files.
        data: Data added to the datamodel.
    """
    makolator = makolator or get_makolator(paths=paths)
    LOGGER.debug("%s", makolator.config)
    top = init_datamodel(makolator.datamodel, top, data=data)
    modfilelists = iter_modfilelists(
        top.mod,
        name,
        target=target,
        filelistparser=filelistparser,
        replace_envvars=True,
        maxlevel=maxlevel,
    )
    with extend_sys_path(paths):
        with ThreadPoolExecutor(max_workers=maxworkers) as executor:
            jobs = []
            for mod, modfilelist in modfilelists:
                if modfilelist.gen == "no":
                    continue
                filepaths: tuple[Path, ...] = modfilelist.filepaths or ()  # type: ignore[assignment]
                template_filepaths: tuple[Path, ...] = modfilelist.template_filepaths or ()  # type: ignore[assignment]
                context = {"mod": mod, "modfilelist": modfilelist}
                if modfilelist.gen == "inplace":
                    for filepath in filepaths:
                        if not filepath.exists():
                            LOGGER.error("Inplace file %r missing", str(filepath))
                            continue
                        jobs.append(executor.submit(makolator.inplace, template_filepaths, filepath, context=context))
                elif template_filepaths:
                    jobs.extend(
                        executor.submit(makolator.gen, template_filepaths, filepath, context=context)
                        for filepath in filepaths
                    )
                else:
                    LOGGER.error(f"No 'template_filepaths' defined for {mod}")
            for job in jobs:
                job.result()


def clean(
    top: Top | BaseMod,
    name: str,
    target: str | None = None,
    filelistparser: FileListParser | None = None,
    makolator: Makolator | None = None,
    maxlevel: int | None = None,
    maxworkers: int | None = None,
    paths: Iterable[Path] | None = None,
    dry_run: bool = False,
    data: Data | None = None,
):
    """
    Remove Generated Files for Top-Module.

    Args:
        top: Top
        name: Filelist Name

    Keyword Args:
        target: Target Filter
        filelistparser: Specific File List Parser
        makolator: Specific Makolator
        maxlevel: Stop Generation on given hierarchy level.
        maxworkers: Maximal Parallelism.
        paths: Search Path For Data Model And Template Files.
        dry_run: Do nothing.
        data: Data added to the datamodel.
    """
    makolator = makolator or get_makolator(paths=paths)
    LOGGER.debug("%s", makolator.config)
    top = init_datamodel(makolator.datamodel, top, data=data)
    modfilelists = iter_modfilelists(
        top.mod,
        name,
        target=target,
        filelistparser=filelistparser,
        replace_envvars=True,
        maxlevel=maxlevel,
    )
    with extend_sys_path(paths):
        with ThreadPoolExecutor(max_workers=maxworkers) as executor:
            jobs = []
            for _, modfilelist in modfilelists:
                filepaths: tuple[Path, ...] = modfilelist.filepaths or ()  # type: ignore[assignment]
                if modfilelist.gen == "full":
                    for filepath in filepaths:
                        print(f"Removing '{filepath!s}'")
                        if not dry_run:
                            jobs.append(executor.submit(filepath.unlink, missing_ok=True))
            for job in jobs:
                job.result()
        if dry_run:
            print("DRY RUN. Nothing done.")


def render_generate(
    top: Top | BaseMod,
    template_filepaths: Paths,
    genfile: Path | None = None,
    makolator: Makolator | None = None,
    paths: Iterable[Path] | None = None,
    data: Data | None = None,
):
    """
    Render Template and Generate File.

    Args:
        top: Top
        template_filepaths: Template Paths

    Keyword Args:
        genfile: Generated File
        makolator: Specific Makolator
        paths: Search Path For Data Model And Template Files.
        data: Data added to the datamodel.
    """
    makolator = makolator or get_makolator(paths=paths)
    LOGGER.debug("%s", makolator.config)
    init_datamodel(makolator.datamodel, top, data=data)
    with extend_sys_path(paths):
        makolator.gen(template_filepaths, dest=genfile)


def render_inplace(
    top: Top | BaseMod,
    template_filepaths: Paths,
    inplacefile: Path,
    makolator: Makolator | None = None,
    ignore_unknown: bool = False,
    paths: Iterable[Path] | None = None,
    data: Data | None = None,
):
    """
    Render Template and Update File.

    Args:
        top: Top
        template_filepaths: Template Paths
        inplacefile: Updated File

    Keyword Args:
        makolator: Specific Makolator
        data: Data added to the datamodel.
        paths: Search Path For Data Model And Template Files.
        ignore_unknown: Ignore unknown inplace markers, instead of raising an error.
    """
    makolator = makolator or get_makolator(paths=paths)
    LOGGER.debug("%s", makolator.config)
    init_datamodel(makolator.datamodel, top, data=data)
    with extend_sys_path(paths):
        makolator.inplace(template_filepaths, filepath=inplacefile, ignore_unknown=ignore_unknown)


def init_datamodel(datamodel: Datamodel, top: Top | BaseMod, data: Data | None = None) -> Top:
    """Initialize Data Model."""
    if isinstance(top, BaseMod):
        top = Top.from_mod(top)
    datamodel.top = top
    if data:
        datamodel.__dict__.update(data)
    return top
