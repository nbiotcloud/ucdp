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
Assignment Handling.

The class [Assigns][ucdp.assigns.Assigns] manages sets of signal assignments.
Either statically in modules but also within flip-flop and multiplexer definitions.

??? Example "Basic Examples"
    All of the following is happening within any hardware module, flip-flop or multiplexer,
    but can also be used within own code.

        >>> import ucdp as u
        >>> signals = u.Idents([
        ...     u.Port(u.ClkRstAnType(), "main_i"),
        ...     u.Port(u.UintType(8), "vec_a_i"),
        ...     u.Port(u.UintType(8), "vec_a_o"),
        ...     u.Port(u.UintType(14), "vec_b_i"),
        ...     u.Port(u.UintType(14), "vec_b_o"),
        ...     u.Port(u.UintType(14), "vec_c_o"),
        ...     u.Signal(u.ClkRstAnType(), "main_s"),
        ...     u.Signal(u.UintType(8), "vec_a_s"),
        ...     u.Signal(u.UintType(4), "vec_b_s"),
        ...     u.Signal(u.UintType(4), "vec_c_s"),
        ... ])
        >>> assigns = u.Assigns(targets=signals, sources=signals)
        >>> assigns.set_default(signals['vec_a_o'], signals['vec_a_i'])
        >>> assigns.set_default(signals['vec_b_o'], signals['vec_b_i'])
        >>> assigns.set(signals['vec_a_o'], signals['vec_a_s'])
        >>> for assign in assigns:
        ...     str(assign)
        'vec_a_o  <----  vec_a_s'
        'vec_b_o  <----  vec_b_i'

??? failure "Multiple Assignments"
    Multiple assignments are forbidden:

        >>> assigns.set(signals['vec_a_o'], signals['vec_a_s'])
        Traceback (most recent call last):
        ...
        ValueError: 'vec_a_o' already assigned to 'vec_a_s'

??? Example "Default Examples"
    Defaults are managed separately:

        >>> for assign in assigns.defaults():
        ...     str(assign)
        'vec_a_o  <----  vec_a_i'
        'vec_b_o  <----  vec_b_i'

??? Example "Mapping"
    With `all=True` the all target signals are mapped:

        >>> assigns = u.Assigns(targets=signals, sources=signals, all=True, sub=True)
        >>> assigns.set_default(signals['vec_a_i'], signals['vec_a_i'])
        >>> assigns.set_default(signals['vec_b_i'], signals['vec_b_i'])
        >>> assigns.set(signals['vec_a_i'], signals['vec_a_s'])
        >>> for assign in assigns:
        ...     str(assign)
        'main_i  ---->  None'
        'main_clk_i  ---->  None'
        'main_rst_an_i  ---->  None'
        'vec_a_i  ---->  vec_a_s'
        'vec_a_o  <----  None'
        'vec_b_i  ---->  vec_b_i'
        'vec_b_o  <----  None'
        'vec_c_o  <----  None'
        'main_s  ---->  None'
        'main_clk_s  ---->  None'
        'main_rst_an_s  ---->  None'
        'vec_a_s  ---->  None'
        'vec_b_s  ---->  None'
        'vec_c_s  ---->  None'

"""

from collections.abc import Iterable, Iterator
from typing import Any

from .exceptions import DirectionError, LockError
from .expr import Expr
from .ident import Ident, Idents, get_expridents
from .note import Note
from .object import Field, LightObject, Object, PrivateField, model_validator
from .orientation import BWD, FWD, IN, INOUT, OUT, Direction
from .signal import BaseSignal, Port
from .typebase import BaseScalarType

_DIRECTION_MAP = {
    IN: "---->",
    OUT: "<----",
    INOUT: "<--->",
    None: None,
}


AssignSource = Expr | Note
""" AssignSource."""

# TODO: signal assignment


class Drivers(Object):
    """
    Drivers.

    This container tracks multiple drivers as every added signal is only allowed to be driven once.

    Attributes:
        drivers: Dictionary with drivers.
    """

    drivers: dict[str, AssignSource] = Field(default_factory=dict)

    def __setitem__(self, name, item):
        drivers = self.drivers
        if name in drivers:
            raise ValueError(f"'{item}' already driven by '{drivers[name]}'")
        drivers[name] = item

    def __iter__(self) -> Iterator[tuple[str, AssignSource]]:  # type: ignore[override]
        yield from self.drivers.items()


class Assign(LightObject):
    """
    A Single Assignment of `expr` to `target`.

    Attributes:
        target: Assigned identifier.
        source: Assigned expression.
    """

    target: BaseSignal
    source: AssignSource | None = None

    @property
    def type_(self):
        """Type."""
        return self.type_

    @property
    def direction(self) -> Direction:
        """Direction."""
        return Direction.cast(self.target.direction)  # type: ignore[return-value]

    def __str__(self):
        return f"{self.target}  {_DIRECTION_MAP[self.direction]}  {self.source}"


_TargetAssigns = dict[str, AssignSource | None]


class Assigns(Object):
    """
    Assignments.

    An instance of [Assigns][ucdp.assigns.Assigns] manages a set of signal assignments.

    Attributes:
        targets: Identifiers allowed to be assigned.
        source: Identifiers allowed to be used in assignment. `targets` by default.
        drivers: Driver tracking, to avoid multiple drivers. To be shared between multiple assignments,
                        where only one driver is allowed.
        all: All Instances Assignment Mode.
        sub: Sublevel Instance Assignment Mode.

    """

    targets: Idents
    sources: Idents
    drivers: Drivers | None = None
    all: bool = False
    sub: bool = False
    _defaults: _TargetAssigns = PrivateField(default_factory=dict)
    _assigns: _TargetAssigns = PrivateField(default_factory=dict)
    __is_locked: bool = PrivateField(default=False)

    @property
    def is_locked(self) -> bool:
        """Locked."""
        return self.__is_locked

    def lock(self) -> None:
        """Lock."""
        assert not self.__is_locked, f"{self} is already locked"
        self.__is_locked = True

    @model_validator(mode="before")
    @classmethod
    def __pre_init(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data["sources"] = data.get("sources") or data.get("targets")
        return data

    def set_default(self, target: BaseSignal, source: AssignSource, cast: bool = False, overwrite: bool = False):
        """Set Default of `target` to `source`.

        Params:
            target: Target.
            source: Source.
            cast: cast to target.
            overwrite: overwrite target.
        """
        if self.__is_locked:
            raise LockError(f"Cannot set default {source} to {target}")
        assert not cast, "TODO"
        self._check(target, source)
        self._set(self._defaults, target, source, overwrite)

    def set(self, target: BaseSignal, source: AssignSource, cast: bool = False, overwrite: bool = False):
        """Set Assignment of `target` to `source`.

        Params:
            target: Target.
            source: Source.
            cast: cast to target.
            overwrite: overwrite target.
        """
        if self.__is_locked:
            raise LockError(f"Cannot set {source} to {target}")
        assert not cast, "TODO"
        self._check(target, source)
        self._set(self._assigns, target, source, overwrite, drivers=self.drivers)

    def get(self, target: BaseSignal) -> AssignSource | None:
        """Get Assignment of `target`."""
        return self._assigns.get(target.name, None)

    def _check(self, target: BaseSignal, source: AssignSource):
        if isinstance(source, Note):
            return

        # Normalize Directions
        # IN/FWD: driver
        # OUT/BWD: sink
        orient = BWD if self.sub else FWD
        sub = "sub-level " if self.sub else ""
        targetdir = isinstance(target, Port) and (target.direction * orient)

        # do not check INOUT
        if not targetdir or not targetdir.mode:
            return

        # Check Expression Source Direction
        for sourceident in get_expridents(source):
            sourcedir = sourceident.direction
            if sourcedir is None:
                sourcedir = IN
            if targetdir == sourcedir:
                raise DirectionError(f"Cannot connect {sub}{target.direction} '{target}' and {sourcedir} '{source}'")

        # Check Types
        connectable = target.type_.is_connectable(source.type_)
        if not connectable:
            msg = f"Cannot assign '{source}' of {source.type_} to {sub}'{target}' of {target.type_}"
            raise TypeError(msg)

    def _set(
        self,
        assigns: _TargetAssigns,
        target: BaseSignal,
        source: AssignSource,
        overwrite: bool,
        drivers: Drivers | None = None,
    ):
        type_ = target.type_
        is_target_scalar = isinstance(type_, BaseScalarType)
        is_source_note = isinstance(source, Note)
        targetdrvdir = IN if self.sub else OUT

        # Expressions are only allowed on BaseScalarType
        if not is_target_scalar and not (isinstance(source, Ident) | is_source_note):
            raise ValueError(f"Cannot assign expression {source} to {target}")

        subtargets: Iterable[BaseSignal]
        subsources: Iterable[AssignSource]

        if is_source_note:
            # Note Assignments
            subtargets = tuple(target.iter())
            subsources = (source,) * len(subtargets)
        elif isinstance(source, Ident):
            # Identifier assignment
            subtargets = target.iter()
            subsources = source.iter()
        else:
            assert is_target_scalar
            # Expression Assignment
            subtargets = (target,)
            subsources = (source,)

        for subtarget, subsource in zip(subtargets, subsources, strict=True):
            if not overwrite and subtarget.name in assigns:
                raise ValueError(f"'{subtarget}' already assigned to '{assigns[subtarget.name]}'")
            if drivers is not None and not is_source_note:
                if subtarget.direction == targetdrvdir:
                    drivers[subtarget.name] = subsource
            assigns[subtarget.name] = subsource

    def __iter__(self):
        return self.iter()

    def iter(self, filter_=None) -> Iterator[Assign]:
        """Iterate over assignments."""
        defaults = self._defaults
        assigns = self._assigns
        for target in self.targets.iter():
            if filter_ and not filter_(target):
                continue
            expr = self._get(assigns, target, default=defaults.get(target.name, None))  # type: ignore[arg-type]
            if expr is not None or self.all:
                yield Assign(target=target, source=expr)

    def defaults(self) -> Iterator[Assign]:
        """Iterate Over Defaults."""
        defaults = self._defaults
        assigns = self._assigns
        for target in self.targets.iter():
            default = self._get(defaults, target)  # type: ignore[arg-type]
            if self.all or default is not None or bool(assigns.get(target.name, None)):
                yield Assign(target=target, source=default)

    @staticmethod
    def _get(assigns: _TargetAssigns, target: BaseSignal, default: AssignSource | None = None) -> AssignSource | None:
        return assigns.get(target.name, default)
