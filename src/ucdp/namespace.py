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
Namespace.

A namespace is nothing more than a dictionary with some benefits:

* items use `item.name` as dictionary key. This is checked.
* items **cannot** be overwritten
* items **cannot** be deleted
* the namespace can be locked for modifications via `lock`.
* iteration over the namespaces yields the items and not their keys.

??? Example "Namespace Examples"
    Examples.

        >>> from collections import namedtuple
        >>> NamedObject = namedtuple('NamedObject', 'name foo bar')
        >>> namespace = Namespace([NamedObject('a', 1, 2)])
        >>> namespace.add(NamedObject('b', 3, 4))
        >>> namespace['c'] = NamedObject('c', 5, 6)
        >>> namespace.is_locked
        False
        >>> for item in namespace:
        ...     item
        NamedObject(name='a', foo=1, bar=2)
        NamedObject(name='b', foo=3, bar=4)
        NamedObject(name='c', foo=5, bar=6)
        >>> for item in namespace.keys():
        ...     item
        'a'
        'b'
        'c'
        >>> for item in namespace.values():
        ...     item
        NamedObject(name='a', foo=1, bar=2)
        NamedObject(name='b', foo=3, bar=4)
        NamedObject(name='c', foo=5, bar=6)
        >>> namespace['b']
        NamedObject(name='b', foo=3, bar=4)
        >>> namespace['d']
        Traceback (most recent call last):
        ...
        KeyError: 'd'
        >>> namespace.get_dym('d')
        Traceback (most recent call last):
        ...
        ValueError: 'd'. Known are 'a', 'b' and 'c'.

    Locking:

        >>> namespace.lock()
        >>> namespace.is_locked
        True
        >>> namespace['d'] = NamedObject('d', 7, 8)
        Traceback (most recent call last):
        ...
        ucdp.exceptions.LockError: Namespace is already locked. Cannot add items anymore.

        >>> len(namespace)
        3
"""

from collections.abc import Iterable
from typing import Any

from .exceptions import DuplicateError, LockError
from .nameutil import didyoumean
from .object import NamedObject


class Namespace(dict):
    """
    Namespace.
    """

    def __init__(self, items: Iterable[NamedObject] | None = None):
        super().__init__()
        self.__is_locked = False
        if items:
            for item in items:
                self[item.name] = item

    @property
    def is_locked(self) -> bool:
        """Locked."""
        return self.__is_locked

    def lock(self) -> None:
        """Lock."""
        if self.__is_locked:
            raise LockError("Namespace is already locked. Cannot lock again.")
        self.__is_locked = True

    def add(self, item: NamedObject, exist_ok: bool = False):
        """Add."""
        try:
            self[item.name] = item
        except DuplicateError as exc:
            if not exist_ok:
                raise exc

    def get_dym(self, name: str) -> NamedObject:
        """Get NamedObject."""
        try:
            item = self[name]
        except KeyError as exc:
            dym = didyoumean(name, self.keys(), known=True)
            raise ValueError(f"{exc!s}.{dym}") from None
        return item

    def __setitem__(self, name, item):
        self._set_items(((name, item),))

    def _set_items(self, items: Iterable[tuple[str, NamedObject]]):
        if self.__is_locked:
            raise LockError("Namespace is already locked. Cannot add items anymore.")
        for name, item in items:
            if item.name != name:
                raise ValueError(f"{item} with must be stored at name '{item.name}' not at '{name}'")
            if item.name in self.keys():
                if item is self[item.name]:
                    raise DuplicateError(f"{self[item.name]!r} already exists")
                raise DuplicateError(f"Name '{item.name}' already taken by {self[item.name]!r}")
            super().__setitem__(name, item)

    def __delitem__(self, key):
        raise TypeError(f"It is forbidden to remove {key!r}.")

    def __iter__(self):
        yield from self.values()

    def __repr__(self):
        return f"{self.__class__.__qualname__}({list(self)})"

    def pop(self, *args) -> Any:
        """
        Pop value.

        If key is in the dictionary, remove it and return its value, else return default.
        If default is not given and key is not in the dictionary, a KeyError is raised.

        This operation is forbidden.
        """
        raise TypeError("It is forbidden to remove any item.")

    def popitem(self) -> tuple[Any, Any]:
        """
        Remove and return a (key, value) pair from the dictionary.

        This operation is forbidden.
        """
        raise TypeError("It is forbidden to remove any item.")

    def set_default(self, key, value=None) -> Any:
        """
        Set Default.

        If key is in the dictionary, return its value.
        If not, insert key with a value of default and return default. ``default`` defaults to None.
        """
        if self.__is_locked:
            raise LockError("Namespace is already locked. Cannot add items anymore.")
        if key in self.keys():
            return self[key]
        self[key] = value
        return value

    def update(self, other: dict) -> None:  # type: ignore[override]
        """Update the dictionary with the key/value pairs from other."""
        self._set_items(other.items())

    def __ior__(self, other):
        if not isinstance(other, dict):
            return NotImplemented
        self._set_items(other.items())
        return self

    def __or__(self, other) -> "Namespace":
        if not isinstance(other, dict):
            return NotImplemented
        if self.__is_locked:
            raise LockError("Namespace is already locked. Cannot add items anymore.")
        items = dict(self)
        items.update(other)
        namespace = self.__class__()
        namespace._set_items(items.items())
        return namespace
