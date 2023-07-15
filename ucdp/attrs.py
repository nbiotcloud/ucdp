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
Refined implementation of https://www.attrs.org/en/stable/.

We restrict ourself to

    * :any:`frozen`
    * :any:`attrs.field`
    * :any:`attrs.NOTHING`
    * :any:`attrs.Factory`
    * :any:`attrs.evolve`

We use a condensed ``repr()`` implementation, which just shows fields different from its default.
"""
import attrs
import mementos

field = attrs.field
NOTHING = attrs.NOTHING
Factory = attrs.Factory
evolve = attrs.evolve
ReusedFrozen = mementos.mementos
asdict = attrs.asdict
astuple = attrs.astuple


def _iter_signature(inst):
    for attrib in inst.__class__.__attrs_attrs__:
        if not attrib.repr or not attrib.init:
            continue
        default = attrib.default
        value = getattr(inst, attrib.name)
        if default is NOTHING:
            yield repr(value)
        else:
            if isinstance(default, Factory):
                try:
                    default = default.factory(inst)
                except (ValueError, TypeError):
                    default = None
            if value != default and value is not NOTHING:
                yield f"{attrib.name}={value!r}"


def _repr(self):
    signature = ", ".join(_iter_signature(self))
    return f"{self.__class__.__qualname__}({signature})"


# pylint: disable=redefined-outer-name,redefined-builtin,unused-argument
def define(maybe_cls=None, frozen=True, repr=True, cmp=None, **kwargs):
    """Recommended attrs Decorator."""

    def wrap(cls):
        cls = attrs.define(cls, frozen=frozen, repr=False, auto_attribs=False, auto_detect=False, eq=cmp, **kwargs)
        if repr:
            cls.__repr__ = _repr
        return cls

    if maybe_cls is None:
        return wrap
    return wrap(maybe_cls)


def frozen(maybe_cls=None, repr=True, **kwargs):
    """Recommended attrs Decorator."""
    return define(maybe_cls, frozen=True, on_setattr=None, repr=repr, **kwargs)
