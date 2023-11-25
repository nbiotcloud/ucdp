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
Structure Types.

A structure assembles multiple type, name, orientation pairs.

* :any:`StructItem` - Struct item
* :any:`StructType` - Standard Struct
* :any:`AGlobalStructType` - A public struct which fills up through all instances.
* :any:`DynamicStructType` - A public struct which fills up per instance.
"""
from typing import Any, Callable, Optional

from pydantic import model_validator

from .const import RE_IDENTIFIER
from .doc import Doc
from .docutil import doc_from_type
from .exceptions import LockError, MissingInheritanceError
from .object import Field, Light, Object, PrivateField
from .orientation import BWD, FWD, Orientation
from .typebase import CompositeType, Type
from .userdict import UserDict


class StructItem(Object):
    """
    Struct Item.

    Args:
        name (str): Name of struct member
        type_ (AType): Type of struct member

    Keyword Args:
        orient (Orient): Orientation of struct member. `FWD` by default
        doc (Doc): Documentation Container
        ifdef (str): IFDEF encapsulation
    """

    name: str = Field(pattern=RE_IDENTIFIER)
    type_: Type
    orientation: Orientation = FWD
    doc: Doc = Field(default_factory=Doc)
    ifdef: Optional[str] = None

    _posargs: tuple[str, ...] = ("name", "type_")

    def __init__(self, name, type_, **kwargs):
        super().__init__(name=name, type_=type_, **kwargs)

    @property
    def title(self):
        """Alias to `doc.title`."""
        return self.doc.title

    @property
    def descr(self):
        """Alias to `doc.descr`."""
        return self.doc.descr

    @property
    def comment(self):
        """Alias to `doc.comment`."""
        return self.doc.comment


StructFilter = Callable[[StructItem], bool]


class BaseStructType(UserDict, CompositeType):
    """Base Type for all Structs."""

    filter_: Optional[StructFilter] = None
    _items: dict[Any, Any] = PrivateField(default_factory=dict)
    _locked: bool = PrivateField(default=False)

    def _add(
        self,
        name: str,
        type_: Type,
        orientation: Orientation = FWD,
        title: Optional[str] = None,
        descr: Optional[str] = None,
        comment: Optional[str] = None,
        ifdef: Optional[str] = None,
    ) -> None:
        """
        Add member `name` with `type_` and `orientation`.

        Args:
            name: Name
            type_: Type
            orientation: Orientation

        Keyword Args:
            title: Full Spoken Name.
            descr: Documentation Description.
            comment: Source Code Comment.
            ifdef: IFDEF encapsulation.

        :meta public:
        """
        if self._locked:
            raise LockError(self)
        items = self._items
        if name not in items.keys():
            doc = doc_from_type(type_, title=title, descr=descr, comment=comment)
            structitem = StructItem(name, type_, orientation=orientation, doc=doc, ifdef=ifdef)
            if not self.filter_ or self.filter_(structitem):
                items[name] = structitem
        else:
            raise ValueError(f"name {name!r} already exists in {self} ({self[name]})")

    def is_connectable(self, other):
        """Check For Valid Connection To `other`."""
        return (
            isinstance(other, BaseStructType)
            and len(self) == len(other)
            and all(self._cmpitem(selfitem, otheritem) for selfitem, otheritem in zip(self.values(), other.values()))
        )

    @staticmethod
    def _cmpitem(selfitem, otheritem):
        return (
            selfitem.name == otheritem.name
            and selfitem.type_.is_connectable(otheritem.type_)
            and selfitem.orientation == otheritem.orientation
            and selfitem.ifdef == otheritem.ifdef
        )

    @property
    def bits(self):
        """Size in Bits."""
        return sum(item.type_.bits for item in self.values())

    @model_validator(mode="after")
    def _post_init(self) -> "BaseStructType":
        raise MissingInheritanceError(BaseStructType)


class StructType(BaseStructType, Light):
    """
    Base class for all structural types.

    The protected method `_build()` should be used to build the type.

    Definition of a struct:

    >>> import ucdp
    >>> class BusType(ucdp.StructType):
    ...     def _build(self):
    ...         self._add('data', ucdp.UintType(8))
    ...         self._add('valid', ucdp.BitType())
    ...         self._add('accept', ucdp.BitType(), orientation=ucdp.BWD)

    Usage of a Struct:

    >>> bus = BusType()
    >>> bus
    BusType()

    The structs behave like a `dict`, with elements hashed by `name`.
    But different to a regular `dict`, it returns items on pure iteration:

    >>> bus.keys()
    dict_keys(['data', 'valid', 'accept'])
    >>> bus.values()
    dict_values([StructItem('data', UintType(8)), StructItem('valid', BitType()), ...])
    >>> bus.items()
    dict_items([('data', StructItem('data', UintType(8))), ('valid', StructItem(...])
    >>> bus['valid']
    StructItem('valid', BitType())
    >>> bus.bits
    10

    Connections are only allowed to other :any:`StructType` with the same key-value mapping.
    Default and isolation values are ignored.

    >>> BusType().is_connectable(BusType())
    True

    >>> class Bus2Type(ucdp.StructType):
    ...     def _build(self):
    ...         self._add('data', ucdp.UintType(8))
    ...         self._add('valid', ucdp.BitType())
    ...         self._add('accept', ucdp.BitType(), orientation=ucdp.FWD)
    >>> BusType().is_connectable(Bus2Type())
    False

    >>> class Bus3Type(ucdp.StructType):
    ...     def _build(self):
    ...         self._add('data', ucdp.UintType(8), title="title")
    ...         self._add('valid', ucdp.BitType(default=1))
    ...         self._add('accept', ucdp.BitType(), orientation=ucdp.BWD)
    >>> BusType().is_connectable(Bus3Type())
    True

    Struct members can be filtered.
    A struct member is added if the filter function returns `True` on a given :any:`StructItem` as argument.

    >>> def myfilter(structitem):
    ...     return "t" in structitem.name
    >>> for item in BusType(filter_=myfilter).values(): item
    StructItem('data', UintType(8))
    StructItem('accept', BitType(), orientation=BWD)

    There are also these predefined filters:

    >>> for item in BusType(filter_=ucdp.fwdfilter).values(): item
    StructItem('data', UintType(8))
    StructItem('valid', BitType())

    >>> for item in BusType(filter_=ucdp.bwdfilter).values(): item
    StructItem('accept', BitType(), orientation=BWD)

    This works also with the `new()` method:

    >>> for item in BusType().new(filter_=ucdp.fwdfilter).values(): item
    StructItem('data', UintType(8))
    StructItem('valid', BitType())
    """

    def _build(self) -> None:
        """Build Type."""

    @model_validator(mode="after")
    def _post_init(self) -> "StructType":
        if self.__class__ is StructType:
            raise MissingInheritanceError(StructType)
        self._build()
        self._locked = True
        return self


class GlobalStructType(BaseStructType, Light):
    """
    A singleton struct which can be filled outside `_build` and is **shared** between instances.

    >>> import ucdp
    >>> class BusType(ucdp.GlobalStructType):
    ...     pass
    >>> bus = BusType()
    >>> bus.add('data', ucdp.UintType(8))
    >>> bus.add('valid', ucdp.BitType())
    >>> bus = BusType()
    >>> bus.add('accept', ucdp.BitType(), orientation=ucdp.BWD)
    >>> tuple(bus)
    ('data', 'valid', 'accept')

    This is forbidden on normal struct:

    >>> class BusType(ucdp.StructType):
    ...     pass
    >>> bus = BusType()
    >>> bus._add('data', ucdp.UintType(8))
    Traceback (most recent call last):
      ...
    ucdp.exceptions.LockError: BusType() is already locked for modification.
    """

    add = BaseStructType._add

    def _build(self) -> None:
        """Build Type."""

    @model_validator(mode="after")
    def _post_init(self) -> "GlobalStructType":
        if self.__class__ is GlobalStructType:
            raise MissingInheritanceError(GlobalStructType)
        self._build()
        return self


class DynamicStructType(BaseStructType):
    """
    A singleton struct which can be filled outside `_build` and is **not** shared between instances.

    >>> import ucdp
    >>> class BusType(ucdp.DynamicStructType):
    ...     pass
    >>> bus = BusType()
    >>> bus.add('data', ucdp.UintType(8))
    >>> bus.add('valid', ucdp.BitType())
    >>> tuple(bus)
    ('data', 'valid')
    >>> bus = BusType()
    >>> bus.add('accept', ucdp.BitType(), orientation=ucdp.BWD)
    >>> tuple(bus)
    ('accept',)

    This is forbidden on normal struct:

    >>> class BusType(ucdp.StructType):
    ...     pass
    >>> bus = BusType()
    >>> bus._add('data', ucdp.UintType(8))
    Traceback (most recent call last):
      ...
    ucdp.exceptions.LockError: BusType() is already locked for modification.
    """

    add = BaseStructType._add

    def _build(self) -> None:
        """Build Type."""

    @model_validator(mode="after")
    def _post_init(self) -> "DynamicStructType":
        if self.__class__ is DynamicStructType:
            raise MissingInheritanceError(DynamicStructType)
        self._build()
        return self


def fwdfilter(structitem):
    """Filter For Forward Elements In Structs."""
    return structitem.orientation == FWD


def bwdfilter(structitem):
    """Filter For Backward Elements In Structs."""
    return structitem.orientation == BWD
