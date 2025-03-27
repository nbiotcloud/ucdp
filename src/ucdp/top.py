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

"""Top."""

from .iterutil import Names
from .modbase import BaseMod
from .modgenerictb import AGenericTbMod
from .moditer import FilterFunc, MaxLevel, ModPostIter, ModPreIter, StopFunc, get_mod, get_mods
from .modtopref import TopModRef
from .object import _CACHED_INSTANCES, Field, Object


class Top(Object):
    """
    Top Module Reference.

    Attributes:
        ref: Top Module Reference
        mod: Top Module Instance
    """

    ref: TopModRef = Field(repr=False)
    mod: BaseMod

    @staticmethod
    def from_mod(mod: BaseMod) -> "Top":
        """Create from Module."""
        if isinstance(mod, AGenericTbMod):
            ref = TopModRef(tb=mod.get_modref(), top=mod.dut.get_modref())
        else:
            ref = TopModRef(top=mod.get_modref())
        return Top(ref=ref, mod=mod)

    def iter(
        self,
        filter_: FilterFunc | None = None,
        stop: StopFunc | None = None,
        maxlevel: MaxLevel | None = None,
        unique: bool = False,
        post: bool = False,
    ):
        """
        Iterate Over All Modules.

        Args:
            filter_: function called with every `mod` as argument, `mod` is returned if `True`.
            stop: stop iteration at `mod` if `stop` function returns `True` for `mod`.
            maxlevel (int): maximum descending in the mod hierarchy.
            unique (bool): Just return module once and **NOT** all instances of it.
            post: Post-Order Iteration Strategy instead of Pre-Order Iteration Strategy.
        """
        if post:
            return ModPostIter(self.mod, filter_=filter_, stop=stop, maxlevel=maxlevel, unique=unique)
        return ModPreIter(self.mod, filter_=filter_, stop=stop, maxlevel=maxlevel, unique=unique)

    def get_mods(self, namepats: Names | None = None, unique: bool = False, base: bool = False):
        """
        Return all modules matching `namepats`.

        Iterate top and all its submodules and return matching ones.

        Keyword Args:
            namepats: Iterable with name pattern (including `*` and `?`) or comma separated string
            unique (bool): Just return every module once.
            base: namepats must match against module `basequalnames` instead of `qual_name`.
        """
        return get_mods(self.mod, namepats=namepats, unique=unique, base=base)

    def get_mod(self, namepats: Names, base: bool = False):
        """
        Return the one and just the one hardware module matching `namepats`.

        Iterate over `mod` and all its submodules and return matching one.

        Keyword Args:
            namepats: Iterable with name pattern (including `*` and `?`) or comma separated string
            base: namepats must match against module `basequalnames` instead of `qual_name`.
        """
        return get_mod(self.mod, namepats, base=base)

    def get_stat(self) -> dict[str, int]:
        """Get Statistics."""
        return {
            "Modules": len(self.get_mods(unique=True)),
            "Module-Instances": len(self.get_mods()),
            "LightObjects": _CACHED_INSTANCES,
        }
