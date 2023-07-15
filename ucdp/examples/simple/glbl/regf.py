#
# MIT License
#
# Copyright (c) 2023 nbiotcloud
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
from glbl.bus import BusType

import ucdp

from .clkgate import ClkGateMod

# This is just a simple implementation, which does not reflect all necessary details of a real register file.


@ucdp.frozen
class Field:
    name: str = ucdp.field()
    type_: ucdp.AType = ucdp.field()
    is_readable: bool = ucdp.field(default=False)
    is_writable: bool = ucdp.field(default=False)
    iotype = ucdp.field(factory=ucdp.DynamicStructType, init=False)

    def __attrs_post_init__(self):
        if self.is_readable:
            self.iotype.add("rd", self.type_, ucdp.BWD)
        if self.is_writable:
            self.iotype.add("wr", self.type_, ucdp.FWD)


@ucdp.frozen
class Word:
    name: str = ucdp.field()
    fields = ucdp.field(factory=list, init=False)
    iotype = ucdp.field(factory=ucdp.DynamicStructType, init=False)

    def add_field(self, name, type_, is_readable=False, is_writable=False, route=None):
        field = Field(name, type_, is_readable=is_readable, is_writable=is_writable)
        self.fields.append(field)
        self.iotype.add(name, field.iotype)
        return field


@ucdp.mod()
class RegfMod(ucdp.ATailoredMod):
    """Register File."""

    # Year for File Header Copyright
    copyright_end_year = 2022

    iotype = ucdp.field(init=False)

    @iotype.default
    def _iotype_default(self):
        return ucdp.DynamicStructType()

    def _build(self):
        self.add_port(ucdp.ClkRstAnType(), "")
        self.add_port(BusType(), "bus_i")
        self.add_port(self.iotype, "regf_o")

        ClkGateMod(self, "u_clk_gate")

    def add_word(self, name):
        """Add a word to register file."""
        word = Word(name)
        self.iotype.add(name, word.iotype)
        return word
