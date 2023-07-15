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
Descriptive Struct Type.

This module serves a struct type variant :any:`DescriptiveStructType` which describes a given `type_` with constants.
"""
from caseconverter import snakecase

from ..attrs import field, frozen
from .array import ArrayType
from .base import AType
from .enum import BaseEnumType
from .orientation import BWD, FWD
from .scalar import BitType, IntegerType
from .struct import AStructType, BaseStructType


@frozen
class DescriptiveStructType(AStructType):

    """
    Struct with constants describing `type_`.

    Args:
        type_(AType): Type to be described

    Bit:

    >>> import ucdp
    >>> for item in DescriptiveStructType(ucdp.BitType(default=1)).values():
    ...     repr(item)
    "StructItem('default_p', BitType(default=1), doc=Doc(title='Default Value'))"

    Unsigned Integer:

    >>> for item in DescriptiveStructType(ucdp.UintType(16, default=3),
    ...                                   filter_=lambda item: item.name in ("default_p", "max_p")):
    ...     repr(item)
    "StructItem('max_p', UintType(16, default=65535), doc=Doc(title='Maximal Value'))"
    "StructItem('default_p', UintType(16, default=3), doc=Doc(title='Default Value'))"

    Signed Integer:

    >>> for item in DescriptiveStructType(ucdp.SintType(8, default=-3)).values():
    ...     repr(item)
    "StructItem('width_p', IntegerType(default=8), doc=Doc(title='Width in Bits'))"
    "StructItem('min_p', SintType(8, default=-128), doc=Doc(title='Minimal Value'))"
    "StructItem('max_p', SintType(8, default=127), doc=Doc(title='Maximal Value'))"
    "StructItem('default_p', SintType(8, default=-3), doc=Doc(title='Default Value'))"

    Enum:

    >>> class MyEnumType(ucdp.AEnumType):
    ...     keytype = ucdp.UintType(2, default=0)
    ...     def _build(self):
    ...         self._add(0, "Forward")
    ...         self._add(1, 8)
    ...         self._add(2, "Bi-Dir")
    >>> for item in DescriptiveStructType(MyEnumType()).values():
    ...     repr(item)
    "StructItem('width_p', IntegerType(default=2), doc=Doc(title='Width in Bits'))"
    "StructItem('min_p', MyEnumType(), doc=Doc(title='Minimal Value'))"
    "StructItem('max_p', MyEnumType(default=3), doc=Doc(title='Maximal Value'))"
    "StructItem('forward_e', UintType(2))"
    "StructItem('8_e', UintType(2, default=1))"
    "StructItem('bi_dir_e', UintType(2, default=2))"
    "StructItem('default_p', MyEnumType(), doc=Doc(title='Default Value'))"

    Struct:

    >>> class SubStructType(ucdp.AStructType):
    ...     def _build(self):
    ...         self._add('a', ucdp.UintType(2))
    ...         self._add('b', ucdp.UintType(3), ucdp.BWD)
    ...         self._add('c', ucdp.UintType(4), ucdp.BIDIR)
    >>> class MyStructType(ucdp.AStructType):
    ...     def _build(self):
    ...         self._add('ctrl', ucdp.UintType(4), title='Control')
    ...         self._add('data', ucdp.ArrayType(ucdp.SintType(16, default=5), 8), ucdp.FWD, descr='Data to be handled')
    ...         self._add('resp', ucdp.BitType(), ucdp.BWD, comment='Sink response')
    ...         self._add('mode', MyEnumType(), ucdp.BWD, comment='Enum')
    ...         self._add('bi', ucdp.UintType(5), ucdp.BIDIR)
    ...         self._add('sub', SubStructType(), ucdp.BWD)
    >>> for item in DescriptiveStructType(MyStructType()).values():
    ...     repr(item)
    "StructItem('bits_p', IntegerType(default=149), doc=Doc(title='Size in Bits'))"
    "StructItem('fwdbits_p', IntegerType(default=135), doc=Doc(title='Forward Size in Bits'))"
    "StructItem('bwdbits_p', IntegerType(default=5), doc=Doc(title='Backward Size in Bits'))"
    "StructItem('bibits_p', IntegerType(default=9), doc=Doc(title='Bi-Directional Size in Bits'))"

    All this works for parameterized types too:

    >>> width_p = ucdp.Param(ucdp.IntegerType(default=16), 'width_p')
    >>> type_ = ucdp.UintType(width_p, default=4)
    >>> for item in DescriptiveStructType(type_).values():
    ...     repr(item)
    "StructItem('width_p', IntegerType(default=Param(IntegerType(default=16), 'width_p')), doc=...
    "StructItem('min_p', UintType(Param(IntegerType(default=16), 'width_p')), doc=...
    "StructItem('max_p', UintType(Param(IntegerType(default=16), 'width_p'), default=Op(Op(2, '**', Param(...
    "StructItem('default_p', UintType(Param(IntegerType(default=16), 'width_p'), default=4), doc=...
    """

    type_: AType = field()
    enumitem_suffix: str = field(default="e")

    def _build(self) -> None:
        self._add_type(self.type_)

    def _add_type(self, type_: AType) -> None:
        # Width
        if not isinstance(type_, (BitType, IntegerType, ArrayType, BaseStructType)):
            title = "Width in Bits"
            self._add("width_p", IntegerType(default=type_.width), title=title, descr=None, comment=title)
            title = "Minimal Value"
            self._add("min_p", type_.new(default=type_.min_), title=title, descr=None, comment=title)
            title = "Maximal Value"
            self._add("max_p", type_.new(default=type_.max_), title=title, descr=None, comment=title)
        if isinstance(type_, (ArrayType, BaseStructType)):
            title = "Size in Bits"
            self._add("bits_p", IntegerType(default=type_.bits), title=title, descr=None, comment=title)
            fwdbits, bwdbits, bibits = _get_dirwith(type_)
            title = "Forward Size in Bits"
            self._add("fwdbits_p", IntegerType(default=fwdbits), title=title, descr=None, comment=title)
            title = "Backward Size in Bits"
            self._add("bwdbits_p", IntegerType(default=bwdbits), title=title, descr=None, comment=title)
            title = "Bi-Directional Size in Bits"
            self._add("bibits_p", IntegerType(default=bibits), title=title, descr=None, comment=title)
        # Enum Items
        if isinstance(type_, BaseEnumType):
            enumitem_suffix = self.enumitem_suffix
            for eitem in type_.values():
                ename = snakecase(str(eitem.value))
                etype = type_.keytype.new(default=eitem.key)
                doc = eitem.doc
                self._add(f"{ename}_{enumitem_suffix}", etype, title=doc.title, descr=doc.descr, comment=doc.comment)
        # Default
        if not isinstance(type_, (BaseStructType, ArrayType)):
            title = "Default Value"
            self._add("default_p", type_, title=title, descr=None, comment=title)


def _get_dirwith(type_, orientation=FWD):
    fwd, bwd, bid = 0, 0, 0
    for item in type_:
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
            bid += itype_.bits
    return fwd, bwd, bid
