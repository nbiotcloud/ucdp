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
    With `inst=True` the all target signals are mapped:

        >>> assigns = u.Assigns(targets=signals, sources=signals, inst=True)
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

from collections.abc import Callable, Iterator
from typing import Any

from ._castingnamespace import CastingNamespace
from ._sliceassign import SliceAssign
from .casting import Casting
from .drivers import Drivers, Source, Target
from .exceptions import DirectionError, LockError
from .expr import Expr, SliceOp
from .exprparser import ExprParser
from .ident import Ident, Idents, get_subname
from .nameutil import split_suffix
from .note import Note
from .object import Object, PrivateField, model_validator
from .orientation import BWD, FWD, IN, INOUT, OUT, Direction
from .signal import BaseSignal, Port

_DIRECTION_MAP = {
    IN: "---->",
    OUT: "<----",
    INOUT: "<--->",
    None: None,
}

TargetFilter = Callable[[BaseSignal], bool]


class Assign(Object):
    """
    A Single Assignment of `expr` to `target`.

    Attributes:
        target: Assigned identifier.
        source: Assigned expression.
    """

    target: BaseSignal
    source: Source | None = None

    @property
    def name(self) -> str | None:
        """Name."""
        return self.target.name

    @property
    def type_(self):
        """Type."""
        return self.target.type_

    @property
    def doc(self):
        """Doc."""
        return self.target.doc

    @property
    def direction(self) -> Direction:
        """Direction."""
        return Direction.cast(self.target.direction)  # type: ignore[return-value]

    @property
    def ifdef(self) -> str | None:
        """IFDEF."""
        return self.target.ifdef

    @property
    def sign(self) -> str | None:
        """Sign."""
        return _DIRECTION_MAP[self.direction]

    def __str__(self):
        return f"{self.target}  {self.sign}  {self.source}"


_TargetAssigns = dict[str, Source | SliceAssign | None]


class Assigns(Object):
    """
    Assignments.

    An instance of [Assigns][ucdp.assigns.Assigns] manages a set of signal assignments.

    Attributes:
        targets: Identifiers allowed to be assigned.
        source: Identifiers allowed to be used in assignment. `targets` by default.
        drivers: Driver tracking, to avoid multiple drivers. To be shared between multiple assignments,
                        where only one driver is allowed.
        inst: All Instances Assignment Mode.
        sub: Sublevel Instance Assignment Mode.

    """

    targets: Idents
    sources: Idents
    drivers: Drivers | None = None
    inst: bool = False
    _defaults: _TargetAssigns = PrivateField(default_factory=dict)
    _assigns: _TargetAssigns = PrivateField(default_factory=dict)
    __is_locked: bool = PrivateField(default=False)

    @property
    def is_locked(self) -> bool:
        """Locked."""
        return self.__is_locked

    def lock(self) -> None:
        """Lock."""
        if self.__is_locked:
            raise LockError("Assigns are already locked. Cannot lock again.")
        self.__is_locked = True

    @model_validator(mode="before")
    @classmethod
    def __pre_init(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data["sources"] = data.get("sources") or data.get("targets")
        return data

    def set_default(
        self,
        target: Target,
        source: Source,
        cast: bool | None = False,
        overwrite: bool = False,
        filter_: TargetFilter | None = None,
    ):
        """Set Default of `target` to `source`.

        Params:
            target: Target.
            source: Source.
            cast: cast to target.
            overwrite: overwrite target.
        """
        if self.__is_locked:
            raise LockError(f"Cannot set default '{source}' to '{target}'")
        casting = self._prepare(target, source, cast)
        self._set(
            self._defaults,
            target,
            source,
            casting,
            overwrite=overwrite,
            filter_=filter_,
        )

    def set(
        self,
        target: BaseSignal,
        source: Source,
        cast: bool | None = False,
        overwrite: bool = False,
        filter_: TargetFilter | None = None,
    ):
        """Set Assignment of `target` to `source`.

        Params:
            target: Target.
            source: Source.
            cast: cast to target.
            overwrite: overwrite target.
        """
        if self.__is_locked:
            raise LockError(f"Cannot set '{source}' to '{target}'")
        casting = self._prepare(target, source, cast)
        self._set(
            self._assigns,
            target,
            source,
            casting,
            drivers=self.drivers,
            overwrite=overwrite,
            filter_=filter_,
        )

    def get(self, target: BaseSignal) -> Source | None:
        """Get Assignment of `target`."""
        source = self._get(self._assigns, target)
        if source is None:
            source = self._get(self._defaults, target)
        return source

    def _prepare(self, target: Target, source: Source, cast: bool | None) -> Casting | None:
        # Note
        if isinstance(source, Note):
            return None

        if not isinstance(source, (Expr, Note)):
            raise ValueError(f"Source {source} is not a Expression or Note")
        if not isinstance(target, (BaseSignal, SliceOp)):
            raise ValueError(f"Target {target} is not a Signal, Port or Slice of them")

        # Normalize Directions
        orient = BWD if self.inst else FWD
        targetdir = isinstance(target, Port) and target.direction and (target.direction * orient)
        sourcedir = isinstance(source, Port) and source.direction and source.direction

        # Check Direction
        if targetdir == sourcedir == IN:
            raise DirectionError(f"Cannot drive '{target}' by '{source}'")

        # Check casting
        is_connectable = target.type_.is_connectable(source.type_) or source.type_.is_connectable(target.type_)
        if cast is False:
            # casting is forbidden
            if not is_connectable:
                hint = self._get_hint(target, source)
                msg = f"Cannot assign '{source}' of type {source.type_} to '{target}' of type {target.type_}.{hint}"
                raise TypeError(msg)
            casting = None
        else:
            casting = self._get_casting(target, source)
            if casting is None:
                if cast is True or not is_connectable:
                    # casting required
                    hint = self._get_hint(target, source)
                    msg = f"Cannot cast '{source}' of {source.type_} to '{target}' of {target.type_}.{hint}"
                    raise TypeError(msg)
        return casting

    @staticmethod
    def _get_casting(target: Expr | Note, source: Expr | Note) -> Casting:
        if isinstance(source, Ident) and isinstance(target, Ident):
            return target.cast(source)
        return None

    def _get_hint(self, target: Target, source: Source) -> str:
        if self._get_casting(target, source) is not None:
            return " Try to cast."

        if self._get_casting(source, target) is not None:
            return " Try to cast, but swap target and source."

        if (
            isinstance(target, Expr)
            and isinstance(source, Expr)
            and (target.type_.is_connectable(source.type_) or source.type_.is_connectable(target.type_))
        ):
            return " You do NOT need to cast!"

        return ""

    def _set(  # noqa: C901, PLR0912
        self,
        assigns: _TargetAssigns,
        target: Target,
        source: Source,
        casting: Casting | None,
        drivers: Drivers | None = None,
        overwrite: bool = False,
        filter_: TargetFilter | None = None,
    ):
        if isinstance(source, Note):
            if isinstance(target, SliceOp):
                raise ValueError(f"Cannot set {source} on slice {target}")
            for subtarget in target.iter(filter_=filter_):
                assigns[subtarget.name] = source
        elif isinstance(target, SliceOp):
            self._setslice(assigns, drivers, target, source, overwrite, filter_)
        else:
            # note: expression-assignments are forbidden on inst=True
            # note: check for valid identifiers?
            if casting:
                subtargets, subsources = self._cast(target, source, casting)  # type: ignore[arg-type]
            else:
                is_sourceident = isinstance(source, Ident)
                subtargets = tuple(target.iter())
                if len(subtargets) != 1 and not is_sourceident:
                    raise ValueError("TODO-x")
                subsources = tuple(source.iter()) if is_sourceident else [source]  # type: ignore[attr-defined,assignment]
            for subtarget, subsource in zip(subtargets, subsources, strict=True):
                if filter_ and not filter_(subtarget):
                    continue

                # reverse
                if not self.inst and not subtarget.direction != IN:
                    subtarget, subsource = subsource, subtarget  # noqa: PLW2901

                if not isinstance(subtarget, BaseSignal):
                    raise ValueError(f"Target {subtarget} is not a Signal or Port")

                if not isinstance(subsource, Expr):
                    raise ValueError(f"Target {subsource} is not an Expression")

                # check
                if subtarget.name in assigns:
                    if not overwrite:
                        raise ValueError(f"'{subtarget}' already assigned to '{assigns[subtarget.name]}'")

                # drivers
                if drivers is not None:
                    drivers.set(subtarget, subsource, overwrite=overwrite)

                # assign
                assigns[subtarget.name] = subsource

    @staticmethod
    def _cast(target: Ident, source: Ident, targetcasting):
        """Cast `source` to `target` with `targetcasting`."""
        subsources = []
        subtargets = []
        casting = dict(targetcasting)
        parser = ExprParser(namespace=CastingNamespace(source=source))
        for subtarget in target.iter():
            subtargetname = get_subname(target, subtarget)
            subtargetbasename = split_suffix(subtargetname)[0]
            subcast = casting.pop(subtargetbasename, None)
            subsource: Expr
            if subcast is None:
                continue
            if subcast == "":
                subsource = source
            else:
                try:
                    subsource = parser(subcast)
                except NameError as err:
                    raise NameError(f"{err} in casting {subcast!r} to '{subtarget}'") from None
            subsources.append(subsource)
            subtargets.append(subtarget)
        return subtargets, subsources

    def __iter__(self):
        return self.iter()

    def iter(self, filter_=None) -> Iterator[Assign]:
        """Iterate over assignments."""
        defaults = self._defaults
        assigns = self._assigns
        for ident in self.targets.iter():
            target: BaseSignal = ident  # type: ignore[assignment]
            if filter_ and not filter_(target):
                continue
            default = self._get(defaults, target)
            source = self._get(assigns, target, default=default)
            if source is not None or self.inst:
                yield Assign(target=target, source=source)

    def defaults(self) -> Iterator[Assign]:
        """Iterate Over Defaults."""
        defaults = self._defaults
        assigns = self._assigns
        for ident in self.targets.iter():
            target: BaseSignal = ident  # type: ignore[assignment]
            default = self._get(defaults, target)
            if self.inst or default is not None or bool(assigns.get(target.name, None)):
                yield Assign(target=target, source=default)

    @staticmethod
    def _get(assigns: _TargetAssigns, target: BaseSignal, default: Source | None = None) -> Source | None:
        source = assigns.get(target.name, default)
        if isinstance(source, SliceAssign):
            return source.get_expr(default)
        return source

    @staticmethod
    def _setslice(
        assigns: _TargetAssigns,
        drivers: Drivers | None,
        target: SliceOp,
        source: Expr,
        overwrite: bool,
        filter_: TargetFilter | None,
    ):
        if not isinstance(target.one, BaseSignal):
            raise ValueError(f"Slice target {target.one} is not a Signal or Port")
        targetident: BaseSignal = target.one
        if filter_ and not filter_(targetident):
            return
        try:
            sliceassign = assigns[targetident.name]
        except KeyError:
            sliceassign = None

        if sliceassign is not None and not isinstance(sliceassign, SliceAssign) and not overwrite:
            raise ValueError(f"'{targetident}' already assigned to '{assigns[targetident.name]}'")

        if sliceassign is None or not isinstance(sliceassign, SliceAssign):
            sliceassign = assigns[targetident.name] = SliceAssign(type_=targetident.type_, expr=targetident)
            if drivers is not None:
                drivers.set(targetident, sliceassign, overwrite=overwrite)

        sliceassign.set(target.slice_, source, overwrite)
