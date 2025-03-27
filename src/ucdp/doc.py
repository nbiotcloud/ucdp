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
Documentation Container.

The documentation container unifies and eases the handling of documentation strings.
Especially [doc_from_type()][ucdp.docutil.doc_from_type] serves the standard approach,
to create doc for a type related instance.
"""

from .object import LightObject


class Doc(LightObject):
    """
    Documentation Container.

    Documentation is always about a title, a long description and an optional source code comment.
    [Doc][ucdp.doc.Doc] carries all 3 of them.

    Attributes:
        title: Full Spoken Name.
        descr: Documentation Description.
        comment: Source Code Comment. Default is 'title'

    ??? Example "Dictorary Examples"
        Basics:

            >>> from tabulate import tabulate
            >>> import ucdp as u
            >>> docs = (
            ...     u.Doc(),
            ...     u.Doc(title='title'),
            ...     u.Doc(title='title', comment=None),
            ...     u.Doc(descr='descr'),
            ...     u.Doc(comment='comment')
            ... )
            >>> print(tabulate([(doc, doc.title, doc.descr, doc.comment, doc.comment_or_title) for doc in docs],
            ...                headers=("Doc()", ".title", ".descr", ".comment", ".comment_or_title")))
            Doc()                   .title    .descr    .comment    .comment_or_title
            ----------------------  --------  --------  ----------  -------------------
            Doc()
            Doc(title='title')      title                           title
            Doc(title='title')      title                           title
            Doc(descr='descr')                descr
            Doc(comment='comment')                      comment     comment

        Documentation instances are singleton and share the same memory:

            >>> Doc(title='title') is Doc(title='title')
            True
    """

    title: str | None = None
    """
    Full Spoken Name.

    Identifier are often appreviations.
    The ``title`` should contain the full spoken name.

    A signal ``amp_gain`` should have the title ``Amplifier Gain``.
    """

    descr: str | None = None
    """
    Documentation Description.

    The ``descr`` can contain any multiline **user** documentation.
    """

    comment: str | None = None
    """
    Source Code Comment.

    Source code should be commented.
    The ``comment`` can contain any developer / **non-user** documentation.
    Anything useful developer information.
    """

    @property
    def comment_or_title(self):
        """Return `comment` if set, otherwise `title`."""
        return self.comment or self.title
