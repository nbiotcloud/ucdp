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

from pathlib import Path

from .filelistparser import FileListParser
from .modbase import BaseMod
from .modfilelist import Paths, iter_modfilelists
from .object import LightObject, Object


class LibPath(LightObject):
    """Library and File Path."""

    libname: str
    path: Path


class FileSet(Object):
    """
    Module File List.

    Attributes:
        target: Target
        filepaths: Source Files
        incdirs: Include Files
    """

    target: str | None = None
    filepaths: tuple[LibPath, ...]
    incdirs: tuple[Path, ...]

    @staticmethod
    def from_mod(
        topmod: BaseMod, name: str, target: str | None = None, filelistparser: FileListParser | None = None
    ) -> "FileSet":
        """Create ``FileSet` for ``mod``."""
        filepaths: list[LibPath] = []
        incdirs: list[Path] = []
        for mod, modfilelist in iter_modfilelists(topmod, name, target=target, filelistparser=filelistparser):
            libname = mod.libname
            _process(filepaths, incdirs, libname, modfilelist.dep_filepaths, modfilelist.dep_incdirs)  # type: ignore[arg-type]
            _process(filepaths, incdirs, libname, modfilelist.filepaths, modfilelist.incdirs)  # type: ignore[arg-type]

        return FileSet(target=target, filepaths=tuple(filepaths), incdirs=tuple(incdirs))


def _process(
    filepaths: list[LibPath],
    incdirs: list[Path],
    libname: str,
    add_filepaths: Paths | None,
    add_incdirs: Paths | None,
):
    # incdir
    for incdir in add_incdirs or []:
        if incdir not in incdirs:
            incdirs.append(incdir)
    # filepath
    for filepath in add_filepaths or []:
        libpath = LibPath(libname=libname, path=Path(filepath))
        if libpath not in filepaths:
            filepaths.append(libpath)
