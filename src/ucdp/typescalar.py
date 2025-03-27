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
Scalar Types.

* :any:`IntegerType`
* :any:`BitType`
* :any:`BoolType`
* :any:`RailType`
* :any:`UintType`
* :any:`SintType`
"""

from typing import Any, ClassVar

from humannum import hex_

from .casting import Casting
from .slices import DOWN, Slice
from .typebase import AScalarType, AVecType, BaseType
from .typebaseenum import BaseEnumType

INTEGER_WIDTH: int = 32


class IntegerType(AScalarType):
    """
    Native Signed 32-Bit Integer.

    Attributes:
        default: Default Value. 0 by default.

    The width is fixed to 32.

    Documentation defaults are empty by default:

    >>> import ucdp as u
    >>> u.IntegerType().title
    >>> u.IntegerType().descr
    >>> u.IntegerType().comment

    Example:
    >>> example = u.IntegerType()
    >>> example
    IntegerType()
    >>> example.width
    32
    >>> example.default
    0

    Another Example:

    >>> example = u.IntegerType(default=8)
    >>> example
    IntegerType(default=8)
    >>> example.width
    32
    >>> example.default
    8

    Selective Coverage Disable:

    >>> example = u.IntegerType()
    >>> example
    IntegerType()

    Range checking:

    >>> 5 in IntegerType()
    True
    >>> range(3, 10) in IntegerType()
    True
    >>> 2**32 in IntegerType()
    False

    Slicing:

    >>> u.IntegerType(default=31)['31:0']
    IntegerType(default=31)
    >>> u.IntegerType(default=31)['3:1']
    UintType(3, default=7)
    >>> u.IntegerType(default=31)['32:31']
    Traceback (most recent call last):
        ...
    ValueError: Cannot slice bit(s) 32:31 from IntegerType(default=31) with dimension [31:0]
    """

    width: ClassVar[int] = INTEGER_WIDTH  # type: ignore[misc]
    """Width in Bits."""

    min_: ClassVar[int] = -1 * 2 ** (width - 1)
    """Minimal Value."""

    max_: ClassVar[int] = 2 ** (width - 1) - 1
    """Maximal Value."""

    logic: bool = True
    """Include X and Z states, not just numeric values."""

    default: Any = 0
    """Default Value."""

    def check(self, value, what="Value") -> int:
        """
        Check `value` for type.

        Values are limited to 32-bit signed [-2147483648, 2147483647].

        >>> import ucdp as u
        >>> example = u.IntegerType()
        >>> example.check(0)
        0
        >>> example.check(2147483647)
        2147483647
        >>> example.check(2147483648)
        Traceback (most recent call last):
          ...
        ValueError: Value 2147483648 is not a 32-bit signed integer with range [-2147483648, 2147483647]
        >>> example.check(-2147483648)
        -2147483648
        >>> example.check(-2147483649)
        Traceback (most recent call last):
          ...
        ValueError: Value -2147483649 is not a 32-bit signed integer with range [-2147483648, 2147483647]
        """
        value = int(value)
        if (value < self.min_) or (value > self.max_):
            raise ValueError(f"{what} {value} is not a 32-bit signed integer with range [{self.min_}, {self.max_}]")
        return value

    def get_hex(self, value=None):
        """
        Return Hex Value.

        >>> import ucdp as u
        >>> u.IntegerType(default=0x10FEC0DE).get_hex()
        Hex('0x10FEC0DE')
        >>> u.IntegerType(default=0x10FEC0DE).get_hex(value=0xBEEF)
        Hex('0x0000BEEF')
        >>> u.IntegerType().get_hex(value=9)
        Hex('0x00000009')
        """
        if value is None:
            value = self.default
        self.check(value)
        value = int(value)
        wrap = 1 << 32
        value = (value + wrap) % wrap
        return hex_(value, width=32)

    def is_connectable(self, other) -> bool:
        """
        Check For Valid Connection To `other`.

        Connections are only allowed to other :any:`IntegerType`.

        >>> IntegerType().is_connectable(IntegerType())
        True
        >>> IntegerType(default=1).is_connectable(IntegerType(default=2))
        True
        """
        return (
            isinstance(other, (SintType, IntegerType))
            and int(other.width) == INTEGER_WIDTH  # type: ignore[operator]
            and self.logic == other.logic
        )

    def __getitem__(self, slice_):
        """Return Sliced Variant."""
        slice_ = Slice.cast(slice_, direction=DOWN)
        if slice_.width == INTEGER_WIDTH and slice_.right == 0:
            return self
        if slice_.left < (INTEGER_WIDTH - 1):
            return UintType(slice_.width, default=slice_.extract(self.default))
        raise ValueError(f"Cannot slice bit(s) {slice_!s} from {self} with dimension [31:0]")


class BitType(AScalarType):
    """
    Native Single Bit.

    Attributes:
        default: Default Value. 0 by default.

    The width is fixed to 1.

    Example:
    >>> import ucdp as u
    >>> example = u.BitType()
    >>> example
    BitType()
    >>> example.width
    1
    >>> example.default
    0

    Another Example:

    >>> example = u.BitType(default=1)
    >>> example
    BitType(default=1)
    >>> example.width
    1
    >>> example.default
    1

    Slicing:

    >>> u.BitType(default=1)[0]
    BitType(default=1)
    >>> u.BitType(default=1)[32:31]
    Traceback (most recent call last):
        ...
    ValueError: Cannot slice bit(s) 32:31 from BitType(default=1)
    """

    width: ClassVar[int] = 1  # type: ignore[misc]
    """Width in Bits."""

    min_: ClassVar[int] = 0  # type: ignore[misc]
    """Minimal Value."""

    max_: ClassVar[int] = 1  # type: ignore[misc]
    """Maximal Value."""

    logic: bool = True
    """Include X and Z states, not just numeric values."""

    default: Any = 0
    """Default Value."""

    @staticmethod
    def check(value, what="Value") -> int:
        """
        Check `value` for type.

        Values are limited to 0 and 1

        >>> import ucdp as u
        >>> example = u.BitType()
        >>> example.check(-1)
        Traceback (most recent call last):
          ...
        ValueError: Value -1 is not a single bit with range [0, 1]
        >>> example.check(0)
        0
        >>> example.check(1)
        1
        >>> example.check(2)
        Traceback (most recent call last):
          ...
        ValueError: Value 2 is not a single bit with range [0, 1]
        >>> example.check(False)
        0
        >>> example.check(True)
        1
        """
        value = int(value)
        if value not in (0, 1):
            raise ValueError(f"{what} {value} is not a single bit with range [0, 1]")
        return value

    def get_hex(self, value=None):
        """
        Return Hex Value.

        >>> import ucdp as u
        >>> u.BitType().get_hex()
        Hex('0x0')
        >>> u.BitType(default=1).get_hex()
        Hex('0x1')
        >>> u.BitType().get_hex(value=1)
        Hex('0x1')
        """
        if value is None:
            value = self.default
        self.check(value)
        return hex_(value, width=1)

    def is_connectable(self, other) -> bool:
        """
        Check For Valid Connection To `other`.

        Connections are only allowed to other :any:`BitType`.

        >>> BitType().is_connectable(BitType())
        True
        >>> BitType(default=1).is_connectable(BitType(default=0))
        True

        A connection to an :any:`UintType()` of width is forbidden (requires a cast).

        >>> BitType().is_connectable(UintType(2))
        False
        """
        return isinstance(other, BitType) and int(other.width) == 1 and self.logic == other.logic  # type: ignore[operator]

    def cast(self, other: BaseType) -> Casting:
        """
        How to cast an input of type `self` from a value of type `other`.

        `self = cast(other)`
        """
        if isinstance(other, (UintType, BitType, SintType, IntegerType, RailType)) and self.width == other.width:  # type: ignore[operator]
            return [("", "")]

        if isinstance(other, BaseEnumType) and self.width == other.keytype.width:  # type: ignore[operator]
            return [("", "")]

        return None

    def __getitem__(self, slice_):
        slice_ = Slice.cast(slice_, direction=DOWN)
        if slice_.width == 1 and slice_.right == 0:
            return self
        raise ValueError(f"Cannot slice bit(s) {slice_!s} from {self}")


class BoolType(AScalarType):
    """
    Native Boolean.

    Attributes:
        default: Default Value. 0 by default.

    The width is fixed to 1.

    Example:
    >>> import ucdp as u
    >>> example = u.BoolType()
    >>> example
    BoolType()
    >>> example.width
    1
    >>> example.default
    0

    Another Example:

    >>> example = u.BoolType(default=True)
    >>> example
    BoolType(default=True)
    >>> example.width
    1
    >>> example.default
    True

    Slicing:

    >>> u.BoolType(default=True)[0]
    BoolType(default=True)
    >>> u.BoolType()[32:31]
    Traceback (most recent call last):
        ...
    ValueError: Cannot slice bit(s) 32:31 from BoolType()
    """

    default: Any = False
    """Default Value."""

    width: ClassVar[int] = 1  # type: ignore[misc]
    """Width in Bits."""

    @staticmethod
    def check(value, what="Value") -> bool:
        """
        Check `value` for type.

        Values are limited to 0 and 1

        >>> import ucdp as u
        >>> example = u.BoolType()
        >>> example.check(-1)
        Traceback (most recent call last):
          ...
        ValueError: Value -1 is not a boolean
        >>> example.check(0)
        0
        >>> example.check(1)
        1
        >>> example.check(2)
        Traceback (most recent call last):
          ...
        ValueError: Value 2 is not a boolean
        >>> example.check(False)
        0
        >>> example.check(True)
        1
        """
        # Note: we need identity check here
        if int(value) in (0, 1):
            return value
        raise ValueError(f"{what} {value} is not a boolean")

    def get_hex(self, value=None):
        """
        Return Hex Value.

        >>> import ucdp as u
        >>> u.BoolType().get_hex()
        Hex('0x0')
        >>> u.BoolType(default=True).get_hex()
        Hex('0x1')
        >>> u.BoolType().get_hex(value=True)
        Hex('0x1')
        """
        if value is None:
            value = self.default
        self.check(value)
        return hex_(value, width=1)

    def is_connectable(self, other) -> bool:
        """
        Check For Valid Connection To `other`.

        Connections are only allowed to other :any:`BoolType`.

        >>> BoolType().is_connectable(BoolType())
        True
        >>> BoolType(default=True).is_connectable(BoolType(default=False))
        True

        A connection to an :any:`UintType()` is forbidden (requires a cast).

        >>> BoolType().is_connectable(UintType(1))
        False
        """
        return isinstance(other, BoolType)

    def __getitem__(self, slice_):
        slice_ = Slice.cast(slice_, direction=DOWN)
        if slice_.width == 1 and slice_.right == 0:
            return self
        raise ValueError(f"Cannot slice bit(s) {slice_!s} from {self}")


class RailType(AScalarType):
    """
    Voltage Rail.

    Attributes:
        default: Default Value. 0 by default.

    The width is fixed to 1.

    Example:
    >>> import ucdp as u
    >>> example = u.RailType()
    >>> example
    RailType()
    >>> example.width
    1
    >>> example.default

    Another Example:

    >>> example = u.RailType(default=1)
    >>> example
    RailType(default=1)
    >>> example.width
    1
    >>> example.default
    1

    Slicing:

    >>> u.RailType(default=1)[0]
    RailType(default=1)
    >>> u.RailType(default=1)[32:31]
    Traceback (most recent call last):
        ...
    ValueError: Cannot slice bit(s) 32:31 from RailType(default=1)
    """

    width: ClassVar[int] = 1  # type: ignore[misc]
    """Width in Bits."""

    logic: bool = True
    """Include X and Z states, not just numeric values."""

    default: Any | None = None
    """Default Value."""

    @staticmethod
    def check(value, what="Value") -> int:
        """
        Check `value` for type.

        Values are limited to 0 and 1

        >>> import ucdp as u
        >>> example = u.RailType()
        >>> example.check(-1)
        Traceback (most recent call last):
          ...
        ValueError: Value -1 is not a single bit with range [0, 1]
        >>> example.check(0)
        0
        >>> example.check(1)
        1
        >>> example.check(2)
        Traceback (most recent call last):
          ...
        ValueError: Value 2 is not a single bit with range [0, 1]
        >>> example.check(False)
        0
        >>> example.check(True)
        1
        """
        value = int(value)
        if value not in (0, 1):
            raise ValueError(f"{what} {value} is not a single bit with range [0, 1]")
        return value

    def get_hex(self, value=None):
        """
        Return Hex Value.

        >>> import ucdp as u
        >>> u.RailType().get_hex()
        >>> u.RailType(default=0).get_hex()
        Hex('0x0')
        >>> u.RailType(default=1).get_hex()
        Hex('0x1')
        >>> u.RailType().get_hex(value=1)
        Hex('0x1')
        """
        if value is None:
            value = self.default
        if value is None:
            return None
        self.check(value)
        return hex_(value, width=1)

    def is_connectable(self, other) -> bool:
        """
        Check For Valid Connection To `other`.

        Connections are only allowed to other :any:`RailType`.

        >>> RailType().is_connectable(RailType())
        True
        >>> RailType(default=1).is_connectable(RailType(default=0))
        True

        A connection to an :any:`BitType()` is forbidden (requires a cast).

        >>> RailType().is_connectable(BitType())
        False
        """
        return isinstance(other, RailType) and self.logic == other.logic

    def cast(self, other: BaseType) -> Casting:
        """
        How to cast an input of type `self` from a value of type `other`.

        `self = cast(other)`
        """
        if isinstance(other, (UintType, BitType, SintType, IntegerType, RailType)) and self.width == other.width:  # type: ignore[operator]
            return [("", "")]

        if isinstance(other, BaseEnumType) and self.width == other.keytype.width:  # type: ignore[operator]
            return [("", "")]

        return None

    def __getitem__(self, slice_):
        slice_ = Slice.cast(slice_, direction=DOWN)
        if slice_.width == 1 and slice_.right == 0:
            return self
        raise ValueError(f"Cannot slice bit(s) {slice_!s} from {self}")


class UintType(AVecType):
    """
    Vector With Unsigned Interpretation.

    Args:
        width (int): Width in bits.

    Attributes:
        default: Default Value. 0 by default.

    Example:
    >>> import ucdp as u
    >>> example = u.UintType(12)
    >>> example
    UintType(12)
    >>> example.width
    12
    >>> example.default
    0

    Another Example:

    >>> example = u.UintType(16, default=8)
    >>> example
    UintType(16, default=8)
    >>> example.width
    16
    >>> example.default
    8

    Selective Coverage Disable:

    >>> example = u.UintType(32)
    >>> example
    UintType(32)

    Slicing:

    >>> u.UintType(16, default=31)[15:0]
    UintType(16, default=31)
    >>> u.UintType(16, default=31)[3:1]
    UintType(3, default=7)
    >>> u.UintType(16, default=31)[16:15]
    Traceback (most recent call last):
        ...
    ValueError: Cannot slice bit(s) 16:15 from UintType(16, default=31)
    """

    min_: ClassVar[int] = 0
    """Minimal Value."""

    default: Any = 0
    """Default Value."""

    def __init__(self, width, **kwargs):
        super().__init__(width=width, **kwargs)

    @property
    def max_(self):
        """Maximum Value."""
        return (2**self.width) - 1

    def check(self, value, what="Value") -> int:
        """
        Check `value` for type.

        >>> import ucdp as u
        >>> example = u.UintType(8)
        >>> example.check(0)
        0
        >>> example.check(255)
        255
        >>> example.check(256)
        Traceback (most recent call last):
          ...
        ValueError: Value 256 is not a 8-bit integer with range [0, 255]
        >>> example.check(-1)
        Traceback (most recent call last):
          ...
        ValueError: Value -1 is not a 8-bit integer with range [0, 255]
        """
        value = int(value)

        if (value < 0) or (value > int(self.max_)):
            raise ValueError(f"{what} {value} is not a {self.width}-bit integer with range [0, {self.max_}]")
        return value

    def get_hex(self, value=None):
        """
        Return Hex Value.

        >>> import ucdp as u
        >>> u.UintType(9).get_hex()
        Hex('0x000')
        >>> u.UintType(9, default=0xFE).get_hex()
        Hex('0x0FE')
        >>> u.UintType(9).get_hex(value=0xFE)
        Hex('0x0FE')
        """
        if value is None:
            value = self.default
        self.check(value)
        return hex_(value, width=self.width)

    def is_connectable(self, other) -> bool:
        """
        Check For Valid Connection To `other`.

        Connections are only allowed to other :any:`UintType` of the same width.

        >>> UintType(8).is_connectable(UintType(8))
        True
        >>> UintType(8).is_connectable(UintType(9))
        False
        >>> UintType(8, default=1).is_connectable(UintType(8, default=0))
        True

        A connection to an :any:`BitType()` is allowed, but :any:`SintType()` is forbidden (requires a cast).

        >>> UintType(1).is_connectable(BitType())
        True
        >>> UintType(1).is_connectable(SintType(1))
        False
        """
        return isinstance(other, (UintType, BitType)) and self.width == other.width and self.logic == other.logic  # type: ignore[operator]

    def cast(self, other: BaseType) -> Casting:
        """
        How to cast an input of type `self` from a value of type `other`.

        `self = cast(other)`
        """
        if isinstance(other, (SintType, IntegerType)) and self.width == other.width:  # type: ignore[operator]
            return [("", "")]

        if isinstance(other, BaseEnumType) and self.width == other.keytype.width:
            return [("", "")]

        return None

    def __getitem__(self, slice_):
        slice_ = Slice.cast(slice_, direction=DOWN)
        if slice_.width == self.width and slice_.right == self.right:
            return self
        if slice_ in self.slice_:
            return UintType(slice_.width, default=slice_.extract(self.default))
        raise ValueError(f"Cannot slice bit(s) {slice_!s} from {self}")


class SintType(AVecType):
    """
    Vector With Unsigned Interpretation.

    Args:
        width (int): Width in bits.

    Attributes:
        default: Default Value. 0 by default.

    Example:
    >>> import ucdp as u
    >>> example = u.SintType(12)
    >>> example
    SintType(12)
    >>> example.width
    12
    >>> example.default
    0

    Another Example:

    >>> example = u.SintType(16, default=8)
    >>> example
    SintType(16, default=8)
    >>> example.width
    16
    >>> example.default
    8

    Slicing:

    >>> u.SintType(16, default=31)[15:0]
    SintType(16, default=31)
    >>> u.SintType(16, default=31)[15:8]
    SintType(8)
    >>> u.SintType(16, default=31)[3:1]
    UintType(3, default=7)
    >>> u.SintType(16, default=31)[16:15]
    Traceback (most recent call last):
        ...
    ValueError: Cannot slice bit(s) 16:15 from SintType(16, default=31)
    """

    default: Any = 0
    """Default Value."""

    @property
    def min_(self):
        """Minimal Value."""
        return -1 * 2 ** (self.width - 1)

    @property
    def max_(self):
        """Maximum Value."""
        return 2 ** (self.width - 1) - 1

    def check(self, value, what="Value") -> int:
        """
        Check `value` for type.

        >>> import ucdp as u
        >>> example = u.SintType(8)
        >>> example.check(-128)
        -128
        >>> example.check(0)
        0
        >>> example.check(127)
        127
        >>> example.check(128)
        Traceback (most recent call last):
          ...
        ValueError: Value 128 is not a 8-bit signed integer with range [-128, 127]
        >>> example.check(-129)
        Traceback (most recent call last):
          ...
        ValueError: Value -129 is not a 8-bit signed integer with range [-128, 127]
        """
        # if width < 1:
        #     raise ValueError(f"Invalid width {width}")
        value = int(value)
        if (value < int(self.min_)) or (value > int(self.max_)):
            raise ValueError(
                f"{what} {value} is not a {self.width}-bit signed integer with range [{self.min_}, {self.max_}]"
            )
        return value

    def get_hex(self, value=None):
        """
        Return Hex Value.

        >>> import ucdp as u
        >>> u.SintType(9).get_hex()
        Hex('0x000')
        >>> u.SintType(9, default=0xFE).get_hex()
        Hex('0x0FE')
        >>> u.SintType(9, default=-20).get_hex()
        Hex('0x1EC')
        >>> u.SintType(9).get_hex(value=0xFE)
        Hex('0x0FE')
        """
        if value is None:
            value = self.default
        self.check(value)
        width = int(self.width)
        wrap = 1 << width
        value = (value + wrap) % wrap
        return hex_(value, width=width)

    def is_connectable(self, other) -> bool:
        """
        Check For Valid Connection To `other`.

        Connections are only allowed to other :any:`SintType` of the same width.

        >>> SintType(8).is_connectable(SintType(8))
        True
        >>> SintType(8).is_connectable(SintType(9))
        False
        >>> SintType(8, default=1).is_connectable(SintType(8, default=0))
        True

        A connection to an :any:`BitType()` or :any:`UintType()` is forbidden (requires a cast).

        >>> SintType(1).is_connectable(BitType())
        False
        >>> SintType(1).is_connectable(UintType(1))
        False
        """
        return isinstance(other, (SintType)) and self.width == other.width and self.logic == other.logic  # type: ignore[operator]

    def cast(self, other: BaseType) -> Casting:
        """
        How to cast an input of type `self` from a value of type `other`.

        `self = cast(other)`
        """
        if isinstance(other, (UintType, BitType, IntegerType)) and self.width == other.width:  # type: ignore[operator]
            return [("", "")]

        if isinstance(other, BaseEnumType) and self.width == other.keytype.width:
            return [("", "")]

        return None

    def __getitem__(self, slice_):
        slice_ = Slice.cast(slice_, direction=DOWN)
        if slice_.width == self.width and slice_.right == self.right:
            return self
        if slice_ in self.slice_:
            if slice_.left == self.slice_.left:
                return SintType(slice_.width, default=slice_.extract(self.default))
            return UintType(slice_.width, default=slice_.extract(self.default))
        raise ValueError(f"Cannot slice bit(s) {slice_!s} from {self}")
