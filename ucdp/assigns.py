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
Assignment Handling.

The class :any:`Assigns` manages sets of signal assignments.
Either statically in modules but also within flip-flop and multiplexer definitions.

All of the following is happening within any hardware module, flip-flop or multiplexer,
but can also be used within own code.

>>> import ucdp
>>> ports = ucdp.Idents([
...     ucdp.Port(ucdp.ClkRstAnType()),
...     ucdp.Port(ucdp.UintType(8), "vec_a_i"),
...     ucdp.Port(ucdp.UintType(8), "vec_a_o"),
...     ucdp.Port(ucdp.UintType(14), "vec_b_i"),
...     ucdp.Port(ucdp.UintType(14), "vec_b_o"),
...     ucdp.Port(ucdp.UintType(14), "vec_c_o"),
... ])
>>> signals = ucdp.Idents([
...     ucdp.Port(ucdp.ClkRstAnType()),
...     ucdp.Port(ucdp.UintType(8), "vec_a_i"),
...     ucdp.Port(ucdp.UintType(8), "vec_a_o"),
...     ucdp.Port(ucdp.UintType(14), "vec_b_i"),
...     ucdp.Port(ucdp.UintType(14), "vec_b_o"),
...     ucdp.Port(ucdp.UintType(14), "vec_c_o"),
...     ucdp.Signal(ucdp.ClkRstAnType(), "main_s"),
...     ucdp.Signal(ucdp.UintType(8), "vec_a_s"),
...     ucdp.Signal(ucdp.UintType(4), "vec_b_s"),
...     ucdp.Signal(ucdp.UintType(4), "vec_c_s"),
... ])
>>> assigns = ucdp.Assigns(ports, signals)
>>> assigns.set_default(ports['vec_a_o'], signals['vec_a_i'])
>>> assigns.set_default(ports['vec_b_o'], signals['vec_b_i'])
>>> assigns.set(ports['vec_a_o'], signals['vec_a_s'])
>>> for assign in assigns:
...     assign.target.name, assign.expr
('vec_a_o', Signal(UintType(8), 'vec_a_s'))
('vec_b_o', Port(UintType(14), name='vec_b_i'))

Multiple assignments are forbidden:

>>> assigns.set(ports['vec_a_o'], signals['vec_a_s'])
Traceback (most recent call last):
  ...
ValueError: 'Port(UintType(8), name='vec_a_o')' already assigned to 'Signal(UintType(8), 'vec_a_s')'

Defaults are managed separately:

>>> for assign in assigns.defaults():
...     assign.target.name, assign.expr
('vec_a_o', Port(UintType(8), name='vec_a_i'))
('vec_b_o', Port(UintType(14), name='vec_b_i'))


With `inst=True` the all target signals are mapped:

>>> assigns = ucdp.Assigns(ports, signals, inst=True)
>>> assigns.set_default(ports['vec_a_i'], signals['vec_a_i'])
>>> assigns.set_default(ports['vec_b_i'], signals['vec_b_i'])
>>> assigns.set(ports['vec_a_i'], signals['vec_a_s'])
>>> for assign in assigns:
...     assign.target.name, assign.expr
('', None)
('clk_i', None)
('rst_an_i', None)
('vec_a_i', Signal(UintType(8), 'vec_a_s'))
('vec_a_o', None)
('vec_b_i', Port(UintType(14), name='vec_b_i'))
('vec_b_o', None)
('vec_c_o', None)
"""
from typing import Any, Callable, Dict, Generator, Optional

from icdutil.slices import Slice

from .attrs import define, field, frozen
from .const import Const
from .expr import CommentExpr, ConcatExpr, ConstExpr, Expr, SliceOp, parse
from .ident import Ident, Idents, get_subname
from .namespace import LockError
from .nameutil import join_names, split_suffix
from .param import Param
from .signal import ASignal, Port
from .types.orientation import BWD, FWD, IN

TargetFilter = Callable[[ASignal], bool]


@frozen
class Assign:

    """
    A Single Assignment of `expr` to `target`.

    Args:
        target (Ident): Assigned identifier.
        expr (Expr): Assigned expression.
    """

    target: Ident = field()
    expr: Optional[Expr] = field(default=None)

    @property
    def type_(self):
        """Target Type."""
        return self.target.type_

    @property
    def name(self):
        """Target Name."""
        return self.target.name

    @property
    def doc(self):
        """Target Doc."""
        return self.target.doc

    @property
    def level(self):
        """Target Level."""
        return self.target.level

    @property
    def ifdef(self):
        """Target IFDEF."""
        return self.target.ifdef


@frozen
class Assigns:

    """
    Assignments.

    An instance of :any:`Assigns` manages a set of signal assignments.

    Args:
        targets (Idents): Identifiers allowed to be assigned.

    Keyword Args:
        sources (Idents): Identifiers allowed to be used in assignment. `targets` by default.
        drivers (dict): Driver tracking, to avoid multiple drivers. To be shared between multiple assignments,
                        where only one driver is allowed.
        inst (bool): Instance Assignment Mode.
    """

    # pylint: disable=too-many-instance-attributes

    targets: Idents = field()
    sources: Idents = field()
    drivers: Optional[dict] = field(default=None, kw_only=True)
    inst: bool = field(default=False, kw_only=True)
    _defaults: Dict[str, Optional[Expr]] = field(factory=dict, init=False)
    _assigns: Dict[Expr, Any] = field(factory=dict, init=False)
    _targetfilter: TargetFilter = field(init=False)
    _locked: bool = field(default=False, init=False)

    @sources.default
    def _sources_default(self):
        return self.targets

    @_targetfilter.default
    def _targetfilter_default(self):
        if self.inst:

            def filter_(signal):
                # pylint: disable=unused-argument
                return True

        else:

            def filter_(signal):
                return signal.direction != IN

        return filter_

    def set_default(self, target: Expr, source: Expr, cast: bool = False, filter_=None):
        """Set Default of `target` to `source`."""
        if self._locked:
            raise LockError(f"Cannot set default {source} to {target}")
        casting = self._check(target, source, cast)
        self._set(self._defaults, {}, target, source, casting, filter_=filter_)

    def set(self, target: Expr, source: Expr, overwrite: bool = False, cast: bool = False, filter_=None, plain=False):
        """Set Assignment of `target` to `source`."""
        # pylint: disable=too-many-arguments
        if self._locked:
            raise LockError(f"Cannot set {source} to {target}")
        if plain:
            assert not cast, "Casting is not supported on plain"
            assert not filter_, "Filtering is not supported on plain"
            # pylint: disable=unsupported-membership-test
            if target in self._assigns:
                if not overwrite:
                    # pylint: disable=unsubscriptable-object
                    raise ValueError(f"'{target}' already assigned to '{self._assigns[target]}'")
            # pylint: disable=unsupported-assignment-operation
            self._assigns[target] = source
        else:
            casting = self._check(target, source, cast)
            self._set(self._assigns, self.drivers, target, source, casting, overwrite=overwrite, filter_=filter_)

    def get(self, target: Expr) -> Optional[Expr]:
        """Get Assignment of `target`."""
        expr = self._assigns.get(target.name, None)  # type: ignore
        # undo string optimization
        if expr is not None:
            expr = parse(expr, namespace=self.sources)
        return expr

    def get_targets(self, source):
        """
        Get Assignments of `source`.
        """
        targets = []
        for assign in self.iter():
            if assign.expr == source:
                targets.append(assign)
        return targets

    def _check(self, target: Expr, source: Expr, cast: bool):
        # Normalize Directions
        #   target: should be an output or signal
        #   source: should be an input or signal
        orient = BWD if self.inst else FWD
        targetdir = isinstance(target, Port) and target.direction and (target.direction * orient)
        sourcedir = isinstance(source, Port) and source.direction and source.direction
        # Check Direction
        if targetdir == sourcedir == IN:
            raise DirectionError(f"Cannot drive '{target}' by '{source}'")
        # Check casting
        connectable = (
            not target.type_
            or not source.type_
            or target.type_.is_connectable(source.type_)
            or source.type_.is_connectable(target.type_)
        )
        if cast is False:
            # casting is forbidden
            if not connectable:
                msg = f"Cannot ASSIGN '{source}' of {source.type_} to '{target}' of {target.type_}"
                raise TypeError(msg)
            casting = None
        else:
            casting = target.type_.cast(source.type_)
            if casting is NotImplemented:
                if cast is True or not connectable:
                    # casting required
                    msg = f"Cannot CAST '{source}' of {source.type_} to '{target}' of {target.type_}"
                    if source.type_.cast(target.type_) is not NotImplemented:
                        msg = f"{msg} - swap target and source!"
                    elif target.type_.is_connectable(source.type_):
                        msg = f"{msg} - you do NOT need to cast!"
                    elif source.type_.is_connectable(target.type_):
                        msg = f"{msg} - you do NOT need to cast, swap target and source!"
                    raise TypeError(msg)
            if connectable:
                casting = None
        return casting

    def _set(self, assigns, drivers, target: Expr, source: Expr, casting, overwrite: bool = False, filter_=None):
        # pylint: disable=too-many-arguments,too-many-branches
        if isinstance(target, (Param, Const)):
            raise ValueError(f"Cannot assign Param/LocalParam: {target}")
        is_slice = isinstance(target, SliceOp) and isinstance(target.one, ASignal)
        assert is_slice or isinstance(target, ASignal), "Implemented On-Demand: expression-assignments"
        if isinstance(source, CommentExpr):
            for subtarget in target.iter(filter_=filter_):
                assigns[subtarget.name] = source
        else:
            # We do not care about replicated code here, as we want to be fast
            targetfilter: TargetFilter = self._targetfilter
            if is_slice:
                assert not casting, "TODO - No casting of slices for now"
                _setslice(assigns, drivers, target, source, overwrite, filter_)
            else:
                # note: expression-assignments are forbidden on inst=True
                # note: check for valid identifiers?
                if casting:
                    subtargets, subsources = self._cast(target, source, casting)
                else:
                    is_sourceident = isinstance(source, Ident)
                    subtargets = tuple(target.iter())
                    assert len(subtargets) == 1 or is_sourceident, "Implemented On-Demand: struct-expressions"
                    subsources = tuple(source.iter()) if is_sourceident else [source]
                assert len(subtargets) == len(subsources)
                for subtarget, subsource in zip(subtargets, subsources):
                    if filter_ and not filter_(subtarget):
                        continue
                    # reverse
                    # pylint: disable=not-callable
                    if not self.inst and not targetfilter(subtarget):
                        subtarget, subsource = subsource, subtarget
                    assert isinstance(subtarget, ASignal), "Implemented On-Demand: expression-assignments"
                    # check
                    if subtarget.name in assigns:
                        if not overwrite:
                            raise ValueError(f"'{subtarget}' already assigned to '{assigns[subtarget.name]}'")
                    if drivers is not None and subtarget.name in drivers:
                        raise ValueError(f"'{subtarget}' already driven by '{drivers[subtarget.name]}'")
                    # assign
                    assigns[subtarget.name] = subsource

    @staticmethod
    def _cast(target, source, targetcasting):
        """Cast `source` to `target` with `targetcasting`."""
        subsources = []
        subtargets = []
        casting = dict(targetcasting)
        for subtarget in target.iter():
            subtargetname = get_subname(target, subtarget)
            subtargetbasename = split_suffix(subtargetname)[0]
            subcast = casting.pop(subtargetbasename, None)
            if subcast is None:
                continue
            try:
                subsource = parse(subcast, namespace=CastNamespace(source))
            except NameError as err:
                raise NameError(f"{err} in casting {subcast!r} to '{subtarget}'") from None
            subsources.append(subsource)
            subtargets.append(subtarget)
        return subtargets, subsources

    def __iter__(self):
        return self.iter()

    def iter(self, filter_=None):
        """Iterate over assignments."""
        defaults = self._defaults
        assigns = self._assigns
        for target in self.targets.iter(filter_=self._targetfilter):
            if filter_ and not filter_(target):
                continue
            expr = assigns.get(target.name, None)
            if isinstance(expr, dict):
                default = defaults.get(target.name, None)
                if default is None:
                    default = ConstExpr(target.type_)
                # else:
                #     default = parse(default, self.sources)
                expr = _concat(expr, default)
            elif expr is None:
                expr = defaults.get(target.name, None)
            if expr is not None:
                yield Assign(target, expr=expr)
            elif self.inst:
                yield Assign(target, expr=expr)

    def defaults(self) -> Generator[Assign, None, None]:
        """Iterate Over Defaults."""
        defaults = self._defaults
        assigns = self._assigns
        for target in self.targets.iter(filter_=self._targetfilter):
            assign = self.inst or bool(assigns.get(target.name, None))
            expr = defaults.get(target.name, None)
            # if assign and expr is None:
            #     expr = target.get_svvalue()
            if assign or expr is not None:
                yield Assign(target, expr=expr)

    @property
    def is_locked(self) -> bool:
        """
        Lock Status.
        """
        return self._locked

    def lock(self):
        """
        Lock.
        """
        object.__setattr__(self, "_locked", True)


def _concat(items, default):
    values = []
    for slice_, item in sorted(items.items(), key=lambda pair: pair[0].right, reverse=True):
        if item is None:
            item = default[slice_.slice]
        values.append(item)
    if len(values) > 1:
        return ConcatExpr(tuple(values))
    return f"{values[0]}"


def _setslice(assigns, drivers, target, source, overwrite, filter_):
    # pylint: disable=too-many-arguments
    targetident = target.one
    if not filter_ or filter_(targetident):
        targetconcat = assigns.get(targetident.name, {})
        if not isinstance(targetconcat, dict):
            if not overwrite:
                raise ValueError(f"'{targetident}' already assigned to '{assigns[targetident.name]}'")
            targetconcat = {}  # TODO: maybe use actual target as base
        if not targetconcat and drivers is not None and targetident.name in drivers:
            raise ValueError(f"'{targetident}' already driven by '{drivers[targetident.name]}'")
        assert isinstance(getattr(targetident.type_, "width", None), int), "Invalid width"
        width = targetident.type_.width
        targetslice = target.slice_
        if targetslice.left >= width:
            raise ValueError(f"Slice {targetslice} exceeds width ({width}) of '{targetident}'")
        if not targetconcat:
            assigns[targetident.name] = targetconcat = {Slice(left=width - 1, right=0): None}
        sslice = _searchpadding(targetconcat, targetslice, overwrite)
        targetconcat.pop(sslice)
        _addpadding(targetconcat, targetslice.right - 1, sslice.right)
        targetconcat[targetslice] = source
        _addpadding(targetconcat, sslice.left, targetslice.left + 1)


def _searchpadding(concat, slice_, overwrite):
    sslice = None
    for islice, iitem in concat.items():
        if islice.mask & slice_.mask:
            if iitem and not overwrite:
                raise ValueError(f"Slice {slice_} is already taken by {iitem}")
            sslice = islice
    return sslice


def _addpadding(concat, left, right):
    if left >= right:
        slice_ = Slice(left, right)
        concat[slice_] = None


@define
class CastNamespace:

    """Namespace Helper for Type Casting."""

    source: Ident = field()

    def __getitem__(self, key):
        source = self.source
        for subsource in source.iter():
            if join_names(source.basename, key) == subsource.basename:
                return subsource
        raise KeyError(key)

    def get(self, key):
        """Get Item."""
        return self[key]


class DirectionError(ValueError):
    """Direction Error."""
