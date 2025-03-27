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
"""Test Route Path."""

import re

from pytest import raises

import ucdp as u


def test_parsepath_full():
    """Full Path."""
    path = u.parse_routepath("u_sub/u_bar/clk_i")
    assert str(path) == "u_sub/u_bar/clk_i"
    assert path.path == "u_sub/u_bar"
    assert path.expr == "clk_i"
    assert path.create is False
    assert path.cast is False


def test_parsepath_empty():
    """Empty Path."""
    with raises(ValueError, match=re.escape("Invalid route path ''")):
        u.parse_routepath("")


def test_parsepath_up():
    """Up Path."""
    path = u.parse_routepath("../port_i")
    assert str(path) == "../port_i"
    assert path.path == ".."
    assert path.expr == "port_i"
    assert path.create is False
    assert path.cast is False


def test_parsepath_cast():
    """Casting."""
    path = u.parse_routepath("cast(u_sub/clk_i)")
    assert str(path) == "cast(u_sub/clk_i)"
    assert path.path == "u_sub"
    assert path.expr == "clk_i"
    assert path.create is False
    assert path.cast is True


def test_parsepath_optcast():
    """'Optional Casting."""
    path = u.parse_routepath("optcast(u_sub/clk_i)")
    assert str(path) == "optcast(u_sub/clk_i)"
    assert path.path == "u_sub"
    assert path.expr == "clk_i"
    assert path.create is False
    assert path.cast is None


def test_parsepath_create():
    """Creating."""
    path = u.parse_routepath("create(u_sub/clk_i)")
    assert str(path) == "create(u_sub/clk_i)"
    assert path.path == "u_sub"
    assert path.expr == "clk_i"
    assert path.create is True
    assert path.cast is False


def test_parsepath_create_cast():
    """Create and Casting."""
    with raises(ValueError, match=re.escape("Invalid route path 'create(cast((u_sub/clk_i))'")):
        u.parse_routepath("create(cast((u_sub/clk_i))")


def test_parsepath_create_cast_bracket():
    """Create and Casting."""
    with raises(ValueError, match=re.escape("Invalid route path 'cast(u_sub/clk_i'")):
        u.parse_routepath("cast(u_sub/clk_i")


def test_parsepath_basepath():
    """Basepath Path."""
    path = u.parse_routepath("u_sub/u_bar/clk_i", basepath="u_sim")
    assert str(path) == "u_sim/u_sub/u_bar/clk_i"
    assert path.path == "u_sim/u_sub/u_bar"
    assert path.expr == "clk_i"
    assert path.create is False
    assert path.cast is False


def test_create_cast():
    """Create and Casting."""
    with raises(u.ValidationError, match=re.escape("[opt]cast() and create() are mutually exclusive")):
        u.RoutePath(expr="clk_i", create=True, cast=True)


def test_expr():
    """Expression."""
    expr = u.Signal(u.UintType(8), "sig_s")
    path = u.parse_routepath(expr)
    assert str(path) == "sig_s"
    assert path.path is None
    assert path.expr is expr
    assert path.create is False
    assert path.cast is False
