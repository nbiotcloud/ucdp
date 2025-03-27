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
"""Test Configuration."""


def test_example_simple(example_simple):
    """Basic Testing."""
    from uart_lib.uart import UartMod

    mod = UartMod()

    assert mod.basename == "uart"
    assert mod.modname == "uart"
    assert mod.libname == "uart_lib"
    assert mod.qualname == "uart_lib.uart"
    assert [repr(item) for item in mod.namespace] == [
        "Port(ClkRstAnType(), 'main_i', direction=IN, doc=Doc(title='Clock and Reset'))",
        "Port(UartIoType(), 'uart_i', direction=IN, doc=Doc(title='UART', comment='RX/TX'), clkrel=ASYNC)",
        "Port(BusType(), 'bus_i', direction=IN, clkrel=ClkRel(clk=Port(ClkType(), "
        "'main_clk_i', direction=IN, doc=Doc(title='Clock'))))",
        "Signal(ClkType(), 'clk_s', doc=Doc(title='Clock'))",
        "Signal(DynamicStructType(), 'core_regf_i_s', direction=OUT)",
    ]
    assert [repr(item) for item in mod.params] == []
    assert [repr(item) for item in mod.ports] == [
        "Port(ClkRstAnType(), 'main_i', direction=IN, doc=Doc(title='Clock and Reset'))",
        "Port(UartIoType(), 'uart_i', direction=IN, doc=Doc(title='UART', comment='RX/TX'), clkrel=ASYNC)",
        "Port(BusType(), 'bus_i', direction=IN, clkrel=ClkRel(clk=Port(ClkType(), "
        "'main_clk_i', direction=IN, doc=Doc(title='Clock'))))",
    ]
    assert [repr(item) for item in mod.ports.leveliter()] == [
        "(0, Port(ClkRstAnType(), 'main_i', direction=IN, doc=Doc(title='Clock and Reset')))",
        "(1, Port(ClkType(), 'main_clk_i', direction=IN, doc=Doc(title='Clock')))",
        "(1, Port(RstAnType(), 'main_rst_an_i', direction=IN, doc=Doc(title='Async "
        "Reset', descr='Low-Active', comment='Async Reset (Low-Active)')))",
        "(0, Port(UartIoType(), 'uart_i', direction=IN, doc=Doc(title='UART', comment='RX/TX'), clkrel=ASYNC))",
        "(1, Port(BitType(), 'uart_rx_o', direction=OUT, clkrel=ASYNC))",
        "(1, Port(BitType(), 'uart_tx_i', direction=IN, clkrel=ASYNC))",
        "(0, Port(BusType(), 'bus_i', direction=IN, "
        "clkrel=ClkRel(clk=Port(ClkType(), 'main_clk_i', direction=IN, "
        "doc=Doc(title='Clock')))))",
        "(1, Port(TransType(), 'bus_trans_i', direction=IN, "
        "clkrel=ClkRel(clk=Port(ClkType(), 'main_clk_i', direction=IN, "
        "doc=Doc(title='Clock')))))",
        "(1, Port(AddrType(32), 'bus_addr_i', direction=IN, "
        "clkrel=ClkRel(clk=Port(ClkType(), 'main_clk_i', direction=IN, "
        "doc=Doc(title='Clock')))))",
        "(1, Port(WriteType(), 'bus_write_i', direction=IN, "
        "clkrel=ClkRel(clk=Port(ClkType(), 'main_clk_i', direction=IN, "
        "doc=Doc(title='Clock')))))",
        "(1, Port(DataType(32), 'bus_wdata_i', direction=IN, "
        "clkrel=ClkRel(clk=Port(ClkType(), 'main_clk_i', direction=IN, "
        "doc=Doc(title='Clock')))))",
        "(1, Port(BitType(default=1), 'bus_ready_o', direction=OUT, "
        "doc=Doc(descr='Transfer is finished on HIGH.'), "
        "clkrel=ClkRel(clk=Port(ClkType(), 'main_clk_i', direction=IN, "
        "doc=Doc(title='Clock')))))",
        "(1, Port(RespType(), 'bus_resp_o', direction=OUT, "
        "clkrel=ClkRel(clk=Port(ClkType(), 'main_clk_i', direction=IN, "
        "doc=Doc(title='Clock')))))",
        "(1, Port(DataType(32), 'bus_rdata_o', direction=OUT, "
        "clkrel=ClkRel(clk=Port(ClkType(), 'main_clk_i', direction=IN, "
        "doc=Doc(title='Clock')))))",
    ]
    assert [repr(item) for item in mod.portssignals] == [
        "Port(ClkRstAnType(), 'main_i', direction=IN, doc=Doc(title='Clock and Reset'))",
        "Port(UartIoType(), 'uart_i', direction=IN, doc=Doc(title='UART', comment='RX/TX'), clkrel=ASYNC)",
        "Port(BusType(), 'bus_i', direction=IN, clkrel=ClkRel(clk=Port(ClkType(), "
        "'main_clk_i', direction=IN, doc=Doc(title='Clock'))))",
        "Signal(ClkType(), 'clk_s', doc=Doc(title='Clock'))",
        "Signal(DynamicStructType(), 'core_regf_i_s', direction=OUT)",
    ]
    assert [repr(item) for item in mod.insts] == [
        "<glbl_lib.clk_gate.ClkGateMod(inst='uart/u_clk_gate', libname='glbl_lib', modname='clk_gate')>",
        "<glbl_lib.regf.RegfMod(inst='uart/u_regf', libname='uart_lib', modname='uart_regf')>",
        "<uart_lib.uart.UartCoreMod(inst='uart/u_core', libname='uart_lib', modname='uart_core')>",
    ]


def test_example_param(example_param):
    """Param Example."""
    from param_lib.param import ParamMod

    mod = ParamMod()
    assert [repr(item) for item in mod.namespace] == [
        "Param(IntegerType(default=10), 'param_p')",
        "Param(IntegerType(default=Log2Expr(Op(Param(IntegerType(default=10), "
        "'param_p'), '+', ConstExpr(IntegerType(default=1))))), 'width_p')",
        "Param(IntegerType(default=Param(IntegerType(default=10), 'param_p')), 'default_p')",
        "Port(UintType(Param(IntegerType(default=10), 'param_p')), 'data_i', direction=IN)",
        "Port(UintType(Param(IntegerType(default=Log2Expr(Op(Param(IntegerType(default=10), "
        "'param_p'), '+', ConstExpr(IntegerType(default=1))))), 'width_p')), "
        "'cnt_o', direction=OUT)",
        "Const(UintType(Param(IntegerType(default=10), 'param_p'), "
        "default=Param(IntegerType(default=Param(IntegerType(default=10), "
        "'param_p')), 'default_p')), 'const_c')",
    ]
