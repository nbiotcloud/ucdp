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
Top Module Handling.

Overview
--------

* The :any:`AMod` class and all its friends intend to describe a hardware module hierarchy,
  starting at one holy top module.
* The class :any:`Top` **holds** this top module instance and all additional information
  required to handle it.
* The class :any:`TopRef` specifies the top module of a design.
* Top modules can be specified by string via the following pattern:

    ``[[tbfilepath:]tbname#][topfilepath:]topname[-subname][@[configfilepath:]configname]``

* ``topname``: Name of the top module.
* ``topfilepath``: Path to python file containing top module.
* ``subname``: Name of the sub module within top module.
* ``tbfilepath``: Path to python file containing testbench module.
* ``tbname``: Name of the testbench.
* ``configfilepath``: Path to python file containing config.
* ``configname``: Name of the config.

* :any:`load()` is one and only method to pickup and instantiate the topmost hardware module.

API
---
"""
from typing import Optional

from .attrs import field, frozen
from .mod.base import BaseMod
from .mod.iter import ModPostIter, ModPreIter, get_mod, get_mods
from .topref import TopRef
from .util import Items


@frozen
class Top:

    """
    Top Module Reference.

    Args:
        mod (BaseMod): Top Module
    """

    spec: TopRef = field(repr=False)
    mod: BaseMod = field()

    def iter(self, filter_=None, stop=None, maxlevel: Optional[int] = None, unique: bool = False, post: bool = False):
        """
        Iterate Over All Modules.

        Keyword Args:
            filter_: function called with every `mod` as argument, `mod` is returned if `True`.
            stop: stop iteration at `mod` if `stop` function returns `True` for `mod`.
            maxlevel (int): maximum descending in the mod hierarchy.
            unique (bool): Just return module once and **NOT** all instances of it.
        """
        # pylint: disable=too-many-arguments
        if post:
            return ModPostIter(self.mod, filter_=filter_, stop=stop, maxlevel=maxlevel, unique=unique)
        return ModPreIter(self.mod, filter_=filter_, stop=stop, maxlevel=maxlevel, unique=unique)

    def get_mods(self, namepats: Items = None, unique: bool = False):
        """
        Return all modules matching `namepats`.

        Iterate top and all its submodules and return matching ones.

        Keyword Args:
            namepats: Iterable with name pattern (including `*` and `?`) or comma separated string
            unique (bool): Just return every module once.
        """
        return get_mods(self.mod, namepats=namepats, unique=unique)

    def get_mod(self, namepats: Items):
        """
        Return the one and just the one hardware module matching `namepats`.

        Iterate over `mod` and all its submodules and return matching one.

        Keyword Args:
            namepats: Iterable with name pattern (including `*` and `?`) or comma separated string
        """
        return get_mod(self.mod, namepats)
