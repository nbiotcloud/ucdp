"""My Name Flavour Atailoredmod Module."""


from fileliststandard import HdlFileList
from glbl_lib.bus import BusType
from glbl_lib.clk_gate import ClkGateMod
from glbl_lib.regf import RegfMod

import ucdp as u


class MyNameFlavourAtailoredmodIoType(u.AStructType):
    """My Name Flavour Atailoredmod IO."""

    title: str = "My Name Flavour Atailoredmod"
    comment: str = "RX/TX"

    def _build(self) -> None:
        self._add("rx", u.BitType(), u.BWD)
        self._add("tx", u.BitType(), u.FWD)


class MyNameFlavourAtailoredmodMod(u.ATailoredMod):
    """My Name Flavour Atailoredmod Module."""

    filelists: u.ClassVar[u.ModFileLists] = (
        HdlFileList(gen="full"),
    )

    def _build(self) -> None:
        """Build."""
        self.add_port(u.ClkRstAnType(), "main_i")
        self.add_port(MyNameFlavourAtailoredmodIoType(), "my_name_flavour_atailoredmod_i", route="create(u_core/my_name_flavour_atailoredmod_i)", clkrel=u.ASYNC)
        self.add_port(BusType(), "bus_i", clkrel="main_clk_i")

        clkgate = ClkGateMod(self, "u_clk_gate")
        clkgate.con("clk_i", "main_clk_i")
        clkgate.con("clk_o", "create(clk_s)")

        regf = RegfMod(self, "u_regf")
        regf.con("main_i", "main_i")
        regf.con("bus_i", "bus_i")

        core = MyNameFlavourAtailoredmodCoreMod(parent=self, name="u_core")

        core.add_port(u.ClkRstAnType(), "main_i")
        core.con("main_clk_i", "clk_s")
        core.con("main_rst_an_i", "main_rst_an_i")
        core.con("create(regf_i)", "u_regf/regf_o")

        word = regf.add_word("ctrl")
        word.add_field("ena", u.EnaType(), is_readable=True, route="u_clk_gate/ena_i")
        word.add_field("strt", u.BitType(), is_writable=True, route="create(u_core/strt_i)")

    def _build_dep(self):
        """Build Dependent Parts."""

    def _build_final(self):
        """Build Post."""


class MyNameFlavourAtailoredmodCoreMod(u.ACoreMod):
    """A Simple My Name Flavour Atailoredmod."""

    filelists: u.ClassVar[u.ModFileLists] = (HdlFileList(gen="inplace"),)

