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
"""Test Module Defines."""

from test2ref import assert_refdata

import ucdp as u


class IpMod(u.AMod):
    """IP."""

    def _build(self):
        self.add_port(u.BitType(), "d_i")
        self.add_port(u.BitType(), "e_i", ifdefs=("HAS_E", "!NO_EXTRA"))
        self.add_port(u.BitType(), "f_i", ifdefs=("!HAS_E", "!NO_EXTRA"))
        self.add_port(u.BitType(), "d_o")


class TopMod(u.AMod):
    """Top."""

    def _build(self):
        IpMod(self, "u_a", defines={"HAS_E": None})
        IpMod(self, "u_b")
        IpMod(self, "u_c", defines={"HAS_E": 1, "NO_EXTRA": 1})
        IpMod(self, "u_d", defines={})


def test_defines(tmp_path, capsys):
    """Test Defines."""
    top = TopMod()
    for inst in top.insts:
        print(inst)
        for port in inst.ports:
            print(" ", repr(port))

    assert_refdata(test_defines, tmp_path, capsys=capsys)
