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

"""Path Utilities."""

import os
import re
from collections.abc import Iterator
from pathlib import Path

_RE_PAT = re.compile(r".*[\*\?\]\[]")
_RE_ENVVAR = re.compile(
    r"^\$(?P<name>(\{(?P<name1>[^\/\\]+)\})|(?P<name0>[^\/\\]+))([\/\\](?P<rem>.*))?$", flags=re.IGNORECASE
)


def improved_glob(pattern: Path | str, basedir: Path | None = None) -> Iterator[Path]:
    """
    Improved version of pathlib.Path.glob().

    * Not existing files are not 'globbed-away'
    * Aware of Environment Variables
    * Output is sorted.
    """
    basedir = basedir or Path()
    patternstr = str(pattern)
    if _is_pattern(patternstr):
        name, path = startswith_envvar(Path(pattern))
        if name:
            vname = f"${name}"
            base = Path(vname)
            value = Path(os.path.expandvars(vname))
            for sub in sorted(value.glob(str(path))):
                rel = sub.relative_to(value)
                yield base / rel
        else:
            yield from sorted(basedir.glob(patternstr))
    else:
        yield basedir / pattern


def improved_resolve(path: Path, basedir: Path | None = None, strict: bool = False, replace_envvars=False) -> Path:
    """
    Improved version of pathlib.Path.resolve().

    * Aware of Environment Variables
    """
    if replace_envvars:
        path = Path(os.path.expandvars(str(path)))
    elif _RE_ENVVAR.match(str(path)):
        if strict:
            raise FileNotFoundError(path)
        return path

    if not path.is_absolute():
        basedir = basedir or Path()
        path = basedir / path
    return path.resolve(strict=strict)


def use_envvars(path: Path, envvarnames: tuple[str, ...]) -> Path:
    """
    Use Environment Variables instead of absolute Paths.

    Do nothing on relative paths.
    """
    if not path.is_absolute():
        return path
    for envvarname in envvarnames:
        value = os.getenv(envvarname)
        if not value:
            continue
        try:
            sub = path.relative_to(Path(value))
        except ValueError:
            continue
        return Path(f"${{{envvarname}}}") / sub
    return path


def startswith_envvar(path: Path, strict: bool = False, barename: bool = False) -> tuple[str | None, Path]:
    """Check if path starts with environment variable."""
    mat = _RE_ENVVAR.match(str(path))
    if not mat:
        return None, path
    varname = mat.group("name0") or mat.group("name1")
    path = Path(mat.group("rem") or ".")
    if strict:
        envpath = os.getenv(varname)
        if not envpath or not Path(envpath).exists():
            raise FileNotFoundError(envpath)

    if barename:
        return varname, path
    return mat.group("name"), path


def _is_pattern(pattern: str) -> bool:
    return bool(_RE_PAT.match(pattern))
