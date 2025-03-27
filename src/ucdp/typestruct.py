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
Structure Types.

A structure assembles multiple type, name, orientation pairs.

* :any:`StructItem` - Struct item
* :any:`StructType` - Standard Struct
* :any:`AAGlobalStructType` - A public struct which fills up through all instances.
* :any:`DynamicStructType` - A public struct which fills up per instance.
"""

from abc import abstractmethod
from collections.abc import Callable
from typing import Any, ClassVar

from .clkrelbase import BaseClkRel
from .consts import PAT_IDENTIFIER
from .dict import Dict
from .doc import Doc
from .docutil import doc_from_type
from .exceptions import LockError
from .object import Field, Light, Object, PosArgs, PrivateField
from .orientation import BWD, FWD, Orientation
from .typebase import ACompositeType, BaseType


class StructItem(Object):
    """
    Struct NamedObject.

    Attributes:
        name: Name of struct member
        type_: Type of struct member
        orientation: Orientation of struct member. `FWD` by default
        doc: Documentation Container
        ifdef: IFDEF encapsulation
        clkrel: Clock Relation
    """

    name: str = Field(pattern=PAT_IDENTIFIER)
    type_: BaseType
    orientation: Orientation = FWD
    doc: Doc = Doc()
    ifdef: str | None = None
    clkrel: BaseClkRel | None = None

    _posargs: ClassVar[PosArgs] = ("name", "type_")

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


class BaseStructType(Dict, ACompositeType):
    """Base Type for all Structs."""

    filter_: StructFilter | None = None
    _items: dict[Any, Any] = PrivateField(default_factory=dict)
    _is_locked: bool = PrivateField(default=False)

    def _add(
        self,
        name: str,
        type_: BaseType,
        orientation: Orientation = FWD,
        title: str | None = None,
        descr: str | None = None,
        comment: str | None = None,
        ifdef: str | None = None,
        clkrel: BaseClkRel | None = None,
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
            clkrel: Clock Relation (For signals and ports only).

        :meta public:
        """
        if self._is_locked:
            raise LockError(f"{self}: Cannot add item {name!r}.")
        items = self._items
        if name not in items.keys():
            doc = doc_from_type(type_, title=title, descr=descr, comment=comment)
            structitem = StructItem(name, type_, orientation=orientation, doc=doc, ifdef=ifdef, clkrel=clkrel)
            if not self.filter_ or self.filter_(structitem):
                items[name] = structitem
        else:
            raise ValueError(f"name {name!r} already exists in {self} ({self[name]})")

    def is_connectable(self, other) -> bool:
        """Check For Valid Connection To `other`."""
        if not isinstance(other, BaseStructType):
            return False
        try:
            return all(
                self._cmpitem(selfitem, otheritem)
                for selfitem, otheritem in zip(self.values(), other.values(), strict=True)
            )
        except ValueError:
            return False

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

    @abstractmethod
    def _build(self) -> None:
        """Build Type."""


class AStructType(BaseStructType, Light):
    """
    Base class for all structural types.

    The protected method `_build()` should be used to build the type.

    Definition of a struct:

    >>> import ucdp as u
    >>> class BusType(u.AStructType):
    ...     def _build(self) -> None:
    ...         self._add('data', u.UintType(8))
    ...         self._add('valid', u.BitType())
    ...         self._add('accept', u.BitType(), orientation=u.BWD)

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

    Connections are only allowed to other :any:`AStructType` with the same key-value mapping.

    >>> BusType().is_connectable(BusType())
    True

    >>> class Bus2Type(u.AStructType):
    ...     def _build(self) -> None:
    ...         self._add('data', u.UintType(8))
    ...         self._add('valid', u.BitType())
    ...         self._add('accept', u.BitType(), orientation=u.FWD)
    >>> BusType().is_connectable(Bus2Type())
    False

    >>> class Bus3Type(u.AStructType):
    ...     def _build(self) -> None:
    ...         self._add('data', u.UintType(8), title="title")
    ...         self._add('valid', u.BitType(default=1))
    ...         self._add('accept', u.BitType(), orientation=u.BWD)
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

    >>> for item in BusType(filter_=u.fwdfilter).values(): item
    StructItem('data', UintType(8))
    StructItem('valid', BitType())

    >>> for item in BusType(filter_=u.bwdfilter).values(): item
    StructItem('accept', BitType(), orientation=BWD)

    This works also with the `new()` method:

    >>> for item in BusType().new(filter_=u.fwdfilter).values(): item
    StructItem('data', UintType(8))
    StructItem('valid', BitType())
    """

    def model_post_init(self, __context: Any) -> None:
        """Run Build."""
        self._build()
        self._is_locked = True


class AGlobalStructType(BaseStructType, Light):
    """
    A singleton struct which can be filled outside `_build` and is **shared** between instances.

    >>> import ucdp as u
    >>> class BusType(u.AGlobalStructType):
    ...     pass
    >>> bus = BusType()
    >>> bus.add('data', u.UintType(8))
    >>> bus.add('valid', u.BitType())
    >>> bus = BusType()
    >>> bus.add('accept', u.BitType(), orientation=u.BWD)
    >>> tuple(bus)
    ('data', 'valid', 'accept')

    This is forbidden on normal struct:

    >>> class BusType(u.AStructType):
    ...     def _build(self) -> None:
    ...         pass
    >>> bus = BusType()
    >>> bus._add('data', u.UintType(8))
    Traceback (most recent call last):
      ...
    ucdp.exceptions.LockError: BusType(): Cannot add item 'data'.
    """

    def add(
        self,
        name: str,
        type_: BaseType,
        orientation: Orientation = FWD,
        title: str | None = None,
        descr: str | None = None,
        comment: str | None = None,
        ifdef: str | None = None,
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
        """
        self._add(
            name,
            type_,
            orientation=orientation,
            title=title,
            descr=descr,
            comment=comment,
            ifdef=ifdef,
        )

    def _build(self) -> None:
        """Build Type."""

    def model_post_init(self, __context: Any) -> None:
        """Run Build."""
        if self.__class__ is AGlobalStructType:
            raise TypeError("Can't instantiate abstract class AGlobalStructType. Please create a subclass.")
        self._build()


class DynamicStructType(BaseStructType):
    """
    A singleton struct which can be filled outside `_build` and is **not** shared between instances.

    >>> import ucdp as u
    >>> class BusType(u.DynamicStructType):
    ...     pass
    >>> bus = BusType()
    >>> bus.add('data', u.UintType(8))
    >>> bus.add('valid', u.BitType())
    >>> tuple(bus)
    ('data', 'valid')
    >>> bus = BusType()
    >>> bus.add('accept', u.BitType(), orientation=u.BWD)
    >>> tuple(bus)
    ('accept',)

    This is forbidden on normal struct:

    >>> class BusType(u.AStructType):
    ...     def _build(self) -> None:
    ...         pass
    >>> bus = BusType()
    >>> bus._add('data', u.UintType(8))
    Traceback (most recent call last):
      ...
    ucdp.exceptions.LockError: BusType(): Cannot add item 'data'.
    """

    def add(
        self,
        name: str,
        type_: BaseType,
        orientation: Orientation = FWD,
        title: str | None = None,
        descr: str | None = None,
        comment: str | None = None,
        ifdef: str | None = None,
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
        """
        self._add(
            name,
            type_,
            orientation=orientation,
            title=title,
            descr=descr,
            comment=comment,
            ifdef=ifdef,
        )

    def _build(self) -> None:
        """Build Type."""

    def model_post_init(self, __context: Any) -> None:
        """Run Build."""
        self._build()


def fwdfilter(structitem):
    """Filter For Forward Elements In Structs."""
    return structitem.orientation == FWD


def bwdfilter(structitem):
    """Filter For Backward Elements In Structs."""
    return structitem.orientation == BWD
