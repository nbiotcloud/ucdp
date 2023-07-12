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


"""Module Utilities."""

from collections import deque
from typing import Optional

from .base import BaseMod
from .config import AVersionConfig
from .mods import CoreMod


def get_topmod(mod: BaseMod) -> BaseMod:
    """Return topmost module of `mod`."""
    while mod.parent:
        mod = mod.parent
    return mod


def get_modbase(mod, required=False):
    """Return module basemodule."""
    modbasename = mod.modbasenames[0]
    base = modbasename if isinstance(mod, CoreMod) or required or mod.modname != modbasename else None
    while isinstance(mod, CoreMod):
        subbase = get_modbase(mod.parent, required=True)
        base = f"{subbase}/{base}"
        mod = mod.parent
    return base


def walk(mod, ref):
    """
    Walk from `mod` to `ref`.
    """
    yield from _get_relpath(mod, ref)


def get_relpath(mod, ref):
    """Determine Relative path of `mod` to `ref`."""
    return tuple(item.name for item in _get_relpath(mod, ref))


def _get_relpath(mod, ref):
    """Determine Relative path of `mod` to `ref`."""
    if mod is ref:
        return tuple()
    stack = deque([(mod, [])])
    while stack:
        mod, path = stack.pop()
        while mod.parents and ref not in mod.parents:
            path.insert(0, mod)
            if len(mod.parents) > 1:
                for parent in mod.parents[1:]:
                    stack.appendleft((parent, path))
            mod = mod.parents[0]
        if ref in mod.parents:
            path.insert(0, mod)
            return tuple(path)
    raise ValueError(f"{mod} is not a submodule of {ref}")


def get_versionconfig(mod, required=False) -> Optional[AVersionConfig]:
    """Return :any:`AVersionConfig`."""
    config = getattr(mod, "version_config", None) or getattr(mod, "config", None)
    if config:
        if not isinstance(config, AVersionConfig):
            raise ValueError(f"{config} is not a ucdp.AVersionConfig")
        return config
    if required:
        raise ValueError(f"No 'config' or 'version_config' found on {mod}")
    return None


def get_version(mod, required=False):
    """Return version of mod."""
    config = get_versionconfig(mod, required=required)
    if config:
        return config.version
    return None
