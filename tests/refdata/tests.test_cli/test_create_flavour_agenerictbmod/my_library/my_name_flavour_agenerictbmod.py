"""My Name Flavour Agenerictbmod Module."""


from fileliststandard import HdlFileList
from glbl_lib.bus import BusType
from glbl_lib.clk_gate import ClkGateMod
from glbl_lib.regf import RegfMod

import ucdp as u


class MyNameFlavourAgenerictbmodMod(u.AGenericTbMod):
    """My Name Flavour Agenerictbmod Module."""

    filelists: u.ClassVar[u.ModFileLists] = (
        HdlFileList(gen="full"),
    )

    def _build(self) -> None:
        dut = self.dut # Design-Under-Test
