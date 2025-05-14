"""My Name No Regf Module."""


from fileliststandard import HdlFileList
from glbl_lib.bus import BusType

import ucdp as u


class MyNameNoRegfIoType(u.AStructType):
    """My Name No Regf IO."""

    title: str = "My Name No Regf"
    comment: str = "RX/TX"

    def _build(self) -> None:
        self._add("rx", u.BitType(), u.BWD)
        self._add("tx", u.BitType(), u.FWD)


class MyNameNoRegfMod(u.AMod):
    """My Name No Regf Module."""

    filelists: u.ClassVar[u.ModFileLists] = (
        HdlFileList(gen="full"),
    )

    def _build(self) -> None:
        """Build."""
        self.add_port(u.ClkRstAnType(), "main_i")
        self.add_port(MyNameNoRegfIoType(), "my_name_no_regf_i", clkrel=u.ASYNC)
        self.add_port(BusType(), "bus_i", clkrel="main_clk_i")

