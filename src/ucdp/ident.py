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
Identifier.

All symbols within a hardware module are identifier and derived from [Ident][ucdp.ident.Ident].
Identifier should be stored in [Idents][ucdp.ident.Idents].
Identifier are itself part of an expression and therefore a child of [Expr][ucdp.expr.Expr].

??? Example "Identifier Examples"
    Basics:

        >>> import ucdp as u
        >>> class ModeType(u.AEnumType):
        ...     keytype: u.AScalarType = u.UintType(2)
        ...     def _build(self) -> None:
        ...         self._add(0, "add")
        ...         self._add(1, "sub")
        ...         self._add(2, "max")
        >>> class MyType(u.AStructType):
        ...     def _build(self) -> None:
        ...         self._add("mode", ModeType())
        ...         self._add("send", u.ArrayType(u.UintType(8), 3))
        ...         self._add("return", u.UintType(4), u.BWD)
        >>> idents = u.Idents([
        ...     u.Ident(u.UintType(8), "vec_a_i"),
        ...     u.Ident(u.UintType(8), "vec_a_o"),
        ...     u.Ident(u.UintType(4), "vec_c_s"),
        ...     u.Ident(MyType(), "my_a_s"),
        ...     u.Ident(u.ArrayType(MyType(), 4), "my_b_s"),
        ... ])

??? Example "Retrieve An Item"
    Retrieve an item:

        >>> idents['vec_a_i']
        Ident(UintType(8), 'vec_a_i')
        >>> idents['my_a_mode_s']
        Ident(ModeType(), 'my_a_mode_s')

??? Example "Simple Iteration"
    Simple iteration:

        >>> for ident in idents:
        ...     ident
        Ident(UintType(8), 'vec_a_i')
        Ident(UintType(8), 'vec_a_o')
        Ident(UintType(4), 'vec_c_s')
        Ident(MyType(), 'my_a_s')
        Ident(ArrayType(MyType(), 4), 'my_b_s')

??? Example "Unrolling Iteration"
    Unrolling iteration:

        >>> for ident in idents.iter():
        ...     ident
        Ident(UintType(8), 'vec_a_i')
        Ident(UintType(8), 'vec_a_o')
        Ident(UintType(4), 'vec_c_s')
        Ident(MyType(), 'my_a_s')
        Ident(ModeType(), 'my_a_mode_s')
        Ident(ArrayType(UintType(8), 3), 'my_a_send_s')
        Ident(UintType(4), 'my_a_return_s')
        Ident(ArrayType(MyType(), 4), 'my_b_s')
        Ident(ArrayType(UintType(4), 4), 'my_b_return_s')
        Ident(ArrayType(ArrayType(UintType(8), 3), 4), 'my_b_send_s')
        Ident(ArrayType(ModeType(), 4), 'my_b_mode_s')

??? Example "Some Features"
    Some features:

        >>> idents['my_b_send_s']
        Ident(ArrayType(ArrayType(UintType(8), 3), 4), 'my_b_send_s')
        >>> 'my_b_send_s' in idents
        True
        >>> 'my_b_send' in idents
        False

"""

from collections import deque
from collections.abc import Callable, Iterable, Iterator
from typing import Any, ClassVar

from .casting import Casting
from .consts import PAT_IDENTIFIER
from .doc import Doc
from .expr import ConcatExpr, ConstExpr, Expr, Log2Expr, MaximumExpr, MinimumExpr, Op, SliceOp, SOp, TernaryExpr
from .namespace import Namespace
from .nameutil import join_names, split_suffix
from .object import Field, Light, NamedObject, PosArgs
from .orientation import DIRECTION_SUFFIXES, AOrientation
from .typearray import ArrayType
from .typebase import BaseType
from .typestruct import BaseStructType, StructItem


class Ident(Expr, NamedObject, Light):
    """Identifier.

    Args:
        type_: Type.
        name: Name.

    Attributes:
        direction: Direction.
        doc: Documentation Container
        ifdef: IFDEF encapsulation

    ??? Example "Ident Examples"
        Attributes:

            >>> import ucdp as u
            >>> ident = Ident(u.UintType(32), 'base_sub_i')
            >>> ident.type_
            UintType(32)
            >>> ident.name
            'base_sub_i'
            >>> ident.direction
            >>> ident.doc
            Doc()

        Calculated Properties:

            >>> ident.basename
            'base_sub'
            >>> ident.suffix
            '_i'
    """

    type_: BaseType
    name: str = Field(pattern=PAT_IDENTIFIER)
    direction: AOrientation | None = Field(default=None, init=False)
    doc: Doc = Doc()
    ifdef: str | None = None

    _posargs: ClassVar[PosArgs] = ("type_", "name")

    def __init__(self, type_: BaseType, name: str, **kwargs):
        super().__init__(type_=type_, name=name, **kwargs)  # type: ignore[call-arg]

    @property
    def basename(self):
        """Base Name."""
        return split_suffix(self.name)[0]

    @property
    def suffix(self):
        """Suffix."""
        return split_suffix(self.name)[1]

    def __str__(self) -> str:
        return self.name

    def __int__(self):
        return int(getattr(self.type_, "default", -1))

    def __iter__(self):
        for _, ident in _iters([self]):
            yield ident

    def iter(self, filter_=None, stop=None, value=None) -> Iterator:
        """Iterate over Hierarchy."""
        for _, ident in _iters([self], filter_=filter_, stop=stop, value=value):
            yield ident

    def leveliter(self, filter_=None, stop=None, value=None) -> Iterator:
        """Iterate over Hierarchy."""
        yield from _iters([self], filter_=filter_, stop=stop, value=value)

    def cast(self, other: "Ident") -> Casting:
        """Cast self=cast(other)."""
        return None

    def _new_structitem(self, structitem: StructItem, **kwargs):
        direction = self.direction and self.direction * structitem.orientation
        if self.suffix:
            if direction is not None and self.suffix in DIRECTION_SUFFIXES:
                suffix = direction and direction.suffix
            else:
                suffix = self.suffix
        else:
            suffix = ""
        basename = join_names(self.basename, structitem.name)
        return self.new(
            type_=structitem.type_,
            name=f"{basename}{suffix}",
            direction=direction,
            doc=structitem.doc,
            ifdef=structitem.ifdef or self.ifdef,
            **kwargs,
        )


#     def iterhier(self, filter_=None, stop=None, maxlevel=None, value=None) -> Iterator:
#        """Iterate over Hierarchy."""
#         hier: List[Ident] = []
#         for ident in self.iter(stop=stop, maxlevel=maxlevel, value=value):
#             hier = hier[: ident.level] + [ident]
#             if not filter_ or filter_(ident):
#                 yield tuple(hier)

#     def get(self, name, value=None):
#        """
#         Get Member of Hierarchy.

#         Args:
#             name: Name

#         Keyword Args:
#             value: value
#             dym (bool): Enriched `ValueError` exception.
#        """
#         if name.startswith("_"):
#             name = f"{self.basename}{name}"
#         return get_ident([self], name, value=value, dym=True)

IdentFilter = Callable[[Ident], bool]
IdentStop = Callable[[Ident], bool]


class Idents(Namespace):
    """
    Identifier Dictionary.

    See examples above.
    """

    def iter(self, filter_: IdentFilter | None = None, stop: IdentStop | None = None) -> Iterator[Ident]:
        """Iterate over all Identifier."""
        for ident in self.values():
            yield from ident.iter(filter_=filter_, stop=stop)

    def leveliter(
        self, filter_: IdentFilter | None = None, stop: IdentStop | None = None
    ) -> Iterator[tuple[int, Ident]]:
        """Iterate over all Identifier with Level."""
        for ident in self.values():
            yield from ident.leveliter(filter_=filter_, stop=stop)

    # def iterhier(self, filter_=None, stop=None, maxlevel=None) -> Iterator:
    #    """Iterate over all Identifier and return hierarchy."""
    #     for ident in self.values():
    #         yield from ident.iterhier(filter_=filter_, stop=stop, maxlevel=maxlevel)

    # def findfirst(self, filter_=None, stop=None, maxlevel=None) -> "Ident" | None:
    #    """Iterate Over Identifier And Find First Match."""
    #     for ident in self.iter(filter_=filter_, stop=stop, maxlevel=maxlevel):
    #         return ident
    #     return None

    def __getitem__(self, name):
        return get_ident(self, name)

    def __contains__(self, item: Any) -> bool:
        if isinstance(item, Ident):
            name = item.name
        elif isinstance(item, str):
            name = item
        else:
            return False
        return _get_ident(self.values(), name) is not None


def _iters(idents: Iterable[Ident], filter_=None, stop=None, value=None, level: int = 0) -> Iterator[tuple[int, Ident]]:  # noqa: C901,PLR0912
    # highly optimized!

    for rootident in idents:
        stack = deque([(level, rootident)])
        while True:
            try:
                identlevel, ident = stack.pop()
            except IndexError:
                break

            if stop and stop(ident):
                break

            type_ = ident.type_
            if value is not None:
                if isinstance(type_, BaseStructType):
                    raise ValueError(f"Cannot apply value {value} for {type_}")
                type_ = type_.new(default=value)
                ident = ident.new(type_=type_)

            if not filter_ or filter_(ident):
                yield identlevel, ident
            if isinstance(type_, BaseStructType):
                substack = deque()
                for structitem in type_.values():
                    child = ident._new_structitem(structitem)
                    if not stop or not stop(child):
                        substack.append((identlevel + 1, child))
                stack.extend(reversed(substack))
            elif isinstance(type_, ArrayType):
                elementident = ident.new(type_=type_.itemtype)
                # do not forward stop and filter_ as these are just intermediate identifiers
                subidents = tuple(_iters([elementident], level=identlevel + 1))
                for sublevel, subident in subidents[1:]:
                    # create array with new element type
                    childtype = type_.new(itemtype=subident.type_)
                    child = subident.new(type_=childtype)
                    if not stop or not stop(child):
                        stack.append((sublevel, child))


def get_ident(idents: Iterable[Ident], name: str, value=None, dym=False) -> Ident | None:
    """Retrieve identifier by `name`, without iterating over the entire identifier tree."""
    assert value is None, "TODO"
    ident = _get_ident(idents, name)
    if ident is not None:
        return ident

    # Beautiful error handling
    msg = f"'{name}' is not known."
    #     if dym and any(idents):
    #         names = [ident.name for ident in _iters(idents)]
    #         nametree = align(_get_identtree(idents), rtrim=True)
    #         msg += f" Known are\n{nametree}\n\n{msg}\n"
    #         msg += didyoumean(name, names, multiline=True)
    raise ValueError(msg)


def get_subname(parent: Ident, ident: Ident):
    """Get name relative to parent."""
    if parent is ident:
        return ident.suffix
    parentbasename = parent.basename
    return ident.name.removeprefix(parentbasename)[1:]


# def get_subnames(idents):
#    """Return names of hierarchical idents."""
#     names = []
#     prefix = ""
#     for ident in idents:
#         basename = ident.basename
#         names.append(basename.removeprefix(prefix))
#         prefix = f"{basename}_"
#     return names


def _get_ident(idents, name) -> Ident | None:
    # TODO: optimize
    for _, ident in _iters(idents):
        if ident.name == name:
            return ident
    return None


# def _get_identtree(idents, pre=""):
#     for ident in _iters(idents):
#         pre = "  " * ident.level
#         yield f"{pre}'{ident.name}'", ident.type_


def get_expridents(expr: Expr) -> tuple[Ident, ...]:
    """
    Determine used identifier in `expr`.
    """
    idents = {}
    heap = deque((expr,))
    while heap:
        item = heap.popleft()
        if isinstance(item, ConstExpr):
            pass
        elif isinstance(item, Op):
            heap.append(item.left)
            heap.append(item.right)
        elif isinstance(item, (SOp, SliceOp)):
            heap.append(item.one)
        elif isinstance(item, (ConcatExpr, MinimumExpr, MaximumExpr)):
            heap.extend(item.items)
        elif isinstance(item, TernaryExpr):
            heap.append(item.cond.left)
            heap.append(item.cond.right)
            heap.append(item.one)
            heap.append(item.other)
        elif isinstance(item, Log2Expr):
            heap.append(item.expr)
        elif isinstance(item, Ident):
            if item.name not in idents:
                idents[item.name] = item
        else:
            raise TypeError(f"Unknown expr {item}")  # pragma: no cover
    return tuple(idents.values())
