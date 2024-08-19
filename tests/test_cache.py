#
# MIT License
#
# Copyright (c) 2024 nbiotcloud
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
"""Test Cache."""

import os
from pathlib import Path
from unittest import mock

from ucdp.cache import Cache


def test_default():
    """Default."""
    with mock.patch.dict(os.environ, {}):
        cache = Cache.init()
        default_path = Path.home() / ".cache" / "ucdp"
        assert cache.path == default_path
        assert cache.templates_path == default_path / "templates"
        assert cache.loader_cache.maxsize != 0
        assert default_path.exists()
        cache.clear()
        assert not default_path.exists()


def test_env(tmp_path):
    """Via Env Path."""
    with mock.patch.dict(os.environ, {"UCDP_CACHE": str(tmp_path)}):
        cache = Cache.init()
        assert cache.path == tmp_path
        assert cache.templates_path == tmp_path / "templates"
        assert cache.loader_cache.maxsize != 0


def test_env_invalid(tmp_path):
    """Via Invalid Env Path."""
    invalid_path = tmp_path / "invalid"
    invalid_path.touch()
    with mock.patch.dict(os.environ, {"UCDP_CACHE": str(invalid_path)}):
        cache = Cache.init()
        assert cache.path is None
        assert cache.templates_path is None
        assert cache.loader_cache.maxsize == 0


def test_env_disabled(tmp_path):
    """Caching Disabled."""
    with mock.patch.dict(os.environ, {"UCDP_CACHE": ""}):
        cache = Cache.init()
        assert cache.path is None
        assert cache.templates_path is None
        assert cache.loader_cache.maxsize == 0