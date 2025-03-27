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
Module Parameter .

??? Example "Parameter Examples"
    Usage:

        >>> from tabulate import tabulate
        >>> import ucdp as u
        >>> u.Param(u.UintType(6), "param_p")
        Param(UintType(6), 'param_p')

        Also complex types can simply be used:

        >>> class AType(u.AStructType):
        ...     def _build(self) -> None:
        ...         self._add("req", u.BitType())
        ...         self._add("data", u.ArrayType(u.UintType(16), 5))
        ...         self._add("ack", u.BitType(), u.BWD)
        >>> class MType(u.AEnumType):
        ...     keytype: u.AScalarType = u.UintType(2)
        ...     def _build(self) -> None:
        ...         self._add(0, "Linear")
        ...         self._add(1, "Cyclic")
        >>> class BType(u.AStructType):
        ...     def _build(self) -> None:
        ...         self._add("foo", AType())
        ...         self._add("mode", MType())
        ...         self._add("bar", u.ArrayType(AType(), 3), u.BWD)

    These types are automatically resolved by iterating over the parameter:

        >>> param = u.Param(BType(), "param_p")
        >>> for item in param:
        ...     print(repr(item))
        Param(BType(), 'param_p')
        Param(AType(), 'param_foo_p')
        Param(BitType(), 'param_foo_req_p')
        Param(ArrayType(UintType(16), 5), 'param_foo_data_p')
        Param(BitType(), 'param_foo_ack_p')
        Param(MType(), 'param_mode_p')
        Param(ArrayType(AType(), 3), 'param_bar_p')
        Param(ArrayType(BitType(), 3), 'param_bar_ack_p')
        Param(ArrayType(ArrayType(UintType(16), 5), 3), 'param_bar_data_p')
        Param(ArrayType(BitType(), 3), 'param_bar_req_p')

    Value:

        >>> for item in u.Param(u.UintType(6), "param_p").iter():
        ...     print(repr(item))
        Param(UintType(6), 'param_p')
        >>> for item in u.Param(u.UintType(6), "param_p").iter(value=42):
        ...     print(repr(item))
        Param(UintType(6, default=42), 'param_p')
"""

from typing import Any

from .ident import Ident, _iters


class Param(Ident):
    """
    Module Parameter.

    Args:
        type_ (AType): Type.
        name (Name): Name.

    Keyword Args:
        doc (Doc): Documentation Container
        value (Any): Value.


    Note:
        Parameter names should end with '_p', but must not.

    ??? Example "Param Examples"
        Example:

            >>> import ucdp as u
            >>> cnt = u.Param(u.UintType(6), "cnt_p")
            >>> cnt
            Param(UintType(6), 'cnt_p')
            >>> cnt.type_
            UintType(6)
            >>> cnt.name
            'cnt_p'
            >>> cnt.basename
            'cnt'
            >>> cnt.suffix
            '_p'
            >>> cnt.doc
            Doc()
            >>> cnt.value

        If the parameter is casted via `int()` it returns `value` if set, other `type_.default`.

            >>> int(u.Param(u.UintType(6, default=2), "cnt_p"))
            2
            >>> int(u.Param(u.UintType(6, default=2), "cnt_p", value=4))
            4

        Parameter are Singleton:

            >>> u.Param(u.UintType(6), "cnt_p") is u.Param(u.UintType(6), "cnt_p")
            True
    """

    value: Any = None

    def __int__(self):
        value = self.value
        if value is None:
            value = self.type_.default
        return int(value or 0)

    def __iter__(self):
        for _, ident in _iters([self], value=self.value):
            yield ident
