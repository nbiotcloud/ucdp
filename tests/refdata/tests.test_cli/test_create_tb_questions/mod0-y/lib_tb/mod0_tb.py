"""Mod0 Tb Module."""


from fileliststandard import HdlFileList
from glbl_lib.bus import BusType
from glbl_lib.clk_gate import ClkGateMod
from glbl_lib.regf import RegfMod

import ucdp as u


class Mod0TbMod(u.ATbMod):
    """Mod0 Tb Module."""

    filelists: u.ClassVar[u.ModFileLists] = (
        HdlFileList(gen="full"),
    )

    def _build(self) -> None:
        dut = self.dut # Design-Under-Test
