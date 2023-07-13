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
Type Orientation and Port Directions.

Types can have an orientation (:any:`Orientation`) and ports have a :any:`Direction`.


Orient
===========

A member in a structural type can have an orientation:

* forward (`FWD`) from source to sink
* backward (`BWD`) from sink to source
* bi-directional (`BIDIR`) both directions

>>> from tabulate import tabulate
>>> orientations = (FWD, BWD, BIDIR)
>>> overview = [(d, d.mode, d.suffix) for d in orientations]
>>> print(tabulate(overview, ("Orient", ".mode", ".suffix")))
Orient      .mode  .suffix
--------  -------  ---------
FWD             1
BWD            -1
BIDIR           0

Direction
=========

Ports have a direction:

* input (`IN`)
* output (`OUT`)
* inout (`INOUT`)

>>> from tabulate import tabulate
>>> directions = (IN, OUT, INOUT)
>>> overview = [(d, d.mode, d.suffix) for d in directions]
>>> print(tabulate(overview, ("Direction", ".mode", ".suffix")))
Direction      .mode  .suffix
-----------  -------  ---------
IN                 1  _i
OUT               -1  _o
INOUT              0  _io

Common Features
===============

You can calculate with :any:`Orientation` ...

>>> FWD * FWD
FWD
>>> FWD * BWD
BWD
>>> FWD * BIDIR
BIDIR

... and :any:`Direction`

>>> IN * FWD
IN
>>> IN * BWD
OUT
>>> IN * FWD * BWD * FWD
OUT
>>> IN * BWD * BWD
IN
>>> OUT * FWD
OUT
>>> OUT * BWD
IN
>>> IN * BIDIR
INOUT
>>> INOUT * BIDIR
INOUT
>>> FWD * OUT
BWD
>>> FWD * INOUT
BIDIR

:any:`Orientation` and :any:`Direction` are singletons. There is just one instance of each.

>>> IN is IN
True
>>> IN is (IN * BWD * BWD)
True

:any:`Orientation` and :any:`Direction` can be compared:

>>> IN == IN
True
>>> IN == OUT
False
>>> IN == FWD
False

API
===
"""

from typing import Dict, Optional

from attrs import define

from ..attrs import ReusedFrozen, field


@define(frozen=True, on_setattr=None, repr=False, auto_attribs=False)
class AOrientation(ReusedFrozen):

    """Abstract Orientation."""

    _NAMEMAP: Dict[int, str] = {}

    mode = field()
    """
    Integer representation.
    """

    # pylint: disable=protected-access
    __name = field(init=False)

    @__name.default
    def _name_default(self):
        return self._NAMEMAP[self.mode]

    def __repr__(self):
        return self.__name

    def __mul__(self, other) -> "AOrientation":
        if isinstance(other, AOrientation):
            return self.__class__(self.mode * other.mode)
        return NotImplemented

    @property
    def suffix(self) -> str:
        """Suffix."""
        return ""


class Orientation(AOrientation):

    """Type Orientation."""

    # pylint: disable=too-few-public-methods

    _NAMEMAP = {
        1: "FWD",
        -1: "BWD",
        0: "BIDIR",
    }


class Direction(AOrientation):

    """Port Direction."""

    _NAMEMAP = {
        1: "IN",
        -1: "OUT",
        0: "INOUT",
    }

    _SUFFIXMAP = {
        1: "_i",
        -1: "_o",
        0: "_io",
    }

    @property
    def suffix(self) -> str:
        """Suffix."""
        return self._SUFFIXMAP[self.mode]

    @staticmethod
    def from_name(name: str) -> Optional["Direction"]:
        """
        Determine :any:`Direction` by suffix of `name`.

        >>> Direction.from_name('ctrl_i')
        IN
        >>> Direction.from_name('ctrl_o')
        OUT
        >>> Direction.from_name('ctrl_io')
        INOUT
        >>> Direction.from_name('ctrl_s')
        >>> Direction.from_name('')
        IN
        """
        if not name:
            return IN
        for mode, suffix in Direction._SUFFIXMAP.items():
            if name.endswith(suffix):
                return Direction(mode)
        return None


FWD = Orientation(1)
BWD = Orientation(-1)
BIDIR = Orientation(0)

IN = Direction(1)
OUT = Direction(-1)
INOUT = Direction(0)


def convert_aorientation(value) -> AOrientation:
    """
    Convert Direction.

    >>> convert_aorientation(FWD)
    FWD
    >>> convert_aorientation("test")
    Traceback (most recent call last):
      ...
    ValueError: Invalid orientation 'test'. Valid are FWD, BWD, BIDIR, IN, OUT and INOUT
    """
    if value in (FWD, BWD, BIDIR, IN, OUT, INOUT):
        return value
    raise ValueError(f"Invalid orientation {value!r}. Valid are FWD, BWD, BIDIR, IN, OUT and INOUT")


def convert_orientation(value) -> Orientation:
    """
    Convert Direction.

    >>> convert_orientation(FWD)
    FWD
    >>> convert_orientation("test")
    Traceback (most recent call last):
      ...
    ValueError: Invalid orientation 'test'. Valid are FWD, BWD and BIDIR
    """
    if value in (FWD, BWD, BIDIR):
        return value
    raise ValueError(f"Invalid orientation {value!r}. Valid are FWD, BWD and BIDIR")


def convert_direction(value) -> Direction:
    """
    Convert Direction.

    >>> convert_direction(IN)
    IN
    >>> convert_direction("test")
    Traceback (most recent call last):
      ...
    ValueError: Invalid direction 'test'. Valid are IN, OUT and INOUT
    """
    if value in (IN, OUT, INOUT):
        return value
    raise ValueError(f"Invalid direction {value!r}. Valid are IN, OUT and INOUT")
