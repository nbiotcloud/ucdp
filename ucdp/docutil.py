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
Doc Utilities.
"""
from .doc import Doc


def doc_from_type(type_, **kwargs):
    """
    Create :any:`Doc` with defaults from `type_`.

    Types may define `title`, `descr` or `comment`. They are taken as default, if no other value is given:

    Please note, that the default comment is title!

    >>> import ucdp
    >>> class MyType(ucdp.BitType):
    ...     title:str = "My Bit Title"
    ...     comment:str = "My Bit Comment"
    >>> ucdp.doc_from_type(MyType())
    Doc(title='My Bit Title', comment='My Bit Comment')
    >>> ucdp.doc_from_type(MyType(), title="My Title")
    Doc(title='My Title', comment='My Bit Comment')
    >>> ucdp.doc_from_type(MyType(), title="My Title", comment="")
    Doc(title='My Title', comment='')
    >>> ucdp.doc_from_type(MyType(), comment="My Comment")
    Doc(title='My Bit Title', comment='My Comment')
    """
    # Some kind of optimized default routine
    dump = type_.model_dump()
    for name in ("title", "descr", "comment"):
        if kwargs.get(name, None) is None:
            kwargs[name] = dump.get(name, None)
    return Doc(**kwargs)
