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

"""Utilities."""

import os
import sys
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from functools import lru_cache
from inspect import getfile
from pathlib import Path

from .logging import LOGGER


def get_paths() -> tuple[Path, ...]:
    """Determine Paths from Environment variable 'UCDP_PATH'."""
    return tuple(Path(item.strip()) for item in os.environ.get("UCDP_PATH", "").split())


@contextmanager
def extend_sys_path(paths: Iterable[Path] | None = None, use_env_default: bool = False):
    """Context with extended sys.path.

    Keyword Args:
        paths: Paths.
        use_env_default: Use UCDP_PATH as default if paths are unset.
    """
    if paths is None and use_env_default:
        paths = get_paths()
    globpaths = []
    for path in paths or []:
        globpaths.extend(glob(path))
    pathstrs = [str(path) for path in globpaths]
    LOGGER.debug("paths=%r", pathstrs)
    if pathstrs:
        orig = sys.path
        sys.path = [*sys.path, *pathstrs]
        yield
        sys.path = orig
    else:
        yield


def get_copyright(obj: Path | object) -> str:
    """Determine from Source Code of ``obj``."""
    if isinstance(obj, Path):
        path = obj
    else:
        path = Path(getfile(obj.__class__))
    return _get_copyright(path)


@lru_cache
def _get_copyright(path: Path) -> str:
    lines = []
    with path.open(encoding="utf-8") as file:
        for line in file:
            if line.startswith("#"):
                lines.append(line[1:])
            else:
                break
    return "".join(lines)


def get_maxworkers() -> int | None:
    """Maximum Number of Workers."""
    try:
        return int(os.environ["UCDP_MAXWORKERS"])
    except (KeyError, ValueError):
        return None


def guess_path(arg: str) -> Path | None:
    """Return Path if arg seems to be a file path."""
    path = Path(arg)
    if path.exists() or len(path.parts) > 1:
        return path
    return None


def glob(path: Path) -> Iterator[Path]:
    """Glob `path`."""
    assert isinstance(path, Path), path
    path = path.absolute()
    pathstr = str(path)
    if "*" in pathstr or "?" in pathstr or "[" in pathstr:
        root = Path(path.parts[0])
        pattern = str(path.relative_to(root))
        yield from sorted(root.glob(pattern))
    else:
        yield path
