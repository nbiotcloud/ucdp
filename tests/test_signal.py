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
"""Signal and Port Testing."""

import ucdp as u


def test_title_descr_attribute():
    """Title, Descr, Comment."""
    signal = u.Signal(u.BitType(), "signal_s")
    assert signal.type_ is u.BitType()
    assert signal.name == "signal_s"
    assert signal.direction == u.FWD
    assert signal.ifdefs == ()
    assert str(signal) == "signal_s"
    assert int(signal) == 0
    assert signal.doc == u.Doc()
    assert signal.title is None
    assert signal.descr is None
    assert signal.comment is None
    assert signal.comment_or_title is None

    signal = u.Signal(u.BitType(), "signal", doc=u.Doc(title="my title", comment="my comment"))
    assert signal.name == "signal"
    assert signal.doc == u.Doc(title="my title", comment="my comment")
    assert signal.title == "my title"
    assert signal.descr is None
    assert signal.comment == "my comment"
    assert signal.comment_or_title == "my comment"

    signal = u.Signal(u.BitType(), "signal", doc=u.Doc(descr="my descr"))
    assert signal.name == "signal"
    assert signal.doc == u.Doc(descr="my descr")
    assert signal.title is None
    assert signal.descr == "my descr"
    assert signal.comment is None
    assert signal.comment_or_title is None
