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
Hardware Module Builder.

"""

from .exceptions import BuildError
from .logging import LOGGER
from .modbase import BaseMod
from .moditer import ModPreIter
from .nameutil import didyoumean

TIMEOUT: int = 10


def _stop_at_locked(mod: BaseMod):
    return mod.is_locked


def _build(mod: BaseMod, name: str):
    insts: set[int] = set()

    for iteration in range(1, TIMEOUT):
        LOGGER.debug("%s: builder: %s iteration %s", mod, name, iteration)
        pending = False
        for inst in ModPreIter(mod=mod, stop=_stop_at_locked):
            instid = hash((inst.qualname, inst.inst))

            # build every instance just once
            if instid in insts:
                continue
            insts.add(instid)

            # Determine build method
            try:
                build_method = getattr(inst, name)
            except AttributeError:
                continue
            if not getattr(inst, f"_has{name}"):
                raise TypeError(f"{inst} is not allowed to have a {name} method.")

            # Invoke build_method
            build_method()
            pending = True

        if not pending:
            break
    else:
        raise BuildError(f"Cannot build {mod}")


def build(mod: BaseMod):
    _build(mod, "_build_dep")

    _build(mod, "_build_final")

    insts = tuple(ModPreIter(mod, stop=_stop_at_locked))

    # route
    for inst in insts:
        inst._router.flush()

    # paramdict+lock
    for inst in insts:
        for name in inst.paramdict:
            advice = didyoumean(name, inst.params.keys(), known=True)
            raise ValueError(f"{inst} has no param {name!r}{advice}")
        # for mux in inst.muxes:
        #     for sel in mux.sels:
        #         if isinstance(sel.type_, BaseEnumType):
        #             inst.add_type_consts(sel.type_, exist_ok=True)
        inst.lock()
