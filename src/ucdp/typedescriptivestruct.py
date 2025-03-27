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
Descriptive Struct Type.

This module serves a struct type variant :any:`DescriptiveStructType` which describes a given `type_` with constants.
"""

from .nameutil import str2identifier
from .orientation import BWD, FWD
from .typearray import ArrayType
from .typebase import BaseType
from .typeenum import BaseEnumType
from .typescalar import IntegerType, SintType, UintType
from .typestruct import AStructType, BaseStructType, StructFilter


class DescriptiveStructType(AStructType):
    """
    Struct with constants describing `type_`.

    Attributes:
        type_: Type to be described

    Bit:

        >>> import ucdp as u
        >>> for item in u.DescriptiveStructType(u.BitType(default=1)).values():
        ...     repr(item)
        "StructItem('default_p', BitType(default=1), doc=Doc(title='Default Value'))"

    Unsigned Integer:

        >>> for item in u.DescriptiveStructType(u.UintType(16, default=3),
        ...                                   filter_=lambda item: item.name in ("default_p", "max_p")).values():
        ...     item
        StructItem('max_p', UintType(16, default=65535), doc=Doc(title='Maximal Value'))
        StructItem('default_p', UintType(16, default=3), doc=Doc(title='Default Value'))

    Signed Integer:

        >>> for item in u.DescriptiveStructType(u.SintType(8, default=-3)).values():
        ...     repr(item)
        "StructItem('width_p', IntegerType(default=8), doc=Doc(title='Width in Bits'))"
        "StructItem('min_p', SintType(8, default=-128), doc=Doc(title='Minimal Value'))"
        "StructItem('max_p', SintType(8, default=127), doc=Doc(title='Maximal Value'))"
        "StructItem('default_p', SintType(8, default=-3), doc=Doc(title='Default Value'))"

    Enum:

        >>> class MyEnumType(u.AEnumType):
        ...     keytype: u.AScalarType = u.UintType(2, default=0)
        ...     def _build(self) -> None:
        ...         self._add(0, "Forward")
        ...         self._add(1, 8)
        ...         self._add(2, "Bi-Dir")
        >>> for item in u.DescriptiveStructType(MyEnumType()).values():
        ...     repr(item)
        "StructItem('width_p', IntegerType(default=2), doc=Doc(title='Width in Bits'))"
        "StructItem('min_p', MyEnumType(default=0), doc=Doc(title='Minimal Value'))"
        "StructItem('max_p', MyEnumType(default=3), doc=Doc(title='Maximal Value'))"
        "StructItem('forward_e', UintType(2))"
        "StructItem('v8_e', UintType(2, default=1))"
        "StructItem('bi_dir_e', UintType(2, default=2))"
        "StructItem('default_p', MyEnumType(), doc=Doc(title='Default Value'))"

    Struct:

        >>> class SubStructType(u.AStructType):
        ...     def _build(self) -> None:
        ...         self._add('a', u.UintType(2))
        ...         self._add('b', u.UintType(3), u.BWD)
        >>> class MyStructType(u.AStructType):
        ...     def _build(self) -> None:
        ...         self._add('ctrl', u.UintType(4), title='Control')
        ...         self._add('data', u.ArrayType(u.SintType(16, default=5), 8), u.FWD, descr='Data to be handled')
        ...         self._add('resp', u.BitType(), u.BWD, comment='Sink response')
        ...         self._add('mode', MyEnumType(), u.BWD, comment='Enum')
        ...         self._add('sub', SubStructType(), u.BWD)
        >>> for item in u.DescriptiveStructType(MyStructType()).values():
        ...     repr(item)
        "StructItem('bits_p', IntegerType(default=140), doc=Doc(title='Size in Bits'))"
        "StructItem('fwdbits_p', IntegerType(default=135), doc=Doc(title='Forward Size in Bits'))"
        "StructItem('bwdbits_p', IntegerType(default=5), doc=Doc(title='Backward Size in Bits'))"
        "StructItem('bibits_p', IntegerType(), doc=Doc(title='Bi-Directional Size in Bits'))"

    """

    # All this works for parameterized types too:

    # >>> width_p = u.Param(u.IntegerType(default=16), 'width_p')
    # >>> type_ = u.UintType(width_p, default=4)
    # >>> for item in u.DescriptiveStructType(type_).values():
    # ...     repr(item)
    # "StructItem('width_p', IntegerType(default=Param(IntegerType(default=16), 'width_p')), doc=...
    # "StructItem('min_p', UintType(Param(IntegerType(default=16), 'width_p')), doc=...
    # "StructItem('max_p', UintType(Param(IntegerType(default=16), 'width_p'), default=Op(Op(2, '**', Param(...
    # "StructItem('default_p', UintType(Param(IntegerType(default=16), 'width_p'), default=4), doc=...

    type_: BaseType
    enumitem_suffix: str = "e"
    filter_: StructFilter | None = None

    def __init__(self, type_: BaseType, **kwargs):
        super().__init__(type_=type_, **kwargs)  # type: ignore[call-arg]

    def _build(self) -> None:
        self._add_type(self.type_)

    def _add_type(self, type_: BaseType) -> None:
        # Width
        if isinstance(type_, (UintType, SintType, BaseEnumType)):
            title = "Width in Bits"
            self._add("width_p", IntegerType(default=type_.width), title=title)
            title = "Minimal Value"
            self._add("min_p", type_.new(default=type_.min_), title=title)
            title = "Maximal Value"
            self._add("max_p", type_.new(default=type_.max_), title=title)
        if isinstance(type_, (ArrayType, BaseStructType)):
            title = "Size in Bits"
            self._add("bits_p", IntegerType(default=type_.bits), title=title)
            fwdbits, bwdbits, bibits = _get_dirwith(type_)
            title = "Forward Size in Bits"
            self._add("fwdbits_p", IntegerType(default=fwdbits), title=title)
            title = "Backward Size in Bits"
            self._add("bwdbits_p", IntegerType(default=bwdbits), title=title)
            title = "Bi-Directional Size in Bits"
            self._add("bibits_p", IntegerType(default=bibits), title=title)
        # Enum Items
        if isinstance(type_, BaseEnumType):
            enumitem_suffix = self.enumitem_suffix
            for eitem in type_.values():
                ename = str2identifier(str(eitem.value))
                etype = type_.keytype.new(default=eitem.key)
                doc = eitem.doc
                self._add(f"{ename}_{enumitem_suffix}", etype, title=doc.title, descr=doc.descr, comment=doc.comment)
        # Default
        if not isinstance(type_, (BaseStructType, ArrayType)):
            title = "Default Value"
            self._add("default_p", type_, title=title)


def _get_dirwith(type_, orientation=FWD):
    fwd, bwd, bid = 0, 0, 0
    for item in type_.values():
        itype_ = item.type_
        iorientation = item.orientation * orientation
        if isinstance(itype_, BaseStructType):
            ifwd, ibwd, ibid = _get_dirwith(itype_, iorientation)
            fwd += ifwd
            bwd += ibwd
            bid += ibid
        elif iorientation == FWD:
            fwd += itype_.bits
        elif iorientation == BWD:
            bwd += itype_.bits
        else:
            raise AssertionError
    return fwd, bwd, bid
