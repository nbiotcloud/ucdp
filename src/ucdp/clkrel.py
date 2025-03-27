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
Clock Relation.
"""

from .clkrelbase import BaseClkRel
from .humannum import Freq
from .signal import BaseSignal


class ClkRel(BaseClkRel):
    """
    Clock Relation.

    >>> import ucdp as u
    >>> clk = u.Port(type_=u.ClkType(), name="clk_i")
    >>> inp = u.Port(type_=u.UintType(8), name="inp_i", clkrel=u.ASYNC)
    >>> inp.clkrel
    ASYNC
    >>> inp.clkrel.info
    'ASYNC'
    >>> outp = u.Port(type_=u.UintType(8), name="outp_o", clkrel=u.ClkRel(clk=clk))
    >>> outp.clkrel
    ClkRel(clk=Port(ClkType(), 'clk_i', direction=IN))
    >>> outp.clkrel.info
    'clk: clk_i'

    """

    clk: BaseSignal | str | None = None
    """Signal."""

    freq_min: Freq | None = None
    freq: Freq | None = None
    freq_max: Freq | None = None

    @property
    def freqs(self) -> tuple[Freq | None, Freq | None, Freq | None]:
        """Frequency Tuple: Min/Typ/Max."""
        return (self.freq_min, self.freq, self.freq_max)

    @property
    def info(self) -> str:
        """Information."""
        result = []
        clk = self.clk
        if clk:
            if isinstance(clk, BaseSignal):
                clk = clk.name
            result.append(f"clk: {clk}")
        freqs = self.freqs
        if any(freqs):
            result.append(str(freqs))
        return " ".join(result)


class _AsyncClkRel(BaseClkRel):
    """Async."""

    @property
    def info(self) -> str:
        """Information."""
        return "ASYNC"

    def __repr__(self) -> str:
        return "ASYNC"

    def __str__(self) -> str:
        return "ASYNC"


ASYNC = _AsyncClkRel()
