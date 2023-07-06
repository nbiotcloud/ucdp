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

from .attrs import NOTHING, Factory, field, frozen
from .doc import Doc
from .nameutil import didyoumean, get_snakecasename, join_names, split_prefix, split_suffix
from .types.array import ArrayType
from .types.base import ACompositeType, AScalarType, AType, AVecType
from .types.clkrst import ClkRstAnType, ClkType, DiffClkRstAnType, DiffClkType, RstAnType, RstAType, RstType
from .types.enum import AEnumType, ASharedEnumType, BaseEnumType, BusyType, DisType, DynamicEnumType, EnaType, EnumItem
from .types.iter import typeiter
from .types.orientation import BIDIR, BWD, FWD, IN, INOUT, OUT, AOrientation, Direction, Orientation
from .types.scalar import BitType, BoolType, IntegerType, RailType, SintType, StringType, UintType
from .types.struct import (
    ASharedStructType,
    AStructType,
    BaseStructType,
    DynamicStructType,
    StructItem,
    bwdfilter,
    fwdfilter,
)
