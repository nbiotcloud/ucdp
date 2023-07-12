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
* :any:`AStructType` - Standard Struct
* :any:`AGlobalStructType` - A public struct which fills up through all instances.
* :any:`DynamicStructType` - A public struct which fills up per instance.
"""
from typing import Callable, Optional

from ..attrs import NOTHING, ReusedFrozen, field, frozen
from ..doc import Doc
from ..nameutil import validate_name
from ..util import AutoNum
from .base import ACompositeType, AType
from .orientation import BWD, FWD, Orientation

_STRUCTNUM = AutoNum()


@frozen
class StructItem(ReusedFrozen):

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

    name = field()
    type_: AType = field()
    orientation: Orientation = field(default=FWD)
    doc: Doc = field(default=Doc())
    ifdef: Optional[str] = field(default=None)

    @name.validator
    def _validate_name(self, attribute, value):
        # pylint: disable=unused-argument
        validate_name(value)

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


@frozen
class BaseStructType(dict, ACompositeType):

    """Base Type for all Structs."""

    filter_: Callable[[StructItem], bool] = field(default=None, kw_only=True, repr=False)
    _locked: bool = False

    def __attrs_post_init__(self):
        self._build()

    def _build(self) -> None:
        """Build Type."""

    def _add(
        self,
        name: str,
        type_: AType,
        orientation: Orientation = FWD,
        title: Optional[str] = NOTHING,  # type: ignore
        descr: Optional[str] = NOTHING,  # type: ignore
        comment: Optional[str] = NOTHING,  # type: ignore
        ifdef: Optional[str] = NOTHING,  # type: ignore
    ) -> None:
        """
        Add member `name` with `type_` and `orientation`.

        Args:
            name (str): Name
            type_ (AType): Type
            orientation (Orientation): Orientation

        Keyword Args:
            title (str): Full Spoken Name.
            descr (str): Documentation Description.
            comment (str): Source Code Comment.

        :meta public:
        """
        # pylint: disable=too-many-arguments
        assert not self._locked, f"{self} is not public and forbidden to be modified."
        if name not in self:
            doc = Doc.from_type(type_, title, descr, comment)
            structitem = StructItem(name, type_, orientation, doc, ifdef)
            # pylint: disable=not-callable
            if not self.filter_ or self.filter_(structitem):
                self[name] = structitem
        else:
            raise ValueError(f"name {name!r} already exists in {self} ({self[name]})")

    def __iter__(self):
        yield from self.values()

    def is_connectable(self, other):
        """Check For Valid Connection To `other`."""

        return (
            isinstance(other, BaseStructType)
            and len(self) == len(other)
            and all(self._cmpitem(selfitem, otheritem) for selfitem, otheritem in zip(self, other))
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
        return sum(item.type_.bits for item in self)


@frozen
class AStructType(BaseStructType, ReusedFrozen):

    """
    Base class for all structural types, b    StructItem('data', UintType(8))
    StructItem('valid', BitType())ehaves like a dictionary.

    The protected method `_build()` should be used to build the type.

    Definition of a struct:

    >>> import ucdp
    >>> class BusType(ucdp.AStructType):
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

    >>> tuple(bus)
    (StructItem('data', UintType(8)), StructItem('valid', BitType()), ...)
    >>> bus.keys()
    dict_keys(['data', 'valid', 'accept'])
    >>> bus.values()
    dict_values([StructItem('data', UintType(8)), StructItem('valid', BitType()), ...])
    >>> for key, item in bus.items():
    ...     print(key, item)
    data StructItem('data', UintType(8))
    valid StructItem('valid', BitType())
    accept StructItem('accept', BitType(), orientation=BWD)
    >>> bus['valid']
    StructItem('valid', BitType())

    Connections are only allowed to other :any:`AStructType` with the same key-value mapping.
    Default and isolation values are ignored.

    >>> BusType().is_connectable(BusType())
    True

    >>> class Bus2Type(ucdp.AStructType):
    ...     def _build(self):
    ...         self._add('data', ucdp.UintType(8))
    ...         self._add('valid', ucdp.BitType())
    ...         self._add('accept', ucdp.BitType(), orientation=ucdp.FWD)
    >>> BusType().is_connectable(Bus2Type())
    False

    >>> class Bus3Type(ucdp.AStructType):
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
    >>> for item in BusType(filter_=myfilter): item
    StructItem('data', UintType(8))
    StructItem('accept', BitType(), orientation=BWD)

    There are also these predefined filters:

    >>> for item in BusType(filter_=ucdp.fwdfilter): item
    StructItem('data', UintType(8))
    StructItem('valid', BitType())

    >>> for item in BusType(filter_=ucdp.bwdfilter): item
    StructItem('accept', BitType(), orientation=BWD)

    This works also with the `new()` method:

    >>> for item in BusType().new(filter_=ucdp.fwdfilter): item
    StructItem('data', UintType(8))
    StructItem('valid', BitType())
    """

    def __attrs_post_init__(self):
        self._build()
        object.__setattr__(self, "_locked", True)


@frozen
class AGlobalStructType(BaseStructType, ReusedFrozen):

    """
    A singleton struct which can be filled outside `_build` and is **shared** between instances.

    >>> import ucdp
    >>> class BusType(ucdp.AGlobalStructType):
    ...     pass
    >>> bus = BusType()
    >>> bus.add('data', ucdp.UintType(8))
    >>> bus.add('valid', ucdp.BitType())
    >>> bus = BusType()
    >>> bus.add('accept', ucdp.BitType(), orientation=ucdp.BWD)
    >>> tuple(bus)
    (StructItem('data', UintType(8)), StructItem('valid', BitType()), StructItem('accept', BitType(), orientation=BWD))

    This is forbidden on normal struct:

    >>> class BusType(ucdp.AStructType):
    ...     pass
    >>> bus = BusType()
    >>> bus._add('data', ucdp.UintType(8))
    Traceback (most recent call last):
      ...
    AssertionError: BusType() is not public and forbidden to be modified.
    """

    add = BaseStructType._add


@frozen
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
    (StructItem('data', UintType(8)), StructItem('valid', BitType()))
    >>> bus = BusType()
    >>> bus.add('accept', ucdp.BitType(), orientation=ucdp.BWD)
    >>> tuple(bus)
    (StructItem('accept', BitType(), orientation=BWD),)

    This is forbidden on normal struct:

    >>> class BusType(ucdp.AStructType):
    ...     pass
    >>> bus = BusType()
    >>> bus._add('data', ucdp.UintType(8))
    Traceback (most recent call last):
      ...
    AssertionError: BusType() is not public and forbidden to be modified.
    """

    idx = field(factory=_STRUCTNUM.get, init=False)

    add = BaseStructType._add

    _dynamic = True


def fwdfilter(structitem):
    """Helper Function to filter for forward elements in structs."""
    return structitem.orientation == FWD


def bwdfilter(structitem):
    """Helper Function to filter for backward elements in structs."""
    return structitem.orientation == BWD
