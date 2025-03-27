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
Utilities.
"""

import functools
import re
from collections.abc import Iterable

from matchor import matchs


@functools.lru_cache(maxsize=128)
def _translate(seps):
    return re.compile(rf"[{seps}]\s*")


Names = Iterable[str] | str


def split(items: Names, seps: str = ";") -> tuple[str, ...]:
    """
    Split items into tuple.

    Args:
        items: Items.
        seps: Separator

    ??? Example "Split Examples"
        Basics:

            >>> split(['abc', 'def'])
            ('abc', 'def')
            >>> split(('abc', 'def'))
            ('abc', 'def')
            >>> split('abc; def')
            ('abc', 'def')
            >>> split('ab;c, def', seps=",")
            ('ab;c', 'def')

        Generators are also handled:

            >>> def func():
            ...     yield 'abc'
            ...     yield 'def'
            >>> split(func())
            ('abc', 'def')

        Empty strings or `None` just result in an empty tuple:

            >>> split("")
            ()
            >>> split(None)
            ()
    """
    if not items:
        items = []
    elif isinstance(items, str):
        items = [item.strip() for item in _translate(seps).split(items)]
    return tuple(items)


def namefilter(namepats: Names):
    """
    Create filter for namepats.

    Args:
        namepats: Name Filter Pattern.

    ??? Example "Namefilter Examples"
        Basics:

            >>> import ucdp as u
            >>> def myfunc(items, filter_=None):
            ...     for item in items:
            ...         if not filter_ or filter_(item):
            ...             print(item)

            >>> items = ('abc', 'cde', 'efg')
            >>> myfunc(items)
            abc
            cde
            efg
            >>> myfunc(items, filter_=u.namefilter(''))
            abc
            cde
            efg
            >>> myfunc(items, filter_=u.namefilter('cde; tuv'))
            cde
            >>> myfunc(items, filter_=u.namefilter('*c*'))
            abc
            cde
            >>> myfunc(items, filter_=u.namefilter('!*c*'))
            efg
            >>> myfunc(items, filter_=u.namefilter('*c*; !*e'))
            abc

            >>> items = ['abc', 'cde', 'efg']
            >>> myfunc(items, filter_=u.namefilter('*c*; !*e'))
            abc
    """
    _patterns: tuple[str, ...] = split(namepats)

    inclist = [pat for pat in _patterns if not pat.startswith("!")]
    exclist = [pat[1:] for pat in _patterns if pat.startswith("!")]

    if inclist:
        if exclist:

            def filter_(name: str):
                return matchs(name, inclist) and not matchs(name, exclist)
        else:

            def filter_(name: str):
                return matchs(name, inclist)
    elif exclist:

        def filter_(name: str):
            return not matchs(name, exclist)
    else:

        def filter_(name: str):
            return True

    return filter_
