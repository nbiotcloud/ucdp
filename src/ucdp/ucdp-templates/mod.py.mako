<%
info = datamodel.info
%>\
"""${info.descr_or_default}."""


from fileliststandard import HdlFileList
from glbl_lib.bus import BusType
% if info.regf:
from glbl_lib.clk_gate import ClkGateMod
from glbl_lib.regf import RegfMod
% endif

import ucdp as u


% if info.is_tb:
class ${info.name_pascalcase}Mod(u.${info.flavour}):
    """${info.descr_or_default}."""

    filelists: u.ClassVar[u.ModFileLists] = (
        HdlFileList(gen="full"),
    )

    def _build(self) -> None:
        dut = self.dut # Design-Under-Test
% else:
class ${info.name_pascalcase}IoType(u.AStructType):
    """${info.name_titlecase} IO."""

    title: str = "${info.name_titlecase}"
    comment: str = "RX/TX"

    def _build(self) -> None:
        self._add("rx", u.BitType(), u.BWD)
        self._add("tx", u.BitType(), u.FWD)


class ${info.name_pascalcase}Mod(u.${info.flavour}):
    """${info.descr_or_default}."""

    filelists: u.ClassVar[u.ModFileLists] = (
        HdlFileList(gen="full"),
    )

    def _build(self) -> None:
        """Build."""
        self.add_port(u.ClkRstAnType(), "main_i")
%   if info.regf:
        self.add_port(${info.name_pascalcase}IoType(), "${info.name_snakecase}_i", route="create(u_core/${info.name_snakecase}_i)", clkrel=u.ASYNC)
%   else:
        self.add_port(${info.name_pascalcase}IoType(), "${info.name_snakecase}_i", clkrel=u.ASYNC)
%   endif:
        self.add_port(BusType(), "bus_i", clkrel="main_clk_i")

%   if info.regf:
        clkgate = ClkGateMod(self, "u_clk_gate")
        clkgate.con("clk_i", "main_clk_i")
        clkgate.con("clk_o", "create(clk_s)")

        regf = RegfMod(self, "u_regf")
        regf.con("main_i", "main_i")
        regf.con("bus_i", "bus_i")

        core = ${info.name_pascalcase}CoreMod(parent=self, name="u_core")

        core.add_port(u.ClkRstAnType(), "main_i")
        core.con("main_clk_i", "clk_s")
        core.con("main_rst_an_i", "main_rst_an_i")
        core.con("create(regf_i)", "u_regf/regf_o")

        word = regf.add_word("ctrl")
        word.add_field("ena", u.EnaType(), is_readable=True, route="u_clk_gate/ena_i")
        word.add_field("strt", u.BitType(), is_writable=True, route="create(u_core/strt_i)")

%   if info.flavour == "ATailoredMod":
    def _build_dep(self):
        """Build Dependent Parts."""

    def _build_final(self):
        """Build Post."""

%   endif

class ${info.name_pascalcase}CoreMod(u.ACoreMod):
    """A Simple ${info.name_titlecase}."""

    filelists: u.ClassVar[u.ModFileLists] = (HdlFileList(gen="inplace"),)

%   endif
% endif
