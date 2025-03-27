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

"""File List Parser."""

import re
from collections.abc import Iterable
from pathlib import Path

from .logging import LOGGER
from .object import Object
from .pathutil import improved_resolve

_RE_COMMENT = re.compile(r"\A(.*?)(\s*(#|//).*)\Z")
_RE_FILELIST = re.compile(r"\A-([fF])\s+(.*?)\Z")
_RE_INCDIR = re.compile(r'\A[+\-]incdir[+\-\s]"?(?P<incdir>.*?)"?\Z')
_RE_FILE = re.compile(r"\A((-sv|-v)\s+)?(?P<filepath>[^+-].*?)\Z")


class FileListParser(Object):
    """File List Parser."""

    def parse_file(  # type: ignore[override]
        self,
        filepaths: list[Path],
        inc_dirs: list[Path],
        filepath: Path,
        replace_envvars: bool = False,
    ):
        """Read File List File.

        Args:
            filepaths: File Paths Container.
            inc_dirs: Include Directories Container.
            filepath: File to be parsed.
            replace_envvars: Resolve Environment Variables.
        """
        with filepath.open(encoding="utf-8") as file:
            basepath = filepath.parent
            self.parse(filepaths, inc_dirs, basepath, file)

        with filepath.open(encoding="utf-8") as file:
            basepath = filepath.parent
            self.parse(filepaths, inc_dirs, basepath, file, replace_envvars=replace_envvars, context=str(filepath))

    def parse(
        self,
        filepaths: list[Path],
        inc_dirs: list[Path],
        basedir: Path,
        items: Iterable[str | Path],
        replace_envvars: bool = False,
        context: str = "",
    ):
        """File List File.

        Args:
            filepaths: File Paths Container.
            inc_dirs: Include Directories Container.
            basedir: Base Directory for Relative Paths.
            items: Items to be parsed.
            replace_envvars: Resolve Environment Variables.
            context: Context for error reporting.
        """
        for lineno, item in enumerate(items, 1):
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
                self.parse_file(filepaths, inc_dirs, filelistpath)
                continue
            # -incdir
            mat = _RE_INCDIR.match(line)
            if mat:
                incdir = self.normalize(basedir, Path(mat.group("incdir")), replace_envvars)
                if incdir not in inc_dirs:
                    inc_dirs.append(incdir)
                continue
            # file
            mat = _RE_FILE.match(line)
            if mat:
                filepath = self.normalize(basedir, Path(mat.group("filepath")), replace_envvars)
                if filepath not in filepaths:
                    filepaths.append(filepath)
                continue
            LOGGER.warning("%s:%d Cannot parse %s", context, lineno, line)

    def resolve(self, basedir: Path, path: Path) -> Path:
        """Return Valid Filepath With Resolved Environment Variables.

        Args:
            basedir: Base Directory.
            path: Path.
        """
        return improved_resolve(path, basedir=basedir, replace_envvars=True, strict=True)

    def normalize(self, basedir: Path, path: Path, replace_envvars: bool) -> Path:
        """Return Normalized Filepaths for File List.

        Args:
            basedir: Base Directory.
            path: Path.
            replace_envvars: Resolve Environment Variables.
        """
        return improved_resolve(path, basedir=basedir, replace_envvars=replace_envvars)
