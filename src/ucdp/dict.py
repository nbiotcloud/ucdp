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
Dictionary.
"""

from typing import Any

from .object import Object, PrivateField


class Dict(Object):
    """
    Re-Implementation of python dictorary, compatible with [Object][ucdp.object.Object].

    ??? Example "Dictorary Examples"
        Basics:

            >>> import ucdp as u
            >>> data = u.Dict()
            >>> data
            Dict()

        Add items:

            >>> data['a'] = 1
            >>> data['c'] = 3
            >>> data['b'] = 2

        Get items:

            >>> data['a']
            1
            >>> data['d']
            Traceback (most recent call last):
            ...
            KeyError: 'd'

        Iteration:

            >>> tuple(data)
            ('a', 'c', 'b')

        Keys:

            >>> data.keys()
            dict_keys(['a', 'c', 'b'])

        Values:

            >>> data.values()
            dict_values([1, 3, 2])

        Key-Value Pairs:

            >>> data.items()
            dict_items([('a', 1), ('c', 3), ('b', 2)])
    """

    _items: dict[Any, Any] = PrivateField(default_factory=dict)

    def __iter__(self):
        yield from self._items.keys()

    def keys(self):
        """Return Dictionary Keys."""
        return self._items.keys()

    def values(self):
        """Return Dictionary Value."""
        return self._items.values()

    def items(self):
        """Return Key-Value Pairs."""
        return self._items.items()

    def get(self, *args, **kwargs):
        """Retrieve Element."""
        return self._items.get(*args, **kwargs)

    def __getitem__(self, key):
        return self._items[key]

    def __setitem__(self, key: Any, value: Any):
        self._items[key] = value

    def __len__(self) -> int:
        return len(self._items)

    def __contains__(self, key) -> bool:
        return key in self._items
