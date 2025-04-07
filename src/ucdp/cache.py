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
Cache.
"""

import os
from pathlib import Path
from shutil import rmtree

from anycache import AnyCache
from platformdirs import user_cache_dir
from pydantic import BaseModel


class Cache(BaseModel):
    """UCDP Caching System."""

    path: Path | None
    maxsize: int = 10 * 1024 * 1024

    @classmethod
    def init(cls) -> "Cache":
        """Initialize."""
        return Cache(path=get_cachepath())

    def disable(self):
        """Disable Caching."""
        self.path = None

    def clear(self):
        """Clear Cache."""
        if self.path:
            rmtree(self.path, ignore_errors=True)

    @property
    def templates_path(self) -> Path | None:
        """Path for Templates."""
        if not self.path:
            return None
        return self.path / "templates"

    @property
    def loader_cache(self) -> AnyCache:
        """Path for Loader."""
        return self._get_anycache("loader")

    def get_cache(self, name: str):
        """Create Cache Function Decorator."""
        return self._get_anycache(name).anycache

    def _get_anycache(self, name: str) -> AnyCache:
        if not self.path:
            return AnyCache(maxsize=0)
        return AnyCache(cachedir=self.path / name, maxsize=self.maxsize)


def get_cachepath() -> Path | None:
    """Get Cache Base Path."""
    try:
        envvar = os.environ["UCDP_CACHE"]
        if not envvar:
            return None
        path = Path(envvar)
    except KeyError:
        try:
            path = Path(user_cache_dir("ucdp", ensure_exists=True))
        except RuntimeError:  # pragma: no cover
            return None
    try:
        path.mkdir(parents=True, exist_ok=True)
        (path / ".initialized").touch()
    except Exception:
        return None
    return path


CACHE = Cache.init()
