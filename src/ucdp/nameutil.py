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
Name Utilities.
"""

import functools
import re

from caseconverter import snakecase
from fuzzywuzzy import process
from humanfriendly.text import concatenate

_FUZZY_MINRATIO: int = 80
_RE_STARTNUM = re.compile(r"^[0-9]")
_RE_SPLIT_PREFIX = re.compile(r"(?i)(?P<prefix>([a-z][a-z]?)_)(?P<basename>([a-z][a-z0-9_]*)?)\Z")
_RE_SPLIT_SUFFIX = re.compile(r"(?i)(?P<basename>([a-z][a-z0-9_]*)?)(?P<suffix>_([a-z][a-z]?))\Z")


@functools.lru_cache
def split_prefix(name: str) -> tuple[str, str]:
    """
    Split Name Into Prefix and Basename.

    >>> split_prefix("i_count")
    ('i_', 'count')
    >>> split_prefix("u_count")
    ('u_', 'count')
    >>> split_prefix("I_VERY_LONG_NAME")
    ('I_', 'VERY_LONG_NAME')
    >>> split_prefix("BT_VERY_LONG_NAME")
    ('BT_', 'VERY_LONG_NAME')
    >>> split_prefix("")
    ('', '')

    The counterpart to this function is `join_names`.
    """
    mat = _RE_SPLIT_PREFIX.match(name)
    if mat:
        return mat.group("prefix", "basename")  # type: ignore[return-value]
    return "", name


@functools.lru_cache
def split_suffix(name: str, suffixes=None) -> tuple[str, str]:
    """
    Split Name Into Basename And Suffix.

    >>> split_suffix("count_i")
    ('count', '_i')
    >>> split_suffix("count_o")
    ('count', '_o')
    >>> split_suffix("count_io")
    ('count', '_io')
    >>> split_suffix("count_t")
    ('count', '_t')
    >>> split_suffix("count_s")
    ('count', '_s')
    >>> split_suffix("_s")
    ('', '_s')
    >>> split_suffix("very_long_name_s")
    ('very_long_name', '_s')
    >>> split_suffix("VERY_LONG_NAME_S")
    ('VERY_LONG_NAME', '_S')
    >>> split_suffix("")
    ('', '')

    The counterpart to this function is `join_names`.
    """
    mat = _RE_SPLIT_SUFFIX.match(name)
    if mat:
        return mat.group("basename", "suffix")  # type: ignore[return-value]
    return name, ""


def join_names(*names, concat="_") -> str:
    """
    Join Names.

    >>> join_names('foo', 'bar')
    'foo_bar'
    >>> join_names('', 'bar')
    'bar'
    >>> join_names('foo', '')
    'foo'

    This function is the counterpart to `split_names`.
    """
    return concat.join(name for name in names if name)


def didyoumean(name, names, known=False, multiline=False) -> str:
    """
    Propose matching names.

    >>> didyoumean('abb', tuple())
    ''
    >>> didyoumean('abb', ('abba', 'ac/dc', 'beatles'), known=True)
    " Known are 'abba', 'ac/dc' and 'beatles'. Did you mean 'abba'?"
    >>> print(didyoumean('zz-top', ('abba', 'ac/dc', 'beatles'), known=True, multiline=True))
    <BLANKLINE>
    Known are 'abba', 'ac/dc' and 'beatles'.
    """
    sep = "\n" if multiline else " "
    if known:
        knowns = concatenate(repr(name) for name in names)
        msg = f"{sep}Known are {knowns}."
    else:
        msg = ""
    # fuzzy
    if names:
        fuzzyitems = (repr(item) for item, ratio in process.extract(name, names, limit=5) if ratio >= _FUZZY_MINRATIO)
        fuzzy = concatenate(fuzzyitems, conjunction="or")
        if fuzzy:
            msg = f"{msg}{sep}Did you mean {fuzzy}?"
    return msg


def get_snakecasename(item):
    """
    Get snakecase name of `cls`.

    >>> class MyClass:
    ...     pass
    >>> get_snakecasename(MyClass)
    'my_class'
    >>> get_snakecasename("MyClass")
    'my_class'
    >>> get_snakecasename("MYClass")
    'myclass'
    """
    if not isinstance(item, str):
        item = item.__name__
    return snakecase(item).removeprefix("_")


def str2identifier(value: str) -> str:
    """
    Convert Any String To Identifier.

    >>> str2identifier('A B C')
    'a_b_c'
    >>> str2identifier('1 2 3')
    'v1_2_3'
    >>> str2identifier('12.3')
    'v123'
    """
    value = snakecase(value)
    mat = _RE_STARTNUM.match(value)
    if mat:
        value = f"v{value}"
    return value
