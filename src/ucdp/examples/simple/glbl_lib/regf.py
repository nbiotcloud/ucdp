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

"""A Simplified Register File."""

from fileliststandard import HdlFileList
from tabulate import tabulate

import ucdp as u

from .bus import BusType
from .clk_gate import ClkGateMod


class Field(u.NamedLightObject, u.ABuildProduct):
    """Bit Field."""

    type_: u.BaseType
    is_readable: bool = False
    is_writable: bool = True
    iotype: u.DynamicStructType = u.Field(default_factory=u.DynamicStructType, init=False)

    def _build(self) -> None:
        if self.is_readable:
            self.iotype.add("rd", self.type_, u.BWD)
        if self.is_writable:
            self.iotype.add("wr", self.type_, u.FWD)


class Word(u.NamedObject):
    """Word with Bit Fields."""

    name: str
    fields: u.Namespace = u.Field(default_factory=u.Namespace, init=False)
    iotype: u.DynamicStructType = u.Field(default_factory=u.DynamicStructType, init=False)

    def add_field(self, name: str, type_: u.BaseType, is_readable: bool = False, is_writable: bool = False, route=None):
        """Add Bit Field."""
        field = Field(name=name, type_=type_, is_readable=is_readable, is_writable=is_writable)
        self.fields.add(field)
        self.iotype.add(name, field.iotype)
        return field


class RegfMod(u.ATailoredMod):
    """Register File."""

    filelists: u.ClassVar[u.ModFileLists] = (HdlFileList(gen="full"),)
    words: u.Namespace = u.Field(default_factory=u.Namespace)

    iotype: u.DynamicStructType = u.Field(default_factory=u.DynamicStructType, init=False)
    tags: u.ClassVar[u.ModTags] = {"bus"}

    def _build(self) -> None:
        self.add_port(u.ClkRstAnType(), "main_i")
        self.add_port(BusType(), "bus_i")
        self.add_port(self.iotype, "regf_o")

        ClkGateMod(self, "u_clk_gate")

    def add_word(self, name):
        """Add a word to register file."""
        word = Word(name=name)
        self.iotype.add(name, word.iotype)
        self.words.add(word)
        return word

    def get_overview(self) -> str:
        """Overview."""
        data = []
        for word in self.words:
            data.append((word.name, "", ""))
            for field in word.fields:
                data.append(("", f".{field.name}", str(field.type_)))  # noqa: PERF401
        headers = ("Word", "Field", "Type")
        return tabulate(data, headers=headers)
