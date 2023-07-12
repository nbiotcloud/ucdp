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
Module Constant.

Usage:

>>> from tabulate import tabulate
>>> import ucdp
>>> ucdp.Const(ucdp.UintType(6), "const_c")
Const(UintType(6), 'const_c')

Also complex types can simply be used:

>>> class AType(ucdp.AStructType):
...     def _build(self):
...         self._add("req", ucdp.BitType())
...         self._add("data", ucdp.ArrayType(ucdp.UintType(16), 5))
...         self._add("ack", ucdp.BitType(), ucdp.BWD)
...         self._add("error", ucdp.BitType(), ucdp.BIDIR)
>>> class MType(ucdp.AEnumType):
...     keytype = ucdp.UintType(2)
...     def _build(self):
...         self._add(0, "Linear")
...         self._add(1, "Cyclic")
>>> class BType(ucdp.AStructType):
...     def _build(self):
...         self._add("foo", AType())
...         self._add("mode", MType())
...         self._add("bar", ucdp.ArrayType(AType(), 3), ucdp.BWD)

>>> const = ucdp.Const(BType(), "const_c")
>>> for item in const:
...     print(repr(item))
Const(BType(), 'const_c')
Const(AType(), 'const_foo_c', level=1)
Const(BitType(), 'const_foo_req_c', level=2)
Const(UintType(16), 'const_foo_data_c', level=2, dims=(Slice('0:4'),))
Const(BitType(), 'const_foo_ack_c', level=2)
Const(BitType(), 'const_foo_error_c', level=2)
Const(MType(), 'const_mode_c', level=1)
Const(AType(), 'const_bar_c', level=1, dims=(Slice('0:2'),))
Const(BitType(), 'const_bar_req_c', level=2, dims=(Slice('0:2'),))
Const(UintType(16), 'const_bar_data_c', level=2, dims=(Slice('0:2'), Slice('0:4')))
Const(BitType(), 'const_bar_ack_c', level=2, dims=(Slice('0:2'),))
Const(BitType(), 'const_bar_error_c', level=2, dims=(Slice('0:2'),))
"""

from typing import Iterator, Tuple

from .attrs import field, frozen
from .ident import Ident


@frozen(cmp=False, hash=True)
class Const(Ident):
    """
    Module Constant.

    Args:
        type_ (AType): Type.
        name (Name()): Name.

    Keyword Args:
        doc (Doc): Documentation Container
        value: Value.

    Constant names should end with '_c', but must not.

    >>> import ucdp
    >>> cnt = ucdp.Const(ucdp.UintType(6), "cnt_c")
    >>> cnt
    Const(UintType(6), 'cnt_c')
    >>> cnt.type_
    UintType(6)
    >>> cnt.name
    'cnt_c'
    >>> cnt.basename
    'cnt'
    >>> cnt.suffix
    '_c'
    >>> cnt.doc
    Doc()
    >>> cnt.value

    If the constant is casted via `int()` it returns `value` if set, other `type_.default`.

    >>> int(ucdp.Const(ucdp.UintType(6, default=2), "cnt_c"))
    2
    >>> int(ucdp.Const(ucdp.UintType(6, default=2), "cnt_c", value=4))
    4

    Constants are Singleton:

    >>> ucdp.Const(ucdp.UintType(6), "cnt_c") is ucdp.Const(ucdp.UintType(6), "cnt_c")
    True
    """

    value = field(default=None, kw_only=True)

    _suffixes: Tuple[str, ...] = ("_c",)

    @value.validator
    def _value_validator(self, attribute, value):
        # pylint: disable=unused-argument
        if value is not None:
            self.type_.check(value)

    def __int__(self):
        value = self.value
        if value is None:
            value = self.type_.default
        return int(value or 0)

    def iter(self, filter_=None, stop=None, maxlevel=None, value=None) -> Iterator:
        """Iterate over Parameter Hierarchy."""
        if value is None:
            value = self.value
        return super().iter(filter_=filter_, stop=stop, maxlevel=maxlevel, value=value)

    def get(self, name, value=None) -> Iterator:
        """Get a specific member in the Parameter Hierarchy."""
        if value is None:
            value = self.value
        return super().get(name, value=value)
