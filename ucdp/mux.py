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
"""Multiplexer."""
from collections import defaultdict
from typing import Generator

from .assigns import Assign, Assigns
from .attrs import field, frozen
from .doc import Doc
from .expr import Expr, parse
from .ident import Ident, Idents
from .signal import Signal
from .types.base import AScalarType, AVecType
from .types.enum import AEnumType


@frozen
class Mux:

    """
    Multiplexer.

    Args:
        name (str): Name
        targets (Idents): Ports and signals allowed to be assigned
        namespace (Idents): Ports, signals, parameter and local parameter as source
        drivers (dict): Drivers, for multiple-driver tracking.
    """

    name: str = field()
    targets: Idents = field(repr=False)
    namespace: Idents = field(repr=False)
    drivers: dict = field(repr=False)
    doc: Doc = field(factory=Doc)

    __assigns: Assigns = field(init=False)  # tracker of all assigned signals
    __mux: dict = field(init=False)  # mux structure

    @__assigns.default
    def _assigns_default(self):
        return Assigns(self.targets, self.namespace, drivers=self.drivers)

    @__mux.default
    def _mux_default(self):
        return defaultdict(dict)

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

    def set(self, sel: Signal, cond: Expr, out: Expr, value: Expr):
        """
        Set Multiplexer.

        Args:
            sel (Signal): Select Signal
            cond (Expr): Condition to be met on `sel`
            out (Expr): Output to be assigned
            value (Expr): Value.
        """
        sel = parse(sel, namespace=self.namespace, types=(AScalarType, AVecType, AEnumType))
        cond = parse(cond, namespace=self.namespace, strict=False)
        out = parse(out, namespace=self.namespace)
        value = parse(value, namespace=self.namespace)
        # conditem = cond.range_ if isinstance(cond, Range) else cond
        # if conditem not in sel.type_:
        #     raise ValueError(f"Condition {cond} is not within range of {sel.type_}")
        mux = self.__mux
        # Track Assignments
        self.__assigns.set(out, value, overwrite=True)
        # Mux Assignments
        try:
            # pylint: disable=unsubscriptable-object
            condassigns = mux[sel][cond]
        except KeyError:
            # pylint: disable=unsubscriptable-object
            mux[sel][cond] = condassigns = Assigns(self.targets, self.namespace)
        condassigns.set(out, value)

    def set_default(self, out: Expr, value: Expr):
        """
        Set Multiplexer.

        Args:
            out (Expr): Output to be assigned
            value (Expr): Value.
        """
        out = parse(out, namespace=self.namespace)
        value = parse(value, namespace=self.namespace)
        self.__assigns.set_default(out, value)

    def defaults(self) -> Generator[Assign, None, None]:
        """Defaults."""
        return self.__assigns.iter_defaults()

    def __iter__(self):
        yield from self.__mux.items()

    @property
    def sels(self) -> Generator[Ident, None, None]:
        """Selects."""
        return self.__mux.keys()

    def __bool__(self):
        return bool(self.__mux)
