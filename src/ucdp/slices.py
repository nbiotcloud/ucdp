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

"""IC Design Related Slice Handling."""

import enum
import re
from typing import Any

from .object import LightObject

_RE_STRING = re.compile(r"\[?(?P<left>[^:\]]+)(:(?P<right>[^\]]+))?\]?")


class SliceDirection(enum.Enum):
    """Slice Direction."""

    DOWN = 0
    UP = 1


DOWN = SliceDirection.DOWN
UP = SliceDirection.UP


class Slice(LightObject):
    """
    Bit slice of `width` bits starting at bit position `left` or `right`.

    >>> s = Slice(right=6, left=9)
    >>> s
    Slice('9:6')
    >>> s.left
    9
    >>> s.right
    6
    >>> s.width
    4
    >>> str(s)
    '9:6'
    >>> s.mask
    960
    >>> s.direction
    <SliceDirection.DOWN: 0>
    >>> s.slice
    slice(9, 6, -1)

    >>> s = Slice(left=6, right=9)
    >>> s
    Slice('6:9')
    >>> s.left
    6
    >>> s.right
    9
    >>> s.width
    4
    >>> str(s)
    '6:9'
    >>> s.mask
    960
    >>> s.direction
    <SliceDirection.UP: 1>
    >>> s.slice
    slice(6, 9, 1)

    >>> Slice(left=7, right=4) in Slice(left=7, right=4)
    True
    >>> Slice(left=7, right=5) in Slice(left=7, right=4)
    True
    >>> Slice(left=6, right=4) in Slice(left=7, right=4)
    True
    >>> Slice(left=7, right=4) in Slice(left=6, right=4)
    False
    >>> Slice(left=7, right=4) in Slice(left=7, right=5)
    False
    >>> Slice(left=7, right=5) in Slice(left=4, right=7)
    False

    >>> Slice('2:1')
    Slice('2:1')
    >>> Slice('1:2')
    Slice('1:2')
    >>> Slice(2)
    Slice('2')
    >>> Slice(right=2)
    Slice('2')
    >>> Slice(right=2, left=3)
    Slice('3:2')
    >>> Slice.cast(slice(2, 1))
    Slice('2:1')
    >>> Slice.cast(slice(1, 2))
    Slice('1:2')
    >>> Slice('')
    Traceback (most recent call last):
      ...
    ValueError: Invalid Slice Specification ''
    """

    left: Any
    right: Any

    def __init__(self, left: Any | None = None, right: Any | None = None) -> None:
        if isinstance(left, str):
            assert right is None, right
            mat = _RE_STRING.match(left)
            if mat:
                left = int(mat.group("left"))
                right = int(mat.group("right")) if mat.group("right") else None
            else:
                raise ValueError(f"Invalid Slice Specification {left!r}") from None
        if left is None:
            left = right
        elif right is None:
            right = left
        super().__init__(left=left, right=right)  # type: ignore[call-arg]

    @property
    def width(self) -> int:
        """Slice Width."""
        return abs(self.left - self.right) + 1

    @staticmethod
    def cast(value, direction=None) -> "Slice":
        """
        Create :any:`Slice` from `value`.

        These three formats are supported:

        >>> Slice.cast("[15:4]")
        Slice('15:4')
        >>> Slice.cast("[4:15]")
        Slice('4:15')
        >>> Slice.cast("[16]")
        Slice('16')
        >>> Slice.cast(range(4,16))
        Slice('4:15')
        >>> Slice.cast(range(15, 3, -1))
        Slice('15:4')
        >>> Slice.cast('16')
        Slice('16')
        >>> Slice.cast(16)
        Slice('16')
        >>> Slice.cast(Slice('16'))
        Slice('16')
        >>> Slice.cast('')
        Traceback (most recent call last):
          ...
        ValueError: Invalid Slice Specification ''
        >>> Slice.cast(None)
        Traceback (most recent call last):
          ...
        ValueError: Invalid Slice Specification None
        >>> Slice.cast("[4]", direction=DOWN)
        Slice('4')
        >>> Slice.cast("[4:15]", direction=DOWN)
        Traceback (most recent call last):
          ...
        ValueError: Slice must be downwards but is 4:15
        """
        slice_ = None
        if isinstance(value, Slice):
            slice_ = value
        elif isinstance(value, slice):
            slice_ = Slice(left=value.start, right=value.stop)
        elif isinstance(value, range):
            values = tuple(value)
            slice_ = Slice(left=values[0], right=values[-1])
        elif isinstance(value, int):
            slice_ = Slice(left=value)
        elif isinstance(value, str):
            mat = _RE_STRING.match(value)
            if mat:
                left = int(mat.group("left"))
                right = int(mat.group("right")) if mat.group("right") else None
                slice_ = Slice(left=left, right=right)
        if slice_ is not None:
            if direction:
                if slice_.direction not in (None, direction):
                    raise ValueError(f"Slice must be {direction.name.lower()}wards but is {slice_!s}")
            return slice_
        raise ValueError(f"Invalid Slice Specification {value!r}") from None

    @property
    def bits(self):
        """
        Colon separated bits.

        >>> Slice(left=4, right=8).bits
        '4:8'
        >>> Slice(left=8, right=4).bits
        '8:4'
        >>> Slice(left=4).bits
        '4'
        >>> Slice(right=4).bits
        '4'
        """
        if self.width > 1:
            return f"{self.left}:{self.right}"
        return f"{self.left}"

    def __str__(self):
        return self.bits

    def __repr__(self):
        if self.width > 1:
            return f"{self.__class__.__qualname__}('{self.left}:{self.right}')"
        return f"{self.__class__.__qualname__}('{self.left}')"

    @property
    def mask(self):
        """
        Mask.

        >>> Slice(left=4, right=8).mask
        496
        >>> Slice(left=8, right=4).mask
        496
        >>> Slice(left=4).mask
        16
        >>> Slice(right=4).mask
        16
        """
        return ((2**self.width) - 1) << min(self.right, self.left)

    @property
    def direction(self):
        """
        Direction.

        >>> Slice(left=4, right=8).direction
        <SliceDirection.UP: 1>
        >>> Slice(left=8, right=4).direction
        <SliceDirection.DOWN: 0>
        >>> Slice(left=4).direction
        >>> Slice(right=4).direction
        """
        if self.left > self.right:
            return SliceDirection.DOWN
        if self.left < self.right:
            return SliceDirection.UP
        return None

    def extract(self, word):
        """
        Extract slice value from `word`.

        >>> slice = Slice(left=5, right=1)
        >>> slice.mask
        62
        >>> slice.extract(0x59)
        12
        """
        return (word & self.mask) >> self.right

    @property
    def slice(self):
        """Python Slice Equivalent."""
        step = -1 if self.left > self.right else 1
        return slice(self.left, self.right, step)

    def __contains__(self, other):
        if isinstance(other, Slice):
            direction = self.direction
            otherdirection = other.direction
            if direction and otherdirection and direction != otherdirection:
                return False
            mask = self.mask
            return mask == mask | other.mask
        return NotImplemented
