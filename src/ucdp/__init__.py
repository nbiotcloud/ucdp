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

from .assigns import Assign, Assigns, Drivers
from .baseclassinfo import BaseClassInfo, get_baseclassinfos
from .buildproduct import ABuildProduct
from .config import AConfig, AUniqueConfig, AVersionConfig, BaseConfig
from .const import Const
from .consts import AUTO, PAT_IDENTIFIER
from .dict import Dict
from .doc import Doc
from .docutil import doc_from_type
from .exceptions import BuildError, DirectionError, DuplicateError, LockError
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
)
from .exprparser import ExprParser, const
from .exprresolver import ExprResolver
from .filelistparser import FileListParser
from .fileset import FileSet, LibPath
from .flipflop import FlipFlop
from .generate import generate
from .humannum import Bin, Bytes, Hex
from .ident import Ident, IdentFilter, Idents, IdentStop, get_ident
from .iterutil import namefilter, split
from .loader import load
from .mod import AMod
from .modbase import BaseMod
from .modbasetop import BaseTopMod
from .modconfigurable import AConfigurableMod
from .modcore import CoreMod
from .modfilelist import (
    ModFileList,
    ModFileLists,
    Paths,
    Placeholder,
    ToPaths,
    iter_modfilelists,
    resolve_modfilelist,
    search_modfilelist,
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
from .signal import BaseSignal, Port, Signal
from .slices import DOWN, UP, Slice, SliceDirection
from .test import Test
from .typearray import ArrayType
from .typebase import ACompositeType, AScalarType, AVecType, BaseScalarType, BaseType
from .typeclkrst import ClkRstAnType, ClkType, DiffClkRstAnType, DiffClkType, RstAnType, RstAType, RstType
from .typedescriptivestruct import DescriptiveStructType
from .typeenum import AEnumType, AGlobalEnumType, BaseEnumType, BusyType, DisType, DynamicEnumType, EnaType, EnumItem
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
from .util import extend_sys_path

__all__ = [
    "ABuildProduct",
    "ACompositeType",
    "AConfig",
    "AConfigurableMod",
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
    "AUniqueConfig",
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
    "ClkRstAnType",
    "ClkType",
    "ConcatExpr",
    "const",
    "Const",
    "ConstExpr",
    "CoreMod",
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
    "DOWN",
    "Drivers",
    "DriversDuplicateError",
    "DuplicateError",
    "DynamicEnumType",
    "DynamicStructType",
    "EnaType",
    "EnumItem",
    "Expr",
    "ExprParser",
    "ExprResolver",
    "extend_sys_path",
    "Field",
    "FileListParser",
    "FileSet",
    "FlipFlop",
    "FWD",
    "fwdfilter",
    "FWDM",
    "generate",
    "get_baseclassinfos",
    "get_ident",
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
    "INM",
    "INOUT",
    "IntegerType",
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
    "Mux",
    "NamedLightObject",
    "NamedObject",
    "namefilter",
    "Namespace",
    "Note",
    "Object",
    "Op",
    "OPEN",
    "Orientation",
    "OUT",
    "OUTM",
    "Param",
    "parse",
    "PAT_IDENTIFIER",
    "Paths",
    "Placeholder",
    "Port",
    "PrivateField",
    "RailType",
    "RangeExpr",
    "resolve_modfilelist",
    "RstAnType",
    "RstAType",
    "RstType",
    "search_modfilelist",
    "Signal",
    "SintType",
    "Slice",
    "SliceDirection",
    "SliceOp",
    "SOp",
    "split_prefix",
    "split_suffix",
    "split",
    "startswith_envvar",
    "str2identifier",
    "StringType",
    "StructFilter",
    "StructItem",
    "ternary",
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
