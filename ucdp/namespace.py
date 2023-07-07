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
Namespace.

A namespace is nothing more than a dictionary with some benefits:

* items use `item.name` as dictionary key. This is checked.
* items **cannot** be overwritten
* items **cannot** be deleted
* the namespace can be locked for modications via `lock`.
* iteration over the namespaces yields the items and not their keys.

>>> from collections import namedtuple
>>> Item = namedtuple('Item', 'name foo bar')
>>> namespace = Namespace([Item('a', 1, 2)])
>>> namespace.add(Item('b', 3, 4))
>>> namespace['c'] = Item('c', 5, 6)
>>> namespace.is_locked
False
>>> for item in namespace:
...     item
Item(name='a', foo=1, bar=2)
Item(name='b', foo=3, bar=4)
Item(name='c', foo=5, bar=6)
>>> for item in namespace.keys():
...     item
'a'
'b'
'c'
>>> for item in namespace.values():
...     item
Item(name='a', foo=1, bar=2)
Item(name='b', foo=3, bar=4)
Item(name='c', foo=5, bar=6)
>>> namespace.get('b')
Item(name='b', foo=3, bar=4)
>>> namespace.get('d')
Traceback (most recent call last):
  ...
ValueError: 'd' Known are 'a', 'b' and 'c'.

Locking:

>>> namespace.lock()
>>> namespace.is_locked
True
>>> namespace['d'] = Item('d', 7, 8)
Traceback (most recent call last):
  ...
ucdp.namespace.LockError: Item(name='d', foo=7, bar=8)

>>> len(namespace)
3
"""

from .nameutil import didyoumean


class Namespace(dict):
    """
    Namespace.
    """

    def __init__(self, items=None):
        super().__init__()
        self.__locked = False
        if items:
            for item in items:
                if item.name in self.keys():
                    raise ValueError(f"{item.name} already exists ({self[item.name]!r})")
                self[item.name] = item

    @property
    def is_locked(self):
        """Locked."""
        return self.__locked

    def lock(self):
        """Lock."""
        assert not self.__locked, f"{self} is already locked"
        self.__locked = True

    def add(self, item, exist_ok=False):
        """Add."""
        try:
            self[item.name] = item
        except DuplicateError as exc:
            if not exist_ok:
                raise exc

    def get(self, name):
        try:
            item = super().__getitem__(name)
        except KeyError as exc:
            dym = didyoumean(name, self.keys(), known=True)
            raise ValueError(f"{exc!s}{dym}") from None
        return item

    def __getitem__(self, name):
        try:
            return super().__getitem__(name)
        except KeyError as exc:
            raise ValueError(str(exc)) from None

    def __setitem__(self, name, item):
        if self.__locked:
            raise LockError(str(item))
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


class LockError(ValueError):
    """Lock Error."""


class DuplicateError(ValueError):
    """Duplicate Error."""
