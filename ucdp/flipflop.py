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

"""Flip Flop."""
from typing import Optional

from .assigns import Assigns
from .attrs import define, field
from .expr import BoolOp
from .ident import Idents
from .signal import ASignal


@define
class FlipFlop(Assigns):

    """FlipFlop."""

    # pylint: disable=too-many-instance-attributes

    clk: ASignal = field()
    rst_an: ASignal = field()
    rst: Optional[BoolOp] = field(default=None)
    ena: Optional[BoolOp] = field(default=None)
    targets: Idents = field(factory=Idents, repr=False)
    sources: Idents = field(factory=Idents, repr=False)
    drivers: dict = field(factory=dict, repr=False)

    @staticmethod
    def create(
        mod, flipflops: dict, clk: ASignal, rst_an: ASignal, rst: Optional[BoolOp], ena: Optional[BoolOp]
    ) -> "FlipFlop":
        """Create FlipFlop Or Use Exisiting One."""
        # pylint: disable=too-many-arguments
        key = clk, rst_an, rst, ena
        try:
            flipflop = flipflops[key]
        except KeyError:
            flipflop = FlipFlop(
                clk,
                rst_an,
                rst=rst,
                ena=ena,
                targets=mod.portssignals,
                sources=mod.namespace,
                drivers=mod.drivers,
            )
            flipflops[key] = flipflop
        return flipflop
