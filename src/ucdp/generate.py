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
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from makolator import Config, Makolator

from .filelistparser import FileListParser
from .logging import LOGGER
from .modbase import BaseMod
from .modfilelist import iter_modfilelists


def get_makolator(show_diff: bool = False, verbose=True) -> Makolator:
    """Create Makolator."""
    template_paths: list[Path] = []
    for path in sys.path:
        template_paths.extend(Path(path).glob("*/templates/"))
    diffout = print if show_diff else None
    config = Config(template_paths=template_paths, marker_linelength=80, diffout=diffout, verbose=verbose)
    return Makolator(config=config)


def generate(
    topmod: BaseMod,
    name: str,
    target: str | None = None,
    filelistparser: FileListParser | None = None,
    makolator: Makolator | None = None,
    maxlevel: int | None = None,
):
    """
    Generate for Top-Module.

    Args:
        topmod: Top Module
        name: Filelist Name

    Keyword Args:
        target: Target Filter
        filelistparser: Specific File List Parser
        makolator: Specific Makolator
        maxlevel: Stop Generation on given hierarchy level.
    """
    makolator = makolator or get_makolator()
    LOGGER.debug("%s", makolator.config)
    modfilelists = iter_modfilelists(
        topmod,
        name,
        target=target,
        filelistparser=filelistparser,
        replace_envvars=True,
        maxlevel=maxlevel,
    )
    with ThreadPoolExecutor() as executor:
        jobs = []
        for mod, modfilelist in modfilelists:
            if modfilelist.gen == "no":
                continue
            filepaths: tuple[Path, ...] = modfilelist.filepaths or ()  # type: ignore[assignment]
            template_filepaths: tuple[Path, ...] = modfilelist.template_filepaths or ()  # type: ignore[assignment]
            context = {"mod": mod}
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
    topmod: BaseMod,
    name: str,
    target: str | None = None,
    filelistparser: FileListParser | None = None,
    makolator: Makolator | None = None,
    maxlevel: int | None = None,
    dry_run: bool = False,
):
    """
    Remove Generated Files for Top-Module.

    Args:
        topmod: Top Module
        name: Filelist Name

    Keyword Args:
        target: Target Filter
        filelistparser: Specific File List Parser
        makolator: Specific Makolator
        maxlevel: Stop Generation on given hierarchy level.
        dry_run: Do nothing.
    """
    makolator = makolator or get_makolator()
    LOGGER.debug("%s", makolator.config)
    modfilelists = iter_modfilelists(
        topmod,
        name,
        target=target,
        filelistparser=filelistparser,
        replace_envvars=True,
        maxlevel=maxlevel,
    )
    for _, modfilelist in modfilelists:
        filepaths: tuple[Path, ...] = modfilelist.filepaths or ()  # type: ignore[assignment]
        if modfilelist.gen == "gen":
            for filepath in filepaths:
                print("Removing '{filepath!s}'")
                if not dry_run:
                    filepath.unlink(missing_ok=True)
    if dry_run:
        print("DRY RUN. Nothing done.")
