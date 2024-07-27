#
# MIT License
#
# Copyright (c) 2024 nbiotcloud
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
Loader.

* [load()][ucdp.loader.load] is one and only method to pickup and instantiate the topmost hardware module.
"""

from importlib import import_module

from .modbase import BaseMod
from .modref import ModRef


def _load_modcls(modref: ModRef) -> type[BaseMod]:
    name = f"{modref.libname}.{modref.modname}"
    try:
        pymod = import_module(name)
    except ModuleNotFoundError as exc:
        if exc.name in (modref.libname, name):
            raise NameError(f"{name!r} not found.") from None
        raise exc
    modclsname = modref.get_modclsname()
    modcls = getattr(pymod, modclsname, None)
    if not modcls:
        raise NameError(f"{name!r} does not contain {modclsname}.") from None
    if not issubclass(modcls, BaseMod):
        raise ValueError(f"{modcls} is not a module aka child of <class ucdp.BaseMod>.")
    return modcls
