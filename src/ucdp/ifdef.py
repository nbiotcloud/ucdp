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

"""Ifdef Support."""

from typing import TypeAlias

from .consts import RE_IFDEF
from .define import Defines

Ifdefs: TypeAlias = tuple[str, ...]


def cast_ifdefs(value: Ifdefs | str | None) -> Ifdefs:
    """
    Cast Ifdefs.

    Examples:

        >>> cast_ifdefs('ASIC')
        ('ASIC',)
        >>> cast_ifdefs('!ASIC')
        ('!ASIC',)
        >>> cast_ifdefs(('ASIC',))
        ('ASIC',)
        >>> cast_ifdefs(('ASIC', 'BEHAV'))
        ('ASIC', 'BEHAV')
        >>> cast_ifdefs('')
        ()
        >>> cast_ifdefs(None)
        ()

    Forbidden:

        >>> cast_ifdefs('AS!')
        Traceback (most recent call last):
            ...
        ValueError: Invalid ifdef 'AS!'
        >>> cast_ifdefs('!!AS')
        Traceback (most recent call last):
            ...
        ValueError: Invalid ifdef '!!AS'
    """
    if not value:
        return ()
    if isinstance(value, str):
        value = (value,)
    if isinstance(value, tuple):
        for item in value:
            if not RE_IFDEF.match(item):
                raise ValueError(f"Invalid ifdef {item!r}")
        return value
    raise ValueError(f"Invalid ifdefs: {value}")


def join_ifdefs(base: Ifdefs, add: Ifdefs) -> Ifdefs:
    """
    Join Ifdefs.

    Examples:

        >>> join_ifdefs(('ASIC',), ('ASIC',))
        ('ASIC',)
        >>> join_ifdefs(('ASIC',), ('BEHAV',))
        ('ASIC', 'BEHAV')
        >>> join_ifdefs(('ASIC',), ('!ASIC',))
        ('!ASIC',)
        >>> join_ifdefs(('!ASIC',), ('ASIC',))
        ('ASIC',)
        >>> join_ifdefs(('ASIC', 'FOO'), ('!ASIC',))
        ('FOO', '!ASIC')
        >>> join_ifdefs(('ASIC', 'FOO'), ('!ASIC', 'FOO'))
        ('FOO', '!ASIC')
        >>> join_ifdefs(('ASIC', 'FOO'), ('!ASIC', 'BAR'))
        ('FOO', '!ASIC', 'BAR')
        >>> join_ifdefs(('!ASIC', 'FOO'), ('ASIC',))
        ('FOO', 'ASIC')
        >>> join_ifdefs(('!ASIC', 'FOO'), ('ASIC', 'FOO'))
        ('FOO', 'ASIC')
        >>> join_ifdefs(('!ASIC', 'FOO'), ('ASIC', 'BAR'))
        ('FOO', 'ASIC', 'BAR')
    """
    result = list(base)
    for ifdef in add:
        # remove inverse
        if ifdef.startswith("!"):
            if ifdef[1:] in result:
                result.remove(ifdef[1:])
        elif f"!{ifdef}" in result:
            result.remove(f"!{ifdef}")

        # add - if missing
        if ifdef not in result:
            result.append(ifdef)
    return tuple(result)


def resolve_ifdefs(defines: Defines | None, ifdefs: Ifdefs) -> Ifdefs | None:
    """
    Resolve Ifdefs.

    >>> import ucdp as u
    >>> defines = u.Defines([u.Define('_FOO'), u.Define('_BAR', value=3)])
    >>> resolve_ifdefs(defines, ())
    ()
    >>> resolve_ifdefs(defines, ('FOO',))
    ()
    >>> resolve_ifdefs(defines, ('BAR',))
    ()
    >>> resolve_ifdefs(defines, ('FOO', 'BAR'))
    ()
    >>> resolve_ifdefs(defines, ('FOO', '!BAR'))
    >>> resolve_ifdefs(defines, ('BAZ',))
    >>> resolve_ifdefs(defines, ('!BAZ',))
    ()

    >>> defines = None
    >>> resolve_ifdefs(defines, ('FOO', '!BAR'))
    ('FOO', '!BAR')
    """
    if defines is None:
        return ifdefs
    for ifdef in ifdefs:
        # abort if ifdef is not there OR
        # abort if ifdef is there but forbidden
        define = "_" + ifdef.removeprefix("!")
        if (define in defines) == ifdef.startswith("!"):
            return None

    return ()
