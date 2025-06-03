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

"""Module File List."""

from collections.abc import Iterable, Iterator
from inspect import getfile
from pathlib import Path
from typing import Annotated, Any, TypeAlias

from matchor import match
from pydantic import PlainSerializer
from pydantic.functional_validators import BeforeValidator

from .consts import Gen
from .filelistparser import FileListParser
from .iterutil import namefilter
from .modbase import BaseMod, get_modbaseclss
from .moditer import ModPostIter
from .object import Field, IdentObject, Object
from .pathutil import improved_resolve

Paths = tuple[Path, ...]
"""Paths."""

StrPaths = tuple[str | Path, ...]
"""StrPaths."""


def _to_paths(values: Iterable[Any]) -> tuple[Path, ...]:
    if isinstance(values, str):
        return (Path(values),)
    return tuple(Path(value) for value in values)


ToPaths = Annotated[
    StrPaths,
    BeforeValidator(_to_paths),
    PlainSerializer(lambda paths: tuple(path.as_posix() for path in paths), return_type=tuple),
]
"""ToPaths."""

Placeholder = dict[str, Any]
"""
Module Attributes for File Path.

These placeholder are filled during `resolve`.
"""

Flavor: TypeAlias = Object | str
Flavors: TypeAlias = tuple[Flavor, ...]


class ModFileList(IdentObject):
    """
    Module File List.

    Attributes:
        gen: Generate Mode
        targets: Implementation Targets
        inc_dirs: Include Directories
        inc_filepaths: Include File paths relative to module
        filepaths: File paths relative to module
        dep_filepaths: Dependency Filepaths
        dep_inc_dirs: Dependency Include Directories
        template_filepaths: Template Filepaths
        inc_template_filepaths: Template Filepaths
        is_leaf: Do not include file lists of sub modules
    """

    gen: Gen = "no"
    target: str | None = None
    inc_dirs: ToPaths = Field(default=(), strict=False)
    inc_filepaths: ToPaths = Field(default=(), strict=False)
    filepaths: ToPaths = Field(default=(), strict=False)
    dep_inc_dirs: ToPaths = Field(default=(), strict=False)
    dep_filepaths: ToPaths = Field(default=(), strict=False)
    template_filepaths: ToPaths = Field(default=(), strict=False)
    inc_template_filepaths: ToPaths = Field(default=(), strict=False)
    flavors: Flavors | None = None
    flavor: Flavor | None = None
    is_leaf: bool = False

    @staticmethod
    def get_mod_placeholder(mod: BaseMod, **kwargs) -> Placeholder:
        """Get Module Placeholder."""
        return {"mod": mod, **kwargs}

    @staticmethod
    def get_cls_placeholder(modcls, **kwargs) -> Placeholder:
        """Get Class Placeholder."""
        return {
            "cls": modcls,
            "modref": modcls.get_modref(),
            **kwargs,
        }

    def get_flavors(self, mod: BaseMod) -> Flavors | None:
        """Determine Flavors."""
        return self.flavors

    def generate(self, mod: BaseMod) -> None:
        """Custom Generate Function."""
        raise NotImplementedError

    def get_gen(self, mod: BaseMod, flavor: Flavor | None) -> Gen:
        """Get Generate."""
        return self.gen


ModFileLists = tuple[ModFileList, ...]
"""ModFileLists."""


def search_modfilelists(
    modfilelists: Iterable[ModFileList],
    name: str,
    target: str | None = None,
) -> Iterator[ModFileList]:
    """Search Matching File List.

    Args:
        modfilelists: ModFileLists.
        name: Filelist name or pattern.
        target: Implementation Target

    """
    for modfilelist in modfilelists:
        # Skip Non-Related File Lists
        if not match(modfilelist.name, name):
            continue
        # Skip Non-Matching Target
        if target and modfilelist.target and not namefilter(modfilelist.target)(target):
            continue
        # Found
        yield modfilelist


def resolve_modfilelist(
    mod: BaseMod,
    name: str,
    target: str | None = None,
    filelistparser: FileListParser | None = None,
    replace_envvars: bool = False,
) -> ModFileList | None:
    """Create `ModFileList` for `mod`.

    Args:
        mod: Module.
        name: Name.
        target: Implementation Target
        filelistparser: FileListParser
        replace_envvars: Resolve Environment Variables.
    """
    for modfilelist in resolve_modfilelists(
        mod, name, target=target, filelistparser=filelistparser, replace_envvars=replace_envvars
    ):
        return modfilelist
    return None


def resolve_modfilelists(
    mod: BaseMod,
    name: str,
    target: str | None = None,
    filelistparser: FileListParser | None = None,
    replace_envvars: bool = False,
) -> Iterator[ModFileList]:
    """Create `ModFileList` for `mod`.

    Args:
        mod: Module.
        name: Name or Pattern
        target: Implementation Target
        filelistparser: FileListParser
        replace_envvars: Resolve Environment Variables.
    """
    for modfilelist in search_modfilelists(mod.filelists, name, target=target):
        # parser
        filelistparser = filelistparser or FileListParser()
        for flavor in modfilelist.get_flavors(mod) or [None]:
            # resolve filepaths, inc_dirs
            inc_dirs: list[Path] = []
            inc_filepaths: list[Path] = []
            filepaths: list[Path] = []
            mod_placeholder = modfilelist.get_mod_placeholder(mod, flavor=flavor)
            _resolve_mod(
                filelistparser,
                mod,
                mod_placeholder,
                filepaths,
                inc_dirs,
                modfilelist.filepaths,
                modfilelist.inc_dirs,
                replace_envvars,
            )
            _resolve_mod(
                filelistparser,
                mod,
                mod_placeholder,
                inc_filepaths,
                inc_dirs,
                modfilelist.inc_filepaths,
                (),
                replace_envvars,
            )
            # resolve dep_filepaths, dep_inc_dirs
            dep_filepaths: list[Path] = []
            dep_inc_dirs: list[Path] = []
            _resolve_mod(
                filelistparser,
                mod,
                mod_placeholder,
                dep_filepaths,
                dep_inc_dirs,
                modfilelist.dep_filepaths,
                modfilelist.dep_inc_dirs,
                replace_envvars,
            )
            # template_filepaths
            template_filepaths: list[Path] = []
            inc_template_filepaths: list[Path] = []
            baseclss = get_modbaseclss(mod.__class__)
            for basecls in reversed(baseclss):
                for basemodfilelist in search_modfilelists(basecls.filelists, modfilelist.name, target=target):
                    cls_placeholder = basemodfilelist.get_cls_placeholder(basecls, flavor=flavor)
                    _resolve_template_filepaths(
                        basecls,
                        cls_placeholder,
                        template_filepaths,
                        basemodfilelist.template_filepaths,
                        replace_envvars,
                    )
                    _resolve_template_filepaths(
                        basecls,
                        cls_placeholder,
                        inc_template_filepaths,
                        basemodfilelist.inc_template_filepaths,
                        replace_envvars,
                    )
            # result
            yield modfilelist.new(
                inc_dirs=tuple(inc_dirs),
                inc_filepaths=tuple(inc_filepaths),
                filepaths=tuple(filepaths),
                dep_filepaths=tuple(dep_filepaths),
                dep_inc_dirs=tuple(dep_inc_dirs),
                template_filepaths=tuple(template_filepaths),
                inc_template_filepaths=tuple(inc_template_filepaths),
                flavors=(flavor,) if flavor is not None else None,
                flavor=flavor,
            )


def iter_modfilelists(
    topmod: BaseMod,
    name: str,
    target: str | None = None,
    filelistparser: FileListParser | None = None,
    replace_envvars: bool = False,
    maxlevel: int | None = None,
) -> Iterator[tuple[BaseMod, ModFileList]]:
    """Iterate over `ModFileLists`.

    Args:
        topmod: Top Module.
        name: Name or Name Pattern.
        target: Implementation Target
        filelistparser: FileListParser
        replace_envvars: Resolve Environment Variables.
        maxlevel: Stop at maximum iteration level.
    """
    filelistparser = filelistparser or FileListParser()

    # stop at leaf
    def stop_insts(inst: BaseMod):
        for modfilelist in search_modfilelists(inst.filelists, name, target=target):
            if modfilelist.is_leaf:
                return True
        return False

    # iterate
    for mod in ModPostIter(topmod, stop_insts=stop_insts, unique=True, maxlevel=maxlevel):
        for modfilelist in resolve_modfilelists(
            mod,
            name=name,
            target=target,
            filelistparser=filelistparser,
            replace_envvars=replace_envvars,
        ):
            yield mod, modfilelist


def _resolve_mod(
    filelistparser: FileListParser,
    mod: BaseMod,
    placeholder: Placeholder,
    filepaths: list[Path],
    inc_dirs: list[Path],
    add_filepaths: StrPaths,
    add_inc_dirs: StrPaths,
    replace_envvars: bool,
) -> None:
    basefile = Path(getfile(mod.__class__))
    basedir = basefile.parent
    if add_inc_dirs:
        items = (Path(str(filepath).format_map(placeholder)) for filepath in add_inc_dirs)
        filelistparser.parse(inc_dirs, inc_dirs, basedir, items, replace_envvars=replace_envvars, context=str(basefile))
    if add_filepaths:
        items = (Path(str(filepath).format_map(placeholder)) for filepath in add_filepaths)
        filelistparser.parse(
            filepaths,
            inc_dirs,
            basedir,
            items,
            replace_envvars=replace_envvars,
            context=str(basefile),
        )


def _resolve_template_filepaths(
    cls,  # class BaseMod
    placeholder: Placeholder,
    filepaths: list[Path],
    add_filepaths: StrPaths,
    replace_envvars: bool,
):
    basedir = Path(getfile(cls)).parent
    if add_filepaths:
        items = tuple(Path(str(item).format_map(placeholder)) for item in add_filepaths)
        for add_filepath in reversed(items):
            try:
                filepath = improved_resolve(
                    add_filepath,
                    basedir=basedir,
                    replace_envvars=replace_envvars,
                    strict=replace_envvars,
                )
            except FileNotFoundError:
                # Template is found through search path
                filepath = add_filepath
            if filepath not in filepaths:
                filepaths.insert(0, filepath)
