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

Ifdefs: TypeAlias = tuple[str, ...]


def cast_ifdefs(value: Ifdefs | str | None) -> Ifdefs:
    """
    Cast Ifdefs.

    >>> cast_ifdefs('ASIC')
    ('ASIC',)
    >>> cast_ifdefs(('ASIC',))
    ('ASIC',)
    >>> cast_ifdefs(('ASIC', 'BEHAV'))
    ('ASIC', 'BEHAV')
    >>> cast_ifdefs('')
    ()
    >>> cast_ifdefs(None)
    ()
    """
    if not value:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, tuple) and all(isinstance(item, str) for item in value):
        return value
    raise ValueError(f"Invalid ifdefs: {value}")
