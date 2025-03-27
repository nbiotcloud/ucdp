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

"""Flip Flop."""

from .assigns import Assigns
from .expr import BoolOp
from .object import model_validator
from .signal import BaseSignal
from .typeclkrst import ClkType, RstAnType


class FlipFlop(Assigns):
    """FlipFlop.

    Attributes:
        clk: Clock
        rst_an: Reset (low active)
        rst: Reset
        ena: Enable

    """

    clk: BaseSignal
    rst_an: BaseSignal
    rst: BoolOp | None = None
    ena: BoolOp | None = None

    @model_validator(mode="after")
    def __post_init(self) -> "FlipFlop":
        if not isinstance(self.clk.type_, ClkType):
            raise ValueError("clk is not of ClkType")
        if not isinstance(self.rst_an.type_, RstAnType):
            raise ValueError("rst_an is not of RstAnType")
        return self
