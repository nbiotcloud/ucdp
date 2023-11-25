#
# MIT License
#
# Copyright (c) 2023 nbiotcloud
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

import re
from typing import Optional, Union

from .const import RE_IDENTIFIER
from .object import Field, LightObject

_re_modref = re.compile(
    # pkg
    r"((?P<pkg>[a-zA-Z][a-zA-Z_0-9]*)\.)?"
    # mod
    r"(?P<mod>[a-zA-Z][a-zA-Z_0-9]*)"
    # cls
    r"(\:(?P<modcls>[a-zA-Z][a-zA-Z_0-9]*))?"
)
_pat = "lib.mod[:cls]"


class ModRef(LightObject):
    """
    Module Reference.

    Args:
        value: Module Name or pattern

    Keyword Args:
        pkg: Package Name
        modcls: Class Name

    >>> ModRef('mod', pkg='lib', modcls='Mod')
    ModRef('mod', pkg='lib', modcls='Mod')

    Just a module:

    >>> spec = ModRef('mod')
    >>> spec
    ModRef('mod')
    >>> str(spec)
    'mod'

    Module from a package:

    >>> spec = ModRef('lib.mod')
    >>> spec
    ModRef('mod', pkg='lib')
    >>> str(spec)
    'lib.mod'

    Module from a package and explicit class:

    >>> spec = ModRef('lib.mod:cls')
    >>> spec
    ModRef('mod', pkg='lib', modcls='cls')
    >>> str(spec)
    'lib.mod:cls'

    A :any:`ModRef` is kept:

    >>> ModRef(ModRef('mod'))
    ModRef('mod')

    Invalid Pattern:

    >>> ModRef('mod:c-ls')
    Traceback (most recent call last):
    ..
    ValueError: 'mod:c-ls' does not match pattern 'lib.mod[:cls]'
    """

    mod: str = Field(pattern=RE_IDENTIFIER)
    pkg: Optional[str] = Field(pattern=RE_IDENTIFIER, default=None)
    modcls: Optional[str] = Field(pattern=RE_IDENTIFIER, default=None)

    _posargs = ("mod",)

    def __init__(self, value: Union["ModRef", str], *, pkg: Optional[str] = None, modcls: Optional[str] = None):
        if isinstance(value, ModRef):
            mod = value.mod
            pkg = value.pkg
            modcls = value.modcls
        elif pkg is None and modcls is None:
            mat = _re_modref.fullmatch(value)
            if mat:
                mod = mat.group("mod")
                pkg = mat.group("pkg")
                modcls = mat.group("modcls")
            else:
                raise ValueError(f"{value!r} does not match pattern {_pat!r}")
        else:
            mod = value

        super().__init__(mod=mod, pkg=pkg, modcls=modcls)

    def __str__(self):
        pkg = f"{self.pkg}." if self.pkg else ""
        mod = self.mod
        modcls = f":{self.modcls}" if self.modcls else ""
        return f"{pkg}{mod}{modcls}"
