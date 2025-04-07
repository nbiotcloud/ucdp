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
Module Utilities.

"""

from collections.abc import Iterator
from inspect import getfile
from pathlib import Path
from typing import Any

from caseconverter import snakecase

from .baseclassinfo import BaseClassInfo, get_baseclassinfos


def get_modbaseinfos(cls_or_inst: Any) -> Iterator[BaseClassInfo]:
    """
    Get Base Classes of `mod`.

    Args:
        cls_or_inst: Class or Instance
    """
    for baseclassinfo in get_baseclassinfos(cls_or_inst):
        if baseclassinfo.libname == "ucdp":
            break
        yield baseclassinfo


def is_tb_from_modname(modname: str) -> bool:
    """
    Determine if module is a testbench component by checking the name.

    Args:
        modname: Module Name
    """
    return modname.endswith("_tb") or "_tb_" in modname


def get_modname(cls):
    """Module Name."""
    return snakecase(cls.__name__.removesuffix("Mod"))


def get_topmodname(cls):
    """Top Module Name."""
    modbaseinfos = tuple(get_modbaseinfos(cls))
    clsname = modbaseinfos[-1].clsname
    return snakecase(clsname.removesuffix("Mod"))


def get_libname(cls) -> str:
    """Module Library Name."""
    return Path(getfile(cls)).parts[-2]


def get_libpath(cls) -> Path:
    """Module Library Path."""
    return Path(getfile(cls)).parent


def get_file(cls, basedir: Path | None = None) -> Path:
    """Get File Path."""
    path = Path(getfile(cls))
    basedir = basedir or Path()
    try:
        return path.relative_to(basedir)
    except ValueError:
        return Path(*path.parts[-2:])
