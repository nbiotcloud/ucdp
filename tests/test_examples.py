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
"""Test Configuration."""


def test_example_simple(example_simple):
    """Basic Testing."""
    from uart.uart import UartMod

    mod = UartMod()

    assert mod.basename == "uart"
    assert mod.modname == "uart"
    assert mod.libname == "uart"
    assert mod.qualname == "uart.uart"
    assert [repr(item) for item in mod.namespace] == [
        "Port(ClkRstAnType(), 'main_i', direction=IN, doc=Doc(title='Clock and Reset'))",
        "Port(UartIoType(), 'uart_i', direction=IN, doc=Doc(title='UART', comment='RX/TX'))",
        "Port(BusType(), 'bus_i', direction=IN)",
        "Signal(ClkType(), 'clk_s', doc=Doc(title='Clock'))",
    ]
    assert [repr(item) for item in mod.params] == []
    assert [repr(item) for item in mod.ports] == [
        "Port(ClkRstAnType(), 'main_i', direction=IN, doc=Doc(title='Clock and Reset'))",
        "Port(UartIoType(), 'uart_i', direction=IN, doc=Doc(title='UART', comment='RX/TX'))",
        "Port(BusType(), 'bus_i', direction=IN)",
    ]
    assert [repr(item) for item in mod.portssignals] == [
        "Port(ClkRstAnType(), 'main_i', direction=IN, doc=Doc(title='Clock and Reset'))",
        "Port(UartIoType(), 'uart_i', direction=IN, doc=Doc(title='UART', comment='RX/TX'))",
        "Port(BusType(), 'bus_i', direction=IN)",
        "Signal(ClkType(), 'clk_s', doc=Doc(title='Clock'))",
    ]
    assert [repr(item) for item in mod.insts] == [
        "<glbl.clk_gate.ClkGateMod(inst='uart/u_clk_gate', libname='glbl', modname='clk_gate')>",
        "<glbl.regf.RegfMod(inst='uart/u_regf', libname='uart', modname='uart_regf')>",
        "<ucdp.modcore.CoreMod(inst='uart/u_core', libname='uart', modname='uart_core')>",
    ]
