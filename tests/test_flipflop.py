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
"""Test Flip-Flop."""

from pytest import fixture

import ucdp as u


@fixture
def idents():
    """Some Ports."""
    return u.Idents(
        [
            u.Port(u.ClkRstAnType(), "main_i"),
            u.Port(u.UintType(8), "vec_a_i"),
            u.Signal(u.UintType(8), "vec_a_s"),
            u.Signal(u.UintType(4), "vec_b_s"),
            u.Signal(u.UintType(4), "vec_c_s"),
        ]
    )


def test_flipflop(idents):
    """Basics."""
    rst_an = u.Signal(u.RstAnType(), "rst_s")
    clk = u.Signal(u.ClkType(), "clk_s")
    flipflop = u.FlipFlop(targets=idents, sources=idents, rst_an=rst_an, clk=clk)

    assert flipflop.rst_an is rst_an
    assert flipflop.clk is clk
    assert flipflop.rst is None
    assert flipflop.ena is None

    # TESTME: rst_an type error
    # TESTME: clk type error


def test_flipflop_rst(idents):
    """Flip Flop with Reset."""

    # TESTME:


def test_flipflop_ena(idents):
    """Flip Flop with Ena."""

    # TESTME:
