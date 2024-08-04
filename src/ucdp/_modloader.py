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

"""
Loading And Searching Facilty.
"""

import re
import sys
from collections.abc import Iterable, Iterator
from functools import lru_cache
from importlib import import_module
from inspect import getfile, isclass
from pathlib import Path
from typing import Any, TypeAlias

from uniquer import unique

from .modbase import BaseMod
from .modref import ModRef, get_modclsname
from .object import Object
from .util import LOGGER

Patterns: TypeAlias = Iterable[str]
Paths: TypeAlias = Iterable[Path]
ModClsRef: TypeAlias = tuple[type[BaseMod], ModRef]

_RE_IMPORT_UCDP = re.compile(r"^\s*class .*Mod\):")

_RE_TOPMODREFPAT = re.compile(
    # [tb]#
    r"((?P<tb>[a-zA-Z_0-9_\.\*]+)#)?"
    # top
    r"(?P<top>[a-zA-Z_0-9_\.\*]+)"
    # [-sub]
    r"(-(?P<sub>[a-zA-Z_0-9_\.\*]+))?"
)


class PyModRef(Object):
    """Python Module Reference."""

    filepath: Path
    libname: str
    modname: str
    mod: Any


class TopModRefPat(Object):
    """Top Module Reference Search Pattern Pattern."""

    top: str
    sub: str | None = None
    tb: str | None = None


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


def _find_pymodrefs() -> Iterator[PyModRef]:
    filepaths: list[Path] = []
    for syspathstr in sys.path:
        filepaths.extend(Path(syspathstr).resolve().glob("*/*.py"))
    for filepath in sorted(unique(filepaths)):
        libname = filepath.parent.name
        modname = filepath.stem

        # skip private
        if libname.startswith("_") or modname.startswith("_") or libname == "ucdp":
            continue

        # skip non-ucdp files
        with filepath.open(encoding="utf-8") as file:
            try:
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
            pymod = import_module(f"{libname}.{modname}")
        except Exception as exc:
            LOGGER.info(f"Skipping {str(filepath)!r} ({exc})")
            continue
        yield PyModRef(filepath=filepath, libname=libname, modname=modname, mod=pymod)


def _find_modclsrefs(pymodref: PyModRef) -> Iterator[ModClsRef]:
    pymod = pymodref.mod
    for name in dir(pymod):
        # Load Class
        modcls = getattr(pymod, name)
        if not isclass(modcls) or not issubclass(modcls, BaseMod):
            continue

        # Ignore imported
        if pymodref.filepath != Path(getfile(modcls)):
            continue

        # Create ModRefInfo
        libname = pymodref.libname
        modname = pymodref.modname
        modclsname = get_modclsname(modname)
        if modclsname == name:
            modref = ModRef(libname=libname, modname=modname)
        else:
            modref = ModRef(libname=libname, modname=modname, modclsname=name)
        yield modcls, modref


def find_modclsrefs() -> Iterator[ModClsRef]:
    for pymodref in _find_pymodrefs():
        yield from _find_modclsrefs(pymodref)


def get_topmodrefpats(patterns: Patterns | None) -> Iterator[TopModRefPat]:
    for pattern in patterns or ["*"]:
        mat = _RE_TOPMODREFPAT.fullmatch(pattern)
        if mat:
            yield TopModRefPat(**mat.groupdict())
        else:
            yield TopModRefPat(top=".")  # never matching
