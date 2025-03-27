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
"""Bus Infrastructure."""

import ucdp as u


class AddrType(u.UintType):
    """Address Type."""

    def __init__(self):
        super().__init__(width=32)


class DataType(u.UintType):
    """Data Type."""

    def __init__(self, width=32, default=0):
        super().__init__(width=width, default=default)


class TransType(u.AEnumType):
    """Transport Type."""

    keytype: u.AScalarType = u.UintType(width=2)

    def _build(self) -> None:
        self._add(0, "idle", "No transfer.")
        self._add(1, "busy", "Idle cycle within transfer.")
        self._add(2, "nonseq", "Single transfer or first transfer of a burst.")
        self._add(3, "seq", "Consecutive transfers of a burst.")


class WriteType(u.AEnumType):
    """Write Type."""

    keytype: u.AScalarType = u.BitType()

    def _build(self) -> None:
        self._add(0, "read", "Read operation.")
        self._add(1, "write", "Write operation.")


class RespType(u.AEnumType):
    """Response Type."""

    keytype: u.AScalarType = u.BitType()

    def _build(self) -> None:
        self._add(0, "okay", "OK.")
        self._add(1, "error", "Error.")


class BusType(u.AStructType):
    """The Bus Type."""

    def _build(self) -> None:
        # FWD
        self._add("trans", TransType())
        self._add("addr", AddrType())
        self._add("write", WriteType())
        self._add("wdata", DataType())
        # BWD
        self._add("ready", u.BitType(default=1), u.BWD, descr="Transfer is finished on HIGH.")
        self._add("resp", RespType(), u.BWD)
        self._add("rdata", DataType(), u.BWD)
