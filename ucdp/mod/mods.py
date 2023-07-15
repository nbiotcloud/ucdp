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
Hardware Modules.

:any:`BaseMod` defines the base interface which is **common to all hardware modules**.
See :any:`BaseMod` for a complete interface description.
Depending on the module customization possibilites one of the following classes should be used for module description:

* :any:`AMod` - a normal Systemverilog module with parameters and a fixed number of ports (maybe `ifdef` encapsulated).
* :any:`AImportedMod` - external module with a long list of files etc.
* :any:`ATailoredMod` - module which is tailored for every use case - mainly the number and names of ports.
* :any:`CoreMod` - Intermediate module hierarchy (i.e. separation of core logic and standard modules)
* :any:`AConfigurableMod` - module which is assembled according to a receipe (:any:`BaseConfig`).
* :any:`ATbMod` - Testbench for any of the above.

The Building Process
--------------------

For the build process modules may use the following methods:

* `_build` - Build the main module functionality
* `_builddep` - Build everything which depends on special add methods
* `build_top` - Create top instance
* `build_tb` - Create testbench


Depending on the module the following build methods are allowed:

=======================  ===========  ===========  ===========  ==========
Module                   `_build`     `_builddep`  `build_top`  `build_tb`
=======================  ===========  ===========  ===========  ==========
:any:`AMod`              required     forbidden    optional     forbidden
:any:`AImportedMod`      optional     forbidden    optional     forbidden
:any:`ATailoredMod`      required     optional     optional     forbidden
:any:`CoreMod`           ignored      forbidden    optional     forbidden
:any:`AConfigurableMod`  required     forbidden    optional     forbidden
:any:`ATbMod`            required     forbidden    optional     optional
=======================  ===========  ===========  ===========  ==========
"""
from logging import getLogger
from typing import Generator, Optional, Tuple

from ..attrs import field, frozen
from ..nameutil import didyoumean, join_names
from ..test import Test
from ..types.enum import BaseEnumType
from .base import BaseMod, get_libname, get_modname
from .config import AVersionConfig, BaseConfig
from .iter import ModPostIter, ModPreIter

_LOGGER = getLogger("ucdp")

# pylint: disable=abstract-method


@frozen(repr=False, init=False)
class _ATopMod(BaseMod):
    _mroidx = -2

    def _build(self) -> None:
        """Build Type."""
        raise NotImplementedError(f"{self.__class__} requires implementation of 'def _build(self):'")

    def _buildpost(self):
        """Build Post."""

    def __attrs_post_init__(self):
        if self.parent:
            self.parent.add_inst(self)

        self._build()
        _builder(self)


@frozen(repr=False, init=False)
class AMod(_ATopMod):

    """
    A Normal Module With Parameters And A Fixed Number Of Ports (maybe `ifdef` encapsulated).

    See :any:`BaseMod` for arguments, attributes and details.

    All module parameter, local parameter, ports, signals and submodules
    **MUST** be added and created within the `_build` method:

    >>> import ucdp
    >>> class AdderMod(ucdp.AMod):
    ...
    ...     copyright_start_year = 2020
    ...     copyright_end_year = 2022
    ...
    ...     def _build(self):
    ...         width_p = self.add_param(ucdp.IntegerType(default=16), 'width_p')
    ...         datatype = ucdp.UintType(width_p)
    ...         self.add_port(datatype, "a_i")
    ...         self.add_port(datatype, "b_i")
    ...         self.add_port(datatype, "y_o")

    .. note:: There is no other build method on purpose!
    """


@frozen(repr=False, init=False)
class AImportedMod(_ATopMod):

    """
    An External Module With A Long List Of Files Etc.

    See :any:`BaseMod` for arguments, attributes and details.

    The module behaves identical to :any:`AMod` but does not use code generation by default.


    >>> import ucdp
    >>> @ucdp.mod
    ... class ExtIpMod(ucdp.AImportedMod):
    ...
    ...     def _build(self):
    ...         # Optional, but not needed
    ...         # Modules with existing python description should be mentioned
    ...         # here with `maninst=True`
    ...         # ClkGate(self, 'u_clkgate', maninst=True)
    ...         pass

    >>> extip = ExtIpMod.build_top()
    >>> extip
    ExtIpMod('ext_ip')
    """

    def _build(self):
        pass


@frozen(repr=False, init=False)
class ATailoredMod(BaseMod):

    """
    Module Which Is Tailored For Every Use Case By The Parent Module, Mainly The Number And Names Of Ports.

    See :any:`BaseMod` for arguments, attributes and details.

    Due to the frozen instance approach, implementation specific containers have to be implemented
    via `ucdp.field()`.

    The source code files are typically generated next to the parent module of tailored module.
    Also the module name is based on the parent module and extended by the instance name.
    A :any:`ATailoredMod` requires a Mako template mostly. The default template is typically located
    next to the python file of the tailored module.

    Tailored modules have **two** build methods:

    * `_build`
    * `_builddep`

    Please take the following points into account:

    * `_build` should be used for all **static** code and initialization.
    * Tailored modules should provide `add` methods to tailor the module instance to the needs of
      the parent module.
    * `_builddep` is called **after** all `add` methods have been called and should be used for all
      **dynamic** aspects which can only be known after the parent module made its adjustments.

    Example Definition:

    >>> import logging
    >>> import ucdp
    >>> LOGGER = logging.getLogger(__name__)
    >>> @ucdp.mod
    ... class DmxMod(ucdp.ATailoredMod):
    ...     copyright_start_year = 2021
    ...     slaves: ucdp.Namespace = ucdp.field(factory=ucdp.Namespace, init=False)
    ...
    ...     def add_slave(self, name, route=None):
    ...         self.slaves[name] = slave = Slave(self, name)
    ...         portname = f"slv_{name}_o"
    ...         self.add_port(ucdp.UintType(16), portname)
    ...         if route:
    ...             self.con(portname, route)
    ...         return slave
    ...
    ...     def _build(self):
    ...         self.add_port(ucdp.UintType(16), "mst_i")
    ...
    ...     def _builddep(self):
    ...         if not self.slaves:
    ...             LOGGER.warning("%r: has no APB slaves", self)
    ...
    >>> @ucdp.frozen()
    ... class Slave:
    ...     dmx: ucdp.BaseMod = ucdp.field(repr=False)
    ...     name: str = ucdp.field()

    Example Usage:

    >>> import ucdp
    >>> @ucdp.mod
    ... class TopMod(ucdp.AMod):
    ...     copyright_start_year = 2020
    ...     copyright_end_year = 2022
    ...     def _build(self):
    ...         dmx = DmxMod(self, 'u_dmx')
    ...         dmx.add_slave('a')
    ...         dmx.add_slave('b')
    >>> top = TopMod()
    >>> top
    TopMod('top')
    >>> top.get_inst('u_dmx')
    DmxMod('top/u_dmx')
    >>> top.get_inst('u_dmx').slaves
    {'a': Slave('a'), 'b': Slave('b')}
    """

    modname: str = field(kw_only=False)
    libname: str = field(init=False)

    @modname.default
    def _modname_default(self):
        modname = self.name.removeprefix("u_")
        if self.parent:
            return join_names(self.parent.modname, modname, concat="_")
        return modname

    @libname.default
    def _libname_default(self):
        if self.parent:
            return self.parent.libname
        return get_libname(self.__class__)

    def _build(self):
        """Build."""
        raise NotImplementedError(f"{self.__class__} requires implementation of 'def _build(self):'")

    def _builddep(self):
        """Build."""

    def _buildpost(self):
        """Build Post."""

    def __attrs_post_init__(self):
        if self.parent:
            self.parent.add_inst(self)

        self._build()
        if not self.parent:
            _builder(self)

    @property
    def copyright_end_year(self):
        """Copyright End Year."""
        if self.parent:
            return self.parent.copyright_end_year
        return None


@frozen(repr=False, init=False)
class CoreMod(BaseMod):

    """
    Intermediate Module Hierarchy (i.e. separation of core logic and standard modules)

    See :any:`BaseMod` for arguments, attributes and details.

    A :any:`CoreMod` should be use to create intermediate module hierarchies.
    :any:`CoreMod` do **not** have a `_build` method. They have to be built by the parent module.

    The source code files are typically generated/located next to the parent module of core module.
    Remember to set the `gen` attribute accordingly to controll the file generation.
    Also the module name is based on the parent module and extended by the instance name.
    A :any:`CoreMod` can have a Mako template.

    Example:

    TODO
    """

    _mroidx = -1
    modname: str = field(kw_only=False)
    libname: str = field(kw_only=False)
    modbasenames: tuple = field(init=False)

    @modname.default
    def _modname_default(self):
        if self.parent:
            return join_names(self.parent.modname, self.name.removeprefix("u_"), concat="_")
        modname = get_modname(self.__class__, nodefault=True)
        if modname:
            return modname
        raise ValueError("Please either set 'modname' or 'parent'")

    @libname.default
    def _libname_default(self):
        if self.parent:
            return self.parent.libname
        return get_libname(self.__class__)

    @modbasenames.default
    def _modbasenames_default(self) -> Tuple[str, ...]:
        names = []
        for cls in self.__class__.__mro__:  # pragma: no cover
            if cls is CoreMod:
                break
            names.append(get_modname(cls))
        if names:
            return tuple(names)
        if self.parent:
            stem = self.name.removeprefix("u_")
            return tuple(join_names(modbasename, stem, concat="_") for modbasename in self.parent.modbasenames)
        return (self.name.removeprefix("u_"),)

    def __attrs_post_init__(self):
        if self.parent:
            self.parent.add_inst(self)

    @property
    def copyright_start_year(self):
        """Copyright Start Year."""
        if self.parent:
            return self.parent.copyright_start_year
        return None

    @property
    def copyright_end_year(self):
        """Copyright End Year."""
        if self.parent:
            return self.parent.copyright_end_year
        return None

    @property
    def is_tb(self):
        """Is Testbench."""
        if self.parent:
            return self.parent.is_tb
        return None


@frozen(repr=False, init=False)
class AConfigurableMod(_ATopMod):

    """
    A Module Which Is Assembled According To A Receipe (:any:`AConfig`).

    See :any:`BaseMod` for arguments, attributes and details.

    Additionally the config has to be provided at instantation.
    A :any:`AConfigurableMod` may define a `default_config` which is taken if no `config` is provided at instantiaion.

    All module parameter, local parameter, ports, signals and submodules
    **MUST** be added and created within the `_build` method depending on the config.


    .. attention:: It is forbidden to implement `add` methods or any other *tailored* functionality.
                   Use a tailored module instead!

    Configurable modules are located next to the python file and use the configuration name in the module name.

    Example:

    >>> import ucdp
    >>> @ucdp.config
    ... class MyConfig(ucdp.AConfig):
    ...
    ...     feature: bool = ucdp.field(default=False)

    >>> class ProcMod(ucdp.AConfigurableMod):
    ...
    ...     default_config = MyConfig('default')
    ...
    ...     def _build(self):
    ...         if self.config.feature:
    ...             self.add_port(ucdp.UintType(8), "feature_i")
    ...             self.add_port(ucdp.UintType(8), "feature_o")
    ...         else:
    ...             self.add_port(ucdp.UintType(8), "default_o")

    Alternativly you can implemented `build_top`:

    >>> class ProcMod(ucdp.AConfigurableMod):
    ...
    ...     def _build(self):
    ...         if self.config.feature:
    ...             self.add_port(ucdp.UintType(8), "feature_i")
    ...             self.add_port(ucdp.UintType(8), "feature_o")
    ...         else:
    ...             self.add_port(ucdp.UintType(8), "default_o")
    ...
    ...     @staticmethod
    ...     def build_top():
    ...         config = MyConfig('default')
    ...         return ProcMod(config=config)

    >>> my = ProcMod.build_top()
    >>> my.modname
    'proc_default'
    >>> my.ports
    {'default_o': Port(UintType(8), name='default_o')}

    >>> my = ProcMod(config=MyConfig('other', feature=True))
    >>> my.modname
    'proc_other'
    >>> my.ports
    {'feature_i': Port(UintType(8), name='feature_i'), 'feature_o': Port(UintType(8), name='feature_o')}
    """

    config: BaseConfig = field(kw_only=True)

    default_config: Optional[BaseConfig] = None

    modname: str = field(init=False, repr=False)

    @modname.default
    def _modname_default(self):
        modname = get_modname(self.__class__)
        configname = self.config.name
        assert configname, f"{self.config} name must be non-empty"
        suffix = f"_{configname}"
        if not modname.endswith(suffix):
            modname = f"{modname}{suffix}"
        return modname

    @config.default
    def _config_default(self):
        default_config = self.__class__.default_config
        if not default_config:
            raise ValueError("'config' is required if no 'default_config' is provided.")
        return default_config

    @property
    def copyright_end_year(self):
        """Copyright End Year."""
        if isinstance(self.config, AVersionConfig):
            return self.config.timestamp.year
        return super().copyright_end_year

    def __repr__(self):
        config = self.config
        configrepr = f"{config.__class__.__qualname__}({config.name!r})"
        return f"{self.__class__.__qualname__}({self.pathstr!r}, config={configrepr})"


@frozen(repr=False, init=False)
class ATbMod(BaseMod):  # type: ignore

    """
    Testbench Module.

    Args:
        dut (BaseMod): Module Under Test.

    Create testbench for `dut`.

    The :any:`TopRef` and :any:`load` function allow to wrap any design module with a testbench.

    Example:

    >>> import ucdp
    >>> class MyMod(ucdp.AMod):
    ...
    ...     def _build(self):
    ...         self.add_port(ucdp.UintType(4), "data_i")
    ...         self.add_port(ucdp.UintType(4), "data_o")
    ...
    >>> class OtherMod(ucdp.AMod):
    ...
    ...     def _build(self):
    ...         self.add_port(ucdp.UintType(4), "data_i")
    ...         self.add_port(ucdp.UintType(4), "data_o")
    ...
    >>> class GenTbMod(ucdp.ATbMod):
    ...
    ...     def _build(self):
    ...         # Build testbench for self.dut here
    ...         pass
    ...
    ...     @staticmethod
    ...     def build_dut():
    ...         return MyMod()

    >>> tb = GenTbMod()
    >>> tb
    GenTbMod(MyMod('my'))
    >>> tb.dut
    MyMod('my')
    >>> tb = GenTbMod(OtherMod())
    >>> tb
    GenTbMod(OtherMod('other'))
    >>> tb.dut
    OtherMod('other')

    :any:`TopRef` and :any:`load` handle that gracefully and allow pairing of testbench and dut on
    command line and in configuration files.
    """

    # pylint: disable=too-many-instance-attributes

    dut: "BaseMod" = field()
    parent: "BaseMod" = field(default=None, init=False)
    name: str = field()
    modname: str = field()
    path: tuple = field(init=False)
    is_tb = True

    title = "Testbench"

    dut_mods = tuple()  # type: ignore

    @dut.default
    def _dut_default(self):
        return self.build_dut()

    @name.default
    def _name_default(self):
        basename = get_modname(self.__class__)
        return f"{basename}_{self.dut.modname}"

    @modname.default
    def _modname_default(self):
        basename = get_modname(self.__class__)
        return f"{basename}_{self.dut.modname}"

    @path.default
    def _path_default(self):
        assert not self.parent
        return (self.name,)

    def _buildpost(self):
        """Build Post."""

    @classmethod
    def build_tb(cls, dut, **kwargs):
        """Build Testbench."""
        return cls(dut, **kwargs)

    @classmethod
    def build_top(cls, **kwargs) -> "BaseMod":
        """
        Build Top Instance.

        Return module as top module.
        """
        dut = cls.build_dut(**kwargs)
        if not isinstance(dut, BaseMod):
            raise ValueError(f"'build_dut()'' of {cls} failed. It did not return a module. It returned ({dut})")
        if cls.dut_mods and not isinstance(dut, cls.dut_mods):
            raise ValueError(f"{dut} is not an instance of {cls.dut_mods}")
        # Avoid duplicate names on use of build_dut()
        return cls.build_tb(dut, modname=get_modname(cls))

    @classmethod
    def build_dut(cls, **kwargs):
        """Build DUT."""
        # pylint: disable=unused-argument
        msg = f"{cls} requires implementation of 'def build_dut(self):' or specify dut i.e. 'my_tb#my_mod'"
        raise NotImplementedError(msg)

    @classmethod
    def duts(cls, mod) -> Generator[BaseMod, None, None]:
        """
        Iterate over `topmod` and return modules which can be tested by this testbench.

        This method should be overwritten for test generation.
        """
        # pylint: disable=using-constant-test,unused-argument
        yield from ModPreIter(mod, filter_=lambda mod: isinstance(mod, cls.dut_mods))

    def tests(self) -> Generator[Test, None, None]:
        """
        Yield Tests to be run on design.

        This method should be overwritten for test generation.
        """
        # pylint: disable=using-constant-test
        yield from tuple()

    def _build(self) -> None:
        """Build Type."""
        raise NotImplementedError(f"{self.__class__} requires implementation of 'def _build(self):'")

    def __attrs_post_init__(self):
        if self.parent:
            self.parent.add_inst(self)

        self.add_inst(self.dut)
        self._build()
        _builder(self)

    def __repr__(self):
        return f"{self.__class__.__qualname__}({self.dut})"


class AGenericTbMod(ATbMod):
    """A Generic Testbench which adapts to dut."""

    _mroidx = -2


def _builder(mod):
    # pylint: disable=protected-access
    # builddep
    for inst in ModPreIter(mod, stop=lambda inst: inst.is_locked, filter_=lambda inst: isinstance(inst, ATailoredMod)):
        inst._builddep()
    # buildpost
    for inst in ModPostIter(mod, stop=lambda inst: inst.is_locked, filter_=lambda inst: not isinstance(inst, CoreMod)):
        inst._buildpost()
    # route
    insts = tuple(ModPreIter(mod, stop=lambda inst: inst.is_locked))
    for inst in insts:
        inst._route()
        # checks
        if not isinstance(inst, ATbMod) and getattr(inst, "build_dut", None):
            _LOGGER.error("%s has 'build_dut' which is forbidden and ignored", inst.__class__.__qualname__)
        if not isinstance(inst, ATailoredMod) and getattr(inst, "builddep", None):
            _LOGGER.error("%s has 'builddep' which is forbidden and ignored", inst.__class__.__qualname__)
        for obsolete in ("_build0", "_build1", "_build2", "_build3", "_build4"):
            if getattr(inst, obsolete, None):
                _LOGGER.error("%s has %r which is obsolete", inst.__class__.__qualname__, obsolete)
    # lock
    for inst in insts:
        for name in inst.paramdict:
            advice = didyoumean(name, inst.params.keys(), known=True)
            raise ValueError(f"{inst} has no param {name!r}{advice}")
        for mux in inst.muxes:
            for sel in mux.sels:
                if isinstance(sel.type_, BaseEnumType):
                    inst.add_type_consts(sel.type_, exist_ok=True)
        inst.lock()
