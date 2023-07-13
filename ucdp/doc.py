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
Documentation Container.

The documentation container unifies and eases the handling of documentation strings.
Especially :any:`Doc.from_type()` serves the standard approach, to create doc for a type related instance.
"""
import typing

from .attrs import NOTHING, ReusedFrozen, field, frozen


@frozen
class Doc(ReusedFrozen):

    """
    Documentation Container.

    Documentation is always about a title, a long description and an optional source code comment.
    :any:`Doc` carries all 3 of them.

    Keyword Args:
        title (str): Full Spoken Name.
        descr (str): Documentation Description.
        comment (str): Source Code Comment. Default is 'title'

    >>> from tabulate import tabulate
    >>> import ucdp
    >>> docs = (
    ...     ucdp.Doc(),
    ...     ucdp.Doc(title='title'),
    ...     ucdp.Doc(title='title', comment=None),
    ...     ucdp.Doc(title='title', comment=ucdp.NOTHING),
    ...     ucdp.Doc(descr='descr'),
    ...     ucdp.Doc(comment='comment')
    ... )
    >>> print(tabulate([(doc, doc.title, doc.descr, doc.comment) for doc in docs],
    ...                headers=("Doc()", ".title", ".descr", ".comment")))
    Doc()                             .title    .descr    .comment
    --------------------------------  --------  --------  ----------
    Doc()
    Doc(title='title')                title               title
    Doc(title='title', comment=None)  title
    Doc(title='title')                title               title
    Doc(descr='descr')                          descr
    Doc(comment='comment')                                comment

    Documentation instances are singleton and share the same memory:

    >>> Doc(title='title') is Doc(title='title')
    True
    """

    # pylint: disable=too-few-public-methods

    title: typing.Optional[str] = field(default=None)
    """
    Full Spoken Name.

    Identifier are often appreviations.
    The ``title`` should contain the full spoken name.

    A signal ``amp_gain`` should have the title ``Amplifier Gain``.
    """

    descr: typing.Optional[str] = field(default=None)
    """
    Documentation Description.

    The ``descr`` can contain any multiline **user** documentation.
    """

    comment: typing.Optional[str] = field()
    """
    Source Code Comment. Default is 'title'.

    Source code should be commented.
    The ``comment`` can contain any developer / **non-user** documentation.
    Anything useful developer information.
    """

    @comment.default  # type: ignore[union-attr]
    def _comment_default(self):
        return self.title or None

    @staticmethod
    def from_type(type_, title=NOTHING, descr=NOTHING, comment=NOTHING):
        """
        Create :any:`Doc` with defaults from `type_`.

        Types may define `title`, `descr` or `comment`. They are taken as default, if no other value is given:

        Please note, that the default comment is title!

        >>> import ucdp
        >>> class MyType(ucdp.BitType):
        ...     title = "My Bit Title"
        ...     comment = "My Bit Comment"
        >>> ucdp.Doc.from_type(MyType())
        Doc(title='My Bit Title', comment='My Bit Comment')
        >>> ucdp.Doc.from_type(MyType(), title="My Title", comment=ucdp.NOTHING)
        Doc(title='My Title', comment='My Bit Comment')
        >>> ucdp.Doc.from_type(MyType(), title="My Title", comment=None)
        Doc(title='My Title', comment=None)
        >>> ucdp.Doc.from_type(MyType(), comment="My Bit Comment")
        Doc(title='My Bit Title', comment='My Bit Comment')
        """
        # Some kind of optimized default routine
        if title is NOTHING:
            title = type_.title
            if comment is NOTHING and type_.comment is not None:
                comment = type_.comment
        elif comment is NOTHING:
            comment = type_.comment if type_.comment is not None else title
        if descr is NOTHING:
            descr = type_.descr
        return Doc(title, descr, comment)
