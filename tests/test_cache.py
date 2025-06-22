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
"""Test Cache."""

import os
from unittest import mock

import ucdp as u
from ucdp.cache import Cache


def test_default(monkeypatch):
    """Default."""
    monkeypatch.delenv("UCDP_CACHE", raising=False)
    cache = Cache.init()
    assert cache.path
    assert cache.templates_path == cache.path / "templates"
    assert cache.path.exists()


def test_get_cache(tmp_path):
    """Get Cache."""
    with mock.patch.dict(os.environ, {"UCDP_CACHE": str(tmp_path)}):
        cache = Cache.init()

        test_get_cache.count = 0

        @cache.get_cache("foo")()
        def myfunc(a, b):
            test_get_cache.count += 1
            return a + b

        assert myfunc(1, 2) == 3
        assert test_get_cache.count == 1
        assert myfunc(1, 2) == 3
        assert test_get_cache.count == 1

        cache.clear()

        assert myfunc(1, 2) == 3
        assert test_get_cache.count == 2


def test_env(tmp_path):
    """Via Env Path."""
    with mock.patch.dict(os.environ, {"UCDP_CACHE": str(tmp_path)}):
        cache = Cache.init()
        assert cache.path == tmp_path
        assert cache.templates_path == tmp_path / "templates"


def test_env_invalid(tmp_path):
    """Via Invalid Env Path."""
    invalid_path = tmp_path / "invalid"
    invalid_path.touch()
    with mock.patch.dict(os.environ, {"UCDP_CACHE": str(invalid_path)}):
        cache = Cache.init()
        assert cache.path is None
        assert cache.templates_path is None


def test_env_disabled(tmp_path):
    """Caching Disabled."""
    with mock.patch.dict(os.environ, {"UCDP_CACHE": ""}):
        cache = Cache.init()
        assert cache.path is None
        assert cache.templates_path is None


def test_cache():
    """Test Cache is Exposed."""
    assert isinstance(u.CACHE, Cache)
