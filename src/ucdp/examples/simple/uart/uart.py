#
# MIT License
#
# Copyright (c) 2024 nbiotcloud
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
"""UART Example."""

from typing import ClassVar

import ucdp as u  # (1)
from fileliststandard import HdlFileList
from glbl.bus import BusType  # (2)
from glbl.clk_gate import ClkGateMod  # (3)
from glbl.regf import RegfMod  # (4)


class UartIoType(u.AStructType):
    """UART IO."""

    title: str = "UART"
    comment: str = "RX/TX"

    def _build(self) -> None:
        self._add("rx", u.BitType(), u.BWD)  # (5)
        self._add("tx", u.BitType(), u.FWD)  # (6)


class UartMod(u.AMod):
    """A Simple UART."""

    filelists: ClassVar[u.ModFileLists] = (HdlFileList(gen="full"),)

    def _build(self) -> None:
        self.add_port(u.ClkRstAnType(), "main_i")
        self.add_port(UartIoType(), "uart_i", route="create(u_core/uart_i)")
        self.add_port(BusType(), "bus_i")

        clkgate = ClkGateMod(self, "u_clk_gate")
        clkgate.con("clk_i", "clk_i")
        clkgate.con("clk_o", "create(clk_s)")

        regf = RegfMod(self, "u_regf")
        regf.con("main_i", "main_i")
        regf.con("bus_i", "bus_i")

        core = u.CoreMod(parent=self, name="u_core")

        core.add_port(u.ClkRstAnType(), "main_i")
        core.con("main_clk_i", "clk_s")
        core.con("main_rst_an_i", "rst_an_i")
        core.con("create(regf_i)", "u_regf/regf_o")

        word = regf.add_word("ctrl")
        word.add_field("ena", u.EnaType(), is_readable=True, route="u_clk_gate/ena_i")
        word.add_field("strt", u.BitType(), is_writable=True, route="create(u_core/strt_i)")
