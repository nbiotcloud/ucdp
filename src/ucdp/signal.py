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
Signal and Port Handling.

A [Signal][ucdp.signal.Signal] is a module internal signal.
A [Port][ucdp.signal.Port] is a module interface signal with a direction IN, OUT or INOUT.

??? Example "Simple Types"
    Usage:

        >>> from tabulate import tabulate
        >>> import ucdp as u
        >>> u.Signal(u.UintType(6), "sig_s")
        Signal(UintType(6), 'sig_s')

        >>> u.Port(u.UintType(6), "port_i")
        Port(UintType(6), 'port_i', direction=IN)
        >>> u.Port(u.UintType(6), "port_o")
        Port(UintType(6), 'port_o', direction=OUT)

??? Example "Complex Types"
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


??? Example "Resolving Types"
    These types are automatically resolved by iterating over the port:

        >>> sig = u.Signal(BType(), "sig_s")
        >>> for item in sig:
        ...     print(repr(item))
        Signal(BType(), 'sig_s')
        Signal(AType(), 'sig_foo_s')
        Signal(BitType(), 'sig_foo_req_s')
        Signal(ArrayType(UintType(16), 5), 'sig_foo_data_s')
        Signal(BitType(), 'sig_foo_ack_s', direction=BWD)
        Signal(MType(), 'sig_mode_s')
        Signal(ArrayType(AType(), 3), 'sig_bar_s', direction=BWD)
        Signal(ArrayType(BitType(), 3), 'sig_bar_ack_s')
        Signal(ArrayType(ArrayType(UintType(16), 5), 3), 'sig_bar_data_s', direction=BWD)
        Signal(ArrayType(BitType(), 3), 'sig_bar_req_s', direction=BWD)

        >>> inp = u.Port(BType(), "inp_i")
        >>> for item in inp:
        ...     print(repr(item))
        Port(BType(), 'inp_i', direction=IN)
        Port(AType(), 'inp_foo_i', direction=IN)
        Port(BitType(), 'inp_foo_req_i', direction=IN)
        Port(ArrayType(UintType(16), 5), 'inp_foo_data_i', direction=IN)
        Port(BitType(), 'inp_foo_ack_o', direction=OUT)
        Port(MType(), 'inp_mode_i', direction=IN)
        Port(ArrayType(AType(), 3), 'inp_bar_o', direction=OUT)
        Port(ArrayType(BitType(), 3), 'inp_bar_ack_i', direction=IN)
        Port(ArrayType(ArrayType(UintType(16), 5), 3), 'inp_bar_data_o', direction=OUT)
        Port(ArrayType(BitType(), 3), 'inp_bar_req_o', direction=OUT)

"""

from typing import ClassVar

from .casting import Casting
from .clkrelbase import BaseClkRel
from .ident import Ident
from .object import PosArgs
from .orientation import FWD, AOrientation, Direction
from .typebase import BaseType
from .typestruct import StructItem


class BaseSignal(Ident):
    """Base Class for All Signals ([Port][ucdp.signal.Port], [Signal][ucdp.signal.Signal]).

    Args:
        type_: Type.
        name: Name.

    Attributes:
        direction: Direction.
        doc: Documentation Container
        ifdef: IFDEF encapsulation

    """

    direction: AOrientation = FWD
    clkrel: BaseClkRel | None = None

    def cast(self, other: Ident) -> Casting:
        """Cast self=cast(other)."""
        return self.type_.cast(other.type_)

    def _new_structitem(self, structitem: StructItem, **kwargs) -> "BaseSignal":
        # self.clkrel.clk should be a true signal at this time
        clkrel = structitem.clkrel
        return super()._new_structitem(structitem, clkrel=clkrel or self.clkrel, **kwargs)


class Signal(BaseSignal):
    """
    Module Internal Signal.

    Args:
        type_: Type.
        name: Name.

    Attributes:
        direction: Direction.
        doc: Documentation Container
        ifdef: IFDEF encapsulation

    ??? Example "Signal Examples"
        Examples.

            >>> import ucdp as u
            >>> count = u.Signal(u.UintType(6), "count_s")
            >>> count
            Signal(UintType(6), 'count_s')
            >>> count.type_
            UintType(6)
            >>> count.name
            'count_s'
            >>> count.basename
            'count'
            >>> count.suffix
            '_s'
            >>> count.direction
            FWD
            >>> count.ifdef

    Note:
        Signal names should end with '_r' or '_s', but must not.
    """

    def __init__(self, type_: BaseType, name: str, **kwargs):
        kwargs.setdefault("direction", FWD)
        super().__init__(type_=type_, name=name, **kwargs)  # type: ignore[call-arg]


class Port(BaseSignal):
    """
    Module Port.

    Args:
        type_: Type.
        name: Name.

    Attributes:
        direction: Direction.
        doc: Documentation Container
        ifdef: IFDEF encapsulation

    ??? Example "Port Examples"
        Examples.

            >>> import ucdp as u
            >>> count = u.Port(u.UintType(6), "count_i")
            >>> count
            Port(UintType(6), 'count_i', direction=IN)
            >>> count.type_
            UintType(6)
            >>> count.name
            'count_i'
            >>> count.basename
            'count'
            >>> count.suffix
            '_i'
            >>> count.ifdef

    ??? Example "Direction"
        The port direction is automatically determined from the name or needs to be specified explicitly:

            >>> u.Port(u.UintType(6), "count_i").direction
            IN
            >>> u.Port(u.UintType(6), "count_o").direction
            OUT
            >>> u.Port(u.UintType(6), "count_io").direction
            INOUT
            >>> u.Port(u.UintType(6), "count").direction
            Traceback (most recent call last):
            ...
            ValueError: 'direction' is required (could not be retrieved from name 'count').
            >>> u.Port(u.UintType(6), "count", direction=u.OUT).direction
            OUT
    """

    direction: Direction
    _posargs: ClassVar[PosArgs] = ("type_", "name")

    def __init__(self, type_: BaseType, name: str, **kwargs):
        if "direction" not in kwargs:
            kwargs["direction"] = direction = Direction.from_name(name)
            if direction is None:
                raise ValueError(f"'direction' is required (could not be retrieved from name {name!r}).")
        super().__init__(type_=type_, name=name, **kwargs)  # type: ignore[call-arg]
