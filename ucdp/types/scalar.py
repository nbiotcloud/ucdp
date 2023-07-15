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

"""Scalar Types aka native Types."""

from humannum import hex_
from icdutil.slices import DOWN, Slice

from ..attrs import ReusedFrozen, field, frozen
from .base import AScalarType, AType, AVecType


@frozen
class IntegerType(AScalarType, ReusedFrozen):

    """
    Native Signed 32-Bit Integer.

    Keyword Args:
        default (int): Default Value. 0 by default.

    The width is fixed to 32.

    Documentation defaults are empty by default:

    >>> import ucdp
    >>> ucdp.IntegerType.title
    >>> ucdp.IntegerType.descr
    >>> ucdp.IntegerType.comment

    Example:

    >>> example = ucdp.IntegerType()
    >>> example
    IntegerType()
    >>> example.width
    32
    >>> example.default
    0

    Another Example:

    >>> example = ucdp.IntegerType(default=8)
    >>> example
    IntegerType(default=8)
    >>> example.width
    32
    >>> example.default
    8

    Selective Coverage Disable:

    >>> example = ucdp.IntegerType()
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

    >>> ucdp.IntegerType(default=31)['31:0']
    IntegerType(default=31)
    >>> ucdp.IntegerType(default=31)['3:1']
    UintType(3, default=7)
    >>> ucdp.IntegerType(default=31)['32:31']
    Traceback (most recent call last):
        ...
    ValueError: Cannot slice bit(s) 32:31 from IntegerType(default=31) with dimension [31:0]
    """

    width = 32
    min_ = -1 * 2 ** (width - 1)
    max_ = 2 ** (width - 1) - 1

    def check(self, value, what="Value") -> int:
        """
        Check `value` for type.

        Values are limited to 32-bit signed [-2147483648, 2147483647].

        >>> import ucdp
        >>> example = ucdp.IntegerType()
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

        >>> import ucdp
        >>> ucdp.IntegerType(default=0x10FEC0DE).get_hex()
        Hex('0x10FEC0DE')
        >>> ucdp.IntegerType(default=0x10FEC0DE).get_hex(value=0xBEEF)
        Hex('0x0000BEEF')
        >>> ucdp.IntegerType().get_hex(value=9)
        Hex('0x00000009')
        """
        if value is None:
            value = self.default
        self.check(value)
        value = int(value)
        wrap = 1 << 32
        value = (value + wrap) % wrap
        return hex_(value, width=32)

    def is_connectable(self, other):
        """
        Check For Valid Connection To `other`.

        Connections are only allowed to other :any:`IntegerType`.
        The default and isolation value have no influence.

        >>> IntegerType().is_connectable(IntegerType())
        True
        >>> IntegerType(default=1).is_connectable(IntegerType(default=2))
        True
        """
        return isinstance(other, (SintType, IntegerType)) and int(other.width) == 32

    def __getitem__(self, slice_):
        """Return Sliced Variant."""
        slice_ = Slice.cast(slice_, direction=DOWN)
        if slice_.width == 32 and slice_.right == 0:
            return self
        if slice_.left < 31:
            return UintType(slice_.width, default=slice_.extract(self.default))
        raise ValueError(f"Cannot slice bit(s) {slice_!s} from {self} with dimension [31:0]")


@frozen
class BitType(AScalarType, ReusedFrozen):

    """
    Native Single Bit.

    Keyword Args:
        default (int): Default Value. 0 by default.

    The width is fixed to 1.

    Example:

    >>> import ucdp
    >>> example = ucdp.BitType()
    >>> example
    BitType()
    >>> example.width
    1
    >>> example.default
    0

    Another Example:

    >>> example = ucdp.BitType(default=1)
    >>> example
    BitType(default=1)
    >>> example.width
    1
    >>> example.default
    1

    Slicing:

    >>> ucdp.BitType(default=1)[0]
    BitType(default=1)
    >>> ucdp.BitType(default=1)[32:31]
    Traceback (most recent call last):
        ...
    ValueError: Cannot slice bit(s) 32:31 from BitType(default=1)
    """

    width = 1
    min_ = 0
    max_ = 1

    @staticmethod
    def check(value, what="Value") -> int:
        """
        Check `value` for type.

        Values are limited to 0 and 1

        >>> import ucdp
        >>> example = ucdp.BitType()
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
        # pylint: disable=arguments-differ
        value = int(value)
        if value not in (0, 1):
            raise ValueError(f"{what} {value} is not a single bit with range [0, 1]")
        return value

    def get_hex(self, value=None):
        """
        Return Hex Value.

        >>> import ucdp
        >>> ucdp.BitType().get_hex()
        Hex('0x0')
        >>> ucdp.BitType(default=1).get_hex()
        Hex('0x1')
        >>> ucdp.BitType().get_hex(value=1)
        Hex('0x1')
        """
        if value is None:
            value = self.default
        self.check(value)
        return hex_(value, width=1)

    def is_connectable(self, other):
        """
        Check For Valid Connection To `other`.

        Connections are only allowed to other :any:`BitType`.
        The default and isolation value have no influence.

        >>> BitType().is_connectable(BitType())
        True
        >>> BitType(default=1).is_connectable(BitType(default=0))
        True

        A connection to an :any:`UintType()` of width is forbidden (requires a cast).

        >>> BitType().is_connectable(UintType(2))
        False
        """
        return isinstance(other, (BitType, UintType)) and int(other.width) == 1

    def __getitem__(self, slice_):
        slice_ = Slice.cast(slice_, direction=DOWN)
        if slice_.width == 1 and slice_.right == 0:
            return self
        raise ValueError(f"Cannot slice bit(s) {slice_!s} from {self}")


@frozen
class BoolType(AScalarType, ReusedFrozen):

    """
    Native Boolean.

    Keyword Args:
        default (int): Default Value. 0 by default.
        iso (int): Isolation Value. Identical to default if omitted.
        no_codecov: Exclude from toggle code coverage. Either `False`, `True` or a tuple of indicies.

    The width is fixed to 1.

    Example:

    >>> import ucdp
    >>> example = ucdp.BoolType()
    >>> example
    BoolType()
    >>> example.width
    1
    >>> example.default
    0

    Another Example:

    >>> example = ucdp.BoolType(default=1)
    >>> example
    BoolType(default=1)
    >>> example.width
    1
    >>> example.default
    1

    Slicing:

    >>> ucdp.BoolType(default=1)[0]
    BoolType(default=1)
    >>> ucdp.BoolType()[32:31]
    Traceback (most recent call last):
        ...
    ValueError: Cannot slice bit(s) 32:31 from BoolType()
    """

    default = field(default=0, kw_only=True)
    width = 1

    @staticmethod
    def check(value, what="Value") -> bool:
        """
        Check `value` for type.

        Values are limited to 0 and 1

        >>> import ucdp
        >>> example = ucdp.BoolType()
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
        # pylint: disable=arguments-differ
        if value not in (False, True):
            raise ValueError(f"{what} {value} is not a boolean")
        return value

    def get_hex(self, value=None):
        """
        Return Hex Value.

        >>> import ucdp
        >>> ucdp.BoolType().get_hex()
        Hex('0x0')
        >>> ucdp.BoolType(default=1).get_hex()
        Hex('0x1')
        >>> ucdp.BoolType().get_hex(value=1)
        Hex('0x1')
        """
        if value is None:
            value = self.default
        self.check(value)
        return hex_(value, width=1)

    def is_connectable(self, other):
        """
        Check For Valid Connection To `other`.

        Connections are only allowed to other :any:`BoolType`.
        The default and isolation value have no influence.

        >>> BoolType().is_connectable(BoolType())
        True
        >>> BoolType(default=True).is_connectable(BoolType(default=0))
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


@frozen
class RailType(AScalarType, ReusedFrozen):

    """
    Voltage Rail.

    Keyword Args:
        default (int): Default Value. 0 by default.
        no_codecov: Exclude from toggle code coverage. Either `False`, `True` or a tuple of indicies.

    The width is fixed to 1.

    Example:

    >>> import ucdp
    >>> example = ucdp.RailType()
    >>> example
    RailType()
    >>> example.width
    1
    >>> example.default

    Another Example:

    >>> example = ucdp.RailType(default=1)
    >>> example
    RailType(default=1)
    >>> example.width
    1
    >>> example.default
    1

    Slicing:

    >>> ucdp.RailType(default=1)[0]
    RailType(default=1)
    >>> ucdp.RailType(default=1)[32:31]
    Traceback (most recent call last):
        ...
    ValueError: Cannot slice bit(s) 32:31 from RailType(default=1)
    """

    default = field(default=None, kw_only=True)
    iso = field(default=None, init=False)
    width = 1

    @staticmethod
    def check(value, what="Value") -> int:
        """
        Check `value` for type.

        Values are limited to 0 and 1

        >>> import ucdp
        >>> example = ucdp.RailType()
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
        # pylint: disable=arguments-differ
        value = int(value)
        if value not in (0, 1):
            raise ValueError(f"{what} {value} is not a single bit with range [0, 1]")
        return value

    def get_hex(self, value=None):
        """
        Return Hex Value.

        >>> import ucdp
        >>> ucdp.RailType().get_hex()
        >>> ucdp.RailType(default=0).get_hex()
        Hex('0x0')
        >>> ucdp.RailType(default=1).get_hex()
        Hex('0x1')
        >>> ucdp.RailType().get_hex(value=1)
        Hex('0x1')
        """
        if value is None:
            value = self.default
        if value is None:
            return None
        self.check(value)
        return hex_(value, width=1)

    def is_connectable(self, other):
        """
        Check For Valid Connection To `other`.

        Connections are only allowed to other :any:`RailType`.
        The default and isolation value have no influence.

        >>> RailType().is_connectable(RailType())
        True
        >>> RailType(default=1).is_connectable(RailType(default=0))
        True

        A connection to an :any:`BitType()` is forbidden (requires a cast).

        >>> RailType().is_connectable(BitType())
        False
        """
        return isinstance(other, RailType)

    # def cast(self, other):
    #     """
    #     How to cast an input of type `self` from a value of type `other`.

    #     `self = cast(other)`
    #     """
    #     # pylint: disable=arguments-differ
    #     if isinstance(other, (BitType, UintType)) and other.width == 1:
    #         yield "", ""
    #     return NotImplemented

    def __getitem__(self, slice_):
        slice_ = Slice.cast(slice_, direction=DOWN)
        if slice_.width == 1 and slice_.right == 0:
            return self
        raise ValueError(f"Cannot slice bit(s) {slice_!s} from {self}")


@frozen
class UintType(AVecType):

    """
    Vector With Unsigned Interpretation.

    Args:
        width (int): Width in bits.

    Keyword Args:
        default (int): Default Value. 0 by default.

    Example:

    >>> import ucdp
    >>> example = ucdp.UintType(12)
    >>> example
    UintType(12)
    >>> example.width
    12
    >>> example.default
    0

    Another Example:

    >>> example = ucdp.UintType(16, default=8)
    >>> example
    UintType(16, default=8)
    >>> example.width
    16
    >>> example.default
    8

    Selective Coverage Disable:

    >>> example = ucdp.UintType(32)
    >>> example
    UintType(32)

    Slicing:

    >>> ucdp.UintType(16, default=31)[15:0]
    UintType(16, default=31)
    >>> ucdp.UintType(16, default=31)[3:1]
    UintType(3, default=7)
    >>> ucdp.UintType(16, default=31)[16:15]
    Traceback (most recent call last):
        ...
    ValueError: Cannot slice bit(s) 16:15 from UintType(16, default=31)
    """

    min_ = 0

    @property
    def max_(self):
        """Maximum Value."""
        return (2**self.width) - 1

    def check(self, value, what="Value") -> int:
        """
        Check `value` for type.

        >>> import ucdp
        >>> example = ucdp.UintType(8)
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

        >>> import ucdp
        >>> ucdp.UintType(9).get_hex()
        Hex('0x000')
        >>> ucdp.UintType(9, default=0xFE).get_hex()
        Hex('0x0FE')
        >>> ucdp.UintType(9).get_hex(value=0xFE)
        Hex('0x0FE')
        """
        if value is None:
            value = self.default
        self.check(value)
        return hex_(value, width=self.width)

    def is_connectable(self, other):
        """
        Check For Valid Connection To `other`.

        Connections are only allowed to other :any:`UintType` of the same width.
        The default and isolation value have no influence.

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
        return isinstance(other, (UintType, BitType)) and self.width == other.width

    # def cast(self, other):
    #     """
    #     How to cast an input of type `self` from a value of type `other`.

    #     `self = cast(other)`
    #     """
    #     # pylint: disable=arguments-differ
    #     if isinstance(other, (SintType, IntegerType)) and self.width == other.width:
    #         yield "", ""
    #     return NotImplemented

    def __getitem__(self, slice_):
        slice_ = Slice.cast(slice_, direction=DOWN)
        if slice_.width == self.width and slice_.right == self.right:
            return self
        if slice_ in self.slice_:
            return UintType(slice_.width, default=slice_.extract(self.default))
        raise ValueError(f"Cannot slice bit(s) {slice_!s} from {self}")


@frozen
class SintType(AVecType):

    """
    Vector With Unsigned Interpretation.

    Args:
        width (int): Width in bits.

    Keyword Args:
        default (int): Default Value. 0 by default.
        iso (int): Isolation Value. Identical to default if omitted.
        no_codecov: Exclude from toggle code coverage. Either `False`, `True` or a tuple of indicies.

    Example:

    >>> import ucdp
    >>> example = ucdp.SintType(12)
    >>> example
    SintType(12)
    >>> example.width
    12
    >>> example.default
    0

    Another Example:

    >>> example = ucdp.SintType(16, default=8)
    >>> example
    SintType(16, default=8)
    >>> example.width
    16
    >>> example.default
    8

    Slicing:

    >>> ucdp.SintType(16, default=31)[15:0]
    SintType(16, default=31)
    >>> ucdp.SintType(16, default=31)[15:8]
    SintType(8)
    >>> ucdp.SintType(16, default=31)[3:1]
    UintType(3, default=7)
    >>> ucdp.SintType(16, default=31)[16:15]
    Traceback (most recent call last):
        ...
    ValueError: Cannot slice bit(s) 16:15 from SintType(16, default=31)
    """

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

        >>> import ucdp
        >>> example = ucdp.SintType(8)
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

        >>> import ucdp
        >>> ucdp.SintType(9).get_hex()
        Hex('0x000')
        >>> ucdp.SintType(9, default=0xFE).get_hex()
        Hex('0x0FE')
        >>> ucdp.SintType(9, default=-20).get_hex()
        Hex('0x1EC')
        >>> ucdp.SintType(9).get_hex(value=0xFE)
        Hex('0x0FE')
        """
        if value is None:
            value = self.default
        self.check(value)
        width = int(self.width)
        wrap = 1 << width
        value = (value + wrap) % wrap
        return hex_(value, width=width)

    def is_connectable(self, other):
        """
        Check For Valid Connection To `other`.

        Connections are only allowed to other :any:`SintType` of the same width.
        The default and isolation value have no influence.

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
        return isinstance(other, (SintType, IntegerType)) and self.width == other.width

    # def cast(self, other):
    #     """
    #     How to cast an input of type `self` from a value of type `other`.

    #     `self = cast(other)`
    #     """
    #     # pylint: disable=arguments-differ
    #     if isinstance(other, (UintType, BitType)) and self.width == other.width:
    #         yield "", ""
    #     return NotImplemented

    def __getitem__(self, slice_):
        slice_ = Slice.cast(slice_, direction=DOWN)
        if slice_.width == self.width and slice_.right == self.right:
            return self
        if slice_ in self.slice_:
            if slice_.left == self.slice_.left:
                return SintType(slice_.width, default=slice_.extract(self.default))
            return UintType(slice_.width, default=slice_.extract(self.default))
        raise ValueError(f"Cannot slice bit(s) {slice_!s} from {self}")


@frozen
class StringType(AType, ReusedFrozen):

    """
    Native String.

    Example:

    >>> import ucdp
    >>> example = ucdp.StringType()
    >>> example
    StringType()
    >>> example.bits
    """

    def is_connectable(self, other):
        """
        Check For Valid Connection To `other`.

        Connections are only allowed to other :any:`StringType`.
        The default and isolation value have no influence.

        >>> StringType().is_connectable(StringType())
        True

        A connection to other types is forbidden.

        >>> StringType().is_connectable(UintType(1))
        False
        """
        return isinstance(other, StringType)

    @property
    def bits(self):
        """Size in Bits."""
        return None
