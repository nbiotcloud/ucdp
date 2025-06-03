#
# MIT License
#
# Copyright (c) 2023-2025 nbiotcloud
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

"""Unified Chip Design Platform."""

from typing import ClassVar

from pydantic import ValidationError

from . import cli
from .assigns import Assign, Assigns
from .baseclassinfo import BaseClassInfo, get_baseclassinfos
from .buildproduct import ABuildProduct
from .cache import CACHE
from .casting import Casting
from .clkrel import ASYNC, ClkRel
from .clkrelbase import BaseClkRel
from .config import AConfig, AVersionConfig, BaseConfig
from .const import Const
from .consts import AUTO, PAT_IDENTIFIER, PAT_OPT_IDENTIFIER, PATH, RE_IDENTIFIER, Gen
from .dict import Dict
from .doc import Doc
from .docutil import doc_from_type
from .drivers import Drivers, Source, Target
from .exceptions import BuildError, DirectionError, DuplicateError, InvalidExpr, LockError, MultipleDriverError
from .expr import (
    BoolOp,
    ConcatExpr,
    ConstExpr,
    Expr,
    Log2Expr,
    MaximumExpr,
    MinimumExpr,
    Op,
    RangeExpr,
    SliceOp,
    SOp,
    TernaryExpr,
)
from .exprparser import ExprParser, cast_booltype, concat, const, log2, maximum, minimum, ternary
from .exprresolver import ExprResolver
from .filelistparser import FileListParser
from .fileset import FileSet, LibPath
from .finder import find
from .flipflop import FlipFlop
from .generate import clean, generate, get_makolator, render_generate, render_inplace
from .humannum import Bin, Bytes, Bytesize, Hex
from .ident import Ident, IdentFilter, Idents, IdentStop, get_expridents, get_ident
from .iterutil import Names, namefilter, split
from .loader import load
from .mod import AMod
from .modbase import BaseMod, ModCls, ModClss, ModTags
from .modbasetop import BaseTopMod
from .modconfigurable import AConfigurableMod
from .modconfigurabletb import AConfigurableTbMod
from .modcore import ACoreMod
from .modfilelist import (
    Flavor,
    Flavors,
    ModFileList,
    ModFileLists,
    Paths,
    Placeholder,
    ToPaths,
    iter_modfilelists,
    resolve_modfilelist,
    resolve_modfilelists,
    search_modfilelists,
)
from .modgenerictb import AGenericTbMod
from .moditer import ModPostIter, ModPreIter, uniquemods
from .modref import ModRef
from .modtailored import ATailoredMod
from .modtb import ATbMod
from .modtopref import TopModRef
from .modtoprefinfo import TopModRefInfo
from .modutil import get_modbaseinfos, is_tb_from_modname
from .mux import Mux
from .namespace import Namespace
from .nameutil import didyoumean, get_snakecasename, join_names, split_prefix, split_suffix, str2identifier
from .note import DEFAULT, OPEN, TODO, UNUSED, Default, Note, note
from .object import (
    Field,
    IdentLightObject,
    IdentObject,
    Light,
    LightObject,
    NamedLightObject,
    NamedObject,
    Object,
    PosArgs,
    PrivateField,
    get_repr,
)
from .orientation import (
    BWD,
    FWD,
    IN,
    INOUT,
    OUT,
    AOrientation,
    Direction,
    Orientation,
)
from .overview import get_overview_tree
from .param import Param
from .pathutil import improved_glob, improved_resolve, startswith_envvar, use_envvars
from .routepath import Routeable, Routeables, RoutePath, parse_routepath, parse_routepaths
from .signal import BaseSignal, Port, Signal
from .slices import DOWN, UP, Slice, SliceDirection, mask_to_slices
from .test import Test
from .top import Top
from .typearray import ArrayType
from .typebase import ACompositeType, AScalarType, AVecType, BaseScalarType, BaseType
from .typebaseenum import BaseEnumType, EnumItem, EnumItemFilter
from .typeclkrst import ClkRstAnType, ClkType, DiffClkRstAnType, DiffClkType, RstAnType, RstAType, RstType
from .typedescriptivestruct import DescriptiveStructType
from .typeenum import AEnumType, AGlobalEnumType, BusyType, DisType, DynamicEnumType, EnaType
from .typefloat import DoubleType, FloatType
from .typescalar import BitType, BoolType, IntegerType, RailType, SintType, UintType
from .typestring import StringType
from .typestruct import (
    AGlobalStructType,
    AStructType,
    BaseStructType,
    DynamicStructType,
    StructFilter,
    StructItem,
    bwdfilter,
    fwdfilter,
)
from .typeutil import is_scalar, is_signed
from .util import extend_sys_path, get_copyright

__all__ = [
    "ASYNC",
    "AUTO",
    "BWD",
    "CACHE",
    "DEFAULT",
    "DOWN",
    "FWD",
    "IN",
    "INOUT",
    "OPEN",
    "OUT",
    "PATH",
    "PAT_IDENTIFIER",
    "PAT_OPT_IDENTIFIER",
    "RE_IDENTIFIER",
    "TODO",
    "UNUSED",
    "UP",
    "ABuildProduct",
    "ACompositeType",
    "AConfig",
    "AConfigurableMod",
    "AConfigurableTbMod",
    "ACoreMod",
    "AEnumType",
    "AGenericTbMod",
    "AGlobalEnumType",
    "AGlobalStructType",
    "AMod",
    "AOrientation",
    "AScalarType",
    "AStructType",
    "ATailoredMod",
    "ATbMod",
    "AVecType",
    "AVersionConfig",
    "ArrayType",
    "Assign",
    "Assigns",
    "BaseClassInfo",
    "BaseClkRel",
    "BaseConfig",
    "BaseEnumType",
    "BaseMod",
    "BaseScalarType",
    "BaseSignal",
    "BaseStructType",
    "BaseTopMod",
    "BaseType",
    "Bin",
    "BitType",
    "BoolOp",
    "BoolType",
    "BuildError",
    "BusyType",
    "Bytes",
    "Bytesize",
    "Casting",
    "ClassVar",
    "ClkRel",
    "ClkRstAnType",
    "ClkType",
    "ConcatExpr",
    "Const",
    "ConstExpr",
    "Default",
    "DescriptiveStructType",
    "Dict",
    "DiffClkRstAnType",
    "DiffClkType",
    "Direction",
    "DirectionError",
    "DisType",
    "Doc",
    "DoubleType",
    "Drivers",
    "DuplicateError",
    "DynamicEnumType",
    "DynamicStructType",
    "EnaType",
    "EnumItem",
    "EnumItemFilter",
    "Expr",
    "ExprParser",
    "ExprResolver",
    "Field",
    "FileListParser",
    "FileSet",
    "Flavor",
    "Flavors",
    "FlipFlop",
    "FloatType",
    "Gen",
    "Hex",
    "Ident",
    "IdentFilter",
    "IdentLightObject",
    "IdentObject",
    "IdentStop",
    "Idents",
    "IntegerType",
    "InvalidExpr",
    "LibPath",
    "Light",
    "LightObject",
    "LockError",
    "Log2Expr",
    "MaximumExpr",
    "MinimumExpr",
    "ModCls",
    "ModClss",
    "ModFileList",
    "ModFileLists",
    "ModPostIter",
    "ModPreIter",
    "ModRef",
    "ModTags",
    "MultipleDriverError",
    "Mux",
    "NamedLightObject",
    "NamedObject",
    "Names",
    "Namespace",
    "Note",
    "Object",
    "Op",
    "Orientation",
    "Param",
    "Paths",
    "Placeholder",
    "Port",
    "PosArgs",
    "PrivateField",
    "RailType",
    "RangeExpr",
    "RoutePath",
    "Routeable",
    "Routeables",
    "RstAType",
    "RstAnType",
    "RstType",
    "SOp",
    "Signal",
    "SintType",
    "Slice",
    "SliceDirection",
    "SliceOp",
    "Source",
    "StringType",
    "StructFilter",
    "StructItem",
    "Target",
    "TernaryExpr",
    "Test",
    "ToPaths",
    "Top",
    "TopModRef",
    "TopModRefInfo",
    "UintType",
    "ValidationError",
    "bwdfilter",
    "cast_booltype",
    "clean",
    "cli",
    "concat",
    "const",
    "didyoumean",
    "doc_from_type",
    "extend_sys_path",
    "find",
    "fwdfilter",
    "generate",
    "get_baseclassinfos",
    "get_copyright",
    "get_expridents",
    "get_ident",
    "get_makolator",
    "get_modbaseinfos",
    "get_overview_tree",
    "get_repr",
    "get_snakecasename",
    "improved_glob",
    "improved_resolve",
    "is_scalar",
    "is_signed",
    "is_tb_from_modname",
    "iter_modfilelists",
    "join_names",
    "load",
    "log2",
    "mask_to_slices",
    "maximum",
    "minimum",
    "namefilter",
    "note",
    "parse_routepath",
    "parse_routepaths",
    "render_generate",
    "render_inplace",
    "resolve_modfilelist",
    "resolve_modfilelists",
    "search_modfilelists",
    "split",
    "split_prefix",
    "split_suffix",
    "startswith_envvar",
    "str2identifier",
    "ternary",
    "uniquemods",
    "use_envvars",
]
