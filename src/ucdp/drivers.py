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
Driver Tracking.

"""

from collections.abc import Iterator
from typing import Annotated

from pydantic import BeforeValidator

from .exceptions import MultipleDriverError
from .expr import Expr, SliceOp
from .logging import LOGGER
from .note import Note
from .object import Field, Object
from .signal import BaseSignal
from .typebase import BaseScalarType

Target = BaseSignal | SliceOp
"""Assignment Target."""

Source = Expr | Note
"""Assignment Source."""


def check_target(target: Target) -> None:
    """
    Check `target`.

    Only ports, signals of any type OR slicing of native types are supported.
    """
    if isinstance(target, BaseSignal):
        return

    if isinstance(target, SliceOp):
        if isinstance(target.one.type_, BaseScalarType):
            return
        raise ValueError(f"Invalid target {target!r}. Slicing is only supported on native types")


ToTarget = Annotated[
    Target,
    BeforeValidator(lambda x: check_target(x)),
]


class Drivers(Object):
    """
    Drivers.

    This container tracks multiple drivers as every added signal is only allowed to be driven once.

    Attributes:
        drivers: Dictionary with drivers.
    """

    drivers: dict[str, Source] = Field(default_factory=dict, init=False)

    def set(self, target: BaseSignal, source: Source, overwrite: bool = False):
        """Set Driver for Target."""
        drivers = self.drivers
        name = target.name
        LOGGER.debug("driver target=%s source=%s", target, source)
        if not overwrite and name in drivers:
            raise MultipleDriverError(f"'{source}' already driven by '{drivers[name]}'")
        drivers[name] = source

    def __iter__(self) -> Iterator[tuple[str, Source]]:  # type: ignore[override]
        yield from self.drivers.items()
