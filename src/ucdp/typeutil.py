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
Type Utilities.

>>> import ucdp as u
>>> from tabulate import tabulate
>>> class UEnumType(u.AEnumType):
...     keytype: u.BaseScalarType = u.UintType(2)
...     def _build(self):
...         self._add(0, 'one')
...         self._add(1, 'two')
>>> class SEnumType(u.AEnumType):
...     keytype: u.BaseScalarType = u.SintType(2)
...     def _build(self):
...         self._add(0, 'one')
...         self._add(-1, 'two')
>>> types = (
...     u.BitType(),
...     u.UintType(10),
...     u.SintType(10),
...     u.BoolType(),
...     u.RailType(),
...     UEnumType(),
...     SEnumType(),
...     u.ClkRstAnType(),
...     u.ArrayType(u.UintType(10),5),
...     u.ArrayType(u.SintType(10),5),
... )

>>> print(tabulate([(t, u.is_scalar(t), u.is_signed(t)) for t in types], headers=("type", "is_scalar", "is_signed")))
type                        is_scalar    is_signed
--------------------------  -----------  -----------
BitType()                   True         False
UintType(10)                True         False
SintType(10)                True         True
BoolType()                  True         False
RailType()                  True         False
UEnumType()                 True         False
SEnumType()                 True         True
ClkRstAnType()              False
ArrayType(UintType(10), 5)  True         False
ArrayType(SintType(10), 5)  True         True
"""

from .typearray import ArrayType
from .typebase import AScalarType, BaseType
from .typebaseenum import BaseEnumType
from .typescalar import IntegerType, SintType


def is_scalar(type_: BaseType) -> bool:
    """Check if `type` is scalar."""
    if isinstance(type_, ArrayType):
        return is_scalar(type_.itemtype)
    if isinstance(type_, BaseEnumType):
        return is_scalar(type_.keytype)
    return isinstance(type_, AScalarType)


def is_signed(type_: BaseType) -> bool | None:
    """
    Check if `type` is signed.
    """
    if isinstance(type_, AScalarType):
        return isinstance(type_, (SintType, IntegerType))
    if isinstance(type_, ArrayType):
        return is_signed(type_.itemtype)
    if isinstance(type_, BaseEnumType):
        return is_signed(type_.keytype)
    return None
