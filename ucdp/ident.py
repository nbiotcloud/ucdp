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
Identifier.

All symbols within a hardware module are identifier and derived from :any:`Ident`.
Identifier should be stored in :any:`Idents`.
Identifier are itself part of an expression and therefore a child of :any:`Expr`.

Example:

>>> import ucdp
>>> class ModeType(ucdp.AEnumType):
...     keytype = ucdp.UintType(2)
...     def _build(self):
...         self._add(0, "add")
...         self._add(1, "sub")
...         self._add(2, "max")
>>> class MyType(ucdp.AStructType):
...     def _build(self):
...         self._add("mode", ModeType())
...         self._add("send", ucdp.ArrayType(ucdp.UintType(8), 3))
...         self._add("return", ucdp.UintType(4), ucdp.BWD)
>>> idents = ucdp.Idents([
...     ucdp.Port(ucdp.UintType(8), "vec_a_i"),
...     ucdp.Port(ucdp.UintType(8), "vec_a_o"),
...     ucdp.Signal(ucdp.UintType(4), "vec_c_s"),
...     ucdp.Signal(MyType(), "my_a_s"),
...     ucdp.Signal(MyType(), "my_b_s"),
... ])

Retrieve an item:

>>> idents['vec_a_i']
Port(UintType(8), name='vec_a_i')
>>> idents['my_a_mode_s']
Signal(ModeType(), 'my_a_mode_s', level=1)

Simple iteration:

>>> for ident in idents:
...     ident
Port(UintType(8), name='vec_a_i')
Port(UintType(8), name='vec_a_o')
Signal(UintType(4), 'vec_c_s')
Signal(MyType(), 'my_a_s')
Signal(MyType(), 'my_b_s')

Unrolling iteration:

>>> for ident in idents.iter():
...     ident
Port(UintType(8), name='vec_a_i')
Port(UintType(8), name='vec_a_o')
Signal(UintType(4), 'vec_c_s')
Signal(MyType(), 'my_a_s')
Signal(ModeType(), 'my_a_mode_s', level=1)
Signal(UintType(8), 'my_a_send_s', level=1, dims=(Slice('0:2'),))
Signal(UintType(4), 'my_a_return_s', level=1, direction=BWD)
Signal(MyType(), 'my_b_s')
Signal(ModeType(), 'my_b_mode_s', level=1)
Signal(UintType(8), 'my_b_send_s', level=1, dims=(Slice('0:2'),))
Signal(UintType(4), 'my_b_return_s', level=1, direction=BWD)

Some features:

>>> idents['my_b_send_s']
Signal(UintType(8), 'my_b_send_s', level=1, dims=(Slice('0:2'),))
>>> 'my_b_send_s' in idents
True
>>> 'my_b_send' in idents
False
"""

from collections import deque
from inspect import isclass
from typing import Iterator, List, Optional, Tuple

from aligntext import align
from icdutil.slices import Slice

from .attrs import evolve, field, frozen
from .doc import Doc
from .expr import Expr
from .namespace import Namespace
from .nameutil import didyoumean, split_suffix, validate_identifier
from .types.array import ArrayType
from .types.base import AType
from .types.orientation import AOrientation
from .types.struct import AGlobalStructType, AStructType, DynamicStructType


class Idents(Namespace):
    """
    Identifier Dictionary.

    See examples above.
    """

    def iter(self, filter_=None, stop=None, maxlevel=None) -> Iterator:
        """Iterate over all Identifier."""
        for ident in self.values():
            yield from ident.iter(filter_=filter_, stop=stop, maxlevel=maxlevel)

    def iterhier(self, filter_=None, stop=None, maxlevel=None) -> Iterator:
        """Iterate over all Identifier and return hierarchy."""
        for ident in self.values():
            yield from ident.iterhier(filter_=filter_, stop=stop, maxlevel=maxlevel)

    def findfirst(self, filter_=None, stop=None, maxlevel=None) -> Optional["Ident"]:
        """Iterate Over Identifier And Find First Match."""
        for ident in self.iter(filter_=filter_, stop=stop, maxlevel=maxlevel):
            return ident
        return None

    def __getitem__(self, name):
        return get_ident(self, name)

    def get(self, name):
        return get_ident(self, name, dym=True)

    def __contains__(self, item):
        if isinstance(item, Ident):
            name = item.name
        elif isinstance(item, str):
            name = item
        else:
            return False
        return _get_ident(self.values(), name) is not None


@frozen(cmp=False, hash=True)
class Ident(Expr):

    """
    Identifier.

    Args:
        type_: Type.
        name (str): Hierarchical name.

    Keyword Args:
        direction: (Direction): Orient or Direction.
        dims: (tuple): Dimensions
        level (int): Hierarchy Level
        doc (Doc): Documentation Container
        ifdef (str): IFDEF encapsulation

    >>> import ucdp
    >>> ident = Ident(ucdp.UintType(32), 'base_sub_i', level=1)
    >>> ident.type_
    UintType(32)
    >>> ident.name
    'base_sub_i'
    >>> ident.level
    1
    >>> ident.direction
    >>> ident.dims
    ()
    >>> ident.doc
    Doc()

    Calculated Properties:

    >>> ident.basename
    'base_sub_i'
    >>> ident.suffix
    ''
    >>> ident.name
    'base_sub_i'
    """

    # pylint: disable=too-many-instance-attributes

    type_: AType = field()
    name: str = field()
    basename: str = field(init=False)
    suffix: str = field(init=False)
    direction: Optional[AOrientation] = field(default=None, kw_only=True)
    level: int = field(default=0, kw_only=True)
    dims: Tuple[Slice, ...] = field(default=tuple(), kw_only=True)
    doc: Doc = field(default=Doc(), kw_only=True)
    ifdef: Optional[str] = field(default=None, kw_only=True)

    _children = field(init=False, factory=list, hash=False)
    _suffixes: Tuple[str, ...] = ()

    @name.validator
    def _name_validator(self, name, value):
        # pylint: disable=unused-argument
        validate_identifier(value)

    @basename.default
    def _basename_default(self) -> str:
        return split_suffix(self.name, suffixes=self._suffixes)[0]

    @suffix.default
    def _suffix_default(self) -> str:
        return split_suffix(self.name, suffixes=self._suffixes)[1]

    @type_.validator
    def _type_validator(self, name, value):
        # pylint: disable=unused-argument
        if isclass(value) and issubclass(value, AType):
            raise ValueError("{value!r} is a class, but must be an instance. You missed the brackets '()'!")

    def __attrs_post_init__(self):
        # Static Children are initialized here once instead of constructing
        # them every time
        type_ = self.type_
        if isinstance(type_, (AGlobalStructType, AStructType)):
            children = self._children
            for sitem in type_.values():
                level = self.level + 1
                direction = self.direction and self.direction * sitem.orientation
                # pylint: disable=consider-using-ternary
                suffix = (direction and direction.suffix) or self.suffix
                ibasename = self.basename
                sname = sitem.name
                basename = f"{ibasename}_{sname}" if ibasename and sname else ibasename or sname
                name = f"{basename}{suffix}"
                ifdef = sitem.ifdef or self.ifdef
                child = evolve(
                    self,
                    type_=sitem.type_,
                    name=name,
                    level=level,
                    direction=direction,
                    dims=self.dims,
                    doc=sitem.doc,
                    ifdef=ifdef,
                )
                children.append(child)
        elif isinstance(type_, ArrayType):
            dims = self.dims + (type_.slice_,)
            self._children.append(evolve(self, type_=type_.type_, dims=dims))

    @property
    def title(self):
        """Alias to `doc.title`."""
        return self.doc.title

    @property
    def descr(self):
        """Alias to `doc.descr`."""
        return self.doc.descr

    @property
    def comment(self):
        """Alias to `doc.comment`."""
        return self.doc.comment

    def new(self, **kwargs) -> "Ident":
        """Return A Copy With Updated Attributes."""
        return evolve(self, **kwargs)

    def __int__(self):
        return int(self.type_.default)

    def __iter__(self):
        return self.iter()

    def iter(self, filter_=None, stop=None, maxlevel=None, value=None) -> Iterator:
        """Iterate over Hierarchy."""
        return _iters([self], filter_=filter_, stop=stop, maxlevel=maxlevel, value=value)

    def iterhier(self, filter_=None, stop=None, maxlevel=None, value=None) -> Iterator:
        """Iterate over Hierarchy."""
        hier: List[Ident] = []
        for ident in self.iter(stop=stop, maxlevel=maxlevel, value=value):
            hier = hier[: ident.level] + [ident]
            if not filter_ or filter_(ident):
                yield tuple(hier)

    def get(self, name, value=None):
        """
        Get Member of Hierarchy.

        Args:
            name: Name

        Keyword Args:
            value: value
            dym (bool): Enriched `ValueError` exception.
        """
        if name.startswith("_"):
            name = f"{self.basename}{name}"
        return get_ident([self], name, value=value, dym=True)


def _iters(idents, filter_=None, stop=None, maxlevel=None, value=None):
    # highly optimized!
    # pylint: disable=too-many-locals,too-many-nested-blocks,too-many-branches
    for ident in idents:
        stack = deque([ident])
        while True:
            try:
                ident = stack.pop()
            except IndexError:
                break
            if stop and stop(ident):
                break
            type_ = ident.type_
            assert value is None, "TODO"
            # pylint: disable=protected-access
            if type_._yield and (not filter_ or filter_(ident)):
                yield ident
            if isinstance(type_, (AGlobalStructType, AStructType)):
                level = ident.level + 1
                if maxlevel is None or level <= maxlevel:
                    for child in reversed(ident._children):
                        if not stop or not stop(child):
                            stack.append(child)
            elif isinstance(type_, DynamicStructType):
                level = ident.level + 1
                if maxlevel is None or level <= maxlevel:
                    for sitem in reversed(type_.values()):
                        direction = ident.direction and ident.direction * sitem.orient
                        # pylint: disable=consider-using-ternary
                        suffix = (direction and direction.suffix) or ident.suffix
                        ibasename = ident.basename
                        sname = sitem.name
                        basename = f"{ibasename}_{sname}" if ibasename and sname else ibasename or sname
                        name = f"{basename}{suffix}"
                        ifdef = sitem.ifdef or ident.ifdef
                        child = evolve(
                            ident,
                            type_=sitem.type_,
                            name=name,
                            level=level,
                            direction=direction,
                            doc=sitem.doc,
                            ifdef=ifdef,
                        )
                        if not stop or not stop(child):
                            stack.append(child)
            elif isinstance(type_, ArrayType):
                dims = ident.dims + (type_.slice_,)
                child = evolve(ident, type_=type_.type_, dims=dims)
                if not stop or not stop(child):
                    stack.append(child)


def get_ident(idents, name, value=None, dym=False):
    """Retrieve identifier by `name`, without iterating over the entire identifier tree."""
    assert value is None, "TODO"
    ident = _get_ident(idents, name)
    if ident is not None:
        return ident

    # Beautiful error handling
    msg = f"'{name}' is not known."
    if dym and any(idents):
        names = [ident.name for ident in _iters(idents)]
        nametree = align(_get_identtree(idents), rtrim=True)
        msg += f" Known are\n{nametree}\n\n{msg}\n"
        msg += didyoumean(name, names, multiline=True)
    raise ValueError(msg)


def get_subname(parent: Ident, ident: Ident):
    """Get name relative to parent."""
    if parent is ident:
        return ident.suffix
    parentbasename = parent.basename
    name = ident.name
    assert name.startswith(parentbasename)
    return name[len(parentbasename) + 1 :]


def get_subnames(idents):
    """Return names of hierarchical idents."""
    names = []
    prefix = ""
    for ident in idents:
        basename = ident.basename
        names.append(basename.removeprefix(prefix))
        prefix = f"{basename}_"
    return names


def _get_ident(idents, name):
    # This method is a derived implementation of _iters and has to be kept in sync with it.
    idents = deque(idents)
    while True:
        try:
            ident = idents.pop()
        except IndexError:
            break
        type_ = ident.type_
        # pylint: disable=protected-access
        if type_._yield and ident.name == name:
            return ident
        # pylint: disable=protected-access
        if type_._dynamic:
            for sitem in reversed(type_.values()):
                ibasename = ident.basename
                sname = sitem.name
                basename = f"{ibasename}_{sname}" if ibasename and sname else ibasename or sname
                if name.startswith(basename):
                    level = ident.level + 1
                    direction = ident.direction and ident.direction * sitem.orient
                    # pylint: disable=consider-using-ternary
                    suffix = (direction and direction.suffix) or ident.suffix
                    sname = f"{basename}{suffix}"
                    ifdef = sitem.ifdef or ident.ifdef
                    child = evolve(
                        ident,
                        type_=sitem.type_,
                        name=sname,
                        level=level,
                        direction=direction,
                        doc=sitem.doc,
                        ifdef=ifdef,
                    )
                    idents.append(child)
        else:
            # pylint: disable=protected-access
            for child in ident._children:
                if name.startswith(child.basename):
                    idents.append(child)
    return None


def _get_identtree(idents, pre=""):
    for ident in _iters(idents):
        pre = "  " * ident.level
        yield f"{pre}'{ident.name}'", ident.type_
