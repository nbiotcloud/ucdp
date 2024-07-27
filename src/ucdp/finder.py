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
Loader.

* [load()][ucdp.loader.load] is one and only method to pickup and instantiate the topmost hardware module.
"""

import re
import sys
from collections.abc import Iterable, Iterator
from importlib import import_module
from inspect import getfile, isclass
from pathlib import Path

from uniquer import unique

from .modbase import BaseMod
from .modref import ModRef, get_modclsname
from .modrefinfo import ModRefInfo
from .util import LOGGER, extend_sys_path

_RE_IMPORT_UCDP = re.compile("^import ucdp")


def find(paths: Iterable[Path] | None = None, variants: bool = False) -> Iterator[ModRefInfo]:
    """List All Available Module References."""
    with extend_sys_path(paths):
        for filepath, pylibname, pymodname, pymod in _find_pymods():
            yield from _find_modrefs(filepath, pylibname, pymodname, pymod, variants)


def _find_pymods():
    filepaths = []
    for syspathstr in sys.path:
        filepaths.extend(Path(syspathstr).resolve().glob("*/*.py"))
    for filepath in sorted(unique(filepaths)):
        pylibname = filepath.parent.name
        pymodname = filepath.stem

        # skip private
        if pylibname.startswith("_") or pymodname.startswith("_"):
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
            pymod = import_module(f"{pylibname}.{pymodname}")
        except Exception as exc:
            LOGGER.info(f"Skipping {str(filepath)!r} ({exc})")
            continue

        yield filepath, pylibname, pymodname, pymod


def _find_modrefs(filepath, pylibname, pymodname, pymod, variants) -> Iterator[ModRefInfo]:
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
            yield ModRefInfo.create(modref, modcls)
        if variants or modclsname != name:
            modref = ModRef(libname=pylibname, modname=pymodname, modclsname=name)
            yield ModRefInfo.create(modref, modcls)
