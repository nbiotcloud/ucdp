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
"""Name Utilities."""
import functools
import re
from typing import Any, Tuple

from caseconverter import snakecase
from fuzzywuzzy import process
from humanfriendly.text import concatenate

_RE_SPLIT_PREFIX = re.compile(r"(?i)(?P<prefix>([a-z]|inst)_)(?P<basename>([a-z][a-z0-9\._]*)?)\Z")
_RE_SPLIT_SUFFIX = re.compile(r"(?i)(?P<basename>([a-z][a-z0-9\._]*)?)(?P<suffix>_([a-z]|io))\Z")
_RE_NAME = re.compile(r"[a-zA-Z0-9][a-zA-Z_0-9\-]*")
_RE_IDENTIFIER = re.compile(r"[a-zA-Z][a-zA-Z_0-9]*")


def validate_name(value: Any):
    """
    Ensure `value` is a name.

    >>> validate_name('abc')
    'abc'
    >>> validate_name('_abc')
    Traceback (most recent call last):
        ...
    ValueError: Invalid name '_abc'
    >>> validate_name('aB9_a')
    'aB9_a'
    >>> validate_name('9ab')
    '9ab'
    """
    if not _RE_NAME.fullmatch(str(value)):
        raise ValueError(f"Invalid name '{value}'")
    return value


def validate_identifier(value: Any):
    """
    Ensure `value` is an identifier.

    >>> validate_identifier('abc')
    'abc'
    >>> validate_identifier('_abc')
    Traceback (most recent call last):
        ...
    ValueError: Invalid identifier '_abc'
    >>> validate_identifier('aB9_a')
    'aB9_a'
    >>> validate_identifier('9ab')
    Traceback (most recent call last):
        ...
    ValueError: Invalid identifier '9ab'
    """
    if not _RE_IDENTIFIER.fullmatch(str(value)):
        raise ValueError(f"Invalid identifier '{value}'")
    return value


@functools.lru_cache()
def split_prefix(name: str, prefixes=None) -> Tuple[str, str]:
    """
    Split Name Into Prefix and Basename.

    >>> split_prefix("i_count")
    ('i_', 'count')
    >>> split_prefix("u_count")
    ('u_', 'count')
    >>> split_prefix("inst_count")
    ('inst_', 'count')
    >>> split_prefix("I_VERY_LONG_NAME")
    ('I_', 'VERY_LONG_NAME')
    >>> split_prefix("BT_VERY_LONG_NAME")
    ('', 'BT_VERY_LONG_NAME')
    >>> split_prefix("")
    ('', '')

    The counterpart to this function is `join_names`.
    """

    mat = _RE_SPLIT_PREFIX.match(name)
    if mat:
        if prefixes is not None:
            prefix, basename = mat.group("prefix", "basename")  # type: ignore
            if prefix in prefixes:
                return prefix, basename
        else:
            return mat.group("prefix", "basename")  # type: ignore
    return "", name


@functools.lru_cache()
def split_suffix(name: str, suffixes=None) -> Tuple[str, str]:
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
        if suffixes is not None:
            basename, suffix = mat.group("basename", "suffix")  # type: ignore
            if suffix in suffixes:
                return basename, suffix
        else:
            return mat.group("basename", "suffix")  # type: ignore
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
        fuzzyitems = (repr(item) for item, ratio in process.extract(name, names, limit=5) if ratio >= 80)
        fuzzy = concatenate(fuzzyitems, conjunction="or")
        if fuzzy:
            msg = f"{msg}{sep}Did you mean {fuzzy}?"
    return msg


def get_snakecasename(cls):
    """
    Get snakecase name of `cls`.

    >>> class MyClass:
    ...     pass
    >>> get_snakecasename(MyClass)
    'my_class'
    """
    return snakecase(cls.__name__).removeprefix("_")
