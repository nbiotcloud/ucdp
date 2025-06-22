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

"""
Loading And Searching Facility.
"""

import re
import sys
from collections.abc import Iterable, Iterator
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from importlib import import_module
from inspect import getfile, isclass
from pathlib import Path
from typing import TypeAlias

from .consts import PKG_PATHS
from .modbase import BaseMod, get_modbaseclss
from .modref import ModRef, get_modclsname
from .modtopref import TopModRef
from .object import Object
from .util import LOGGER, get_maxworkers, guess_path

Patterns: TypeAlias = Iterable[str]
Paths: TypeAlias = Iterable[Path]

_RE_IMPORT_UCDP = re.compile(r"^\s*class .*Mod\):")

_RE_TOPMODREFPAT = re.compile(
    # [tb]#
    r"((?P<tb>[a-zA-Z_0-9_\.\*]+)#)?"
    # top
    r"(?P<top>[a-zA-Z_0-9_\.\*]+)"
    # [-sub]
    r"(-(?P<sub>[a-zA-Z_0-9_\.\*]+))?"
)


class TopModRefPat(Object):
    """Top Module Reference Search Pattern Pattern."""

    top: str
    sub: str | None = None
    tb: str | None = None

    def __str__(self):
        result = self.top
        if self.sub:
            result = f"{result}-{self.sub}"
        if self.tb:
            result = f"{self.tb}#{result}"
        return result


@lru_cache
def build_top(modcls, **kwargs):
    """Build Top Module."""
    return modcls.build_top(**kwargs)


@lru_cache
def load_modcls(modref: ModRef) -> type[BaseMod]:
    """Load Module Class."""
    name = f"{modref.libname}.{modref.modname}"
    try:
        pymod = import_module(name)
    except ModuleNotFoundError as exc:
        if exc.name in (modref.libname, name):
            raise NameError(f"{name!r} not found.") from None
        raise exc
    modclsname = modref.get_modclsname()
    modcls = getattr(pymod, modclsname, None)
    if not modcls:
        raise NameError(f"{name!r} does not contain {modclsname}.") from None
    if not issubclass(modcls, BaseMod):
        raise ValueError(f"{modcls} is not a module aka child of <class ucdp.BaseMod>.")
    return modcls


def find_modrefs(local: bool | None = None) -> tuple[ModRef, ...]:
    # determine directories with python files
    dirpaths: set[Path] = set()
    modrefs: list[ModRef] = []
    for syspathstr in sys.path:
        syspath = Path(syspathstr).resolve()
        if local is not None and local is any(syspath.is_relative_to(pkg_path) for pkg_path in PKG_PATHS):
            continue
        for filepath in syspath.glob("*/*.py"):
            dirpath = filepath.parent
            if dirpath.name.startswith("_") or dirpath.name == "ucdp":
                continue
            dirpaths.add(dirpath)

    maxworkers = get_maxworkers()
    with ThreadPoolExecutor(max_workers=maxworkers) as exe:
        # start
        jobs = [
            exe.submit(_find_modrefs, sys.path, tuple(sorted(dirpath.glob("*.py")))) for dirpath in sorted(dirpaths)
        ]
        # collect
        for job in jobs:
            modrefs.extend(job.result())
    return tuple(modrefs)


def _find_modrefs_files(modrefs: tuple[ModRef, ...], envpath: list[str], filepaths: tuple[Path, ...]) -> list[Path]:
    paths: set[Path] = set(filepaths)
    for modref in modrefs:
        modcls = load_modcls(modref)
        for basecls in get_modbaseclss(modcls):
            paths.add(Path(getfile(basecls)))
    return sorted(paths)


def _find_modrefs(envpath: list[str], filepaths: tuple[Path, ...]) -> tuple[ModRef, ...]:  # noqa: C901
    modrefs = []
    for filepath in filepaths:
        pylibname = filepath.parent.name
        pymodname = filepath.stem
        if pymodname.startswith("_"):
            continue
        # skip non-ucdp files
        try:
            with filepath.open(encoding="utf-8") as file:
                for line in file:
                    if _RE_IMPORT_UCDP.match(line):
                        break
                else:
                    continue
        except Exception as exc:
            LOGGER.info(f"Skipping {str(filepath)!r} ({exc})")
            continue

        # import module
        try:
            pymod = import_module(f"{pylibname}.{pymodname}")
        except Exception as exc:
            LOGGER.warning(f"Skipping {str(filepath)!r} ({exc})")
            continue

        # Inspect Module
        for name in dir(pymod):
            # Load Class
            modcls = getattr(pymod, name)
            if not isclass(modcls) or not issubclass(modcls, BaseMod):
                continue

            # Ignore imported
            if filepath != Path(getfile(modcls)):
                continue

            # Create ModRefInfo
            modclsname = get_modclsname(pymodname)
            if modclsname == name:
                modref = ModRef(libname=pylibname, modname=pymodname)
            else:
                modref = ModRef(libname=pylibname, modname=pymodname, modclsname=name)
            modrefs.append(modref)

    return tuple(modrefs)


def get_topmodrefpats(patterns: Patterns | None) -> Iterator[TopModRefPat | TopModRef]:
    for pattern in patterns or []:
        path = guess_path(pattern)
        if path:
            yield TopModRef.cast(path)
        else:
            mat = _RE_TOPMODREFPAT.fullmatch(pattern)
            if mat:
                yield TopModRefPat(**mat.groupdict())
            else:
                yield TopModRefPat(top=".")  # never matching
