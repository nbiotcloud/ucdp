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
UCDP Base Objects.

There are two base objects:

* [Object][ucdp.object.Object]
* [LightObject][ucdp.object.LightObject]

Every UCDP object must be derived from [Object][ucdp.object.Object].

DOCME: what for what
DOCME: pydantic, strict, no extra
DOCME: use examples
DOCME: caching
"""

from typing import Any, ClassVar, TypeAlias

import pydantic as pyd
from pydantic._internal._model_construction import ModelMetaclass

from .consts import PAT_IDENTIFIER

_cache: dict[tuple[Any, ...], Any] = {}

PosArgs: TypeAlias = tuple[str, ...]

Field = pyd.Field
PrivateField = pyd.PrivateAttr
ConfigDict = pyd.ConfigDict
model_validator = pyd.model_validator
computed_field = pyd.computed_field

_CACHED_INSTANCES: int = 0


class Object(pyd.BaseModel):
    """Read-Only :any:`pydantic` Base Model."""

    model_config = pyd.ConfigDict(
        extra="forbid",
        frozen=True,
        revalidate_instances="never",
        strict=True,
        validate_default=True,
        arbitrary_types_allowed=True,
    )

    _posargs: ClassVar[PosArgs] = ()

    def new(self, **kwargs):
        """Return A Copy With Updated Attributes."""
        data = {}
        values = self.__dict__
        for name in self.model_fields_set:
            data[name] = values[name]
        data.update(kwargs)
        return self.__class__(**data)

    def __str__(self) -> str:
        """String."""
        return get_repr(self)

    def __repr__(self) -> str:
        """Representation."""
        return get_repr(self)


class CachedModelMetaclass(ModelMetaclass):
    """Meta Class for Cached Model Instances."""

    _cache: ClassVar[dict[tuple[Any, ...], Any]] = {}

    def __call__(self, *args, **kwargs):
        """Create New Instance or Return Existing One."""
        key = (self, *args, *sorted(kwargs.items()))
        try:
            try:
                inst = self._cache[key]
            except KeyError:
                global _CACHED_INSTANCES  # noqa: PLW0603
                _CACHED_INSTANCES += 1
                inst = self._cache[key] = super().__call__(*args, **kwargs)
        except TypeError as exc:
            try:
                hash(self)
            except TypeError:  # pragma: no cover
                raise TypeError(f"{self} is not constant.") from None
            # Determine what caused TypeError
            for idx, arg in enumerate(args):
                try:
                    hash(arg)
                except TypeError:  # noqa: PERF203
                    raise TypeError(f"{self}: {idx} argument {arg!r} is not constant.") from None
            for name, value in kwargs.items():
                try:
                    hash(name)
                    hash(value)
                except TypeError:  # noqa: PERF203
                    raise TypeError(f"{self}: {name!r} argument {value!r} is not constant.") from None
            raise exc
        return inst


class Light(metaclass=CachedModelMetaclass):
    """DOCME."""


class LightObject(Object, Light):
    """DOCME."""


class NamedObject(Object):
    """NamedObject.

    Attributes:
        name: Name.
    """

    name: str


class NamedLightObject(NamedObject, Light):
    """Cacheable NamedObject.

    Attributes:
        name: Name.
    """


class IdentObject(NamedObject):
    """
    Identifier Object.

    Attributes:
        name: Name.
    """

    name: str = Field(pattern=PAT_IDENTIFIER)


class IdentLightObject(IdentObject, Light):
    """Cacheable IdentObject.

    Attributes:
        name: Name.
    """


def get_repr(obj) -> str:
    """DOCME."""
    posargs = obj._posargs
    model_fields_set = obj.model_fields_set
    values = obj.__dict__
    sign_args = tuple(repr(values[key]) for key in posargs)
    sign_kwargs = (
        f"{key}={values[key]!r}"
        for key, field in obj.__class__.model_fields.items()
        if field.repr and key in model_fields_set and key not in posargs and values[key] != field.default
    )
    sign = ", ".join((*sign_args, *sign_kwargs))
    return f"{obj.__class__.__qualname__}({sign})"
