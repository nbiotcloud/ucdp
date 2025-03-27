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
Hardware Module.
"""

from .modbasetop import BaseTopMod
from .modutil import get_modname, get_topmodname


class AMod(BaseTopMod):
    """
    A Normal Module With Parameters And A Fixed Number Of Ports (maybe `ifdef` encapsulated).

    See [BaseMod][ucdp.modbase.BaseMod] for arguments, attributes and details.

    All module parameter, local parameter, ports, signals and submodules
    **MUST** be added and created within the `_build` method:


    ???+ Example "AMod Build Examples"
        _build(self):

            >>> import ucdp as u
            >>> class AdderMod(u.AMod):
            ...
            ...     def _build(self) -> None:
            ...         width_p = self.add_param(u.IntegerType(default=16), 'width_p')
            ...         datatype = u.UintType(width_p)
            ...         self.add_port(datatype, "a_i")
            ...         self.add_port(datatype, "b_i")
            ...         self.add_port(datatype, "y_o")

    Warning:
        There is no other build method on purpose!
    """

    @property
    def modname(self) -> str:
        """Module Name."""
        return get_modname(self.__class__)

    @property
    def topmodname(self) -> str:
        """Top Module Name."""
        return get_topmodname(self.__class__)
