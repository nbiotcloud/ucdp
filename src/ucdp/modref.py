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

"""Module Reference."""

# DOCME: pkg vs lib

import re
from typing import Union

from .consts import PAT_IDENTIFIER
from .object import Field, LightObject

RE_MODREF = re.compile(
    # lib
    r"(?P<lib>[a-zA-Z][a-zA-Z_0-9]*)\."
    # mod
    r"(?P<mod>[a-zA-Z][a-zA-Z_0-9]*)"
    # cls
    r"(\.(?P<modcls>[A-Z][a-zA-Z_0-9]*Mod))?"
)
PAT_MODREF = "lib.my[.MyMod]"


class ModRef(LightObject):
    """
    Module Reference.

    Args:
        lib: Library Name
        mod: Module Name

    Keyword Args:
        modcls: Class Name

    >>> ModRef('glbl_lib', 'clk_gate', modcls='ClkGateMod')
    ModRef('glbl_lib', 'clk_gate', modcls='ClkGateMod')

    Just a module:

    >>> spec = ModRef.cast('glbl_lib.clk_gate')
    >>> spec
    ModRef('glbl_lib', 'clk_gate')
    >>> str(spec)
    'glbl_lib.clk_gate'

    Module from a package and explicit class:

    >>> spec = ModRef.cast('glbl_lib.clk_gate.ClkGateMod')
    >>> spec
    ModRef('glbl_lib', 'clk_gate', modcls='ClkGateMod')
    >>> str(spec)
    'glbl_lib.clk_gate.ClkGateMod'

    Invalid Pattern:

    >>> ModRef.cast('lib.my:c-ls')
    Traceback (most recent call last):
    ..
    ValueError: 'lib.my:c-ls' does not match pattern 'lib.my[.MyMod]'
    """

    lib: str = Field(pattern=PAT_IDENTIFIER)
    mod: str = Field(pattern=PAT_IDENTIFIER)
    modcls: str | None = Field(pattern=PAT_IDENTIFIER, default=None)

    _posargs: tuple[str, ...] = ("lib", "mod")

    def __init__(self, lib: str, mod: str, modcls: str | None = None):
        super().__init__(lib=lib, mod=mod, modcls=modcls)  # type: ignore[call-arg]

    def __str__(self) -> str:
        modcls = f".{self.modcls}" if self.modcls else ""
        return f"{self.lib}.{self.mod}{modcls}"

    @staticmethod
    def cast(value: Union["ModRef", str]) -> "ModRef":
        """Cast `value` to `ModRef`."""
        if isinstance(value, ModRef):
            return value

        mat = RE_MODREF.fullmatch(value)
        if mat:
            return ModRef(**mat.groupdict())

        raise ValueError(f"{value!r} does not match pattern {PAT_MODREF!r}")
