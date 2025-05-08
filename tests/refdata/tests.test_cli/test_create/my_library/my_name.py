"""My Name Example."""

from fileliststandard import HdlFileList
from glbl_lib.bus import BusType  # (2)
from glbl_lib.clk_gate import ClkGateMod  # (3)
from glbl_lib.regf import RegfMod  # (4)

import ucdp as u  # (1)


class MyNameIoType(u.AStructType):
    """My Name IO."""

    title: str = "My Name"
    comment: str = "RX/TX"

    def _build(self) -> None:
        self._add("rx", u.BitType(), u.BWD)  # (5)
        self._add("tx", u.BitType(), u.FWD)  # (6)


class MyNameMod(u.AMod):
    """A Simple My Name."""

    filelists: u.ClassVar[u.ModFileLists] = (
        HdlFileList(gen="full"),
        u.ModFileList(
            name="header",
            filepaths=("$PRJROOT/{mod.modname}.hpp"),
            template_filepaths=("hpp.mako"),
        ),
    )

    tags: u.ClassVar[u.ModTags] = {"intf"}

    def _build(self) -> None:
        self.add_port(u.ClkRstAnType(), "main_i")
        self.add_port(MyNameIoType(), "my_name_i", route="create(u_core/my_name_i)", clkrel=u.ASYNC)
        self.add_port(BusType(), "bus_i", clkrel="main_clk_i")

        clkgate = ClkGateMod(self, "u_clk_gate")
        clkgate.con("clk_i", "main_clk_i")
        clkgate.con("clk_o", "create(clk_s)")

        regf = RegfMod(self, "u_regf")
        regf.con("main_i", "main_i")
        regf.con("bus_i", "bus_i")

        core = MyNameCoreMod(parent=self, name="u_core")

        core.add_port(u.ClkRstAnType(), "main_i")
        core.con("main_clk_i", "clk_s")
        core.con("main_rst_an_i", "main_rst_an_i")
        core.con("create(regf_i)", "u_regf/regf_o")

        word = regf.add_word("ctrl")
        word.add_field("ena", u.EnaType(), is_readable=True, route="u_clk_gate/ena_i")
        word.add_field("strt", u.BitType(), is_writable=True, route="create(u_core/strt_i)")


class MyNameCoreMod(u.ACoreMod):
    """A Simple My Name."""

    filelists: u.ClassVar[u.ModFileLists] = (HdlFileList(gen="inplace"),)
