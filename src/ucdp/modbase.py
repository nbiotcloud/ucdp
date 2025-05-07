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
Base Hardware Module.

[BaseMod][ucdp.modbase.BaseMod] defines the base interface which is **common to all hardware modules**.
"""

from abc import abstractmethod
from functools import cached_property
from inspect import getmro
from typing import Any, ClassVar, Optional, TypeAlias, Union, no_type_check

from aligntext import align
from caseconverter import snakecase
from uniquer import uniquetuple

from .assigns import Assigns, Drivers, Note, Source
from .baseclassinfo import get_baseclassinfos
from .clkrel import ClkRel
from .clkrelbase import BaseClkRel
from .const import Const
from .consts import UPWARDS
from .doc import Doc
from .docutil import doc_from_type
from .exceptions import LockError
from .expr import BoolOp, Expr
from .exprparser import ExprParser, Parseable, cast_booltype
from .flipflop import FlipFlop
from .ident import Ident, Idents
from .iterutil import namefilter
from .logging import LOGGER
from .modref import ModRef
from .modutil import get_modbaseinfos
from .mux import Mux
from .namespace import Namespace
from .nameutil import join_names, split_prefix
from .object import Field, NamedObject, Object, PrivateField, computed_field
from .orientation import FWD, IN, Direction, Orientation
from .param import Param
from .routepath import Routeables, RoutePath, parse_routepaths
from .signal import BaseSignal, Port, Signal
from .typebase import BaseType
from .typedescriptivestruct import DescriptiveStructType
from .typestruct import StructItem

ModTags: TypeAlias = set[str]


class BaseMod(NamedObject):
    """
    Hardware Module.

    Args:
        parent: Parent Module. `None` by default for top module.
        name: Instance name. Required if parent is provided.

    Keyword Args:
        title (str): Title
        descr (str): Description
        comment (str): Comment
        paramdict (dict): Parameter values for this instance.
    """

    filelists: ClassVar[Any] = ()
    tags: ClassVar[ModTags] = ModTags()

    parent: Optional["BaseMod"] = None
    paramdict: dict = Field(default_factory=dict, repr=False)

    title: str | None = None
    descr: str | None = None
    comment: str | None = None

    has_hiername: bool = True

    virtual: bool = False

    # private

    drivers: Drivers = Field(default_factory=Drivers, init=False, repr=False)
    namespace: Idents = Field(default_factory=Idents, init=False, repr=False)
    params: Idents = Field(default_factory=Idents, init=False, repr=False)
    ports: Idents = Field(default_factory=Idents, init=False, repr=False)
    portssignals: Idents = Field(default_factory=Idents, init=False, repr=False)
    insts: Namespace = Field(default_factory=Namespace, init=False, repr=False)

    _has_build_dep: bool = PrivateField(default=False)
    _has_build_final: bool = PrivateField(default=False)

    __is_locked: bool = PrivateField(default=False)
    __instcons: dict[str, tuple[Assigns, ExprParser]] = PrivateField(default_factory=dict)
    __flipflops: dict[int, FlipFlop] = PrivateField(default_factory=dict)
    __muxes: Namespace = PrivateField(default_factory=Namespace)
    __parents = PrivateField(default_factory=list)

    def __init__(self, parent: Optional["BaseMod"] = None, name: str | None = None, **kwargs):
        cls = self.__class__
        if not cls.__name__.endswith("Mod"):
            raise NameError(f"Name of {cls} MUST end with 'Mod'")
        if not name:
            if parent:
                raise ValueError("'name' is required for sub modules.")
            name = snakecase(cls.__name__.removesuffix("Mod"))
        super().__init__(parent=parent, name=name, **kwargs)  # type: ignore[call-arg]

    @property
    def doc(self) -> Doc:
        """Documentation."""
        return Doc(title=self.title, descr=self.descr, comment=self.comment)

    @property
    def basename(self) -> str:
        """Base Name Derived From Instance."""
        return split_prefix(self.name)[1]

    @property
    @abstractmethod
    def modname(self) -> str:
        """Module Name."""

    @property
    @abstractmethod
    def topmodname(self) -> str:
        """Top Module Name."""

    @property
    def libname(self) -> str:
        """Library Name."""
        return self.libpath.name

    @property
    @abstractmethod
    def libpath(self) -> str:
        """Library Path."""

    @cached_property
    def qualname(self) -> str:
        """Qualified Name (Library Name + Module Name)."""
        return f"{self.libname}.{self.modname}"

    @cached_property
    def basequalnames(self) -> tuple[str, ...]:
        """Qualified Name (Library Name + Module Name) of Base Modules."""
        return uniquetuple(f"{bci.libname}.{bci.modname}" for bci in get_modbaseinfos(self))

    @classmethod
    def get_modref(cls) -> ModRef:
        """Python Class Reference."""
        bci = next(get_baseclassinfos(cls))
        return ModRef(
            libname=bci.libname,
            modname=bci.modname,
            modclsname=bci.clsname,
        )

    @classmethod
    def get_basemodrefs(cls) -> tuple[ModRef, ...]:
        """Python Class Reference."""
        return tuple(
            ModRef(
                libname=bci.libname,
                modname=bci.modname,
                modclsname=bci.clsname,
            )
            for bci in get_modbaseinfos(cls)
        )

    @property
    def hiername(self) -> str:
        """Hierarchical Name."""
        mod: BaseMod | None = self
        names: list[str] = []
        while mod is not None:
            if mod.has_hiername:
                names.insert(0, split_prefix(mod.name)[1])
            mod = mod.parent
        return join_names(*names)

    @property
    @abstractmethod
    def is_tb(self) -> bool:
        """Determine if module belongs to Testbench or Design."""

    @property
    def path(self) -> tuple["BaseMod", ...]:
        """Path."""
        path = [self]
        parent = self.parent
        while parent:
            path.insert(0, parent)
            parent = parent.parent
        return tuple(path)

    @property
    def inst(self) -> str:
        """Path String."""
        parts: list[str] = []
        mod = self
        while mod.parent:
            parts.insert(0, mod.name)
            mod = mod.parent
        parts.insert(0, mod.modname)
        return "/".join(parts)

    @computed_field
    @cached_property
    def assigns(self) -> Assigns:
        """Assignments."""
        return Assigns(targets=self.portssignals, sources=self.namespace, drivers=self.drivers)

    @computed_field
    @cached_property
    def parser(self) -> ExprParser:
        """Expression Parser."""
        return ExprParser(namespace=self.namespace, context=str(self))

    @computed_field
    @cached_property
    def _router(self) -> "Router":
        """Router."""
        return Router(mod=self)

    @property
    def parents(self) -> tuple["BaseMod", ...]:
        """Parents."""
        return tuple(self.__parents)

    @classmethod
    def build_top(cls, **kwargs) -> "BaseMod":
        """
        Build Top Instance.

        Return module as top module.
        """
        return cls(**kwargs)

    def add_param(
        self,
        arg: BaseType | Param,
        name: str | None = None,
        title: str | None = None,
        descr: str | None = None,
        comment: str | None = None,
        ifdef: str | None = None,
        exist_ok: bool = False,
    ) -> Param:
        """
        Add Module Parameter (:any:`Param`).

        Args:
            arg: Type or Parameter
            name: Name. Mandatory if arg is a Type.

        Keyword Args:
            title: Full Spoken Name.
            descr: Documentation Description.
            comment: Source Code Comment.
            ifdef: IFDEF pragma
            exist_ok: Do not complain about already existing item
        """
        if isinstance(arg, Param):
            value = self.paramdict.pop(arg.name, None)
            param: Param = arg.new(value=value)
            assert name is None
        else:
            type_: BaseType = arg
            doc = doc_from_type(type_, title=title, descr=descr, comment=comment)
            value = self.paramdict.pop(name, None)
            param = Param(type_=type_, name=name, doc=doc, ifdef=ifdef, value=value)
        if self.__is_locked:
            raise LockError(f"{self}: Cannot add parameter {name!r}.")
        self.namespace.add(param, exist_ok=exist_ok)
        self.params.add(param, exist_ok=exist_ok)
        return param

    def add_const(
        self,
        arg: BaseType | Const,
        name: str | None = None,
        title: str | None = None,
        descr: str | None = None,
        comment: str | None = None,
        ifdef: str | None = None,
        exist_ok: bool = False,
    ) -> Const:
        """
        Add Module Internal Constant (:any:`Const`).

        Args:
            arg: Type or Parameter
            name: Name. Mandatory if arg is a Type.

        Keyword Args:
            title: Full Spoken Name.
            descr: Documentation Description.
            comment: Source Code Comment.
            ifdef: IFDEF pragma
            exist_ok: Do not complain about already existing item
        """
        if isinstance(arg, Const):
            const: Const = arg
            assert name is None
        else:
            type_: BaseType = arg
            doc = doc_from_type(type_, title=title, descr=descr, comment=comment)
            const = Const(type_=type_, name=name, doc=doc, ifdef=ifdef)
        if self.__is_locked:
            raise LockError(f"{self}: Cannot add constant {name!r}.")
        self.namespace.add(const, exist_ok=exist_ok)
        return const

    def add_type_consts(self, type_: BaseType, exist_ok: bool = False, only=None, name=None, item_suffix="e"):
        """
        Add description of `type_` as local parameters.

        Args:
            type_: Type to be described.

        Keyword Args:
            exist_ok (bool): Do not complain, if parameter already exists.
            name (str): Name of the local parameter. Base on `type_` name by default.
            only (str): Limit parameters to these listed in here, separated by ';'
            item_suffix (str): Enumeration Suffix.
        """
        name = name or snakecase(type_.__class__.__name__.removesuffix("Type"))
        if only:
            patfilter = namefilter(only)

            def filter_(item: StructItem):
                return patfilter(item.name)

            type_ = DescriptiveStructType(type_, filter_=filter_, enumitem_suffix=item_suffix)
        else:
            type_ = DescriptiveStructType(type_, enumitem_suffix=item_suffix)
        self.add_const(type_, name, exist_ok=exist_ok, title=type_.title, descr=type_.descr, comment=type_.comment)

    def add_port(
        self,
        type_: BaseType,
        name: str,
        direction: Direction | None = None,
        title: str | None = None,
        descr: str | None = None,
        comment: str | None = None,
        ifdef: str | None = None,
        route: Routeables | None = None,
        clkrel: str | Port | BaseClkRel | None = None,
    ) -> Port:
        """
        Add Module Port (:any:`Port`).

        Args:
            type_: Type.
            name: Name.

        Keyword Args:
            direction: Signal Direction. Automatically detected if `name` ends with '_i', '_o', '_io'.
            title: Full Spoken Name.
            descr: Documentation Description.
            comment: Source Code Comment. Default is 'title'
            ifdef: IFDEF mapping
            route: Routes (iterable or string separated by ';')
            clkrel: Clock relation.
        """
        doc = doc_from_type(type_, title, descr, comment)
        if direction is None:
            direction = Direction.from_name(name) or IN
        if clkrel is not None:
            clkrel = self._resolve_clkrel(clkrel)
        port = Port(type_, name, direction=direction, doc=doc, ifdef=ifdef, clkrel=clkrel)
        if self.__is_locked:
            raise LockError(f"{self}: Cannot add port {name!r}.")
        self.namespace[name] = port
        self.portssignals[name] = port
        self.ports[name] = port
        for routepath in parse_routepaths(route):
            self._router.add(RoutePath(expr=port), routepath)
        return port

    def _resolve_clkrel(self, clkrel: str | Port | BaseClkRel) -> BaseClkRel:
        if isinstance(clkrel, BaseClkRel):
            return clkrel
        if isinstance(clkrel, BaseSignal):
            return ClkRel(clk=clkrel)
        if isinstance(clkrel, str):
            port = self.ports[clkrel]
            return ClkRel(clk=port)
        raise ValueError(f"Invalid {clkrel=}")

    def add_signal(
        self,
        type_: BaseType,
        name: str,
        direction: Orientation = FWD,
        title: str | None = None,
        descr: str | None = None,
        comment: str | None = None,
        ifdef: str | None = None,
        route: Routeables | None = None,
        clkrel: str | Port | BaseClkRel | None = None,
    ) -> Signal:
        """
        Add Module Internal Signal (:any:`Signal`).

        Args:
            type_: Type.
            name: Name.

        Keyword Args:
            direction: Signal Direction. Automatically detected if `name` ends with '_i', '_o', '_io'.
            title: Full Spoken Name.
            descr: Documentation Description.
            comment: Source Code Comment. Default is 'title'
            ifdef: IFDEF mapping
            route: Routes (iterable or string separated by ';')
            clkrel: Clock relation.
        """
        doc = doc_from_type(type_, title, descr, comment)
        if clkrel is not None:
            clkrel = self._resolve_clkrel(clkrel)
        signal = Signal(type_, name, direction=direction, doc=doc, ifdef=ifdef, clkrel=clkrel)
        if self.__is_locked:
            raise LockError(f"{self}: Cannot add signal {name!r}.")
        self.namespace[name] = signal
        self.portssignals[name] = signal
        for routepath in parse_routepaths(route):
            self._router.add(RoutePath(expr=signal), routepath)
        return signal

    def add_port_or_signal(
        self,
        type_: BaseType,
        name: str,
        direction: Direction | None = None,
        title: str | None = None,
        descr: str | None = None,
        comment: str | None = None,
        ifdef: str | None = None,
        route: Routeables | None = None,
        clkrel: str | Port | BaseClkRel | None = None,
    ) -> BaseSignal:
        """
        Add Module Port (:any:`Port`) or Signal (:any:`Signal`) depending on name.

        Args:
            type_: Type.
            name: Name.

        Keyword Args:
            direction: Signal Direction. Automatically detected if `name` ends with '_i', '_o', '_io'.
            title: Full Spoken Name.
            descr: Documentation Description.
            comment: Source Code Comment. Default is 'title'
            ifdef: IFDEF mapping
            route: Routes (iterable or string separated by ';')
            clkrel: Clock relation.
        """
        if direction is None:
            direction = Direction.from_name(name)
        if direction is None:
            return self.add_signal(
                type_,
                name,
                title=title,
                descr=descr,
                comment=comment,
                ifdef=ifdef,
                route=route,
                clkrel=clkrel,
            )
        return self.add_port(
            type_,
            name,
            direction=direction,
            title=title,
            descr=descr,
            comment=comment,
            ifdef=ifdef,
            route=route,
            clkrel=clkrel,
        )

    def set_parent(self, parent: "BaseMod") -> None:
        """
        Set Parent.

        Do not use this method, until you really really really know what you do.
        """
        self.__parents.append(parent)

    def assign(
        self,
        target: Parseable,
        source: Parseable | Note,
        cast: bool = False,
        overwrite: bool = False,
    ):
        """
        Assign `target` to `source`.

        The assignment is done **without** routing.

        Args:
            target: Target to be driven. Must be known within this module.
            source: Source driving target. Must be known within this module.

        Keyword Args:
            cast (bool): Cast. `False` by default.
            overwrite (bool): Overwrite existing assignment.
            filter_ (str, Callable): Target names or function to filter target identifiers.
        """
        if self.__is_locked:
            raise LockError(f"{self}: Cannot add assign '{source}' to '{target}'.")
        parser = self.parser
        assigntarget: BaseSignal = parser.parse(target, only=BaseSignal)  # type: ignore[assignment]
        assignsource: Source = parser.parse_note(source, only=Source)  # type: ignore[arg-type]
        self.assigns.set(assigntarget, assignsource, cast=cast, overwrite=overwrite)

    def add_inst(self, inst: "BaseMod") -> None:
        """
        Add Submodule `inst`.

        Args:
            inst: Instance.
        """
        if self.__is_locked:
            raise LockError(f"{self}: Cannot add instance '{inst}'.")
        inst.set_parent(self)
        self.insts.add(inst)  # type: ignore[arg-type]
        assigns = Assigns(targets=inst.ports, sources=self.namespace, drivers=Drivers(), inst=True)
        parser = ExprParser(namespace=inst.ports, context=str(inst))
        self.__instcons[inst.name] = assigns, parser

    def get_inst(self, inst_or_name: Union["BaseMod", str]) -> "BaseMod":
        """
        Get Module Instance.
        """
        if not isinstance(inst_or_name, str):
            try:
                return self.insts[inst_or_name.name]
            except KeyError:
                raise ValueError(f"{inst_or_name} is not a sub-module of {self}") from None
        inst = self
        for part in inst_or_name.split("/"):
            if part == UPWARDS:
                if inst.parent is None:
                    raise ValueError(f"{self}: {inst} has no parent.")
                inst = inst.parent
            else:
                try:
                    inst = inst.insts.get_dym(part)  # type: ignore[assignment]
                except ValueError as exc:
                    raise ValueError(f"{self} has no sub-module {exc}") from None
        return inst

    def set_instcon(
        self,
        inst: Union["BaseMod", str],
        port: Parseable,
        expr: Parseable,
        cast: bool = False,
        overwrite: bool = False,
    ):
        """
        Connect `port` of `inst` to `expr` without routing.

        The assignment is done **without** routing.

        Args:
            inst: Module Instance
            port: Port to be connected. Must be known within module instance.
            expr: Expression. Must be known within this module.

        Keyword Args:
            cast: Cast. `False` by default.
            overwrite: Overwrite existing assignment.
        """
        if self.__is_locked:
            raise LockError(f"{self}: Cannot connect '{port}' of'{inst}' to '{expr}'.")
        mod: BaseMod = self.get_inst(inst)
        assigns, parser = self.__instcons[mod.name]
        assigntarget: BaseSignal = parser.parse(port, only=BaseSignal)  # type: ignore[assignment]
        assignsource: Source = self.parser.parse_note(expr, only=Source)  # type: ignore[arg-type]
        assigns.set(assigntarget, assignsource, cast=cast, overwrite=overwrite)

    def get_instcons(self, inst: Union["BaseMod", str]) -> Assigns:
        """Retrieve All Instance Connections Of `inst`."""
        mod: BaseMod = self.get_inst(inst)
        return self.__instcons[mod.name][0]

    def add_flipflop(
        self,
        type_: BaseType,
        name: str,
        clk: Parseable,
        rst_an: Parseable,
        nxt: Parseable | None = None,
        rst: Parseable | None = None,
        ena: Parseable | None = None,
        route: Routeables | None = None,
    ) -> Signal:
        """
        Add Module Internal Flip-Flop.

        Args:
            type_: Type.
            name: Name.
            clk: Clock. Module Clock by default.
            rst_an: Reset. Module Reset by default.

        Keyword Args:
            nxt: Next Value. Basename of `name` with _nxt_s by default.
            rst: Synchronous Reset.
            ena: Enable Condition.
            route: Routing of flip-flop output.
        """
        parser = self.parser
        if self.__is_locked:
            raise LockError(f"{self}: Cannot add flipflop {name!r}.")
        out = self.add_signal(type_, name)
        # clk
        clk_sig: BaseSignal = parser.parse(clk, only=BaseSignal)  # type: ignore[assignment]
        # rst_an
        rst_an_sig: BaseSignal = parser.parse(rst_an, only=BaseSignal)  # type: ignore[assignment]
        # nxt
        if nxt is None:
            nxt = self.add_signal(type_, f"{out.basename}_nxt_s")
        else:
            nxt = parser.parse(nxt)
            # TODO: check connectable of nxt and out?
        # rst
        rst_expr: BoolOp | None = cast_booltype(parser.parse(rst)) if rst is not None else None
        # ena
        ena_expr: BoolOp | None = cast_booltype(parser.parse(ena)) if ena is not None else None
        # flipflop
        flipflop = self._create_flipflop(clk_sig, rst_an_sig, rst_expr, ena_expr)
        flipflop.set(out, nxt)
        # route
        for routepath in parse_routepaths(route):
            self._router.add(RoutePath(expr=out), routepath)
        return out

    def _create_flipflop(
        self,
        clk: BaseSignal,
        rst_an: BaseSignal,
        rst: BoolOp | None = None,
        ena: BoolOp | None = None,
    ) -> FlipFlop:
        flipflops = self.__flipflops
        key = hash((clk, rst_an, rst, ena))
        try:
            return flipflops[key]
        except KeyError:
            pass
        flipflops[key] = flipflop = FlipFlop(
            clk=clk,
            rst_an=rst_an,
            rst=rst,
            ena=ena,
            targets=self.portssignals,
            sources=self.namespace,
            drivers=self.drivers,
        )
        return flipflop

    @property
    def flipflops(self) -> tuple[FlipFlop, ...]:
        """
        Flip Flops.
        """
        return tuple(self.__flipflops.values())

    def add_mux(
        self,
        name,
        title: str | None = None,
        descr: str | None = None,
        comment: str | None = None,
    ) -> Mux:
        """
        Add Multiplexer with `name` And Return It For Filling.

        Args:
            name (str): Name.

        Keyword Args:
            title (str): Full Spoken Name.
            descr (str): Documentation Description.
            comment (str): Source Code Comment.

        See :any:`Mux.set()` how to fill the multiplexer and the example above.
        """
        if self.__is_locked:
            raise LockError(f"{self}: Cannot add mux {name!r}.")
        doc = Doc(title=title, descr=descr, comment=comment)
        self.__muxes[name] = mux = Mux(
            name=name,
            targets=self.portssignals,
            namespace=self.namespace,
            # drivers=self.drivers,
            parser=self.parser,
            doc=doc,
        )
        return mux

    @property
    def muxes(self) -> tuple[Mux, ...]:
        """
        Iterate over all Multiplexer.
        """
        return tuple(self.__muxes.values())

    def get_mux(self, mux: Mux | str) -> Mux:
        """Get Multiplexer."""
        if not isinstance(mux, str):
            return self.__muxes.get_dym(mux.name)  # type: ignore[return-value]
        return self.__muxes.get_dym(mux)  # type: ignore[return-value]

    @property
    def is_locked(self) -> bool:
        """
        Return If Module Is Already Completed And Locked For Modification.

        Locking is done by the build process **automatically** and **MUST NOT** be done earlier or later.
        Use a different module type or enumeration or struct type, if you have issues with locking.
        """
        return self.__is_locked

    def lock(self):
        """
        Lock.

        Locking is done via this method by the build process **automatically** and **MUST NOT** be done earlier or
        later. Use a different module type or enumeration or struct type, if you have issues with locking.
        """
        if self.__is_locked:
            raise LockError(f"{self} is already locked. Cannot lock again.")
        for _, obj in self:
            if isinstance(obj, Namespace):
                obj.lock()
        self.__is_locked = True

    def check_lock(self):
        """Check if module is locked for modifications."""
        if self.__is_locked:
            raise LockError(f"{self}: Is already locked for modifications.")

    def con(self, port: Routeables, source: Routeables):
        """Connect `port` to `dest`."""
        parents = self.__parents
        if not parents:
            raise TypeError(f"{self} is top module. Connections cannot be made.")
        router = parents[-1]._router
        for subtarget in parse_routepaths(port, basepath=self.name):
            for subsource in parse_routepaths(source):
                router.add(subtarget, subsource)

    def route(self, target: Routeables, source: Routeables):
        """Route `source` to `target` within the actual module."""
        router = self._router
        for subtarget in parse_routepaths(target):
            for subsource in parse_routepaths(source):
                router.add(subtarget, subsource)

    def __str__(self):
        modref = self.get_modref()
        return f"<{modref}(inst={self.inst!r}, libname={self.libname!r}, modname={self.modname!r})>"

    def __repr__(self):
        modref = self.get_modref()
        return f"<{modref}(inst={self.inst!r}, libname={self.libname!r}, modname={self.modname!r})>"

    def get_overview(self) -> str:
        """
        Return Brief Module Overview.

        This Module Overview is intended to be overwritten by the user.
        """
        return ""

    def get_info(self, sub: bool = False) -> str:
        """Module Information."""
        header = f"## `{self.libname}.{self.modname}` (`{self.get_modref()}`)"
        parts = [
            header,
            self._get_ident_info("Parameters", self.params),
            self._get_ident_info("Ports", self.ports),
        ]
        if sub:
            parts.append(self._get_sub_info())
        return "\n\n".join(parts)

    def _get_ident_info(self, title: str, idents: Idents):
        def entry(level, ident):
            pre = "  " * level
            dinfo = f" ({ident.direction})" if ident.direction else ""
            return (
                f"{pre}{ident.name}{dinfo}",
                f"{pre}{ident.type_}",
            )

        parts = [
            f"### {title}",
            "",
        ]
        if idents:
            data = [("Name ", "Type"), ("----", "----")]
            data += [entry(level, ident) for level, ident in idents.leveliter()]
            parts.append(align(data, seps=(" | ", " |"), sepfirst="| "))
        else:
            parts.append("-")
        return "\n".join(parts)

    def _get_sub_info(self) -> str:
        parts = [
            "### Submodules",
            "",
        ]
        if self.insts:
            data = [("Name", "Module"), ("----", "------")]
            data += [(f"`{inst.name}`", f"`{inst.libname}.{inst.modname}`") for inst in self.insts]
            parts.append(align(data, seps=(" | ", " |"), sepfirst="| "))
        else:
            parts.append("-")
        return "\n".join(parts)


class Router(Object):
    """The One And Only Router."""

    mod: BaseMod
    __routes: list[tuple[RoutePath, RoutePath]] = PrivateField(default_factory=list)

    def add(self, tpath: RoutePath, spath: RoutePath) -> None:
        """Add route from `source` to `tpath`."""
        LOGGER.debug("%s: router: add '%s' to '%s'", self.mod, spath, tpath)
        self.__routes.append(self._create(tpath, spath))

    def flush(self) -> None:
        """Create Pending Routes."""
        for tpath, spath in self.__routes:
            tpathc, spathc = self._create(tpath, spath)
            self._route(tpathc, spathc)
        self.__routes.clear()

    def _create(self, tpath: RoutePath, spath: RoutePath) -> tuple[RoutePath, RoutePath]:
        if tpath.create:
            if self.__create(spath, tpath):
                tpath = tpath.new(create=False)
        elif spath.create:
            if self.__create(tpath, spath):
                spath = spath.new(create=False)
        return tpath, spath

    @no_type_check  # TODO: fix types
    def __create(self, rpath: RoutePath, cpath: RoutePath) -> bool:
        """Create `cpath` based on `rpath`."""
        assert not rpath.create
        assert cpath.create
        mod = self.mod
        # Resolve reference path
        try:
            rmod = mod.get_inst(rpath.path) if rpath.path else mod
            rident: Ident = rmod.parser.parse(rpath.expr, only=Ident)  # type: ignore[assignment]
            cmod = mod.get_inst(cpath.path) if cpath.path else mod
        except (ValueError, NameError, KeyError):
            return False
        self.__create_port_or_signal(cmod, rident, cpath.expr)
        return True

    @no_type_check  # TODO: fix types
    def _route(self, tpath: RoutePath, spath: RoutePath):  # noqa: C901, PLR0912, PLR0915
        mod = self.mod
        LOGGER.debug("%s router: routing %r to %r", mod, spath, tpath)
        # Referenced modules
        tmod = mod.get_inst(tpath.path) if tpath.path else mod
        smod = mod.get_inst(spath.path) if spath.path else mod
        # Referenced expression/signal
        texpr = tmod.parser.parse(tpath.expr) if not isinstance(tpath.expr, Note) else tpath.expr
        sexpr = smod.parser.parse(spath.expr) if not isinstance(spath.expr, Note) else spath.expr
        tident = None if not isinstance(texpr, Ident) else texpr
        sident = None if not isinstance(sexpr, Ident) else sexpr
        tparts = tpath.parts
        sparts = spath.parts
        # One of the both sides need to exist
        rident = tident or sident
        assert rident is not None
        direction = (
            tident.direction * sident.direction
            if tident and tident.direction is not None and sident and sident.direction is not None
            else rident.direction
        )

        cast = _merge_cast(tpath.cast, spath.cast)
        assert len(tparts) in (0, 1)
        assert len(sparts) in (0, 1)
        if tparts:
            # target is submodule
            assert tparts[0] != UPWARDS
            if sparts:
                assert sparts[0] != UPWARDS
                # source and target are submodules
                tcon = None if tident is None else mod.get_instcons(tmod).get(tident)
                scon = None if sident is None else mod.get_instcons(smod).get(sident)
                if tcon is None and scon is None:
                    modname = split_prefix(tmod.name)[1]
                    name = join_names(modname, rident.name, "s")
                    rsig = mod.add_signal(rident.type_, name, ifdef=rident.ifdef, direction=direction)
                    Router.__routesubmod(mod, tmod, rident, texpr, rsig, tname=tpath.expr, cast=tpath.cast)
                    Router.__routesubmod(mod, smod, rident, sexpr, rsig, tname=spath.expr, cast=spath.cast)
                elif tcon is None:
                    Router.__routesubmod(mod, tmod, rident, texpr, scon, tname=tpath.expr, cast=tpath.cast)
                elif scon is None:
                    Router.__routesubmod(mod, smod, rident, sexpr, tcon, tname=spath.expr, cast=spath.cast)
                else:
                    mod.assign(tcon, scon, cast=cast)
            else:
                tcon = None if tident is None else mod.get_instcons(tmod).get(tident)
                if tcon is None:
                    Router.__routesubmod(mod, tmod, rident, texpr, sexpr, tpath.expr, spath.expr, cast=cast)
                else:
                    if sexpr is None:
                        sexpr = Router.__create_port_or_signal(mod, rident, spath.expr)
                    mod.assign(tcon, sexpr, cast=cast)
        elif sparts:
            scon = None if sident is None else mod.get_instcons(smod).get(sident)
            assert sparts[0] != UPWARDS
            if scon is None:
                Router.__routesubmod(mod, smod, rident, sexpr, texpr, spath.expr, tpath.expr, cast=cast)
            else:
                if texpr is None:
                    texpr = Router.__create_port_or_signal(mod, rident, tpath.expr)
                mod.assign(scon, texpr, cast=cast)
        else:
            # connect signals of `mod`
            if texpr is None:
                texpr = Router.__create_port_or_signal(mod, rident, tpath.expr)
            if sexpr is None:
                sexpr = Router.__create_port_or_signal(mod, rident, spath.expr)
            mod.assign(texpr, sexpr, cast=cast)

    @staticmethod
    def __routesubmod(
        mod: BaseMod, submod: BaseMod, rident: Ident, texpr, sexpr, tname=None, sname=None, cast=False
    ) -> Expr:
        if texpr is None:
            assert tname is not None
            assert rident is not None and rident.type_
            texpr = submod.add_port(rident.type_, tname, ifdef=rident.ifdef)
        if sexpr is None:
            sexpr = Router.__create_port_or_signal(mod, rident, sname)
        if not isinstance(texpr, Port):
            raise ValueError(f"Cannot route {type(texpr)} to module instance {submod}")
        try:
            mod.set_instcon(submod, texpr, sexpr, cast=cast)
        except TypeError as err:
            raise TypeError(f"{mod}: {err}") from None
        return sexpr

    @staticmethod
    def __create_port_or_signal(mod: BaseMod, rident: Ident, name: str) -> BaseSignal:
        assert isinstance(rident, Ident)
        assert name is not None
        assert rident is not None and rident.type_ is not None, (mod, name)
        type_ = rident.type_
        direction = Direction.from_name(name)
        signal: BaseSignal
        if direction is not None:
            signal = mod.add_port(type_, name, ifdef=rident.ifdef, direction=direction)
        else:
            signal = mod.add_signal(type_, name, ifdef=rident.ifdef)
        LOGGER.debug("%s: router: creating %r", mod, signal)
        return signal


def _merge_cast(one, other):
    # TODO: get rid of this.
    if one or other:
        return True
    if one is None or other is None:
        return None
    return False


ModCls: TypeAlias = type[BaseMod]
ModClss: TypeAlias = set[type[BaseMod]]


def get_modbaseclss(cls):
    """Get Module Base Classes."""
    clss = []
    for basecls in getmro(cls):
        if basecls is BaseMod:
            break
        clss.append(basecls)
    return clss
