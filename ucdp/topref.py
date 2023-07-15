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

"""Top Module Reference."""

import re
from typing import Optional

from .attrs import field, frozen
from .modref import ModRef
from .util import opt


@frozen
class TopRef:

    """
    Top Module Reference.

    Args:
        top (str): Name of the top module.

    Keyword Args:
        sub (str): Name of the sub module within top module.
        tb (str): Name of the testbench.
    """

    top: ModRef = field(converter=ModRef.convert)
    sub: Optional[ModRef] = field(converter=opt(ModRef.convert), default=None)
    tb: Optional[ModRef] = field(converter=opt(ModRef.convert), default=None)

    _re = re.compile(
        # [tb]#
        r"((?P<tb>[^#\- ]+)#)?"
        # top
        r"(?P<top>[^#\- ]+)"
        # [-sub]
        r"(-(?P<sub>[^#\- ]+))?"
    )
    _pat = "[tb#]top[-sub]"

    @staticmethod
    def convert(value) -> "TopRef":
        """
        Create :any:`TopRef` from string `value`.

        Just a top module:

        >>> topref = TopRef.convert("chip")
        >>> topref
        TopRef(ModRef('chip'))
        >>> str(topref)
        'chip'

        Top Module with Testbench:

        >>> topref = TopRef.convert("tb#chip")
        >>> topref
        TopRef(ModRef('chip'), tb=ModRef('tb'))
        >>> str(topref)
        'tb#chip'

        # Top Module with Testbench and Sub:

        >>> topref = TopRef.convert("tb#chip-sub")
        >>> topref
        TopRef(ModRef('chip'), sub=ModRef('sub'), tb=ModRef('tb'))
        >>> str(topref)
        'tb#chip-sub'

        A :any:`ModRef` is kept:

        >>> TopRef.convert(TopRef(ModRef('chip')))
        TopRef(ModRef('chip'))

        Invalid Pattern:

        >>> TopRef.convert('mo#d#e')
        Traceback (most recent call last):
        ..
        ValueError: 'mo#d#e' does not match pattern '[tb#]top[-sub]'
        """
        if isinstance(value, TopRef):
            return value

        mat = TopRef._re.fullmatch(value)
        if mat:
            return TopRef(**mat.groupdict())

        raise ValueError(f"{value!r} does not match pattern {TopRef._pat!r}")

    def __str__(self):
        result = str(self.top)
        if self.sub:
            result = f"{result}-{self.sub}"
        if self.tb:
            result = f"{self.tb}#{result}"
        return result
