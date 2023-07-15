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
Unified Chip Design Platform.
"""
from icdutil.slices import Slice

from .assigns import Assign, Assigns
from .attrs import NOTHING, Factory, field, frozen
from .const import Const
from .doc import Doc
from .expr import (
    TODO,
    BoolOp,
    CommentExpr,
    ConcatExpr,
    ConstExpr,
    Expr,
    InvalidExpr,
    Log2Func,
    MaximumFunc,
    MinimumFunc,
    Op,
    Range,
    SignedFunc,
    SliceOp,
    SOp,
    TernaryExpr,
    UnsignedFunc,
    cast,
    cast_booltype,
    concat,
    const,
    create,
    get_idents,
    log2,
    maximum,
    minimum,
    parse,
    signed,
    ternary,
    unsigned,
)
from .flipflop import FlipFlop
from .ident import Ident, Idents
from .loader import load
from .mod.base import BaseMod, get_modbasecls, get_modname, mod
from .mod.config import AConfig, AUniqueConfig, AVersionConfig, config
from .mod.iter import ModPostIter, ModPreIter
from .mod.mods import AConfigurableMod, AGenericTbMod, AImportedMod, AMod, ATailoredMod, ATbMod, CoreMod, _ATopMod
from .mod.util import get_relpath, get_topmod, walk
from .modref import ModRef
from .mux import Mux
from .namespace import DuplicateError, LockError, Namespace
from .nameutil import didyoumean, get_snakecasename, join_names, split_prefix, split_suffix
from .param import Param
from .router import Router, RouterError
from .signal import ASignal, Port, Signal
from .test import Test
from .top import Top
from .topref import TopRef
from .types.array import ArrayType
from .types.base import ACompositeType, AScalarType, AType, AVecType, tailoredtype
from .types.clkrst import ClkRstAnType, ClkType, DiffClkRstAnType, DiffClkType, RstAnType, RstAType, RstType
from .types.descriptivestruct import DescriptiveStructType
from .types.enum import (
    AUTO,
    AEnumType,
    AGlobalEnumType,
    BaseEnumType,
    BusyType,
    DisType,
    DynamicEnumType,
    EnaType,
    EnumItem,
)
from .types.iter import typeiter
from .types.orientation import BIDIR, BWD, FWD, IN, INOUT, OUT, AOrientation, Direction, Orientation
from .types.scalar import BitType, BoolType, IntegerType, RailType, SintType, StringType, UintType
from .types.struct import (
    AGlobalStructType,
    AStructType,
    BaseStructType,
    DynamicStructType,
    StructItem,
    bwdfilter,
    fwdfilter,
)
from .util import namefilter
