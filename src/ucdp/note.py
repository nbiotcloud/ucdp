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
TODO = Note(note="TODO")
