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

"""Module Specification."""

import re
from typing import Optional, Union

from .attrs import field, frozen


@frozen
class ModRef:

    """
    Module Specification.

    Args:
        mod: Module Name

    Keyword Args:
        pkg: Package Name
        cls: Class Name
    """

    mod: str = field()
    pkg: str = field(default=None)
    cls: Optional[str] = field(default=None)

    _re = re.compile(
        # pkg
        r"((?P<pkg>[a-zA-Z][a-zA-Z_0-9]*)\.)?"
        # mod
        r"(?P<mod>[a-zA-Z][a-zA-Z_0-9]*)"
        # cls
        r"(\:(?P<cls>[a-zA-Z][a-zA-Z_0-9]*))?"
    )
    _pat = "lib.mod[:cls]"

    @staticmethod
    def convert(value: Union["ModRef", str]) -> "ModRef":
        """
        Convert.

        Just a module:

        >>> spec = ModRef.convert('mod')
        >>> spec
        ModRef('mod')
        >>> str(spec)
        'mod'

        Module from a package:

        >>> spec = ModRef.convert('lib.mod')
        >>> spec
        ModRef('mod', pkg='lib')
        >>> str(spec)
        'lib.mod'

        Module from a package and explicit class:

        >>> spec = ModRef.convert('lib.mod:cls')
        >>> spec
        ModRef('mod', pkg='lib', cls='cls')
        >>> str(spec)
        'lib.mod:cls'

        A :any:`ModRef` is kept:

        >>> ModRef.convert(ModRef('mod'))
        ModRef('mod')

        Invalid Pattern:

        >>> ModRef.convert('mod:c-ls')
        Traceback (most recent call last):
        ..
        ValueError: 'mod:c-ls' does not match pattern 'lib.mod[:cls]'
        """

        if isinstance(value, ModRef):
            return value

        mat = ModRef._re.fullmatch(value)
        if mat:
            return ModRef(**mat.groupdict())

        raise ValueError(f"{value!r} does not match pattern {ModRef._pat!r}")

    def __str__(self):
        pkg = f"{self.pkg}." if self.pkg else ""
        mod = self.mod
        cls = f":{self.cls}" if self.cls else ""
        return f"{pkg}{mod}{cls}"
