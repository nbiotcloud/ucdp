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

"""Unified Chip Design Platform."""

from pydantic import ValidationError

from . import cli
from .assigns import Assign, Assigns
from .baseclassinfo import BaseClassInfo, get_baseclassinfos
from .buildproduct import ABuildProduct
from .casting import Casting
from .config import AConfig, AVersionConfig, BaseConfig
from .const import Const
from .consts import AUTO, PAT_IDENTIFIER
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
from .exprparser import ExprParser, cast_booltype, const
from .exprresolver import ExprResolver
from .filelistparser import FileListParser
from .fileset import FileSet, LibPath
from .flipflop import FlipFlop
from .generate import clean, generate, get_makolator, render_generate, render_inplace
from .humannum import Bin, Bytes, Bytesize, Hex
from .ident import Ident, IdentFilter, Idents, IdentStop, get_expridents, get_ident
from .iterutil import Names, namefilter, split
from .loader import load
from .mod import AMod
from .modbase import BaseMod
from .modbasetop import BaseTopMod
from .modconfigurable import AConfigurableMod
from .modcore import ACoreMod
from .modfilelist import (
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
from .moditer import ModPostIter, ModPreIter, uniquemods
from .modref import ModRef
from .modtailored import ATailoredMod
from .modtb import AGenericTbMod, ATbMod
from .modtopref import TopModRef
from .modutil import get_modbaseinfos, is_tb_from_modname
from .mux import Mux
from .namespace import Namespace
from .nameutil import didyoumean, get_snakecasename, join_names, split_prefix, split_suffix, str2identifier
from .note import OPEN, TODO, Note
from .object import Field, Light, LightObject, NamedLightObject, NamedObject, Object, PrivateField, get_repr
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
from .param import Param
from .pathutil import improved_glob, improved_resolve, startswith_envvar, use_envvars
from .routepath import Routeable, Routeables, RoutePath, parse_routepath, parse_routepaths
from .signal import BaseSignal, Port, Signal
from .slices import DOWN, UP, Slice, SliceDirection
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
from .util import extend_sys_path, get_copyright

__all__ = [
    "ABuildProduct",
    "ACompositeType",
    "AConfig",
    "AConfigurableMod",
    "ACoreMod",
    "AEnumType",
    "AGenericTbMod",
    "AGlobalEnumType",
    "AGlobalStructType",
    "AMod",
    "AOrientation",
    "ArrayType",
    "AScalarType",
    "Assign",
    "Assigns",
    "AStructType",
    "ATailoredMod",
    "ATbMod",
    "AUTO",
    "AVecType",
    "AVersionConfig",
    "BaseClassInfo",
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
    "BWD",
    "bwdfilter",
    "BWDM",
    "Bytes",
    "cast_booltype",
    "Casting",
    "clean",
    "cli",
    "ClkRstAnType",
    "ClkType",
    "ConcatExpr",
    "const",
    "Const",
    "ConstExpr",
    "DescriptiveStructType",
    "Dict",
    "didyoumean",
    "DiffClkRstAnType",
    "DiffClkType",
    "Direction",
    "DirectionError",
    "DisType",
    "doc_from_type",
    "Doc",
    "DoubleType",
    "DOWN",
    "Drivers",
    "DriversDuplicateError",
    "DuplicateError",
    "DynamicEnumType",
    "DynamicStructType",
    "EnaType",
    "EnumItem",
    "EnumItemFilter",
    "Expr",
    "ExprParser",
    "ExprResolver",
    "extend_sys_path",
    "Field",
    "FileListParser",
    "FileSet",
    "FlipFlop",
    "FloatType",
    "FWD",
    "fwdfilter",
    "FWDM",
    "generate",
    "get_baseclassinfos",
    "get_copyright",
    "get_expridents",
    "get_ident",
    "get_makolator",
    "get_modbaseinfos",
    "get_repr",
    "get_snakecasename",
    "Hex",
    "Ident",
    "IdentFilter",
    "Idents",
    "IdentStop",
    "improved_glob",
    "improved_resolve",
    "IN",
    "Top",
    "INM",
    "INOUT",
    "IntegerType",
    "InvalidExpr",
    "is_tb_from_modname",
    "iter_modfilelists",
    "join_names",
    "LibPath",
    "Light",
    "LightObject",
    "load",
    "LockError",
    "Log2Expr",
    "MaximumExpr",
    "MinimumExpr",
    "ModFileList",
    "ModFileLists",
    "ModPostIter",
    "ModPreIter",
    "ModRef",
    "MultipleDriverError",
    "Mux",
    "NamedLightObject",
    "NamedObject",
    "namefilter",
    "Names",
    "Bytesize",
    "Namespace",
    "Note",
    "Object",
    "Op",
    "OPEN",
    "Orientation",
    "OUT",
    "OUTM",
    "Param",
    "parse_routepath",
    "parse_routepaths",
    "parse",
    "PAT_IDENTIFIER",
    "Paths",
    "Placeholder",
    "Port",
    "PrivateField",
    "RailType",
    "RangeExpr",
    "render_generate",
    "render_inplace",
    "resolve_modfilelist",
    "resolve_modfilelists",
    "Routeable",
    "Routeables",
    "RoutePath",
    "RstAnType",
    "RstAType",
    "RstType",
    "search_modfilelists",
    "Signal",
    "SintType",
    "Slice",
    "SliceDirection",
    "SliceOp",
    "SOp",
    "Source",
    "split_prefix",
    "split_suffix",
    "split",
    "startswith_envvar",
    "str2identifier",
    "StringType",
    "StructFilter",
    "StructItem",
    "Target",
    "ternary",
    "TernaryExpr",
    "Test",
    "TODO",
    "ToPaths",
    "TopModRef",
    "UintType",
    "uniquemods",
    "UP",
    "use_envvars",
    "ValidationError",
]
