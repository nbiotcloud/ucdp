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
Enumeration Types.

An enumeration is a normal base type with a specific mapping of values to a another meaning.

* :any:`EnumItem` - Enumeration item
* :any:`AEnumType` - Standard Enumeration
* :any:`AGlobalEnumType` - A public enumeration which fills up through all instances.
* :any:`DynamicEnumType` - A public enumeration which fills up per instance.
* :any:`EnaType` - Native single bit with `ena` and `dis` enumeration, active-high
* :any:`DisType` - Native single bit with `ena` and `dis` enumeration, low-high
"""

from abc import abstractmethod
from collections.abc import Callable
from typing import Any

from humanfriendly.text import concatenate
from pydantic import model_validator

from .consts import AUTO
from .dict import Dict
from .doc import Doc
from .exceptions import LockError
from .object import Field, Light, Object, PrivateField
from .typebase import BaseScalarType
from .typescalar import AScalarType, BitType, IntegerType


class EnumItem(Object):
    """
    Enumeration NamedObject.

    Args:
        key (int): key value to be mapped.
        value: Mapped value.

    Keyword Args:
        doc (Doc): Documentation Container

    Enumeration items are typically created by :any:`EnumType._add`.
    """

    key: int
    value: Any
    doc: Doc = Doc()

    _posargs: tuple[str, ...] = ("key", "value")

    def __init__(self, key, value, **kwargs):
        super().__init__(key=key, value=value, **kwargs)


ItemFilter = Callable[[EnumItem], bool]


class BaseEnumType(BaseScalarType, Dict):
    """Base Type for all Enums."""

    keytype: AScalarType = IntegerType()
    valuetype: Any = None
    default: Any = None
    filter_: ItemFilter | None = Field(default=None, repr=False)
    _locked: bool = PrivateField(default=False)

    def _add(self, key, value, title: str | None = None, descr: str | None = None, comment: str | None = None) -> None:
        """
        Add NamedObject To Enumeration.

        Args:
            key (int): key value to be mapped.
            value: Mapped value.

        Keyword Args:
            title (str): Full Spoken Name.
            descr (str): Documentation Description.
            comment (str): Source Code Comment.

        :meta public:
        """
        if self._locked:
            raise LockError(self)
        items = self._items
        if key is AUTO:
            keys = items.keys()
            key = max(keys) + 1 if keys else 0
        self.keytype.check(key)
        valuetype = self.valuetype
        if valuetype:
            valuetype.check(value)
        if key in items.keys():
            raise ValueError(f"key {key!r} already exists in {self}")
        doc = Doc(title=title, descr=descr, comment=comment)
        enumitem = EnumItem(key, value, doc=doc)
        if not self.filter_ or self.filter_(enumitem):
            items[key] = enumitem

    @property
    def width(self):
        """Width in Bits."""
        return self.keytype.width

    def check(self, value, what="Value"):
        """Check `value`."""
        return self.keytype.check(value, what)

    def encode(self, value, usedefault=False):
        """Encode Value."""
        if usedefault:
            try:
                return self.get_byvalue(value).key
            except ValueError:
                return self.default
        return self.get_byvalue(value).key

    def decode(self, value, usedefault=False):
        """Decode Value."""
        if usedefault:
            try:
                return self.get_bykey(value).value
            except ValueError:
                return self.get_bykey(self.default).value
        else:
            return self.get_bykey(value).value

    @property
    def is_full(self) -> bool:
        """Return `True` if Enumeration Is Fully Encoded."""
        return len(self) == (2 ** int(self.width))

    def get_bykey(self, key) -> EnumItem:
        """Return :any:`EnumItem` with key `key`."""
        item = self.get(key)
        if item is not None:
            return item
        keys = concatenate([repr(item) for item in self.keys()])
        raise ValueError(f"{self} does not contain key {key!r}. Known keys are {keys}.")

    def get_byvalue(self, value) -> EnumItem:
        """Return :any:`EnumItem` with value `value`."""
        for item in self.values():
            if item.value == value:
                return item
        values = concatenate([repr(item.value) for item in self.values()])
        raise ValueError(f"{self} does not contain value {value!r}. Known values are {values}.")

    def get_value(self, key):
        """Return `value` for `key`."""
        return self.get_bykey(key).value

    def get_key(self, value):
        """Return `key` for `value`."""
        return self.get_byvalue(value).key

    def get_hex(self, value=None):
        """Get Hex Value."""
        if value is None:
            value = self.default
        return self.keytype.get_hex(value=value)

    def is_connectable(self, other):
        """Check For Valid Connection To `other`."""
        return (
            isinstance(other, BaseEnumType)
            and self.keytype.is_connectable(other.keytype)
            and self.valuetype == other.valuetype
            and len(self) == len(other)
            and self.keys() == other.keys()
            and all(
                selfitem.value == otheritem.value
                for selfitem, otheritem in zip(self.values(), other.values(), strict=False)
            )
        ) or (self.keytype.is_connectable(other))

    def __getitem__(self, slice_):
        """Return Slice."""
        return self.keytype[slice_]

    @property
    def min_(self):
        """Minimal Value."""
        return self.keytype.min_

    @property
    def max_(self):
        """Maximal Value."""
        return self.keytype.max_

    @property
    def bits(self):
        """Size in Bits."""
        return self.keytype.bits

    # def cast(self, other):
    #     """
    #     How to cast an input of type `self` from a value of type `other`.

    #     `self = cast(other)`
    #     """
    #     if isinstance(other, BaseEnumType) and self.keytype.is_connectable(other.keytype):
    #         yield "", ""
    #     return NotImplemented

    @model_validator(mode="after")
    def __post_init(self) -> "BaseEnumType":
        if self.default is None:
            self.__dict__["default"] = self.keytype.default
        return self

    @abstractmethod
    def _build(self) -> None:
        """Build Type."""


class AEnumType(BaseEnumType, Light):
    """
    Base class for all enumerations, behaves like a dictionary.

    Keyword Args:
        default (int): Default Value. Default value of `keytype` by default.
        iso (int): Isolation Value. Default value of `keytype` by default.

    The protected method `_build()` should be used to build the type.

    Definition of an enumeration:

    >>> import ucdp as u
    >>> class ModeType(u.AEnumType):
    ...     keytype: u.AScalarType = u.UintType(2, default=1)
    ...     def _build(self) -> None:
    ...         self._add(0, "linear", title="Linear Mode", descr="Just Linear", comment="be careful")
    ...         self._add(1, "cyclic", title="Cyclic Mode", descr="The Cyclic Mode")
    ...         self._add(2, "loop", title="Run in a Loop")

    Usage of an Enumeration:

    >>> mode = ModeType()
    >>> mode
    ModeType()

    The enumeration behaves like a `dict`, with elements hashed by `name`.
    But different to a regular `dict`, it returns items on pure iteration:

    >>> tuple(mode)
    (0, 1, 2)
    >>> mode.keys()
    dict_keys([0, 1, 2])
    >>> mode.values()
    dict_values([EnumItem(0, 'linear', doc=...), EnumItem(1, 'cyclic', doc=...), EnumItem(2, 'loop', doc=...)])
    >>> for key, item in mode.items():
    ...     print(key, item)
    0 EnumItem(0, 'linear', doc=...)
    1 EnumItem(1, 'cyclic', doc=...)
    2 EnumItem(2, 'loop', doc=...)

    Enumeration items have these attributes:

    >>> from tabulate import tabulate
    >>> print(tabulate([(item.key, item.value, item.doc) for item in mode.values()],
    ...                headers=(".key", ".value", ".doc")))
      .key  .value    .doc
    ------  --------  -------------------------------------------------------------------
         0  linear    Doc(title='Linear Mode', descr='Just Linear', comment='be careful')
         1  cyclic    Doc(title='Cyclic Mode', descr='The Cyclic Mode')
         2  loop      Doc(title='Run in a Loop')

    To retrieve an item by value:

    >>> mode.get_byvalue('loop')
    EnumItem(2, 'loop', doc=Doc(title='Run in a Loop'))
    >>> mode.get_byvalue('unknown')
    Traceback (most recent call last):
      ...
    ValueError: ModeType() does not contain value 'unknown'. Known values are 'linear', 'cyclic' and 'loop'.
    >>> mode.get_key('loop')
    2
    >>> mode.get_value(2)
    'loop'

    To check a value against the key, use the standard `check` method:

    >>> mode.check(0)
    0
    >>> mode.check(1)
    1

    To encode a mapped value, use the `encode` method

    >>> mode.encode('linear')
    0
    >>> mode.encode('cyclic')
    1
    >>> mode.encode('other')
    Traceback (most recent call last):
      ..
    ValueError: ModeType() does not contain value 'other'. Known values are 'linear', 'cyclic' and 'loop'.
    >>> mode.encode('other', usedefault=True)
    1

    Decoding works likewise:

    >>> mode.decode(0)
    'linear'
    >>> mode.decode(1)
    'cyclic'
    >>> mode.decode(3)
    Traceback (most recent call last):
      ...
    ValueError: ModeType() does not contain key 3. Known keys are 0, 1 and 2.
    >>> mode.decode(3, usedefault=True)
    'cyclic'

    You can also check, if a value is within the range:

    >>> 0 in mode
    True
    >>> 3 in mode
    False

    Enumerations are also singleton:

    >>> ModeType() is ModeType()
    True
    >>> ModeType() is ModeType(default=1)
    False

    >>> ModeType() == ModeType()
    True
    >>> ModeType() == ModeType(default=2)
    False

    Attributes `width`, `default` are taken from `keytype`:

    >>> mode = ModeType()
    >>> mode.width
    2
    >>> mode.default
    1
    >>> mode.check(3)
    3
    >>> mode.check(4)
    Traceback (most recent call last):
      ...
    ValueError: Value 4 is not a 2-bit integer with range [0, 3]

    Attributes `default` can be overwritten:

    >>> mode = ModeType(default=2)
    >>> mode.width
    2
    >>> mode.default
    2

    A mapping type, which translates one type to another:

    Definition of an enumeration:

    >>> import ucdp as u
    >>> class MappingType(u.AEnumType):
    ...     keytype: u.AScalarType = u.UintType(2)
    ...     valuetype: u.UintType = u.UintType(16)
    ...     def _build(self) -> None:
    ...         self._add(0, 7)
    ...         self._add(1, 31)
    ...         self._add(2, 2**14-1)
    ...         self._add(3, 2**16-1)
    >>> mapping = MappingType()
    >>> for item in mapping.values():
    ...     print(repr(item))
    EnumItem(0, 7)
    EnumItem(1, 31)
    EnumItem(2, 16383)
    EnumItem(3, 65535)

    Get Hex

    >>> mapping.get_hex()
    Hex('0x0')
    >>> mapping.get_hex(value=3)
    Hex('0x3')

    Size in Bits:

    >>> mapping.bits
    2

    To determine if the enumeration is fully decoded, use `is_full`:

    >>> import ucdp as u
    >>> class AType(u.AEnumType):
    ...     keytype: u.AScalarType = u.UintType(1)  # 2 possible values
    ...     def _build(self) -> None:
    ...         self._add(0, "linear")
    ...         self._add(1, "cyclic")
    >>> AType().is_full
    True

    >>> class BType(u.AEnumType):
    ...     keytype: u.AScalarType = u.UintType(2) # 4 possible values
    ...     def _build(self) -> None:
    ...         self._add(0, "linear")
    ...         self._add(1, "cyclic")
    >>> BType().is_full
    False

    Connections are only allowed to other :any:`EnumType` with the same key-value mapping.
    Default and isolation values are ignored.

    >>> class CType(u.AEnumType):
    ...     keytype: u.AScalarType = u.UintType(1)  # 2 possible values
    ...     def _build(self) -> None:
    ...         self._add(0, "linear", title="other comment")
    ...         self._add(1, "cyclic")

    >>> class DType(u.AEnumType):
    ...     keytype: u.AScalarType = u.UintType(1)  # 2 possible values
    ...     def _build(self) -> None:
    ...         self._add(0, "linear")

    >>> AType().is_connectable(AType())
    True
    >>> AType().is_connectable(BType())
    False
    >>> AType().is_connectable(CType())
    True
    >>> AType().is_connectable(DType())
    False

    Slicing:

    >>> BType()[1:0]
    UintType(2)
    >>> BType()[1]
    UintType(1)

    Values can be used twice:

    >>> class DuplType(u.AEnumType):
    ...     keytype: u.AScalarType = u.UintType(2)
    ...     def _build(self) -> None:
    ...         self._add(0, 'a')
    ...         self._add(1, 'b')
    ...         self._add(2, 'c')
    ...         self._add(3, 'b')

    >>> dupl = DuplType()
    >>> dupl
    DuplType()
    >>> dupl.get_value(1)
    'b'
    >>> dupl.get_value(3)
    'b'
    >>> dupl.get_key('b')
    1

    The `new()` method creates a new variant:

    >>> class MyType(u.AEnumType):
    ...     keytype: u.AScalarType = u.UintType(2)
    ...     def _build(self) -> None:
    ...         self._add(0, "linear")
    ...         self._add(1, "cyclic")
    ...         self._add(2, "auto")

    >>> MyType()
    MyType()
    >>> MyType().new(default=1)
    MyType(default=1)
    >>> MyType().new(filter_=lambda item: item.value != "cyclic")
    MyType()
    """

    def model_post_init(self, __context: Any) -> None:
        """Run Build."""
        self._build()
        self._locked = True


class AGlobalEnumType(BaseEnumType, Light):
    """
    A singleton enumeration which can be filled outside `_build` and is **shared** between instances.

    >>> import ucdp as u
    >>> class CtrlType(u.AGlobalEnumType):
    ...     keytype: u.AScalarType = u.UintType(3)
    >>> ctrl = CtrlType()
    >>> ctrl.add(0, 'zero')

    >>> ctrl = CtrlType()
    >>> ctrl.add(1, 'one')
    >>> ctrl.add(7, 'seven')

    >>> ctrl.keys()
    dict_keys([0, 1, 7])

    >>> ctrl = CtrlType()
    >>> ctrl.keys()
    dict_keys([0, 1, 7])

    This is forbidden on normal enumeration:

    >>> class CtrlType(u.AEnumType):
    ...     keytype: u.AScalarType = u.UintType(3)
    ...     def _build(self) -> None:
    ...         pass
    >>> ctrl = CtrlType()
    >>> ctrl._add(0, 'zero')
    Traceback (most recent call last):
      ...
    ucdp.exceptions.LockError: CtrlType() is already locked for modification.
    """

    def add(self, key, value, title: str | None = None, descr: str | None = None, comment: str | None = None) -> None:
        """
        Add NamedObject To Enumeration.

        Args:
            key (int): key value to be mapped.
            value: Mapped value.

        Keyword Args:
            title (str): Full Spoken Name.
            descr (str): Documentation Description.
            comment (str): Source Code Comment.
        """
        self._add(key=key, value=value, title=title, descr=descr, comment=comment)

    def _build(self) -> None:
        """Build Type."""

    def model_post_init(self, __context: Any) -> None:
        """Run Build."""
        if self.__class__ is AGlobalEnumType:
            raise TypeError("Can't instantiate abstract class AGlobalEnumType. Please create a subclass.")
        self._build()


class DynamicEnumType(BaseEnumType):
    """
    A enumeration which can be filled outside `_build` and is **not** shared between instances.

    >>> import ucdp as u
    >>> class CtrlType(u.DynamicEnumType):
    ...     keytype: u.AScalarType = u.UintType(3)
    >>> ctrl = CtrlType()
    >>> ctrl.add(0, 'zero')
    >>> ctrl.keys()
    dict_keys([0])

    >>> ctrl = CtrlType()
    >>> ctrl.add(1, 'one')
    >>> ctrl.add(7, 'seven')
    >>> ctrl.keys()
    dict_keys([1, 7])

    This is forbidden on normal enumeration:

    >>> class CtrlType(u.AEnumType):
    ...     keytype: u.AScalarType = u.UintType(3)
    ...     def _build(self) -> None:
    ...         pass
    >>> ctrl = CtrlType()
    >>> ctrl._add(0, 'zero')
    Traceback (most recent call last):
      ...
    ucdp.exceptions.LockError: CtrlType() is already locked for modification.
    """

    def add(self, key, value, title: str | None = None, descr: str | None = None, comment: str | None = None) -> None:
        """
        Add NamedObject To Enumeration.

        Args:
            key (int): key value to be mapped.
            value: Mapped value.

        Keyword Args:
            title (str): Full Spoken Name.
            descr (str): Documentation Description.
            comment (str): Source Code Comment.
        """
        self._add(key=key, value=value, title=title, descr=descr, comment=comment)

    def _build(self) -> None:
        """Build Type."""

    def model_post_init(self, __context: Any) -> None:
        """Run Build."""
        self._build()


class EnaType(AEnumType):
    """
    Enable (positive logic).

    >>> enable = EnaType()
    >>> enable
    EnaType()
    >>> enable.width
    1
    >>> enable.default
    0
    >>> for item in enable.values():
    ...     print(repr(item))
    EnumItem(0, 'dis', doc=Doc(title='disabled'))
    EnumItem(1, 'ena', doc=Doc(title='enabled'))

    >>> enable = EnaType(default=1)
    >>> enable.default
    1
    """

    keytype: AScalarType = BitType()
    title: str = "Enable"

    def _build(self) -> None:
        self._add(0, "dis", "disabled")
        self._add(1, "ena", "enabled")

    # def is_connectable(self, other):
    #     """Return True if connectable to `other`."""
    #     return (isinstance(other, BitType) and self.default == other.default) or super().is_connectable(other)


class DisType(AEnumType):
    """
    Enable (positive logic).

    >>> disable = DisType()
    >>> disable
    DisType()
    >>> disable.width
    1
    >>> disable.default
    0
    >>> for item in disable.values():
    ...     print(repr(item))
    EnumItem(0, 'ena', doc=Doc(title='enabled'))
    EnumItem(1, 'dis', doc=Doc(title='disabled'))

    >>> disable = DisType(default=1)
    >>> disable.default
    1
    """

    keytype: AScalarType = BitType()
    title: str = "Disable"

    def _build(self) -> None:
        self._add(0, "ena", "enabled")
        self._add(1, "dis", "disabled")


class BusyType(AEnumType):
    """
    Busy.

    >>> busy = BusyType()
    >>> busy
    BusyType()
    >>> busy.width
    1
    >>> busy.default
    0
    >>> for item in busy.values():
    ...     print(repr(item))
    EnumItem(0, 'idle', doc=Doc(title='Idle'))
    EnumItem(1, 'busy', doc=Doc(title='Busy'))

    >>> busy = BusyType(default=1)
    >>> busy.default
    1
    """

    keytype: AScalarType = BitType()
    title: str = "Busy"

    def _build(self) -> None:
        self._add(0, "idle", "Idle")
        self._add(1, "busy", "Busy")
