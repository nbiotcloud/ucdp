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
Signal and Port Handling.

A :any:`Signal` is a module internal signal.
A :any:`Port` is a module interface signal with a direction IN, OUT or INOUT.

Usage:

>>> from tabulate import tabulate
>>> import ucdp
>>> ucdp.Signal(ucdp.UintType(6), "sig_s")
Signal(UintType(6), 'sig_s')

>>> ucdp.Port(ucdp.UintType(6), "port_i")
Port(UintType(6), name='port_i')
>>> ucdp.Port(ucdp.UintType(6), "port_o")
Port(UintType(6), name='port_o')

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

These types are automatically resolved by iterating over the port:

>>> sig = ucdp.Signal(BType(), "sig_s")
>>> for item in sig:
...     print(repr(item))
Signal(BType(), 'sig_s')
Signal(AType(), 'sig_foo_s', level=1)
Signal(BitType(), 'sig_foo_req_s', level=2)
Signal(UintType(16), 'sig_foo_data_s', level=2, dims=(Slice('0:4'),))
Signal(BitType(), 'sig_foo_ack_s', level=2, direction=BWD)
Signal(BitType(), 'sig_foo_error_s', level=2, direction=BIDIR)
Signal(MType(), 'sig_mode_s', level=1)
Signal(AType(), 'sig_bar_s', level=1, direction=BWD, dims=(Slice('0:2'),))
Signal(BitType(), 'sig_bar_req_s', level=2, direction=BWD, dims=(Slice('0:2'),))
Signal(UintType(16), 'sig_bar_data_s', level=2, direction=BWD, dims=(Slice('0:2'), Slice('0:4')))
Signal(BitType(), 'sig_bar_ack_s', level=2, dims=(Slice('0:2'),))
Signal(BitType(), 'sig_bar_error_s', level=2, direction=BIDIR, dims=(Slice('0:2'),))

>>> inp = ucdp.Port(BType(), "inp_i")
>>> for item in inp:
...     print(repr(item))
Port(BType(), name='inp_i')
Port(AType(), name='inp_foo_i', level=1)
Port(BitType(), name='inp_foo_req_i', level=2)
Port(UintType(16), name='inp_foo_data_i', level=2, dims=(Slice('0:4'),))
Port(BitType(), name='inp_foo_ack_o', level=2)
Port(BitType(), name='inp_foo_error_io', level=2)
Port(MType(), name='inp_mode_i', level=1)
Port(AType(), name='inp_bar_o', level=1, dims=(Slice('0:2'),))
Port(BitType(), name='inp_bar_req_o', level=2, dims=(Slice('0:2'),))
Port(UintType(16), name='inp_bar_data_o', level=2, dims=(Slice('0:2'), Slice('0:4')))
Port(BitType(), name='inp_bar_ack_i', level=2, dims=(Slice('0:2'),))
Port(BitType(), name='inp_bar_error_io', level=2, dims=(Slice('0:2'),))
"""
from typing import Any, Optional, Tuple

from .attrs import field, frozen
from .doc import Doc
from .ident import Ident
from .nameutil import split_suffix
from .types.orientation import FWD, IN, AOrientation, Direction, convert_aorientation, convert_direction


@frozen(cmp=False, hash=True)
class ASignal(Ident):

    """Base Class for All Signals (:any:`Port`, :any:`Signal`)."""

    # Direction is always forward
    direction: AOrientation = field(default=FWD, converter=convert_aorientation, kw_only=True)
    dims: Tuple[Any, ...] = field(default=tuple(), kw_only=True)
    doc: Doc = field(default=Doc(), kw_only=True)


@frozen(cmp=False, hash=True)
class Signal(ASignal):

    """
    Module Internal Signal.

    Args:
        type_ (AbstractType): Type.
        name (Name()): Name.

    >>> import ucdp
    >>> count = ucdp.Signal(ucdp.UintType(6), "count_s")
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

    Signal names should end with '_r' or '_s', but must not.
    """

    _suffixes: Tuple[str, ...] = ("_r", "_s")


@frozen(cmp=False, hash=True)
class Port(ASignal):

    """
    Module Port.

    Args:
        type_ (AbstractType): Type.

    Keyword Args:
        name (Name()): Name. Default is None.
        direction (Direction): Signal Direction. Automatically detected if `name` ends with '_i', '_o', '_io'.
        title (str): Full Spoken Name.
        descr (str): Documentation Description.
        comment (str): Source Code Comment.
        ifdef (str): Encapsulate port with ifdef.

    >>> import ucdp
    >>> count = ucdp.Port(ucdp.UintType(6), "count_i")
    >>> count
    Port(UintType(6), name='count_i')
    >>> count.type_
    UintType(6)
    >>> count.name
    'count_i'
    >>> count.direction
    IN
    >>> count.basename
    'count'
    >>> count.suffix
    '_i'

    The port direction is automatically determined from the name or needs to be specified explicitly:

    >>> ucdp.Port(ucdp.UintType(6)).direction
    IN
    >>> ucdp.Port(ucdp.UintType(6), "count_i").direction
    IN
    >>> ucdp.Port(ucdp.UintType(6), "count_o").direction
    OUT
    >>> ucdp.Port(ucdp.UintType(6), "count_io").direction
    INOUT
    >>> ucdp.Port(ucdp.UintType(6), "count").direction
    Traceback (most recent call last):
      ...
    ValueError: 'direction' is required (could not be retrieved from name 'count').
    >>> ucdp.Port(ucdp.UintType(6), "count", direction=ucdp.OUT).direction
    OUT
    """

    # pylint: disable=too-many-instance-attributes

    name: str = field(default="")
    basename: str = field(init=False)
    suffix: str = field(init=False)
    direction: Direction = field(converter=convert_direction, kw_only=True)
    level: int = field(default=0, kw_only=True)
    dims: Tuple[Any, ...] = field(default=tuple(), kw_only=True)
    doc: Doc = field(default=Doc(), kw_only=True)
    ifdef: Optional[str] = field(default=None, kw_only=True)

    _suffixes = ("_i", "_o", "_io")

    @basename.default
    def _basename_default(self) -> str:
        return split_suffix(self.name, suffixes=self._suffixes)[0]

    @suffix.default
    def _suffix_default(self) -> str:
        return split_suffix(self.name, suffixes=self._suffixes)[1]

    @direction.default
    def _direction_default(self):
        if self.name:
            direction = Direction.from_name(self.name)
            if direction is None:
                raise ValueError(f"'direction' is required (could not be retrieved from name {self.name!r}).")
            return direction
        return IN
