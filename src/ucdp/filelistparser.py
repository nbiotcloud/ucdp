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

"""File List Parser."""

import re
from collections.abc import Iterable
from pathlib import Path

from .logging import LOGGER
from .object import Object
from .pathutil import improved_resolve, use_envvars

_RE_COMMENT = re.compile(r"\A(.*?)(\s*(#|//).*)\Z")
_RE_FILELIST = re.compile(r"\A-([fF])\s+(.*?)\Z")
_RE_INCDIR = re.compile(r'\A[+\-]incdir[+\-\s]"?(?P<incdir>.*?)"?\Z')
_RE_FILE = re.compile(r"\A((-sv|-v)\s+)?(?P<filepath>[^+-].*?)\Z")


class FileListParser(Object):
    """File List Parser."""

    envvarnames: tuple[str, ...] = ()

    def parse_file(self, filepaths: list[Path], incdirs: list[Path], filepath: Path):  # type: ignore[override]
        """Read File List File."""
        with filepath.open(encoding="utf-8") as file:
            basepath = filepath.parent
            self.parse(filepaths, incdirs, basepath, file)

    def parse(self, filepaths: list[Path], incdirs: list[Path], basedir: Path, items: Iterable[str | Path]):
        """File List File."""
        for item in items:
            line = str(item).strip()
            # comment
            mat = _RE_COMMENT.match(line)
            if mat:
                line = mat.group(1).strip()
            if not line:
                continue
            # -f
            mat = _RE_FILELIST.match(line)
            if mat:
                filelistpath = self.resolve(basedir, Path(mat.group(2)))
                self.parse_file(filepaths, incdirs, filelistpath)
                continue
            # -incdir
            mat = _RE_INCDIR.match(line)
            if mat:
                incdir = self.normalize(basedir, Path(mat.group("incdir")))
                if incdir not in incdirs:
                    incdirs.append(incdir)
                continue
            # file
            mat = _RE_FILE.match(line)
            if mat:
                filepath = self.normalize(basedir, Path(mat.group("filepath")))
                if filepath not in filepaths:
                    filepaths.append(filepath)
                continue
            LOGGER.warning("Cannot parse %s", line)

    def resolve(self, basedir: Path, path: Path) -> Path:
        """Return Valid Filepath With Resolved Environment Variables."""
        return improved_resolve(path, basedir=basedir, replace_envvars=True, strict=True)

    def normalize(self, basedir: Path, path: Path) -> Path:
        """Return Normalized Filepaths for File List."""
        return use_envvars(improved_resolve(path, basedir=basedir), self.envvarnames)
