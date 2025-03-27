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

"""File Set."""

from pathlib import Path

from .filelistparser import FileListParser
from .modbase import BaseMod
from .modfilelist import Paths, iter_modfilelists
from .object import LightObject, Object


class LibPath(LightObject):
    """
    Library and File Path.

    Attributes:
        libname: Library Name
        path: Path
    """

    libname: str
    path: Path


class FileSet(Object):
    """
    Module File List.

    Attributes:
        target: Target
        filepaths: Source Files
        inc_dirs: Include Directories
    """

    target: str | None = None
    filepaths: tuple[LibPath, ...]
    inc_dirs: tuple[Path, ...]

    @staticmethod
    def from_mod(
        topmod: BaseMod, name: str, target: str | None = None, filelistparser: FileListParser | None = None
    ) -> "FileSet":
        """Create ``FileSet` for ``mod``."""
        filepaths: list[LibPath] = []
        inc_dirs: list[Path] = []
        for mod, modfilelist in iter_modfilelists(topmod, name, target=target, filelistparser=filelistparser):
            libname = mod.libname
            _process(filepaths, inc_dirs, libname, modfilelist.dep_filepaths, modfilelist.dep_inc_dirs)  # type: ignore[arg-type]
            _process(filepaths, inc_dirs, libname, modfilelist.filepaths, modfilelist.inc_dirs)  # type: ignore[arg-type]

        return FileSet(target=target, filepaths=tuple(filepaths), inc_dirs=tuple(inc_dirs))

    def __iter__(self):
        for incdir in self.inc_dirs:
            yield f"-incdir {incdir}"
        for libfilepath in self.filepaths:
            yield str(libfilepath.path)


def _process(
    filepaths: list[LibPath],
    inc_dirs: list[Path],
    libname: str,
    add_filepaths: Paths | None,
    add_inc_dirs: Paths | None,
):
    # inc_dir
    for inc_dir in add_inc_dirs or []:
        if inc_dir not in inc_dirs:
            inc_dirs.append(inc_dir)
    # filepath
    for filepath in add_filepaths or []:
        libpath = LibPath(libname=libname, path=Path(filepath))
        if libpath not in filepaths:
            filepaths.append(libpath)
