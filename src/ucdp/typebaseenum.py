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
from typing import Any, ClassVar

from humanfriendly.text import concatenate
from pydantic import model_validator

from .casting import Casting
from .consts import AUTO
from .dict import Dict
from .doc import Doc
from .exceptions import LockError
from .object import Field, Object, PosArgs, PrivateField
from .typebase import AScalarType, BaseScalarType, BaseType


class EnumItem(Object):
    """
    Enumeration NamedObject.

    Args:
        key (int): key value to be mapped.
        value (Any): Mapped value.

    Keyword Args:
        doc (Doc): Documentation Container

    Enumeration items are typically created by :any:`EnumType._add`.
    """

    key: int
    value: Any
    doc: Doc = Doc()

    _posargs: ClassVar[PosArgs] = ("key", "value")

    def __init__(self, key, value, **kwargs):
        super().__init__(key=key, value=value, **kwargs)


EnumItemFilter = Callable[[EnumItem], bool]


class BaseEnumType(BaseScalarType, Dict):
    """Base Type for all Enums."""

    keytype: AScalarType
    valuetype: Any = None
    default: Any = None
    filter_: EnumItemFilter | None = Field(default=None, repr=False)
    _is_locked: bool = PrivateField(default=False)

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
        if self._is_locked:
            raise LockError(f"{self}: Cannot add item {key!r}={value!r}.")
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
            and self.keys() == other.keys()
            and all(
                selfitem.value == otheritem.value
                for selfitem, otheritem in zip(self.values(), other.values(), strict=False)
            )
        )

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

    def cast(self, other: BaseType) -> Casting:
        """
        How to cast an input of type `self` from a value of type `other`.

        `self = cast(other)`
        """
        if isinstance(other, BaseEnumType) and self.keytype.is_connectable(other.keytype):
            return [("", "")]

        if isinstance(other, BaseScalarType) and (self.keytype.is_connectable(other) or self.width == other.width):
            return [("", "")]

        return None

    @model_validator(mode="after")
    def __post_init(self) -> "BaseEnumType":
        if self.default is None:
            self.__dict__["default"] = self.keytype.default
        return self

    @abstractmethod
    def _build(self) -> None:
        """Build Type."""
