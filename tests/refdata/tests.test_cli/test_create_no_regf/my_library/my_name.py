"""My Name Module."""
"""AMod. """


from fileliststandard import HdlFileList
from glbl_lib.bus import BusType

import ucdp as u


class MyNameIoType(u.AStructType):
    """My Name IO."""

    title: str = "My Name"
    comment: str = "RX/TX"

    def _build(self) -> None:
        self._add("rx", u.BitType(), u.BWD)
        self._add("tx", u.BitType(), u.FWD)


class MyNameMod(u.AMod):
    """My Name Module."""

    filelists: u.ClassVar[u.ModFileLists] = (
        HdlFileList(gen="full"),
    )

    def _build(self) -> None:
        self.add_port(u.ClkRstAnType(), "main_i")
        self.add_port(MyNameIoType(), "my_name_i", clkrel=u.ASYNC)
        self.add_port(BusType(), "bus_i", clkrel="main_clk_i")

