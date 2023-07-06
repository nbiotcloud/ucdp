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
"""Type Iterator."""
from collections import namedtuple
from typing import Generator

from ..nameutil import join_names
from .array import ArrayType
from .base import AScalarType, AType
from .enum import BaseEnumType
from .orientation import FWD, Orientation
from .scalar import StringType
from .struct import BaseStructType

SubType = namedtuple("SubType", "name type_ orientation")


def typeiter(
    name: str, type_: AType, orientation: Orientation = FWD, filter_=None, stop=None
) -> Generator[SubType, None, None]:
    """
    Utility to flatten type hierarchies.

    Args:
        name: basename of identifier. Can be empty.
        type_: Type to iterate over.

    Keyword Args:
        orientation (Orientation): Initial orientation.
        filter_: Only yield elements which return `True` on `filter_(subtype)`
        stop: Stop on elements which return `True` on `stop(subtype)`
    """
    if isinstance(type_, (AScalarType, BaseEnumType, StringType)):
        subtype = SubType(name, type_, orientation)
        if not filter_ or filter_(subtype):
            yield subtype
    elif isinstance(type_, BaseStructType):
        subtype = SubType(name, type_, orientation)
        if not filter_ or filter_(subtype):
            yield subtype
        for sitem in type_.values():
            sorientation = orientation * sitem.orientation
            sname = join_names(name, sitem.name)
            subtype = SubType(sname, sitem.type_, sorientation)
            if not stop or not stop(subtype):
                yield from typeiter(sname, sitem.type_, sorientation, filter_, stop)
    elif isinstance(type_, ArrayType):
        subtype = SubType(name, type_.type_, orientation)
        if not stop or not stop(subtype):
            yield from typeiter(name, type_.type_, orientation, filter_, stop)
    else:
        assert False, f"Unsupported Type {type_!r}."
