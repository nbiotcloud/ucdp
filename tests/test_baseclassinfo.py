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
"""Test Configuration."""

import pydantic

import ucdp as u


def test_example_simple(example_simple):
    """Example."""
    from glbl_lib.clk_gate import ClkGateMod
    from uart_lib.uart import UartMod

    assert tuple(u.get_baseclassinfos(UartMod)) == (
        u.BaseClassInfo(cls=UartMod, libname="uart_lib", modname="uart", clsname="UartMod"),
        u.BaseClassInfo(cls=u.AMod, libname="ucdp", modname="mod", clsname="AMod"),
        u.BaseClassInfo(cls=u.BaseTopMod, libname="ucdp", modname="modbasetop", clsname="BaseTopMod"),
        u.BaseClassInfo(cls=u.BaseMod, libname="ucdp", modname="modbase", clsname="BaseMod"),
        u.BaseClassInfo(cls=u.NamedObject, libname="ucdp", modname="object", clsname="NamedObject"),
        u.BaseClassInfo(cls=u.Object, libname="ucdp", modname="object", clsname="Object"),
        u.BaseClassInfo(cls=pydantic.main.BaseModel, libname="pydantic", modname="main", clsname="BaseModel"),
    )

    assert tuple(u.get_baseclassinfos(UartMod())) == tuple(u.get_baseclassinfos(UartMod))

    assert tuple(u.get_baseclassinfos(ClkGateMod)) == (
        u.BaseClassInfo(cls=ClkGateMod, libname="glbl_lib", modname="clk_gate", clsname="ClkGateMod"),
        u.BaseClassInfo(cls=u.AMod, libname="ucdp", modname="mod", clsname="AMod"),
        u.BaseClassInfo(cls=u.BaseTopMod, libname="ucdp", modname="modbasetop", clsname="BaseTopMod"),
        u.BaseClassInfo(cls=u.BaseMod, libname="ucdp", modname="modbase", clsname="BaseMod"),
        u.BaseClassInfo(cls=u.NamedObject, libname="ucdp", modname="object", clsname="NamedObject"),
        u.BaseClassInfo(cls=u.Object, libname="ucdp", modname="object", clsname="Object"),
        u.BaseClassInfo(cls=pydantic.main.BaseModel, libname="pydantic", modname="main", clsname="BaseModel"),
    )
