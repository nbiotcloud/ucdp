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
"""Multiplexer."""

from collections import defaultdict
from collections.abc import Iterator
from functools import cached_property

from .assigns import Assign, Assigns, Drivers
from .doc import Doc
from .expr import Expr
from .exprparser import ExprParser, Parseable
from .ident import Ident, Idents
from .object import Field, NamedObject, computed_field
from .signal import BaseSignal
from .typebase import BaseScalarType

MuxBranch = dict[Expr, Assigns]


class Mux(NamedObject):
    """
    Multiplexer.

    Attributes:
        name: Name
        targets: Ports and signals allowed to be assigned
        namespace: Ports, signals, parameter and local parameter as source
        drivers: Drivers, for multiple-driver tracking.
        parser: Parser
        doc: Documentation
    """

    targets: Idents = Field(repr=False)
    namespace: Idents = Field(repr=False)
    drivers: Drivers = Field(repr=False, default_factory=dict)
    parser: ExprParser = Field(repr=False)
    doc: Doc = Doc()

    @computed_field(repr=False)
    @cached_property
    def __assigns(self) -> Assigns:
        return Assigns(targets=self.targets, sources=self.namespace, drivers=self.drivers)

    @computed_field(repr=False)
    @cached_property
    def __mux(self) -> dict[Expr, MuxBranch]:
        return defaultdict(dict)

    def set(self, sel: Parseable, cond: Parseable, out: Parseable, value: Parseable):
        """
        Set Multiplexer.

        Args:
            sel: Select Signal
            cond: Condition to be met on `sel`
            out: Output to be assigned
            value: Value.
        """
        parse = self.parser.parse
        selexpr = parse(sel, types=BaseScalarType)
        condexpr = parse(cond)
        outexpr: BaseSignal = parse(out, only=BaseSignal)  # type: ignore[assignment]
        valueexpr = parse(value)
        mux = self.__mux
        # Track Assignments
        self.__assigns.set(outexpr, valueexpr, overwrite=True)
        # Mux Assignments
        try:
            condassigns = mux[selexpr][condexpr]
        except KeyError:
            mux[selexpr][condexpr] = condassigns = Assigns(targets=self.targets, sources=self.namespace)
        condassigns.set(outexpr, valueexpr)

    def set_default(self, out: Parseable, value: Parseable):
        """
        Set Multiplexer.

        Args:
            out: Output to be assigned
            value: Value.
        """
        parse = self.parser.parse
        outexpr: BaseSignal = parse(out, only=BaseSignal)  # type: ignore[assignment]
        valueexpr = parse(value)
        self.__assigns.set_default(outexpr, valueexpr)

    def defaults(self) -> Iterator[Assign]:
        """Defaults."""
        return self.__assigns.defaults()

    def __iter__(self) -> Iterator[tuple[Expr, MuxBranch]]:  # type: ignore[override]
        yield from self.__mux.items()

    @property
    def sels(self) -> tuple[Ident, ...]:
        """Selects."""
        return tuple(self.__mux.keys())  # type: ignore[arg-type]
