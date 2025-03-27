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
Module Constant.

??? Example "Constant Examples"
    Usage:

        >>> from tabulate import tabulate
        >>> import ucdp as u
        >>> u.Const(u.UintType(6), "const_p")
        Const(UintType(6), 'const_p')

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

    These types are automatically resolved by iterating over the Constant:

        >>> const = u.Const(BType(), "const_p")
        >>> for item in const:
        ...     print(repr(item))
        Const(BType(), 'const_p')
        Const(AType(), 'const_foo_p')
        Const(BitType(), 'const_foo_req_p')
        Const(ArrayType(UintType(16), 5), 'const_foo_data_p')
        Const(BitType(), 'const_foo_ack_p')
        Const(MType(), 'const_mode_p')
        Const(ArrayType(AType(), 3), 'const_bar_p')
        Const(ArrayType(BitType(), 3), 'const_bar_ack_p')
        Const(ArrayType(ArrayType(UintType(16), 5), 3), 'const_bar_data_p')
        Const(ArrayType(BitType(), 3), 'const_bar_req_p')
"""

from .ident import Ident


class Const(Ident):
    """
    Module Constant.

    Args:
        type_: Type.
        name: Name.

    Attributes:
        direction: Direction.
        doc: Documentation Container
        ifdef: IFDEF encapsulation


    ??? Example "Constant Examples"
        Basics:

            >>> import ucdp as u
            >>> cnt = u.Const(u.UintType(6), "cnt_p")
            >>> cnt
            Const(UintType(6), 'cnt_p')
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

    ??? Example "Casting Constant"
        If the constant is casted via `int()` it returns `value` if set, other `type_.default`.

            >>> int(u.Const(u.UintType(6, default=2), "cnt_p"))
            2

    ??? Example "Constant are Singleton"
        Constant are Singleton:

            >>> u.Const(u.UintType(6), "cnt_p") is u.Const(u.UintType(6), "cnt_p")
            True
    """
