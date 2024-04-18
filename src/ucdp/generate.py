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

"""Code Generator based of FileLists."""

from typing import TYPE_CHECKING

from makolator import Makolator

from .filelistparser import FileListParser
from .logging import LOGGER
from .modbase import BaseMod
from .modfilelist import iter_modfilelists

if TYPE_CHECKING:
    from pathlib import Path


def generate(
    topmod: BaseMod,
    name: str,
    target: str | None = None,
    filelistparser: FileListParser | None = None,
    makolator: Makolator | None = None,
):
    """
    Generate for Top-Module.

    Args:
        topmod: Top Module
        name: Filelist Name

    Keyword Args:
        target: Target Filter
        filelistparser: Specific File List Parser
        makolator: Specific Makolator
    """
    makolator = makolator or Makolator()
    for mod, modfilelist in iter_modfilelists(topmod, name, target=target, filelistparser=filelistparser):
        if modfilelist.gen == "no":
            continue
        filepaths: tuple[Path, ...] = modfilelist.filepaths or ()  # type: ignore[assignment]
        template_filepaths: tuple[Path, ...] = modfilelist.template_filepaths or ()  # type: ignore[assignment]
        context = {"mod": mod}
        if modfilelist.gen == "inplace":
            for filepath in filepaths:
                if not filepath.exists():
                    LOGGER.error("Inplace file %r missing", str(filepath))
                    continue
                makolator.inplace(template_filepaths, filepath, context=context)
        elif template_filepaths:
            for filepath in filepaths:
                makolator.gen(template_filepaths, filepath, context=context)
        else:
            LOGGER.error(f"No 'template_filepaths' defined for {mod}")
