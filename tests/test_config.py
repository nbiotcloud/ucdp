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

"""Type Testing."""
from humannum import Bytes, bytes_, hex_
from pytest import raises

import ucdp


def test_config():
    """Test Configuration."""

    @ucdp.config
    class MyConfig(ucdp.AConfig):
        """My Configuration."""

        mem_baseaddr = ucdp.field(converter=hex_)  # required without default
        ram_size = ucdp.field(converter=bytes_, default="256 KB")  # required with default
        rom_size = ucdp.field(converter=ucdp.util.opt(bytes_), default=None)  # optional
        feature: bool = ucdp.field(default=False)  # boolean

    with raises(ValueError):
        MyConfig("stupid name", mem_baseaddr="0xA000")

    config = MyConfig("configname", mem_baseaddr="0xA000")
    assert config.name == "configname"
    assert config.mem_baseaddr == 0xA000
    assert config.ram_size == Bytes("256 KB")
    assert config.rom_size is None
    assert not config.feature
