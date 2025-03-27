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

    def __repr__(self):
        return self.name


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
    DOWN
    >>> s.slice
    slice(9, 6, -1)
    >>> tuple(s)
    (9, 8, 7, 6)
    >>> s.prev
    5
    >>> s.nxt
    10

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
    UP
    >>> s.slice
    slice(6, 9, 1)
    >>> tuple(s)
    (6, 7, 8, 9)
    >>> s.prev
    5
    >>> s.nxt
    10

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
    width: Any

    def __init__(  # noqa: C901, PLR0912
        self,
        left: Any | None = None,
        right: Any | None = None,
        width: Any | None = None,
        direction: SliceDirection | None = None,
    ) -> None:
        if isinstance(left, str):
            if right is not None:
                raise ValueError("'right' must be None")
            if width is not None:
                raise ValueError("'width' must be None")
            mat = _RE_STRING.match(left)
            if mat:
                left = int(mat.group("left"))
                right = int(mat.group("right")) if mat.group("right") else None
            else:
                raise ValueError(f"Invalid Slice Specification {left!r}") from None

        # this is quite complex here - but left, right and width may be u.Expr and we want to have them minimal
        if width is not None:
            if left is None:
                # 'width' given
                if direction in (None, SliceDirection.DOWN):
                    # downwards
                    if right is None:
                        right = 0
                    if isinstance(width, int) and width == 1:
                        left = right
                    elif isinstance(right, int) and right == 0:
                        left = width - 1
                    else:
                        left = width - 1 + right
                elif right is None:
                    left = 0
                    right = width - 1
                else:
                    left = right - (width - 1)

            elif right is None:
                # left and width given
                if direction in (None, SliceDirection.DOWN):
                    # downwards
                    right = left - (width - 1)
                else:
                    # upwards
                    right = left + (width - 1)
            else:
                # 'left', 'right' and 'width' given
                raise ValueError("'left', 'right' AND 'width' given, this is one too much")

        elif left is None:
            left = right
            width = 1
        elif right is None:
            right = left
            width = 1
        else:
            width = self._calc_width(left, right)
        _check_direction(left, right, direction)
        super().__init__(left=left, right=right, width=width)  # type: ignore[call-arg]

    @staticmethod
    def _calc_width(left: Any, right: Any) -> Any:
        """Slice Width."""
        return abs(left - right) + 1

    @staticmethod
    def cast(value, direction: SliceDirection | None = None) -> "Slice":
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
        ValueError: Slice must be downwards but is upwards
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
                slice_ = Slice(left=left, right=right, direction=direction)
        if slice_ is not None:
            _check_direction(slice_.left, slice_.right, direction)
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

    @property
    def prev(self):
        """Previous Bit respecting direction."""
        if self.left >= self.right:
            return self.right - 1
        return self.left - 1

    @property
    def nxt(self):
        """Next Free Bit respecting direction."""
        if self.left >= self.right:
            return self.right + self.width
        return self.left + self.width

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
    def direction(self) -> SliceDirection | None:
        """
        Direction.

        >>> Slice(left=4, right=8).direction
        UP
        >>> Slice(left=8, right=4).direction
        DOWN
        >>> Slice(left=4).direction
        >>> Slice(right=4).direction
        """
        return _get_direction(self.left, self.right)

    def extract(self, word: int, is_signed: bool = False) -> int:
        """
        Extract slice value from `word`.

        >>> slice = Slice(width=4, right=4)
        >>> hex(slice.mask)
        '0xf0'
        >>> slice.extract(0x193)
        9
        >>> slice.extract(0x193, is_signed=True)
        -7
        """
        value = (word & self.mask) >> self.right
        if is_signed:
            value = _unsigned_to_signed(value, self.width)
        return value

    def update(self, word, value, is_signed: bool = False):
        """
        Extract slice value from `word`.

        >>> slice = Slice(width=4, right=4)
        >>> hex(slice.mask)
        '0xf0'
        >>> hex(slice.update(0x123, 9))
        '0x193'
        >>> hex(slice.update(0x123, -7, is_signed=True))
        '0x193'
        >>> slice.update(0x123, -7)
        Traceback (most recent call last):
          ...
        ValueError: -7 is not a unsigned 4 bit integer
        """
        mask = self.mask
        if is_signed:
            value = _signed_to_unsigned(value, self.width)
        else:
            _check_unsigned(value, self.width)
        return (word & ~mask) | ((value << self.right) & mask)

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

    def __iter__(self):
        if self.left > self.right:
            yield from range(self.left, self.right - 1, -1)
        else:
            yield from range(self.left, self.right + 1, 1)


def _get_direction(left: Any, right: Any) -> SliceDirection | None:
    if left > right:
        return SliceDirection.DOWN
    if left < right:
        return SliceDirection.UP
    return None


def _check_direction(left: Any, right: Any, direction: SliceDirection | None):
    slicedirection = _get_direction(left, right)
    if direction and slicedirection and direction != slicedirection:
        req = direction.name.lower()
        act = slicedirection.name.lower()
        raise ValueError(f"Slice must be {req}wards but is {act}wards")


def _signed_to_unsigned(value: int, width: int) -> int:
    high = (1 << (width - 1)) - 1
    low = ~high
    if value < low or value > high:
        msg = f"{value} is not a signed {width} bit integer"
        raise ValueError(msg)
    return (value + (1 << width)) & (~(-1 << width))


def _check_unsigned(value: int, width: int) -> None:
    low = 0
    high = (1 << width) - 1
    if value < low or value > high:
        msg = f"{value} is not a unsigned {width} bit integer"
        raise ValueError(msg)


def _unsigned_to_signed(value: int, width: int) -> int:
    _check_unsigned(value, width)
    if value & (1 << (width - 1)):  # MSB set->negative
        return value - (1 << width)
    return value


def mask_to_slices(mask: int) -> tuple[Slice, ...]:
    """
    Convert `mask` to tuple of :any:`Slice` instances.

    >>> mask_to_slices(0x0FFFFFF0)
    (Slice('27:4'),)
    >>> mask_to_slices(0x0FFF0FF0)
    (Slice('11:4'), Slice('27:16'))
    """
    slices = []
    right = None
    for idx, bit in enumerate(reversed("0" + bin(mask)[2:])):
        if bit == "1":
            if right is None:
                right = idx
        elif right is not None:
            left = idx - 1
            slices.append(Slice(left=left, right=right))
            right = None
    return tuple(slices)
