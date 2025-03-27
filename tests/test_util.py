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
"""Test Utilities."""

import sys
from inspect import getfile
from pathlib import Path

import ucdp as u

COPYRIGHT = [
    "",
    " MIT License",
    "",
    " Copyright (c) 2024-2025 nbiotcloud",
    "",
    " Permission is hereby granted, free of charge, to any person obtaining a copy",
    ' of this software and associated documentation files (the "Software"), to deal',
    " in the Software without restriction, including without limitation the rights",
    " to use, copy, modify, merge, publish, distribute, sublicense, and/or sell",
    " copies of the Software, and to permit persons to whom the Software is",
    " furnished to do so, subject to the following conditions:",
    "",
    " The above copyright notice and this permission notice shall be included in all",
    " copies or substantial portions of the Software.",
    "",
    ' THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR',
    " IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,",
    " FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE",
    " AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER",
    " LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,",
    " OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE",
    " SOFTWARE.",
    "",
]


def test_get_copyright(example_simple):
    """Test Copyright."""
    top = u.load("glbl_lib.clk_gate", paths=None)
    assert u.get_copyright(top.mod).splitlines() == COPYRIGHT
    assert u.get_copyright(Path(getfile(top.mod.__class__))).splitlines() == COPYRIGHT


def test_extend_sys_path(tmp_path):
    """Test Extend Sys Path."""
    before = tuple(sys.path)

    with u.extend_sys_path([]):
        pass
    assert before == tuple(sys.path)

    assert str(tmp_path) not in sys.path
    with u.extend_sys_path([tmp_path]):
        assert str(tmp_path) in sys.path

    assert before == tuple(sys.path)
