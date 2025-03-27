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
Module Iterator.

Module Iteration Strategies:

* :any:`ModPreIter` - yield top module **before** the child-modules.
* :any:`ModPostIter` - yield top module **after** the child-modules.
"""

from abc import abstractmethod
from collections.abc import Callable, Iterable, Iterator
from itertools import chain
from typing import TypeAlias

import uniquer

from .iterutil import Names, namefilter
from .modbase import BaseMod
from .object import Object

FilterFunc: TypeAlias = Callable[[BaseMod], bool]
StopFunc: TypeAlias = Callable[[BaseMod], bool]
MaxLevel: TypeAlias = int


def _no_filter(mod: BaseMod):
    return True


def _no_stop(mod: BaseMod):
    return False


class BaseModIter(Object):
    """Base Class for Module Iterators."""

    mod: BaseMod
    filter_: FilterFunc | None = None
    stop: StopFunc | None = None
    stop_insts: StopFunc | None = None
    maxlevel: MaxLevel | None = None
    unique: bool = False

    def __init__(self, mod: BaseMod, **kwargs):
        super().__init__(mod=mod, **kwargs)  # type: ignore[call-arg]

    def __iter__(self):
        mod = self.mod
        filter_ = self.filter_ or _no_filter
        stop = self.stop or _no_stop
        stop_insts = self.stop_insts or _no_stop
        maxlevel = self.maxlevel or -1
        iter_ = self._iter([mod], filter_, stop, stop_insts, maxlevel - 1)
        if self.unique:
            iter_ = uniquemods(iter_)
        return iter_

    @staticmethod
    @abstractmethod
    def _iter(
        mods: Iterable[BaseMod], filter_: FilterFunc, stop: StopFunc, stop_insts: StopFunc, maxlevel: MaxLevel
    ) -> Iterator[BaseMod]:
        pass  # pragma: no cover


class ModPreIter(BaseModIter):
    """

    Iterate over module hierarchy starting at `mod`, using the pre-order strategy.

    Yield top module **before** the child-modules.

    Attributes:
        filter_: function called with every `mod` as argument, `mod` is returned if `True`.
        stop: stop iteration at `mod` if `stop` function returns `True` for `mod`.
        maxlevel (int): maximum descending in the mod hierarchy.
        unique (bool): Just return module once.

    ??? Example "Module Pre Iterator Examples"
        pre-order strategy Examples.

            >>> import ucdp as u
            >>> class CMod(u.AMod):
            ...     def _build(self) -> None:
            ...         pass
            >>> class EMod(u.AMod):
            ...     def _build(self) -> None:
            ...         pass
            >>> class AMod(u.AMod):
            ...     def _build(self) -> None:
            ...         pass
            >>> class DMod(u.AMod):
            ...     def _build(self) -> None:
            ...         CMod(self, "c")
            ...         EMod(self, "e")
            >>> class BMod(u.AMod):
            ...     def _build(self) -> None:
            ...         AMod(self, "a")
            ...         DMod(self, "d")
            >>> class HMod(u.AMod):
            ...     def _build(self) -> None:
            ...         pass
            >>> class IMod(u.AMod):
            ...     def _build(self) -> None:
            ...         HMod(self, "h")
            >>> class GMod(u.AMod):
            ...     def _build(self) -> None:
            ...         IMod(self, "i")
            >>> class FMod(u.AMod):
            ...     def _build(self) -> None:
            ...         BMod(self, "b")
            ...         GMod(self, "g")

            >>> f = FMod(None, "f")
            >>> [mod.name for mod in ModPreIter(f)]
            ['f', 'b', 'a', 'd', 'c', 'e', 'g', 'i', 'h']
            >>> [mod.name for mod in ModPreIter(f, maxlevel=3)]
            ['f', 'b', 'a', 'd', 'g', 'i']
            >>> [mod.name for mod in ModPreIter(f, maxlevel=3, filter_=lambda n: n.name not in 'eg')]
            ['f', 'b', 'a', 'd', 'i']
            >>> [mod.name for mod in ModPreIter(f, maxlevel=3, filter_=lambda n: n.name not in 'eg',
            ...                                 stop=lambda n: n.name == 'd')]
            ['f', 'b', 'a', 'i']
            >>> [mod.name for mod in ModPreIter(f, maxlevel=3, stop=lambda n: n.name == 'd')]
            ['f', 'b', 'a', 'g', 'i']
            >>> [mod.name for mod in ModPreIter(f, filter_=lambda n: n.name not in 'eg')]
            ['f', 'b', 'a', 'd', 'c', 'i', 'h']
            >>> [mod.name for mod in ModPreIter(f, stop=lambda n: n.name == 'd')]
            ['f', 'b', 'a', 'g', 'i', 'h']
            >>> [mod.name for mod in ModPreIter(f, filter_=lambda n: n.name not in 'eg', stop=lambda n: n.name == 'd')]
            ['f', 'b', 'a', 'i', 'h']
            >>> [mod.name for mod in ModPreIter(f)]
            ['f', 'b', 'a', 'd', 'c', 'e', 'g', 'i', 'h']
            >>> [mod.modname for mod in ModPreIter(f, unique=True)]
            ['f', 'b', 'a', 'd', 'c', 'e', 'g', 'i', 'h']
            >>> [mod.name for mod in ModPreIter(f, stop_insts=lambda n: n.name == 'b')]
            ['f', 'b', 'g', 'i', 'h']
    """

    @staticmethod
    def _iter(
        mods: Iterable[BaseMod], filter_: FilterFunc, stop: StopFunc, stop_insts: StopFunc, maxlevel: MaxLevel
    ) -> Iterator[BaseMod]:
        # TODO: heap impl
        for mod in mods:
            if stop(mod):
                continue
            if filter_(mod):
                yield mod
            if not stop_insts(mod) and maxlevel:
                yield from ModPreIter._iter(mod.insts, filter_, stop, stop_insts, maxlevel - 1)


class ModPostIter(BaseModIter):
    """
    Iterate over module hierarchy starting at `mod`, using the post-order strategy.

    Yield top module **after** the child-modules.

    Attributes:
        filter_ (FilterFunc): function called with every `mod` as argument, `mod` is returned if `True`.
        stop (StopFunc): stop iteration at `mod` if `stop` function returns `True` for `mod`.
        maxlevel (int): maximum descending in the mod hierarchy.
        unique (bool): Just return module once.

    ??? Example "Module Post Iterator Examples"
        pre-order strategy Examples.

            >>> import ucdp as u
            >>> class CMod(u.AMod):
            ...     def _build(self) -> None:
            ...         pass
            >>> class EMod(u.AMod):
            ...     def _build(self) -> None:
            ...         pass
            >>> class AMod(u.AMod):
            ...     def _build(self) -> None:
            ...         pass
            >>> class DMod(u.AMod):
            ...     def _build(self) -> None:
            ...         CMod(self, "c")
            ...         EMod(self, "e")
            >>> class BMod(u.AMod):
            ...     def _build(self) -> None:
            ...         AMod(self, "a")
            ...         DMod(self, "d")
            >>> class HMod(u.AMod):
            ...     def _build(self) -> None:
            ...         pass
            >>> class IMod(u.AMod):
            ...     def _build(self) -> None:
            ...         HMod(self, "h")
            >>> class GMod(u.AMod):
            ...     def _build(self) -> None:
            ...         IMod(self, "i")
            >>> class FMod(u.AMod):
            ...     def _build(self) -> None:
            ...         BMod(self, "b")
            ...         GMod(self, "g")

            >>> f = FMod(None, "f")
            >>> [mod.name for mod in ModPostIter(f)]
            ['a', 'c', 'e', 'd', 'b', 'h', 'i', 'g', 'f']
            >>> [mod.name for mod in ModPostIter(f, maxlevel=3)]
            ['a', 'd', 'b', 'i', 'g', 'f']
            >>> [mod.name for mod in ModPostIter(f, maxlevel=3, filter_=lambda n: n.name not in 'eg')]
            ['a', 'd', 'b', 'i', 'f']
            >>> [mod.name for mod in ModPostIter(f, maxlevel=3, filter_=lambda n: n.name not in 'eg',
            ...                                  stop=lambda n: n.name == 'd')]
            ['a', 'b', 'i', 'f']
            >>> [mod.name for mod in ModPostIter(f, maxlevel=3, stop=lambda n: n.name == 'd')]
            ['a', 'b', 'i', 'g', 'f']
            >>> [mod.name for mod in ModPostIter(f, filter_=lambda n: n.name not in 'eg')]
            ['a', 'c', 'd', 'b', 'h', 'i', 'f']
            >>> [mod.name for mod in ModPostIter(f, stop=lambda n: n.name == 'd')]
            ['a', 'b', 'h', 'i', 'g', 'f']
            >>> [mod.name for mod in ModPostIter(f, filter_=lambda n: n.name not in 'eg', stop=lambda n: n.name == 'd')]
            ['a', 'b', 'h', 'i', 'f']
            >>> [mod.name for mod in ModPostIter(f)]
            ['a', 'c', 'e', 'd', 'b', 'h', 'i', 'g', 'f']
            >>> [mod.modname for mod in ModPostIter(f, unique=True)]
            ['a', 'c', 'e', 'd', 'b', 'h', 'i', 'g', 'f']
            >>> [mod.name for mod in ModPostIter(f, stop_insts=lambda n: n.name == 'b')]
            ['b', 'h', 'i', 'g', 'f']
    """

    @staticmethod
    def _iter(
        mods: Iterable[BaseMod], filter_: FilterFunc, stop: StopFunc, stop_insts: StopFunc, maxlevel: MaxLevel
    ) -> Iterator[BaseMod]:
        # TODO: heap impl
        for mod in mods:
            if stop(mod):
                continue
            if not stop_insts(mod) and maxlevel:
                yield from ModPostIter._iter(mod.insts, filter_, stop, stop_insts, maxlevel - 1)
            if filter_(mod):
                yield mod


def get_mod(topmod: BaseMod, namepats: Names, base=False) -> BaseMod:
    """
    Return the one and just the one hardware module matching `namepats`.

    Iterate over `topmod` and all its submodules and return matching one.

    Args:
        topmod: Top module instance

    Parameter:
        namepats: Iterable with name pattern (including `*` and `?`) or comma separated string.
        base: namepats must match against module `basequalnames` instead of `qual_name`.
    """
    mods = get_mods(topmod, namepats, unique=True, base=base)
    if len(mods) == 1:
        return mods[0]
    listed_mods = mods or ModPostIter(topmod, unique=True)
    if base:
        names = sorted(uniquer.unique(chain.from_iterable(mod.basequalnames for mod in listed_mods)))
    else:
        names = sorted(uniquer.unique(mod.qualname for mod in listed_mods))
    if mods:
        lines = (f"Found multiple hardware modules for {namepats!r}:", *names)
    else:
        lines = (f"{namepats!r} not found. Known are:", *names)
    raise ValueError("\n  ".join(lines))


def get_mods(
    topmod: BaseMod, namepats: Names | None = None, unique: bool = False, base: bool = False
) -> tuple[BaseMod, ...]:
    """
    Return all modules matching `namepats` from hierarchy of `topmod`.

    Iterate over `topmod` and all its submodules and return matching ones.

    Args:
        topmod: Top module instance

    Keyword Args:
        namepats: Iterable with name pattern (including `*` and `?`) or comma separated string. All by default.
        unique (bool): Just return every module once.
        base: namepats must match against module `basequalnames` instead of `qual_name`.
    """
    if namepats:
        patfilter = namefilter(namepats)

        if base:

            def filter_(mod):
                qualnames = uniquer.unique(mod.basequalnames)
                return any(patfilter(qualname) for qualname in qualnames)
        else:

            def filter_(mod):
                return patfilter(mod.qualname)

        return tuple(ModPostIter(topmod, filter_=filter_, unique=unique))
    return tuple(ModPostIter(topmod, unique=unique))


def uniquemods(mods: Iterable[BaseMod]) -> Iterator[BaseMod]:
    """Iterate over unique modules."""
    qualnames = set()
    for mod in mods:
        qualname = mod.qualname
        if qualname not in qualnames:
            qualnames.add(qualname)
            yield mod
