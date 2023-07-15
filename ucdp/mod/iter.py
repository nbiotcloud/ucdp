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

"""
Module Iterator.

Module Iteration Strategies:

* :any:`ModPreIter` - yield top module **before** the child-modules.
* :any:`ModPostIter` - yield top module **after** the child-modules.
"""
from typing import Any, Callable, Generator, Iterable, Optional, Tuple

from matchor import matchs
from uniquer import uniquetuple

from ..attrs import field, frozen
from ..mod.base import BaseMod
from ..util import Items, split

FilterFunc = Callable[[Any], bool]
StopFunc = Callable[[Any], bool]
MaxLevel = Optional[int]


@frozen
class ModPreIter:
    """
    Iterate over module hierarchy starting at `mod`, using the pre-order strategy.

    Yield top module **before** the child-modules.

    Keyword Args:
        filter_: function called with every `mod` as argument, `mod` is returned if `True`.
        stop: stop iteration at `mod` if `stop` function returns `True` for `mod`.
        maxlevel (int): maximum descending in the mod hierarchy.
        unique (bool): Just return module once.

    >>> import ucdp
    >>> class CMod(ucdp.AMod):
    ...     def _build(self):
    ...         pass
    >>> class EMod(ucdp.AMod):
    ...     def _build(self):
    ...         pass
    >>> class AMod(ucdp.AMod):
    ...     def _build(self):
    ...         pass
    >>> class DMod(ucdp.AMod):
    ...     def _build(self):
    ...         CMod(self, "c")
    ...         EMod(self, "e")
    >>> class BMod(ucdp.AMod):
    ...     def _build(self):
    ...         AMod(self, "a")
    ...         DMod(self, "d")
    >>> class HMod(ucdp.AMod):
    ...     def _build(self):
    ...         pass
    >>> class IMod(ucdp.AMod):
    ...     def _build(self):
    ...         HMod(self, "h")
    >>> class GMod(ucdp.AMod):
    ...     def _build(self):
    ...         IMod(self, "i")
    >>> class FMod(ucdp.AMod):
    ...     def _build(self):
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
    """

    mod: BaseMod = field()
    filter_: FilterFunc = field(default=None, kw_only=True)
    stop: StopFunc = field(default=None, kw_only=True)
    maxlevel: MaxLevel = field(default=None, kw_only=True)
    unique: bool = field(default=False, kw_only=True)

    __iter = field(init=False, repr=False)

    @__iter.default
    def _create_iter(self):
        mod = self.mod
        filter_ = self.filter_
        stop = self.stop
        maxlevel = self.maxlevel
        # Use highly optimized iterator depending on arguments
        if filter_:
            if stop:
                if maxlevel is not None and maxlevel > 0:
                    iter_ = ModPreIter._iter_filter_stop_maxlevel([mod], filter_, stop, maxlevel - 1)
                else:
                    iter_ = ModPreIter._iter_filter_stop([mod], filter_, stop)
            else:
                if maxlevel is not None and maxlevel > 0:
                    iter_ = ModPreIter._iter_filter_maxlevel([mod], filter_, maxlevel - 1)
                else:
                    iter_ = ModPreIter._iter_filter([mod], filter_)
        else:
            if stop:
                if maxlevel is not None and maxlevel > 0:
                    iter_ = ModPreIter._iter_stop_maxlevel([mod], stop, maxlevel - 1)
                else:
                    iter_ = ModPreIter._iter_stop([mod], stop)
            else:
                if maxlevel is not None and maxlevel > 0:
                    iter_ = ModPreIter._iter_maxlevel([mod], maxlevel - 1)
                else:
                    iter_ = ModPreIter._iter([mod])
        if self.unique:
            iter_ = uniquemods(iter_)
        return iter_

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.__iter)

    @staticmethod
    def _iter_filter_stop_maxlevel(mods, filter_, stop, maxlevel):
        for mod in mods:
            if stop(mod):
                continue
            if filter_(mod):
                yield mod
            if maxlevel:
                yield from ModPreIter._iter_filter_stop_maxlevel(mod.insts, filter_, stop, maxlevel - 1)

    @staticmethod
    def _iter_filter_stop(mods, filter_, stop):
        for mod in mods:
            if stop(mod):
                continue
            if filter_(mod):
                yield mod
            yield from ModPreIter._iter_filter_stop(mod.insts, filter_, stop)

    @staticmethod
    def _iter_filter_maxlevel(mods, filter_, maxlevel):
        for mod in mods:
            if filter_(mod):
                yield mod
            if maxlevel:
                yield from ModPreIter._iter_filter_maxlevel(mod.insts, filter_, maxlevel - 1)

    @staticmethod
    def _iter_filter(mods, filter_):
        for mod in mods:
            if filter_(mod):
                yield mod
            yield from ModPreIter._iter_filter(mod.insts, filter_)

    @staticmethod
    def _iter_stop_maxlevel(mods, stop, maxlevel):
        for mod in mods:
            if stop(mod):
                continue
            yield mod
            if maxlevel:
                yield from ModPreIter._iter_stop_maxlevel(mod.insts, stop, maxlevel - 1)

    @staticmethod
    def _iter_stop(mods, stop):
        for mod in mods:
            if stop(mod):
                continue
            yield mod
            yield from ModPreIter._iter_stop(mod.insts, stop)

    @staticmethod
    def _iter_maxlevel(mods, maxlevel):
        for mod in mods:
            yield mod
            if maxlevel:
                yield from ModPreIter._iter_maxlevel(mod.insts, maxlevel - 1)

    @staticmethod
    def _iter(mods):
        for mod in mods:
            yield mod
            yield from ModPreIter._iter(mod.insts)


@frozen
class ModPostIter:
    """
    Iterate over module hierarchy starting at `mod`, using the post-order strategy.

    Yield top module **after** the child-modules.

    Keyword Args:
        filter_: function called with every `mod` as argument, `mod` is returned if `True`.
        stop: stop iteration at `mod` if `stop` function returns `True` for `mod`.
        maxlevel (int): maximum descending in the mod hierarchy.
        unique (bool): Just return module once.

    >>> import ucdp
    >>> @ucdp.mod
    ... class CMod(ucdp.AMod):
    ...     def _build(self):
    ...         pass
    >>> @ucdp.mod
    ... class EMod(ucdp.AMod):
    ...     def _build(self):
    ...         pass
    >>> @ucdp.mod
    ... class AMod(ucdp.AMod):
    ...     def _build(self):
    ...         pass
    >>> @ucdp.mod
    ... class DMod(ucdp.AMod):
    ...     def _build(self):
    ...         CMod(self, "c")
    ...         EMod(self, "e")
    >>> @ucdp.mod
    ... class BMod(ucdp.AMod):
    ...     def _build(self):
    ...         AMod(self, "a")
    ...         DMod(self, "d")
    >>> @ucdp.mod
    ... class HMod(ucdp.AMod):
    ...     def _build(self):
    ...         pass
    >>> @ucdp.mod
    ... class IMod(ucdp.AMod):
    ...     def _build(self):
    ...         HMod(self, "h")
    >>> @ucdp.mod
    ... class GMod(ucdp.AMod):
    ...     def _build(self):
    ...         IMod(self, "i")
    >>> @ucdp.mod
    ... class FMod(ucdp.AMod):
    ...     def _build(self):
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
    """

    mod: BaseMod = field()
    filter_: FilterFunc = field(default=None, kw_only=True)
    stop: StopFunc = field(default=None, kw_only=True)
    maxlevel: MaxLevel = field(default=None, kw_only=True)
    unique: bool = field(default=False, kw_only=True)

    __iter = field(init=False, repr=False)

    @__iter.default
    def _create_iter(self):
        mod = self.mod
        filter_ = self.filter_
        stop = self.stop
        maxlevel = self.maxlevel
        # Use highly optimized iterator depending on arguments
        if filter_:
            if stop:
                if maxlevel is not None and maxlevel > 0:
                    iter_ = ModPostIter._iter_filter_stop_maxlevel([mod], filter_, stop, maxlevel - 1)
                else:
                    iter_ = ModPostIter._iter_filter_stop([mod], filter_, stop)
            else:
                if maxlevel is not None and maxlevel > 0:
                    iter_ = ModPostIter._iter_filter_maxlevel([mod], filter_, maxlevel - 1)
                else:
                    iter_ = ModPostIter._iter_filter([mod], filter_)
        else:
            if stop:
                if maxlevel is not None and maxlevel > 0:
                    iter_ = ModPostIter._iter_stop_maxlevel([mod], stop, maxlevel - 1)
                else:
                    iter_ = ModPostIter._iter_stop([mod], stop)
            else:
                if maxlevel is not None and maxlevel > 0:
                    iter_ = ModPostIter._iter_maxlevel([mod], maxlevel - 1)
                else:
                    iter_ = ModPostIter._iter([mod])
        if self.unique:
            iter_ = uniquemods(iter_)
        return iter_

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.__iter)

    @staticmethod
    def _iter_filter_stop_maxlevel(mods, filter_, stop, maxlevel):
        for mod in mods:
            if stop(mod):
                continue
            if maxlevel:
                yield from ModPostIter._iter_filter_stop_maxlevel(mod.insts, filter_, stop, maxlevel - 1)
            if filter_(mod):
                yield mod

    @staticmethod
    def _iter_filter_stop(mods, filter_, stop):
        for mod in mods:
            if stop(mod):
                continue
            yield from ModPostIter._iter_filter_stop(mod.insts, filter_, stop)
            if filter_(mod):
                yield mod

    @staticmethod
    def _iter_filter_maxlevel(mods, filter_, maxlevel):
        for mod in mods:
            if maxlevel:
                yield from ModPostIter._iter_filter_maxlevel(mod.insts, filter_, maxlevel - 1)
            if filter_(mod):
                yield mod

    @staticmethod
    def _iter_filter(mods, filter_):
        for mod in mods:
            yield from ModPostIter._iter_filter(mod.insts, filter_)
            if filter_(mod):
                yield mod

    @staticmethod
    def _iter_stop_maxlevel(mods, stop, maxlevel):
        for mod in mods:
            if stop(mod):
                continue
            if maxlevel:
                yield from ModPostIter._iter_stop_maxlevel(mod.insts, stop, maxlevel - 1)
            yield mod

    @staticmethod
    def _iter_stop(mods, stop):
        for mod in mods:
            if stop(mod):
                continue
            yield from ModPostIter._iter_stop(mod.insts, stop)
            yield mod

    @staticmethod
    def _iter_maxlevel(mods, maxlevel):
        for mod in mods:
            if maxlevel:
                yield from ModPostIter._iter_maxlevel(mod.insts, maxlevel - 1)
            yield mod

    @staticmethod
    def _iter(mods):
        for mod in mods:
            yield from ModPostIter._iter(mod.insts)
            yield mod


def get_mod(topmod: BaseMod, namepats: Items) -> BaseMod:
    """
    Return the one and just the one hardware module matching `namepats`.

    Iterate over `topmod` and all its submodules and return matching one.

    Args:
        topmod: Top module instance

    Keyword Args:
        namepats: Iterable with name pattern (including `*` and `?`) or comma separated string. All by default.
    """
    mods = get_mods(topmod, namepats, unique=True)
    if len(mods) == 1:
        return mods[0]
    if mods:
        modnames = tuple(sorted(mod.modname for mod in mods))
        lines = (f"Found multiple hardware modules for {namepats!r}:",) + modnames
    else:
        modnames = _unique_modnames(ModPostIter(topmod, unique=True))
        lines = (f"{namepats!r} not found. Known are:",) + modnames
    raise ValueError("\n  ".join(lines))


def get_mods(topmod: BaseMod, namepats: Items = None, unique: bool = False) -> Tuple[BaseMod, ...]:
    """
    Return all modules matching `namepats` from hierarchy of `topmod`.

    Iterate over `topmod` and all its submodules and return matching ones.

    Args:
        topmod: Top module instance

    Keyword Args:
        namepats: Iterable with name pattern (including `*` and `?`) or comma separated string. All by default.
        unique (bool): Just return every module once.
    """
    namepats = split(namepats)
    if namepats:

        def filter_(mod):
            # pylint: disable=unused-argument
            modnames = uniquetuple((mod.modname,) + mod.modbasenames)
            return any(matchs(modname, namepats) for modname in modnames)

        return tuple(ModPostIter(topmod, filter_=filter_, unique=unique))
    return tuple(ModPostIter(topmod, unique=unique))


def _iter_modnames(mods):
    for mod in mods:
        yield mod.modname
        yield from mod.modbasenames


def _unique_modnames(mods):
    return uniquetuple(sorted(_iter_modnames(mods)))


def uniquemods(mods: Iterable[BaseMod]) -> Generator[BaseMod, None, None]:
    """Iterate over unique modules."""
    modnames = set()
    for mod in mods:
        modname = mod.modname
        if modname not in modnames:
            modnames.add(modname)
            yield mod
