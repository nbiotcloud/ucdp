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
"""
Clock and Reset Types.

* :any:`ClkType` - Clock
* :any:`RstAType` - Asynchronous Reset (High-Active)
* :any:`RstAnType` - Asynchronous Reset (Low-Active)
* :any:`RstType` - Synchronous Reset (High-Active)
* :any:`ClkRstAnType` - Clock and Async Reset Pair
* :any:`DiffClkType` - Differential Clock
* :any:`DiffClkRstAnType` - Differential Clock and Async Reset
"""

from .clkrelbase import BaseClkRel
from .typebase import AScalarType
from .typeenum import AEnumType
from .typescalar import BitType
from .typestruct import AStructType


class ClkType(BitType):
    """
    Clock Type.

    Single bit used as clock.

    >>> import ucdp as u
    >>> clk = u.ClkType()
    >>> clk
    ClkType()
    >>> clk.width
    1
    """

    title: str = "Clock"


class RstAType(AEnumType):
    """
    Async high-active Reset Type.

    Single bit used as asynchronous reset.

    >>> import ucdp as u
    >>> rst = u.RstAType()
    >>> rst
    RstAType()
    >>> rst.width
    1
    >>> for item in rst.values():
    ...     print(repr(item))
    EnumItem(0, 'inactive', doc=Doc(title='Reset not active'))
    EnumItem(1, 'active', doc=Doc(title='Reset active'))
    """

    keytype: AScalarType = BitType()
    title: str = "Async Reset"
    descr: str = "High-Active"
    comment: str = "Async Reset (High-Active)"

    def _build(self) -> None:
        self._add(0, "inactive", "Reset not active")
        self._add(1, "active", "Reset active")


class RstAnType(AEnumType):
    """
    Async low-active Reset Type.

    Single bit used as asynchronous low-active reset.

    >>> import ucdp as u
    >>> rst = u.RstAnType()
    >>> rst
    RstAnType()
    >>> rst.width
    1
    >>> for item in rst.values():
    ...     print(repr(item))
    EnumItem(0, 'active', doc=Doc(title='Reset active'))
    EnumItem(1, 'inactive', doc=Doc(title='Reset not active'))
    """

    keytype: AScalarType = BitType()
    title: str = "Async Reset"
    descr: str = "Low-Active"
    comment: str = "Async Reset (Low-Active)"

    def _build(self) -> None:
        self._add(0, "active", "Reset active")
        self._add(1, "inactive", "Reset not active")


class RstType(AEnumType):
    """
    Sync Reset.

    Single bit used as synchronous reset.

    >>> import ucdp as u
    >>> rst = u.RstType()
    >>> rst
    RstType()
    >>> rst.width
    1
    >>> for item in rst.values():
    ...     print(repr(item))
    EnumItem(0, 'inactive', doc=Doc(title='Reset not active'))
    EnumItem(1, 'active', doc=Doc(title='Reset active'))
    """

    keytype: AScalarType = BitType()
    title: str = "Synchronous Reset"
    descr: str = "High-Active"

    def _build(self) -> None:
        self._add(0, "inactive", "Reset not active")
        self._add(1, "active", "Reset active")


class ClkRstAnType(AStructType):
    """
    Clock, Async Reset Pair.

    >>> import ucdp as u
    >>> clkrst = u.ClkRstAnType()
    >>> for item in clkrst.values():
    ...     print(repr(item))
    StructItem('clk', ClkType(), doc=Doc(title='Clock'))
    StructItem('rst_an', RstAnType(), doc=Doc(title='Async Reset', descr='Low-Active', comment='Async Reset ...'))
    """

    title: str = "Clock and Reset"
    clkrel: BaseClkRel | None = None

    def _build(self) -> None:
        self._add("clk", ClkType(), clkrel=self.clkrel)
        self._add("rst_an", RstAnType())


class DiffClkType(AStructType):
    """
    Differential Clock.

    >>> import ucdp as u
    >>> diffclk = u.DiffClkType()
    >>> for item in diffclk.values():
    ...     print(repr(item))
    StructItem('p', ClkType(), doc=Doc(title='Clock'))
    StructItem('n', ClkType(default=1), doc=Doc(title='Inverted Clock'))
    """

    title: str = "Differential Clock"
    clkrel: BaseClkRel | None = None

    def _build(self) -> None:
        self._add("p", ClkType(default=0), clkrel=self.clkrel)
        self._add("n", ClkType(default=1), title="Inverted Clock", clkrel=self.clkrel)


class DiffClkRstAnType(AStructType):
    """
    Differential Clock and Reset.

    >>> import ucdp as u
    >>> diffclkrst = u.DiffClkRstAnType()
    >>> for item in diffclkrst.values():
    ...     print(repr(item))
    StructItem('clk', DiffClkType(), doc=Doc(title='Differential Clock'))
    StructItem('rst_an', RstAnType(), doc=Doc(title='Async Reset', descr='Low-Active', comment='Async Reset ...'))
    """

    title: str = "Differential Clock and Reset"
    clkrel: BaseClkRel | None = None

    def _build(self) -> None:
        self._add("clk", DiffClkType(clkrel=self.clkrel))
        self._add("rst_an", RstAnType())
