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
Module Information.
"""

from inspect import getdoc

from aligntext import align

from .ident import Idents
from .modbase import BaseMod
from .modfilelist import iter_modfilelists


def get_modinfo(mod: BaseMod, sub: bool = False) -> str:
    """Module Information."""
    header = f"# Module `{mod.libname}.{mod.modname}`\n\nPython: `{mod.get_modref()}`"
    parts = [
        header,
        getdoc(mod),
        _get_ident_info(mod, "Parameters", mod.params),
        _get_ident_info(mod, "Ports", mod.ports),
        _get_fileinfos(mod),
    ]
    if sub:
        parts.append(_get_sub_info(mod))
    return "\n\n".join(parts)


def _get_ident_info(mod: BaseMod, title: str, idents: Idents):
    def entry(level, ident):
        pre = ". " * level
        dinfo = f" (`{ident.direction}`)" if ident.direction else ""
        return (
            f"{pre}`{ident.name}`{dinfo}",
            f"{pre}`{ident.type_}`",
        )

    if idents:
        data = [entry(level, ident) for level, ident in idents.leveliter()]
        content = align([("Name ", "Type"), ("----", "----"), *data], seps=(" | ", " |"), sepfirst="| ")
    else:
        content = "None"
    return f"## {title}\n\n{content}"


def _get_fileinfos(mod: BaseMod):
    parts = []
    for _, modfilelist in iter_modfilelists(mod, maxlevel=1):
        parts += (f"### Filelist `{modfilelist.name}`", "")
        dump = modfilelist.model_dump(exclude_defaults=True, exclude=("name",))
        data = [(f"`{name}`", _format_value(value)) for name, value in dump.items()]
        parts.extend((align([("Name ", "Type"), ("----", "----"), *data], seps=(" | ", " |"), sepfirst="| "), ""))
    if not parts:
        parts = ["None"]
    return "\n".join(("## Files\n", *parts))


def _get_sub_info(mod: BaseMod) -> str:
    parts = [
        "## Submodules",
        "",
    ]
    if mod.insts:
        data = [("Name", "Module"), ("----", "------")]
        data += [(f"`{inst.name}`", f"`{inst.libname}.{inst.modname}`") for inst in mod.insts]
        parts.append(align(data, seps=(" | ", " |"), sepfirst="| "))
        parts.append("")
    else:
        parts.append("-")
    return "\n".join(parts)


def _format_value(value) -> str:
    if isinstance(value, tuple):
        return "\n".join(_format_value(item) for item in value)
    return f"`{value!s}`"
