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
import functools
import re


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


@functools.lru_cache(maxsize=128)
def _translate(seps):
    return re.compile(rf"[{seps}]\s*")


def split(items, seps=";"):
    """
    Split items into tuple.

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


def namefilter(names):
    """
    Create filter for names.
    """
    # >>> import ucdp
    # >>> from collections import namedtuple
    # >>> def myfunc(items, filter_=None):
    # ...     for item in items:
    # ...         if not filter_ or filter_(item):
    # ...             print(item)
    # >>> Item = namedtuple('Item', "name value")

    # >>> items = (Item('abc', 0), Item('cde', 1), Item('efg', 7))
    # >>> myfunc(items)
    # Item(name='abc', value=0)
    # Item(name='cde', value=1)
    # Item(name='efg', value=7)
    # >>> myfunc(items, filter_=ucdp.namefilter(''))
    # Item(name='abc', value=0)
    # Item(name='cde', value=1)
    # Item(name='efg', value=7)
    # >>> myfunc(items, filter_=ucdp.namefilter('cde; tuv'))
    # Item(name='cde', value=1)
    # >>> myfunc(items, filter_=ucdp.namefilter('*c*'))
    # Item(name='abc', value=0)
    # Item(name='cde', value=1)
    # >>> myfunc(items, filter_=ucdp.namefilter('!*c*'))
    # Item(name='efg', value=7)
    # >>> myfunc(items, filter_=ucdp.namefilter('*c*; !*e'))
    # Item(name='abc', value=0)

    names = split(names)

    # if names:
    #     inclist = [x for x in names if not x.startswith("!")]
    #     exclist = [x[1:] for x in names if x.startswith("!")]

    #     def filter_(item):
    #         if not isinstance(item, str):
    #             item = item.name
    #         if inclist:
    #             if exclist:
    #                 return matchs(item, inclist) and not matchs(item, exclist)
    #             return matchs(item, inclist)
    #         return not matchs(item, exclist)

    # else:

    def filter_(item):
        # pylint: disable=unused-argument
        return True

    return filter_


def opt(converter):
    """
    Optional.
    """

    def check(value):
        if value is not None:
            return converter(value)
        return None

    return check
