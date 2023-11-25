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
UCDP Base Objects.

There are two base objects:

* :any:`Object`
* :any:`LightObject`

Every UCDP object must be derived from :any:`Object`.

DOCME: what for what
DOCME: pydantic, strict, no extra
DOCME: use examples
DOCME: caching
"""
from typing import Any, ClassVar

import pydantic as pyd
from pydantic._internal._model_construction import ModelMetaclass

_cache: dict[tuple[Any, ...], Any] = {}

Field = pyd.Field
PrivateField = pyd.PrivateAttr


class Object(pyd.BaseModel):
    """Read-Only :any:`pydantic` Base Model."""

    model_config = pyd.ConfigDict(
        extra="forbid",
        frozen=True,
        revalidate_instances="never",
        strict=True,
        validate_default=True,
    )

    _posargs: tuple[str, ...] = ()

    def __str__(self):
        return get_repr(self)

    def __repr__(self):
        return get_repr(self)


class CachedModelMetaclass(ModelMetaclass):
    """Meta Class for Cached Model Instances."""

    _cache: ClassVar[dict[tuple[Any, ...], Any]] = {}

    def __call__(self, *args, **kwargs):
        """Create New Instance or Return Existing One."""
        key = (self, *args, *sorted(kwargs.items()))
        try:
            inst = self._cache[key]
        except KeyError:
            inst = self._cache[key] = super().__call__(*args, **kwargs)
        return inst


class Light(metaclass=CachedModelMetaclass):
    """DOCME."""


class LightObject(Object, Light):
    """DOCME."""


def get_repr(obj):
    """DOCME."""
    posargs = obj._posargs
    values = obj.model_dump(exclude_unset=True, exclude_defaults=True)
    defaults = obj.model_dump()
    model_fields = obj.model_fields
    sign_args = tuple(repr(obj.__dict__.get(key, values.pop(key, None) or defaults[key])) for key in posargs)
    sign_kwargs = (f"{key}={obj.__dict__[key]!r}" for key in values if model_fields[key].repr)
    sign = ", ".join((*sign_args, *sign_kwargs))
    return f"{obj.__class__.__qualname__}({sign})"
