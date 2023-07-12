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
Hardware Module.

Do **not** use :any:`BaseMod` as direct base class for your module implementation. See its friends:

* :any:`AMod`
* :any:`AImportedMod`
* :any:`ATailoredMod`
* :any:`CoreMod`
* :any:`AConfigurableMod`
* :any:`ATbMod`

:any:`BaseMod` defines the base interface which is **common to all hardware modules**.
"""
from inspect import getfile, getmro
from pathlib import Path
from typing import Dict, Generator, Optional, Tuple, Union

from attrs.exceptions import FrozenInstanceError
from caseconverter import snakecase

from ..assigns import Assigns, DirectionError
from ..attrs import NOTHING, astuple, define, field, frozen
from ..const import Const
from ..doc import Doc
from ..expr import Expr, cast_booltype, parse
from ..flipflop import FlipFlop
from ..ident import Idents
from ..mux import Mux
from ..namespace import LockError, Namespace
from ..nameutil import get_snakecasename, join_names, split_suffix, validate_identifier
from ..param import Param
from ..router import RoutePath, Router, parsepath, parsepaths
from ..signal import ASignal, Port, Signal
from ..types.base import AType
from ..types.clkrst import ClkType, RstAnType
from ..types.descriptivestruct import DescriptiveStructType
from ..types.orientation import FWD, IN, INOUT, OUT, AOrientation, Direction
from ..util import namefilter, split


def mod(maybe_cls=None, mutable=None):  # type: ignore
    """Decorator needed for all modules with `hw.attrib`."""

    if mutable:
        mutable = split(mutable)

        def _setattr(self, name, value):
            if name not in mutable:
                raise FrozenInstanceError()
            object.__setattr__(self, name, value)

        def wrap(cls):
            wrapped = define(cls, repr=False, frozen=True, init=False)

            wrapped.__setattr__ = _setattr

            return wrapped

    else:

        def wrap(cls):
            return define(cls, repr=False, frozen=True, init=False)

    if maybe_cls is None:
        return wrap
    return wrap(maybe_cls)


@frozen(init=False, repr=False)
class BaseMod:

    """
    Hardware Module.
    """

    # Args:
    #     parent (BaseMod): Parent Module. `None` by default for top module.
    #     name (str): Instance name. Required if parent is provided.

    # Keyword Args:
    #     title (str): Title
    #     descr (str): Description
    #     comment (str): Comment
    #     maninst (bool): Manual instantiation, track module as submodule, but module has to be instantiated manually
    #                     within source code.
    #     is_hull (bool): Just implement an empty shell with tied outputs.
    #     paramdict (dict): Parameter values for this instance.
    #     modname (str): Module name, derived from classname by default and ends with `_hull` in case of `is_hull=True`.
    #                    Use default whenever possible!
    #     libname (str): Library name, derived from path of python file.
    #                    Use default whenever possible!
    #     addrmap_name (str): Address map Name
    #                         Use default whenever possible!
    #     addrmap_hiername (str): Hierarchical address map name, derived from module hierarchy.
    #                             Use default whenever possible!

    # Define a module:

    # >>> import ucdp
    # >>> class SelType(ucdp.AEnumType):
    # ...     keytype = ucdp.UintType(2, default=2)
    # ...
    # ...     def _build(self):
    # ...         self._add(0, "my_a")
    # ...         self._add(1, "my_b")
    # ...         self._add(2, "my_c")
    # >>> class AdderMod(ucdp.AMod):
    # ...
    # ...     copyright_start_year = 2020
    # ...     copyright_end_year = 2022
    # ...
    # ...     def _build(self):
    # ...         width_p = self.add_param(ucdp.IntegerType(default=16), 'width_p')
    # ...         datatype = ucdp.UintType(width_p)
    # ...         self.add_port(datatype, "a_i")
    # ...         self.add_port(datatype, "b_i")
    # ...         self.add_port(datatype, "y_o")
    # >>> class AluMod(ucdp.AMod):
    # ...
    # ...     copyright_start_year = 2020
    # ...     copyright_end_year = 2022
    # ...
    # ...     def _build(self):
    # ...         width_p = self.add_param(ucdp.IntegerType(default=16), 'width_p')
    # ...         datatype = ucdp.UintType(width_p)
    # ...         self.add_localparam(datatype.new(default=(2**int(width_p)-1)), 'max_p')
    # ...         self.add_port(ucdp.ClkRstAnType())
    # ...         self.add_port(datatype, "a_i")
    # ...         self.add_port(datatype, "b_i")
    # ...         self.add_port(datatype, "c_i")
    # ...         self.add_port(datatype, "y_o")
    # ...         self.add_port(SelType(), "sel_i")
    # ...         self.add_signal(ucdp.BitType(), "max_s")
    # ...         self.add_signal(datatype, "my_s")
    # ...         self.add_flipflop(datatype, "data_r", nxt="my_s")
    # ...         self.add_signal(datatype, "mux_s")
    # ...         mainmux = self.add_mux("main")
    # ...         mainmux.set("sel_i", "my_a", "y_o", "a_i")
    # ...         mainmux.set("sel_i", "my_b", "y_o", "b_i")
    # ...         mainmux.set("sel_i", "my_c", "y_o", "c_i")
    # ...         adder = AdderMod(self, "u_adder0")
    # ...         adder.con("a_i", "a_i")
    # ...         adder.con("b_i", "b_i")

    # Instantiate a module:

    # >>> class TopMod(ucdp.AMod):
    # ...
    # ...     copyright_start_year = 2020
    # ...     copyright_end_year = 2022
    # ...
    # ...     def _build(self):
    # ...         AluMod(self, 'u_alu')

    # The top module

    # >>> top = TopMod.build_top()
    # >>> top
    # TopMod('top')
    # >>> alu = top.get_inst('u_alu')
    # >>> alu
    # AluMod('top/u_alu')
    # >>> adder = top.get_inst('u_alu/u_adder0')
    # >>> adder
    # AdderMod('top/u_alu/u_adder0')

    # Class attributes which **might** be set by child classes (see example above)

    # * `copyright_start_year` - First year of edit.
    # * `copyright_end_year` - Latest year of edit
    # * `module_id` - 0 by default.
    # * `no_codecov` - Disable code coverage
    # * `hdl` - HDL implementation enable **OR** list of targets
    # * `hdl_gen` - Code Generation Mode - FULL by default.
    # * `hdl_incfilenames` - List of HDL include files to be listed at the top of the file.
    # * `hdl_incdirs` - List of HDL include search paths.
    # * `is_model` - module is just a model, not synthesizeable
    # * `is_tb` - module is for testbench only, not synthesizeable
    # * `data_suffix` - Suffix for data files
    # * `has_liberty` - Module has liberty file
    # * `has_lef` - Module has LEF file
    # * `has_upf` - Module has UPF file

    # >>> for name in ('copyright_start_year', 'copyright_end_year', 'module_id', 'no_codecov',
    # ...              'hdl', 'hdl_gen', 'hdl_incfilenames', 'hdl_incdirs',
    # ...              'is_model', 'is_tb', 'data_suffix', 'has_liberty'):
    # ...     print(f'{name:<20s}: {getattr(top, name)}')
    # copyright_start_year: 2020
    # copyright_end_year  : 2022
    # module_id           : 0
    # no_codecov          : False
    # hdl                 : True
    # hdl_gen             : Gen.FULL
    # hdl_incfilenames    : ['ucdp.svh']
    # hdl_incdirs         : ['${SIDEHWHOME}/inc']
    # is_model            : False
    # is_tb               : False
    # data_suffix         : None
    # has_liberty         : False

    # Every hardware module has these attributes:

    # * **modbasenames** - :any:`tuple` module basenames derived from python class hierarchy.
    #   simple modules just contain one name:

    #     >>> top.modbasenames
    #     ('top',)
    #     >>> alu.modbasenames
    #     ('alu',)

    # * **path** - :any:`tuple` with hierarchial path members from top down to module itself

    #     >>> top.path
    #     ('top',)
    #     >>> alu.path
    #     ('top', 'u_alu')

    # * **pathstr** - :any:`str` with hierarchial path

    #     >>> top.pathstr
    #     'top'
    #     >>> alu.pathstr
    #     'top/u_alu'

    # * **drivers** - :any:`dict` with signal and port drivers

    #     >>> top.drivers
    #     {}
    #     >>> alu.drivers
    #     {}

    # * **namespace** - :any:`Idents` with all parameters, local parameters, ports and signals

    #     >>> for item in top.namespace:
    #     ...     item
    #     >>> for item in alu.namespace:
    #     ...     item
    #     Param(IntegerType(default=16), 'width_p')
    #     LocalParam(UintType(Param(IntegerType(default=16), 'width_p'), default=65535), 'max_p')
    #     Port(ClkRstAnType(), doc=Doc(title='Clock and Reset'))
    #     Port(UintType(Param(IntegerType(default=16), 'width_p')), name='a_i')
    #     Port(UintType(Param(IntegerType(default=16), 'width_p')), name='b_i')
    #     Port(UintType(Param(IntegerType(default=16), 'width_p')), name='c_i')
    #     Port(UintType(Param(IntegerType(default=16), 'width_p')), name='y_o')
    #     Port(SelType(), name='sel_i')
    #     Signal(BitType(), 'max_s')
    #     Signal(UintType(Param(IntegerType(default=16), 'width_p')), 'my_s')
    #     Signal(UintType(Param(IntegerType(default=16), 'width_p')), 'data_r')
    #     Signal(UintType(Param(IntegerType(default=16), 'width_p')), 'mux_s')
    #     LocalParam(DescriptiveStructType(SelType()), 'sel')

    # * **ports** - :any:`Idents` with all ports

    #     >>> for item in top.ports:
    #     ...     item
    #     >>> for item in alu.ports:
    #     ...     item
    #     Port(ClkRstAnType(), doc=Doc(title='Clock and Reset'))
    #     Port(UintType(Param(IntegerType(default=16), 'width_p')), name='a_i')
    #     Port(UintType(Param(IntegerType(default=16), 'width_p')), name='b_i')
    #     Port(UintType(Param(IntegerType(default=16), 'width_p')), name='c_i')
    #     Port(UintType(Param(IntegerType(default=16), 'width_p')), name='y_o')
    #     Port(SelType(), name='sel_i')

    # * **portssignals** - :any:`Idents` with all **signals and ports**

    #     >>> for item in top.portssignals:
    #     ...     item
    #     >>> for item in alu.portssignals:
    #     ...     item
    #     Port(ClkRstAnType(), doc=Doc(title='Clock and Reset'))
    #     Port(UintType(Param(IntegerType(default=16), 'width_p')), name='a_i')
    #     Port(UintType(Param(IntegerType(default=16), 'width_p')), name='b_i')
    #     Port(UintType(Param(IntegerType(default=16), 'width_p')), name='c_i')
    #     Port(UintType(Param(IntegerType(default=16), 'width_p')), name='y_o')
    #     Port(SelType(), name='sel_i')
    #     Signal(BitType(), 'max_s')
    #     Signal(UintType(Param(IntegerType(default=16), 'width_p')), 'my_s')
    #     Signal(UintType(Param(IntegerType(default=16), 'width_p')), 'data_r')
    #     Signal(UintType(Param(IntegerType(default=16), 'width_p')), 'mux_s')

    # * **insts** - :any:`Namespace` with all submodule instances

    #     >>> for item in top.insts:
    #     ...     item
    #     AluMod('top/u_alu')
    #     >>> for item in alu.insts:
    #     ...     item
    #     AdderMod('top/u_alu/u_adder0')

    # TODO: Optional Rule Attributes
    # """

    # pylint: disable=too-many-arguments,too-many-public-methods

    # class attributes

    copyright_years: Optional[int] = None  # current by default
    copyright_start_year: Optional[int] = None  # current by default

    title: Optional[str] = None
    descr: Optional[str] = None
    comment: Optional[str] = None

    has_hiername: bool = False

    # instance attributes

    parent: "BaseMod" = field(default=None)
    name: str = field()
    doc: Doc = field(default=Doc(), kw_only=True)
    paramdict: dict = field(factory=dict, kw_only=True, repr=False)

    # private

    modname: str = field(init=False, repr=False)
    modbasenames: Tuple[str, ...] = field(init=False, repr=False)
    libname: str = field(init=False, repr=False)
    path: Tuple[str, ...] = field(init=False, repr=False)
    _locked: bool = field(default=False, init=False, repr=False)
    drivers: dict = field(factory=dict, init=False, repr=False)
    namespace: Idents = field(factory=Idents, init=False, repr=False)
    params: Idents = field(factory=Idents, init=False, repr=False)
    ports: Idents = field(factory=Idents, init=False, repr=False)
    portssignals: Idents = field(factory=Idents, init=False, repr=False)
    insts: Namespace = field(factory=Namespace, init=False, repr=False)
    assigns: Assigns = field(init=False, repr=False)
    __instcons: Dict[str, Assigns] = field(factory=dict, init=False, repr=False)
    __flipflops: dict = field(factory=dict, init=False, repr=False)
    __muxes: Namespace = field(factory=Namespace, init=False, repr=False)
    __parents = field(factory=list, init=False, repr=False)
    __router = field(init=False, repr=False)

    _mroidx = -1

    def __init__(self, *args, **kwargs):
        cls = self.__class__
        kwargs["doc"] = Doc(
            title=kwargs.pop("title", cls.title) or None,
            descr=kwargs.pop("descr", cls.descr) or None,
            comment=kwargs.pop("comment", cls.comment) or None,
        )
        if not cls.__name__.endswith("Mod"):
            raise ValueError(f"Name of {cls} MUST end with 'Mod'")
        if cls.__name__ == "BaseMod":
            raise ValueError("BaseMod is forbidden to be used directly")
        # pylint: disable=no-member
        self.__attrs_init__(*args, **kwargs)

    @name.default
    def _name_default(self):
        if self.parent:
            raise ValueError("'name' is required for sub modules.")
        return get_modname(self.__class__)

    @property
    def hiername(self):
        """Hierarchical name"""
        basename = self.name.removeprefix("u_") if self.has_hiername else ""
        if basename and self.parent:
            return join_names(self.parent.hiername, basename, concat="_")
        return basename

    @modname.default
    def _modname_default(self):
        return get_modname(self.__class__)

    @modbasenames.default
    def _modbasenames_default(self) -> Tuple[str, ...]:
        return tuple(get_modname(cls) for cls in get_mro(self.__class__))

    @libname.default
    def _libname_default(self):
        try:
            return self.__class__.libname
        except AttributeError:
            filepath = Path(getfile(self.__class__))
            return filepath.parts[-2]

    @path.default
    def _path_default(self):
        path = [self.name]
        parent = self.parent
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        return tuple(path)

    @assigns.default
    def _assigns_default(self):
        return Assigns(self.portssignals, self.namespace, drivers=self.drivers)

    @__router.default
    def _router_default(self):
        return Router(self)

    def _route(self):
        self.__router.flush()

    @property
    def basename(self):
        """Base Name."""
        return self.name.removeprefix("u_")

    @property
    def pathstr(self):
        """Path String."""
        return "/".join(self.path)

    @property
    def parents(self):
        """Parents."""
        return tuple(self.__parents)

    @classmethod
    def build_top(cls, **kwargs) -> "BaseMod":
        """
        Build Top Instance.

        Return module as top module.
        """
        return cls(**kwargs)

    def parse(self, expr, only=None, types=None) -> Expr:
        """Parse Expression Within Namespace Of This Module."""
        return parse(expr, namespace=self.namespace, only=only, types=types, context=str(self))

    def add_param(
        self,
        type_or_param: Union[AType, Param],
        name: Optional[str] = None,
        title: str = NOTHING,  # type: ignore
        descr: str = NOTHING,  # type: ignore
        comment: str = NOTHING,  # type: ignore
        ifdef: str = NOTHING,  # type: ignore
        exist_ok: bool = False,
    ) -> Param:
        """
        Add Module Parameter (:any:`Param`).

        Args:
            type_or_aparam: Type or Parameter
            name (str): Name. Mandatory if type_or_aparam is a Type.

        Keyword Args:
            title (str): Full Spoken Name.
            descr (str): Documentation Description.
            comment (str): Source Code Comment.
            ifdef (str): IFDEF pragma
            exist_ok (bool): Do not complain about already existing item
        """
        # pylint: disable=too-many-arguments
        param: Param
        if isinstance(type_or_param, Param):
            assert name is None
            param = type_or_param
        else:
            assert name is not None
            type_: AType = type_or_param
            validate_identifier(name)
            doc = Doc.from_type(type_, title, descr, comment)
            assert isinstance(
                self.paramdict, dict
            ), f"'paramdict' is not a dict, did you use a ',' instead of ':'? ({self.paramdict})"
            value = self.paramdict.pop(name, None)
            if value is not None and not isinstance(value, Expr):
                value = type_.encode(value)
            param = Param(type_, name, doc=doc, ifdef=ifdef, value=value)
        if self._locked:
            raise LockError(f"{self}: Cannot add param {name!r}. Module built was already completed and is froozen.")
        self.namespace.add(param, exist_ok=exist_ok)
        self.params.add(param, exist_ok=exist_ok)
        return param

    def add_const(
        self,
        type_or_const: Union[AType, Const],
        name: Optional[str] = None,
        title: str = NOTHING,  # type: ignore
        descr: str = NOTHING,  # type: ignore
        comment: str = NOTHING,  # type: ignore
        ifdef: str = NOTHING,  # type: ignore
        exist_ok: bool = False,
    ) -> Const:
        """
        Add Module Internal Constant (:any:`Const`).

        Args:
            type_or_const: Type or Constant
            name (str): Name. Mandatory if type_or_const is a Type.

        Keyword Args:
            title (str): Full Spoken Name.
            descr (str): Documentation Description.
            comment (str): Source Code Comment.
            ifdef (str): IFDEF pragma
            exist_ok (bool): Do not complain about already existing item
        """
        # pylint: disable=too-many-arguments
        const: Const
        if isinstance(type_or_const, Const):
            assert name is None
            const = type_or_const
        else:
            assert name is not None
            type_: AType = type_or_const
            validate_identifier(name)
            doc = Doc.from_type(type_, title, descr, comment)
            const = Const(type_, name, doc=doc, ifdef=ifdef)
        if self._locked:
            raise LockError(f"{self}: Cannot add constant {name!r}. Module built was already completed and is froozen.")
        self.namespace.add(const, exist_ok=exist_ok)
        return const

    def add_type_consts(self, type_, exist_ok=False, only=None, name=None, item_suffix="e"):
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
        name = name or get_snakecasename(type_.__class__).removesuffix("_type")
        type_ = DescriptiveStructType(type_, filter_=namefilter(only), enumitem_suffix=item_suffix)
        self.add_const(type_, name, exist_ok=exist_ok, title=type_.title, descr=type_.descr, comment=type_.comment)

    def add_port(
        self,
        type_: AType,
        name: str = "",
        direction: Direction = NOTHING,  # type: ignore
        title: str = NOTHING,  # type: ignore
        descr: str = NOTHING,  # type: ignore
        comment: str = NOTHING,  # type: ignore
        ifdef: str = NOTHING,  # type: ignore
        route=None,
    ) -> Port:
        """
        Add Module Port (:any:`Port`).

        Args:
            type_ (AType): Type.

        Keyword Args:
            name (str): Name. Default is None.
            direction (Direction): Signal Direction. Automatically detected if `name` ends with '_i', '_o', '_io'.
            title (str): Full Spoken Name.
            descr (str): Documentation Description.
            comment (str): Source Code Comment.
            ifdef (str): IFDEF mapping
            route: Routes (iterable or string separated by ';')
        """
        # pylint: disable=too-many-arguments
        doc = Doc.from_type(type_, title, descr, comment)
        port = Port(type_, name, direction=direction, doc=doc, ifdef=ifdef)
        if self._locked:
            raise LockError(f"{self}: Cannot add port {name!r}. Module built was already completed and is froozen.")
        self.namespace[name] = port
        self.portssignals[name] = port
        self.ports[name] = port
        for route_ in parsepaths(route):
            self.__router.add(RoutePath(port), route_)
        return port

    def add_signal(
        self,
        type_: AType,
        name: str,
        direction: AOrientation = FWD,
        title: str = NOTHING,  # type: ignore
        descr: str = NOTHING,  # type: ignore
        comment: str = NOTHING,  # type: ignore
        ifdef: str = NOTHING,  # type: ignore
        no_codecov=None,
        route=None,
    ) -> Signal:
        """
        Add Module Internal Signal (:any:`Signal`).

        Args:
            type_ (AType): Type.
            name (str): Name.

        Keyword Args:
            direction: Direction (Just for bidir signals)
            ifdef (str): IFDEF
            no_codecov: Disable Toggle Coverage.
            route: Routes (iterable or string separated by ';')
        """
        if direction is not NOTHING:
            direction = FWD * direction
        doc = Doc.from_type(type_, title, descr, comment)
        signal = Signal(type_, name, doc=doc, ifdef=ifdef, direction=direction, no_codecov=no_codecov)
        if self._locked:
            raise LockError(f"{self}: Cannot add port {name!r}. Module built was already completed and is froozen.")
        self.namespace[name] = signal
        self.portssignals[name] = signal
        for route_ in parsepaths(route):
            self.__router.add(RoutePath(signal), route_)
        return signal

    def add_port_or_signal(
        self,
        type_: AType,
        name: str = "",
        direction: Direction = NOTHING,  # type: ignore
        title: str = NOTHING,  # type: ignore
        descr: str = NOTHING,  # type: ignore
        comment: str = NOTHING,  # type: ignore
        ifdef: str = NOTHING,  # type: ignore
        route=None,
    ) -> ASignal:
        """
        Add Module Port (:any:`Port`) or Signal (:any:`Signal`) depending on name.

        Args:
            type_ (AType): Type.

        Keyword Args:
            name (str): Name. Default is None.
            direction (Direction): Signal Direction. Automatically detected if `name` ends with '_i', '_o', '_io'.
            title (str): Full Spoken Name.
            descr (str): Documentation Description.
            comment (str): Source Code Comment.
            ifdef (str): IFDEF mapping
            route: Routes (iterable or string separated by ';')
        """
        if direction is NOTHING:
            direction = Direction.from_name(name) or FWD
        if direction in (IN, OUT, INOUT):
            return self.add_port(type_, name, direction, title, descr, comment, ifdef, route)
        return self.add_signal(type_, name, direction, ifdef, route)

    def set_parent(self, parent):
        """
        Set Parent.

        Do not use this method, until you really really really know what you do.
        """
        self.__parents.append(parent)

    def assign(
        self, target: Expr, source: Expr, cast: bool = False, overwrite: bool = False, filter_=None, plain=False
    ):
        """
        Assign `target` to `source`.

        The assignment is done **without** routing.

        Args:
            target (Expr): Target to be driven. Must be known within this module.
            source (Expr): Source driving target. Must be known within this module.

        Keyword Args:
            cast (bool): Cast. `False` by default.
            overwrite (bool): Overwrite existing assignment.
            filter_ (str, Callable): Target names or function to filter target identifiers.
        """
        if self._locked:
            raise LockError(
                f"{self}: Cannot add assign '{source}' to '{target}'. "
                "Module built was already completed and is froozen."
            )
        if isinstance(filter_, str):
            filter_ = namefilter(filter_)
        try:
            if not plain:
                target = parse(target, namespace=self.namespace, context=str(self))
                source = parse(source, namespace=self.namespace, context=str(self))
            self.assigns.set(target, source, cast=cast, overwrite=overwrite, filter_=filter_, plain=plain)
        except DirectionError as err:
            raise DirectionError(f"{self}: {err}") from err

    def add_inst(self, inst: "BaseMod"):
        """
        Add Submodule `inst`.

        Do not use this method, until you really really really know what you do.

        Args:
            inst (AMod)
        """
        inst.set_parent(self)
        self.insts.add(inst)
        self.__instcons[inst.name] = Assigns(inst.ports, self.namespace, drivers=self.drivers, inst=True)

    def get_inst(self, name: Union[str, "BaseMod"]) -> "BaseMod":
        """
        Get Module Instance.

        See example above.
        """
        if isinstance(name, BaseMod):
            return name
        inst = self
        try:
            for part in name.split("/"):
                if part == "..":
                    inst = inst.parent
                else:
                    inst = inst.insts[part]
            return inst
        except ValueError as err:
            raise ValueError(f"{inst}: {err}") from None

    def set_instcon(
        self, inst: "BaseMod", port: Port, expr: Expr, cast: bool = False, overwrite: bool = False, filter_=None
    ):
        """
        Connect `port` of `inst` to `expr` without routing.

        The assignment is done **without** routing.

        Args:
            inst (BaseMod): Module Instance
            port (Port): Port to be connected. Must be known within module instance.
            expr (Expr): Expression. Must be known within this module.

        Keyword Args:
            cast (bool): Cast. `False` by default.
            overwrite (bool): Overwrite existing assignment.
            filter_ (str, Callable): Target names or function to filter target identifiers.
        """
        if self._locked:
            raise LockError(
                f"{self}: Cannot add {inst} instance connections of {port} to {expr}. "
                "Module built was already completed and is froozen."
            )
        if isinstance(filter_, str):
            filter_ = namefilter(filter_)
        port = parse(port, namespace=inst.ports, context=str(self))
        expr = parse(expr, namespace=self.namespace, context=str(self))
        try:
            self.__instcons[inst.name].set(port, expr, cast=cast, overwrite=overwrite, filter_=filter_)
        except DirectionError as exc:
            raise DirectionError(f"{self}: {exc}") from None

    def get_instcons(self, inst: "BaseMod") -> Assigns:
        """Retrieve All Instance Connections Of `inst`."""
        return self.__instcons[inst.name]

    def add_flipflop(
        self, type_: AType, name: str, nxt=None, clk=None, rst_an=None, rst=None, ena=None, route=None
    ) -> Signal:
        """
        Add Module Internal Flip-Flop.

        Args:
            type_ (AType): Type.
            name (str): Name.

        Keyword Args:
            nxt: Next Value. Basename of `name` with _nxt_s by default.
            clk: Clock. Module Clock by default.
            rst_an: Reset. Module Reset by default.
            rst: Synchronous Reset
            ena: Enable Condition.
        """
        # pylint: disable = too-many-arguments
        if self._locked:
            raise LockError(
                f"{self}: Cannot add flipflop {name!r}. " "Module built was already completed and is froozen."
            )
        out = self.add_signal(type_, name)
        if route:
            self.route(route, out)
        # nxt
        if nxt is None:
            basename = split_suffix(name)[0]
            nxt = self.add_signal(type_, f"{basename}_nxt_s")
        else:
            nxt = self.parse(nxt)
        # -
        clk = self._check_clkrst(name, clk, "clk", _clkfilter)
        rst_an = self._check_clkrst(name, rst_an, "rst_an", _rstanfilter)
        if rst is not None:
            rst = cast_booltype(self.parse(rst))
            # check_booltype(f"{self}: flipflop {name}, rst", rst.type_, BoolType)
        if ena is not None:
            ena = cast_booltype(self.parse(ena))
            # check_booltype(f"{self}: flipflop {name}, ena", ena.type_, BoolType)
        flipflop = FlipFlop.create(self, self.__flipflops, clk, rst_an, rst, ena)
        flipflop.set(out, nxt)
        # type-warnings
        # check_types(f"flipflop {name}, clk", clk.type_, ClkType)
        # check_types(f"flipflop {name}, rst_an", rst_an.type_, RstAnType)
        return out

    def _check_clkrst(self, name, expr, what, filter_):
        if expr is None:
            expr = self.namespace.findfirst(filter_=filter_)
        else:
            expr = self.parse(expr, only=(Port, Signal))
        if expr is None:
            raise ValueError(f"flipflop {name} requires {what}.")
        return expr

    def flipflops(self) -> Generator[FlipFlop, None, None]:
        """
        Iterate over all Flip Flops.

        This method is only needed for the Systemverilog code generation.
        """
        yield from self.__flipflops.values()

    def add_mux(
        self,
        name,
        title: str = NOTHING,  # type: ignore
        descr: str = NOTHING,  # type: ignore
        comment: str = NOTHING,  # type: ignore
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
        if self._locked:
            raise LockError(f"{self}: Cannot add mux {name!r}. " "Module built was already completed and is froozen.")
        doc = Doc(title, descr, comment)
        self.__muxes[name] = mux = Mux(name, self.portssignals, self.namespace, self.drivers, doc)
        return mux

    @property
    def muxes(self) -> Generator[Mux, None, None]:
        """
        Iterate over all Multiplexer.

        This method is only needed for the Systemverilog code generation.
        """
        return self.__muxes.values()

    def get_mux(self, mux: Union[Mux, str]) -> Mux:
        """Get Multiplexer."""
        if isinstance(mux, str):
            mux = self.muxes[mux]
        return mux

    @property
    def is_locked(self) -> bool:
        """
        Return If Module Is Already Completed And Locked For Modification.

        Locking is done by the build process **automatically** and **MUST NOT** be done earlier or later.
        Use a different module type or enumeration or struct type, if you have issues with locking.
        """
        return self._locked

    def lock(self):
        """
        Lock.

        Locking is done via this method by the build process **automatically** and **MUST NOT** be done earlier or
        later. Use a different module type or enumeration or struct type, if you have issues with locking.
        """
        assert not self._locked, f"{self} is already locked"
        # pylint: disable=protected-access
        for item in astuple(self, recurse=False):
            if isinstance(item, Namespace):
                item.lock()
        object.__setattr__(self, "_locked", True)

    def con(self, port, dest):
        """Connect `port` to `dest`."""
        parents = self.__parents
        if not parents:
            raise TypeError(f"{self} is top module. Connections cannot be made.")
        parent = parents[-1]
        parent.route(parsepath(port, basepath=self.name), dest)

    def route(self, target, source):
        """Route `source` to `target` within the actual module."""
        for subtarget in parsepaths(target):
            for subsource in parsepaths(source):
                self.__router.add(subtarget, subsource)

    def __repr__(self):
        return f"{self.__class__.__qualname__}({self.pathstr!r})"


def _clkfilter(ident):
    return isinstance(ident.type_, ClkType) and isinstance(ident, (Port, Signal))


def _rstanfilter(ident):
    return isinstance(ident.type_, RstAnType) and isinstance(ident, (Port, Signal))


def get_mro(modcls):
    """Get Module Resolve Order for `modcls`."""
    classes = []
    for cls in getmro(modcls):  # pragma: no cover
        if cls is BaseMod:
            break
        classes.append(cls)
    # pylint: disable=protected-access
    return tuple(classes[: modcls._mroidx])


def get_modbasecls(cls_or_inst):
    """
    Get Base Class of `mod`.

    >>> import ucdp
    >>> class MyMod(ucdp.AMod):
    ...     def _build(self): pass
    >>> class MyMyMod(MyMod):
    ...     def _build(self): pass
    >>> class MyTbMod(ucdp.ATbMod):
    ...     def _build(self): pass
    >>> class MyTailMod(ucdp.ATailoredMod):
    ...     def _build(self): pass

    >>> ucdp.get_modbasecls(MyMod)
    <class 'ucdp.mod.mods.AMod'>
    >>> ucdp.get_modbasecls(MyMod())
    <class 'ucdp.mod.mods.AMod'>
    >>> ucdp.get_modbasecls(MyMyMod())
    <class 'ucdp.mod.mods.AMod'>
    >>> ucdp.get_modbasecls(MyTbMod)
    <class 'ucdp.mod.mods.ATbMod'>
    >>> ucdp.get_modbasecls(MyTailMod)
    <class 'ucdp.mod.mods.ATailoredMod'>
    """
    modcls = cls_or_inst.__class__ if isinstance(cls_or_inst, BaseMod) else cls_or_inst
    classes = []
    for cls in getmro(modcls):  # pragma: no cover
        if cls is BaseMod:
            break
        classes.append(cls)
    # pylint: disable=protected-access
    return classes[modcls._mroidx]


def get_modname(cls):
    """
    Get Module Name.

    The module name is derived from the class name if not explicitly set as class attribute.
    """
    if isinstance(cls.modname, str):
        return cls.modname
    return snakecase(cls.__name__.removesuffix("Mod"))
