# MIT License
#
# Copyright (c) 2025 nbiotcloud
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

"""
Note.

This note can be used instead of an expression.
"""

from .object import LightObject


class Note(LightObject):
    """
    Simply Note on Assignments.

    Attributes:
        note: Note.

    ??? Example "Note Examples"
        Example.

            >>> import ucdp as u
            >>> u.OPEN
            Note(note='OPEN')
            >>> u.TODO
            Note(note='TODO')
    """

    note: str

    def __str__(self):
        return self.note


OPEN = Note(note="OPEN")
"""Open Note."""

TODO = Note(note="TODO")
"""Todo Note."""


def note(note: str) -> Note:
    """Create Note."""
    return Note(note=note)


class Default(Note):
    """Default Value Note."""


DEFAULT = Default(note="DEFAULT")
