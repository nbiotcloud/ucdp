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

"""Module File List."""

from collections.abc import Iterable, Iterator
from inspect import getfile, getmro
from pathlib import Path
from typing import Annotated, Any

from pydantic.functional_validators import BeforeValidator

from .consts import Gen
from .filelistparser import FileListParser
from .iterutil import namefilter
from .modbase import BaseMod
from .moditer import ModPostIter
from .object import Field, NamedLightObject
from .pathutil import improved_resolve

Paths = tuple[Path, ...]
"""Paths."""

StrPaths = tuple[str | Path, ...]
"""StrPaths."""


def _to_paths(values: Iterable[Any]) -> tuple[Path, ...]:
    if isinstance(values, str):
        return (Path(values),)
    return tuple(Path(value) for value in values)


ToPaths = Annotated[StrPaths, BeforeValidator(_to_paths)]
"""ToPaths."""

Placeholder = dict[str, Any]
"""
Module Attributes for File Path.

These placeholder are filled during `resolve`.
"""


class ModFileList(NamedLightObject):
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
    is_leaf: bool = False
    merge: bool = False

    @staticmethod
    def get_mod_placeholder(mod) -> Placeholder:
        """Get Module Placeholder."""
        return {"mod": mod}

    @staticmethod
    def get_cls_placeholder(cls) -> Placeholder:
        """Get Class Placeholder."""
        return {
            "cls": cls,
            "modref": cls.get_modref(),
        }


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
        name: Module name.
        target: Implementation Target

    """
    for modfilelist in modfilelists:
        # Skip Non-Related File Lists
        if modfilelist.name != name:
            continue
        # Skip Non-Matching Target
        if target and modfilelist.target and not namefilter(modfilelist.target)(target):
            continue
        # Found
        yield modfilelist
        if not modfilelist.merge:
            break


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
    modfilelists = tuple(search_modfilelists(mod.filelists, name, target=target))
    if not modfilelists:
        return None
    for modfilelist in modfilelists:
        mod_placeholder = modfilelist.get_mod_placeholder(mod)
        # parser
        filelistparser = filelistparser or FileListParser()
        # resolve filepaths, inc_dirs
        inc_dirs: list[Path] = []
        inc_filepaths: list[Path] = []
        filepaths: list[Path] = []
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
    baseclss = _get_baseclss(mod.__class__)
    for basecls in reversed(baseclss):
        basemodfilelists = tuple(search_modfilelists(basecls.filelists, name, target=target))
        if not basemodfilelists:
            continue
        for basemodfilelist in basemodfilelists:
            cls_placeholder = basemodfilelist.get_cls_placeholder(basecls)
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
    return modfilelist.new(
        inc_dirs=tuple(inc_dirs),
        inc_filepaths=tuple(inc_filepaths),
        filepaths=tuple(filepaths),
        dep_filepaths=tuple(dep_filepaths),
        dep_inc_dirs=tuple(dep_inc_dirs),
        template_filepaths=tuple(template_filepaths),
        inc_template_filepaths=tuple(inc_template_filepaths),
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
        name: Name.
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
        modfilelist = resolve_modfilelist(
            mod,
            name=name,
            target=target,
            filelistparser=filelistparser,
            replace_envvars=replace_envvars,
        )
        if modfilelist is None:
            continue
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


def _get_baseclss(cls):
    clss = []
    for basecls in getmro(cls):
        if basecls is BaseMod:
            break
        clss.append(basecls)
    return clss
