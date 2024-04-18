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

"""File Set."""

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
StrPaths = tuple[str | Path, ...]


def _to_paths(values: Iterable[Any]) -> tuple[Path, ...]:
    return tuple(Path(value) for value in values)


ToPaths = Annotated[StrPaths, BeforeValidator(_to_paths)]

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
        filepaths: File paths relative to module
        incdirs: Include Directories
        dep_filepaths: Dependency Filepaths
        dep_incdirs: Dependency Include Directories
        template_filepaths: Template Filepaths
        is_leaf: Do not include file lists of sub modules
    """

    gen: Gen = "no"
    target: str | None = None
    incdirs: ToPaths = Field(default=(), strict=False)
    filepaths: ToPaths = Field(default=(), strict=False)
    dep_incdirs: ToPaths = Field(default=(), strict=False)
    dep_filepaths: ToPaths = Field(default=(), strict=False)
    template_filepaths: ToPaths = Field(default=(), strict=False)
    is_leaf: bool = False

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


def search_modfilelist(
    modfilelists: Iterable[ModFileList],
    name: str,
    target: str | None = None,
) -> ModFileList | None:
    """Search Matching File List."""
    for modfilelist in modfilelists:
        # Skip Non-Related File Lists
        if modfilelist.name != name:
            continue
        # Skip Non-Matching Target
        if target and modfilelist.target and not namefilter(modfilelist.target)(target):
            continue
        # Found
        return modfilelist
    # Not Found
    return None


def resolve_modfilelist(
    mod: BaseMod,
    name: str,
    target: str | None = None,
    filelistparser: FileListParser | None = None,
) -> ModFileList | None:
    """Create ``ModFileList` for ``mod``."""
    modfilelist = search_modfilelist(mod.filelists, name, target=target)
    if modfilelist is None:
        return None
    mod_placeholder = modfilelist.get_mod_placeholder(mod)
    # parser
    filelistparser = filelistparser or FileListParser()
    # resolve filepaths, incdirs
    filepaths: list[Path] = []
    incdirs: list[Path] = []
    _resolve_mod(
        filelistparser,
        mod,
        mod_placeholder,
        filepaths,
        incdirs,
        modfilelist.filepaths,
        modfilelist.incdirs,
    )
    # resolve dep_filepaths, dep_incdirs
    dep_filepaths: list[Path] = []
    dep_incdirs: list[Path] = []
    _resolve_mod(
        filelistparser,
        mod,
        mod_placeholder,
        dep_filepaths,
        dep_incdirs,
        modfilelist.dep_filepaths,
        modfilelist.dep_incdirs,
    )
    # template_filepaths
    template_filepaths: list[Path] = []
    baseclss = _get_baseclss(mod.__class__)
    for basecls in reversed(baseclss):
        basemodfilelist = search_modfilelist(basecls.filelists, name, target=target)
        if not basemodfilelist:
            continue
        cls_placeholder = basemodfilelist.get_cls_placeholder(basecls)
        _resolve_template_filepaths(
            basecls,
            cls_placeholder,
            template_filepaths,
            basemodfilelist.template_filepaths,
        )
    # result
    return modfilelist.new(
        filepaths=tuple(filepaths),
        incdirs=tuple(incdirs),
        dep_filepaths=tuple(dep_filepaths),
        dep_incdirs=tuple(dep_incdirs),
        template_filepaths=tuple(template_filepaths),
    )


def iter_modfilelists(
    topmod: BaseMod,
    name: str,
    target: str | None = None,
    filelistparser: FileListParser | None = None,
) -> Iterator[tuple[BaseMod, ModFileList]]:
    """Iterate over `ModFileLists`."""
    filelistparser = filelistparser or FileListParser()

    # stop at leaf
    def stop_insts(inst: BaseMod):
        filelist = search_modfilelist(inst.filelists, name, target=target)
        if not filelist:
            return False
        return filelist.is_leaf

    # iterate
    for mod in ModPostIter(topmod, stop_insts=stop_insts, unique=True):
        modfilelist = resolve_modfilelist(mod, name=name, target=target, filelistparser=filelistparser)
        if modfilelist is None:
            continue
        yield mod, modfilelist


def _resolve_mod(
    filelistparser: FileListParser,
    mod: BaseMod,
    placeholder: Placeholder,
    filepaths: list[Path],
    incdirs: list[Path],
    add_filepaths: StrPaths,
    add_incdirs: StrPaths,
) -> None:
    basedir = Path(getfile(mod.__class__)).parent
    if add_incdirs:
        items = (Path(str(filepath).format_map(placeholder)) for filepath in add_incdirs)
        filelistparser.parse(incdirs, incdirs, basedir, items)
    if add_filepaths:
        items = (Path(str(filepath).format_map(placeholder)) for filepath in add_filepaths)
        filelistparser.parse(filepaths, incdirs, basedir, items)


def _resolve_template_filepaths(
    cls,  # class BaseMod
    placeholder: Placeholder,
    filepaths: list[Path],
    add_filepaths: StrPaths,
):
    basedir = Path(getfile(cls)).parent
    if add_filepaths:
        items = tuple(Path(str(item).format_map(placeholder)) for item in add_filepaths)
        for add_filepath in reversed(items):
            filepath = improved_resolve(add_filepath, basedir=basedir)
            if filepath not in filepaths:
                filepaths.insert(0, filepath)


def _get_baseclss(cls):
    clss = []
    for basecls in getmro(cls):
        if basecls is BaseMod:
            break
        clss.append(basecls)
    return clss
