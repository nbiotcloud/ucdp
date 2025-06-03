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

"""Code Generator based of FileLists."""

import sys
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from contextlib import AbstractContextManager, contextmanager
from pathlib import Path
from typing import Any

from makolator import Config, Datamodel, Existing, Makolator
from uniquer import uniquelist

from .cache import CACHE
from .filelistparser import FileListParser
from .logging import LOGGER
from .modbase import BaseMod
from .modfilelist import iter_modfilelists
from .object import Object
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
    with extend_sys_path(paths, use_env_default=True):
        for path in sys.path:
            template_paths.extend(Path(path).glob("*/ucdp-templates/"))
    return uniquelist(template_paths)


def get_makolator(
    show_diff: bool = False,
    verbose: bool = True,
    paths: Iterable[Path] | None = None,
    create: bool = False,
    force: bool | None = None,
) -> Makolator:
    """
    Create Makolator.

    Keyword Args:
        show_diff: Show Changes.
        verbose: Display updated files.
        paths: Search Path For Data Model And Template Files.
        create: Create missing inplace files.
        force: overwrite existing files.
    """
    diffout = print if show_diff else None
    template_paths = get_template_paths(paths=paths)
    if force is True:
        existing = Existing.OVERWRITE
    elif force is None:
        existing = Existing.KEEP_TIMESTAMP
    else:
        existing = Existing.KEEP

    config = Config(
        template_paths=template_paths,
        marker_linelength=80,
        diffout=diffout,
        verbose=verbose,
        cache_path=CACHE.templates_path,
        track=True,
        create=create,
        existing=existing,
    )
    return Makolator(config=config)


def get_datamodel(top: Top | BaseMod, data: Data | None = None) -> Datamodel:
    """Create Data Model."""
    datamodel = Datamodel()
    if isinstance(top, BaseMod):
        top = Top.from_mod(top)
    if data:
        datamodel.__dict__.update(data)
    datamodel.top = top
    return datamodel


class Generator(Object):
    """Generator."""

    makolator: Makolator
    maxworkers: int | None = None
    check: bool = False
    no_stat: bool = False

    def __enter__(self) -> "Generator":
        LOGGER.debug("%s", self.makolator.config)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        makolator = self.makolator
        config = makolator.config
        tracker = makolator.tracker
        if not self.no_stat and config.verbose and config.track:
            print(tracker.stat)
        if self.check:
            assert config.track
            if tracker.total != tracker.identical:
                modified = tracker.total - tracker.identical
                LOGGER.error("%d files modified", modified)

    @contextmanager
    def top(
        self,
        top: Top | BaseMod,
        data: Data | None = None,
    ) -> AbstractContextManager[Top]:
        """Initialize Data Model."""
        makolator = self.makolator
        makolator.datamodel = datamodel = get_datamodel(top, data=data)
        yield datamodel.top

    def generate(
        self,
        top: Top | BaseMod,
        name: str,
        target: str | None = None,
        paths: Iterable[Path] | None = None,
        filelistparser: FileListParser | None = None,
        maxlevel: int | None = None,
        data: Data | None = None,
    ):
        """
        Generate for Top-Module.

        Args:
            top: Top
            name: Filelist Name

        Keyword Args:
            target: Target Filter
            paths: Search Path For Data Model And Template Files.
            filelistparser: Specific File List Parser
            maxlevel: Stop Generation on given hierarchy level.
            data: Data added to the datamodel.
        """
        with self.top(top, data=data) as top_:
            modfilelists = iter_modfilelists(
                top_.mod,
                name,
                target=target,
                filelistparser=filelistparser,
                replace_envvars=True,
                maxlevel=maxlevel,
            )
            with extend_sys_path(paths, use_env_default=True):
                self._generate(modfilelists)

    def _generate(self, modfilelists) -> None:
        makolator = self.makolator

        def _inplace(template_filepaths, filepath, context):
            if not filepath.exists() and not makolator.config.create:
                LOGGER.error("Inplace file %r missing", str(filepath))
            else:
                makolator.inplace(template_filepaths, filepath, context=context)

        def _gen(template_filepaths, filepath, context):
            makolator.gen(template_filepaths, filepath, context=context)

        with ThreadPoolExecutor(max_workers=self.maxworkers) as exe:
            jobs = []  # type: ignore [var-annotated]
            for mod, modfilelist in modfilelists:
                gen = modfilelist.get_gen(mod, modfilelist.flavor)
                if gen == "no":
                    continue
                if gen == "custom":
                    jobs.append(exe.submit(modfilelist.generate, mod))
                    continue
                filepaths: tuple[Path, ...] = modfilelist.filepaths or ()  # type: ignore[assignment]
                template_filepaths: tuple[Path, ...] = modfilelist.template_filepaths or ()  # type: ignore[assignment]
                inc_filepaths: tuple[Path, ...] = modfilelist.inc_filepaths or ()  # type: ignore[assignment]
                inc_template_filepaths: tuple[Path, ...] = modfilelist.inc_template_filepaths or ()  # type: ignore[assignment]
                ctx = {"mod": mod, "modfilelist": modfilelist}
                if gen == "inplace":
                    jobs.extend(exe.submit(_inplace, inc_template_filepaths, path, ctx) for path in inc_filepaths)
                    jobs.extend(exe.submit(_inplace, template_filepaths, path, ctx) for path in filepaths)
                else:
                    jobs.extend(exe.submit(_gen, inc_template_filepaths, path, ctx) for path in inc_filepaths)
                    jobs.extend(exe.submit(_gen, template_filepaths, path, ctx) for path in filepaths)
            for job in jobs:
                job.result()


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
    create: bool = False,
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
        create: Create missing inplace files.
    """
    makolator = makolator or get_makolator(paths=paths, create=create)
    with Generator(makolator=makolator, maxworkers=maxworkers) as generator:
        generator.generate(
            top=top,
            name=name,
            target=target,
            filelistparser=filelistparser,
            maxlevel=maxlevel,
            data=data,
        )


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
    with Generator(makolator=makolator, no_stat=True) as generator:
        with generator.top(top, data=data) as top_:
            modfilelists = iter_modfilelists(
                top_.mod,
                name,
                target=target,
                filelistparser=filelistparser,
                replace_envvars=True,
                maxlevel=maxlevel,
            )
            with extend_sys_path(paths, use_env_default=True):
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
    no_stat: bool = False,
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
        no_stat: Skip Statistics
    """
    makolator = makolator or get_makolator(paths=paths)
    with Generator(makolator=makolator, no_stat=no_stat) as generator:
        with generator.top(top, data=data):
            with extend_sys_path(paths, use_env_default=True):
                makolator.gen(template_filepaths, dest=genfile)


def render_inplace(
    top: Top | BaseMod,
    template_filepaths: Paths,
    inplacefile: Path,
    makolator: Makolator | None = None,
    ignore_unknown: bool = False,
    paths: Iterable[Path] | None = None,
    data: Data | None = None,
    no_stat: bool = False,
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
        no_stat: Skip Statistics
    """
    makolator = makolator or get_makolator(paths=paths)
    with Generator(makolator=makolator, no_stat=no_stat) as generator:
        with generator.top(top, data=data):
            with extend_sys_path(paths, use_env_default=True):
                makolator.inplace(template_filepaths, filepath=inplacefile, ignore_unknown=ignore_unknown)
