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
"""UART Example."""
from glbl.bus import BusType
from glbl.clkgate import ClkGateMod
from glbl.regf import RegfMod

import ucdp


class UartIoType(ucdp.AStructType):
    title = "UART"
    comment = "RX/TX"

    def _build(self):
        self._add("rx", ucdp.BitType(), ucdp.BWD)
        self._add("tx", ucdp.BitType(), ucdp.BWD)


class UartMod(ucdp.AMod):
    """A Simple UART."""

    # Year for File Header Copyright
    copyright_end_year = 2022

    comment = """\
My Description

Mode  Power       Description
----  ----------  ------------------
"""

    def _build(self):
        self.add_port(ucdp.ClkRstAnType())
        self.add_port(UartIoType(), "uart_i", route="create(u_core/uart_i)")
        self.add_port(BusType(), "bus_i")

        divmax_p = self.add_param(ucdp.IntegerType(default=2**16 - 1), "divmax_p")

        clkgate = ClkGateMod(self, "u_clkgate")
        clkgate.con("clk_i", "clk_i")
        clkgate.con("clk_o", "create(clk_s)")

        regf = RegfMod(self, "u_regf")
        regf.con("", "")
        regf.con("bus_i", "bus_i")

        core = ucdp.CoreMod(self, "u_core", paramdict={"divmax_p": divmax_p})
        core.add_param(ucdp.IntegerType(default=2**16 - 1), "divmax_p")

        core.add_const(ucdp.IntegerType(default=ucdp.log2(divmax_p - 1)), "divwid_p")
        core.add_port(ucdp.ClkRstAnType(), "")
        core.con("clk_i", "clk_s")
        core.con("rst_an_i", "rst_an_i")

        core.add_port(ucdp.UintType(2), "sel_i")
        core.add_port(ucdp.UintType(8), "y_o")
        core.add_port(ucdp.UintType(6), "d_o")
        core.add_port(ucdp.UintType(9), "a_i")

        core.add_flipflop(ucdp.UintType(6), "d_r", nxt="a_i[7:2]", route="d_o")

        coremux = core.add_mux("mymux")
        coremux.set("sel_i", "2d1", "y_o", "a_i[7:0]")

        word = regf.add_word("ctrl")
        word.add_field("ena", ucdp.EnaType(), is_readable=True, route="u_clkgate/ena_i")
        word.add_field("strt", ucdp.BitType(), is_writable=True, route="create(u_core/strt_i)")
