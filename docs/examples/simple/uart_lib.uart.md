# Module `uart_lib.uart`

Python: `uart_lib.uart.UartMod`

A Simple UART.

## Parameters

None

## Ports

| Name                     | Type                   |
| ----                     | ----                   |
| `main_i` (`IN`)          | `ClkRstAnType()`       |
| . `main_clk_i` (`IN`)    | . `ClkType()`          |
| . `main_rst_an_i` (`IN`) | . `RstAnType()`        |
| `uart_i` (`IN`)          | `UartIoType()`         |
| . `uart_rx_o` (`OUT`)    | . `BitType()`          |
| . `uart_tx_i` (`IN`)     | . `BitType()`          |
| `bus_i` (`IN`)           | `BusType()`            |
| . `bus_trans_i` (`IN`)   | . `TransType()`        |
| . `bus_addr_i` (`IN`)    | . `AddrType(32)`       |
| . `bus_write_i` (`IN`)   | . `WriteType()`        |
| . `bus_wdata_i` (`IN`)   | . `DataType(32)`       |
| . `bus_ready_o` (`OUT`)  | . `BitType(default=1)` |
| . `bus_resp_o` (`OUT`)   | . `RespType()`         |
| . `bus_rdata_o` (`OUT`)  | . `DataType(32)`       |

## Files

### Filelist `hdl`

| Name                 | Type                                                                        |
| ----                 | ----                                                                        |
| `gen`                | `full`                                                                      |
| `filepaths`          | `$PRJROOT/uart_lib/uart/rtl/uart.sv`                                        |
| `template_filepaths` | `/Users/iccode17/projects/ucdp/src/ucdp/examples/simple/uart_lib/main.mako` |

### Filelist `header`

| Name                 | Type                                                                       |
| ----                 | ----                                                                       |
| `filepaths`          | `$PRJROOT/uart.hpp`                                                        |
| `template_filepaths` | `/Users/iccode17/projects/ucdp/src/ucdp/examples/simple/uart_lib/hpp.mako` |
