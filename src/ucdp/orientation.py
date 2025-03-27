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
Type Orientation and Port Directions.

Types can have an orientation (:any:`Orientation`) and ports have a :any:`Direction`.


Orient
===========

A member in a structural type can have an orientation:

* forward (`FWD`) from source to sink
* backward (`BWD`) from sink to source

>>> from tabulate import tabulate
>>> import ucdp as u
>>> orientations = (u.FWD, u.BWD)
>>> overview = [(d, d.mode, d.name, d.suffix) for d in orientations]
>>> print(tabulate(overview, ("Orient", ".mode", ".name", ".suffix")))
Orient      .mode  .name    .suffix
--------  -------  -------  ---------
FWD             1  FWD
BWD            -1  BWD

Direction
=========

Ports have a direction:

* input (`IN`)
* output (`OUT`)
* inout (`INOUT`)
* input-monitor (`INM`)
* output-monitor (`OUTM`)

>>> from tabulate import tabulate
>>> import ucdp as u
>>> directions = (u.IN, u.OUT, u.INOUT)
>>> overview = [(d, d.mode, d.name, d.suffix) for d in directions]
>>> print(tabulate(overview, ("Direction", ".mode", ".name", ".suffix")))
Direction      .mode  .name    .suffix
-----------  -------  -------  ---------
IN                 1  IN       _i
OUT               -1  OUT      _o
INOUT              0  INOUT    _io

Common Features
===============

You can calculate with :any:`Orientation` ...

>>> FWD * FWD
FWD
>>> FWD * BWD
BWD

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
>>> INOUT * FWD
INOUT
>>> INOUT * BWD
INOUT
>>> FWD * OUT
BWD

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

from typing import ClassVar, Optional, Union

from .object import LightObject


class AOrientation(LightObject):
    """Abstract Orientation."""

    _NAMEMAP: ClassVar[dict[int, str]] = {}

    mode: int
    """
    Integer representation.
    """

    def __init__(self, mode):
        if mode not in self._NAMEMAP:
            raise ValueError(f"Invalid mode {mode}")
        super().__init__(mode=mode)

    @property
    def name(self):
        """Name."""
        return self._NAMEMAP[self.mode]

    def __str__(self):
        return self._NAMEMAP[self.mode]

    def __repr__(self):
        return self._NAMEMAP[self.mode]

    def __mul__(self, other) -> "AOrientation":
        if isinstance(other, AOrientation):
            return self.__class__(mode=self.mode * other.mode)
        return NotImplemented

    @property
    def suffix(self) -> str:
        """Suffix."""
        return ""

    @classmethod
    def cast(cls, value: Union["AOrientation", int]) -> "AOrientation":
        """Cast `value`."""
        if isinstance(value, cls):
            return value
        if isinstance(value, AOrientation):
            return cls(mode=value.mode)
        if isinstance(value, int) and value in cls._NAMEMAP.keys():
            return cls(mode=value)
        raise ValueError(f"Cannot cast {value}")


class Orientation(AOrientation):
    """
    Type Orientation.

    >>> import ucdp as u
    >>> u.Orientation.cast(1)
    FWD
    >>> u.Orientation.cast(u.FWD)
    FWD
    >>> u.Orientation.cast(u.IN)
    FWD
    """

    _NAMEMAP: ClassVar[dict[int, str]] = {
        1: "FWD",
        -1: "BWD",
    }


class Direction(AOrientation):
    """Port Direction."""

    _NAMEMAP: ClassVar[dict[int, str]] = {
        1: "IN",
        -1: "OUT",
        0: "INOUT",
    }

    _SUFFIXMAP: ClassVar[dict[int, str]] = {
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
        """
        for mode, suffix in Direction._SUFFIXMAP.items():
            if name.endswith(suffix):
                return Direction(mode=mode)
        return None


FWD = Orientation(mode=1)
BWD = Orientation(mode=-1)

IN = Direction(mode=1)
OUT = Direction(mode=-1)
INOUT = Direction(mode=0)
