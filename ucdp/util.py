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

"""
Utilities
"""

import re
from typing import Any

_RE_IDENTIFIER = re.compile(r"([a-zA-Z0-9][a-zA-Z_0-9\-]*)?")


def check_name(value: Any):
    """Check `value` against regular expression."""
    if not _RE_IDENTIFIER.fullmatch(str(value)):
        raise ValueError("Invalid identifier '{value}'")
    return value


class AutoNum:

    """
    Auto Numbering.

    >>> autonum = AutoNum()
    >>> autonum.get()
    0
    >>> autonum.get()
    1
    """

    # pylint: disable=too-few-public-methods

    def __init__(self, start=0):
        self.cnt = start

    def get(self):
        """Get Fresh Number."""
        num = self.cnt
        self.cnt += 1
        return num
