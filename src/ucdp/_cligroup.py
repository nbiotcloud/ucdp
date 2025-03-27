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

"""Command Line Interface."""

import importlib
import os
from functools import lru_cache
from importlib.metadata import entry_points
from pathlib import Path

import click

from .logging import LOGGER
from .util import extend_sys_path

Paths = tuple[Path, ...]
PATHS = tuple(Path(path) for path in os.environ.get("UCDP_PATH", "").split())


@lru_cache
def _find_commands(paths: Paths):
    return dict(__find_commands(paths))


def __find_commands(paths: Paths):  # pragma: no cover
    """Find Commands."""
    for entry_point in entry_points(group="ucdp.cli"):
        yield entry_point.name, entry_point.value
    if paths:
        with extend_sys_path(paths, use_env_default=True):
            for path in paths:
                for clifile in path.glob("*/cli.py"):
                    libname, modname = clifile.parts[-2], clifile.stem
                    climod = importlib.import_module(f"{libname}.cli")
                    clicmds = getattr(climod, "UCDP_COMMANDS", [])
                    if not isinstance(clicmds, (list, tuple)):
                        LOGGER.warning("Invalid UCDP_COMMANDS in %s", clifile)
                        continue
                    for clicmd in clicmds:
                        yield clicmd, f"{libname}.{modname}.{clicmd}"


class MainGroup(click.Group):  # pragma: no cover
    """Main Command Group with Dynamically Loaded Commands."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def list_commands(self, ctx):
        """List Commands."""
        base = super().list_commands(ctx)
        lazy = list(_find_commands(PATHS))
        return sorted(base + lazy)

    def get_command(self, ctx, name):
        """Load Command."""
        if name in _find_commands(PATHS):
            try:
                return self._load(name)
            except Exception as exc:  # pragma: no cover
                LOGGER.error("Could not load command '%s' (%s)", name, exc)
        return super().get_command(ctx, name)

    def _load(self, name):
        import_path = _find_commands(PATHS)[name]
        modname, cmd_object_name = import_path.rsplit(".", 1)
        mod = importlib.import_module(modname)
        return getattr(mod, cmd_object_name)
