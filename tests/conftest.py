"""Pytest Configuration and Fixtures."""

import os
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

from pytest import fixture

import ucdp as u

EXAMPLES_PATH = Path(u.__file__).parent / "examples"
TESTDATA_PATH = Path(__file__).parent / "testdata"
TESTS_PATH = Path(__file__).parent


@contextmanager
def _env(prjroot: Path, path: Path | None = None):
    """Environment."""
    path = path or prjroot
    env = {
        "PRJROOT": str(prjroot),
        "UCDP_PATH": str(path),
        "UCDP_MAXWORKERS": "1",
        "UCDP_NO_COLOR": "1",
    }

    with u.extend_sys_path((path,)):
        with mock.patch.dict(os.environ, env):
            yield path


@fixture
def prjroot(tmp_path):
    """Add access to ``examples/simple``."""
    yield tmp_path


@fixture
def example_simple(prjroot):
    """Add access to ``examples/simple``."""
    with _env(prjroot, path=EXAMPLES_PATH / "simple") as path:
        yield path


@fixture
def example_bad(prjroot):
    """Add access to ``examples/bad``."""
    with _env(prjroot, path=EXAMPLES_PATH / "bad") as path:
        yield path


@fixture
def example_filelist(prjroot):
    """Add access to ``examples/filelist``."""
    with _env(prjroot, path=EXAMPLES_PATH / "filelist") as path:
        yield path


@fixture
def example_param(prjroot):
    """Add access to ``examples/param``."""
    with _env(prjroot, path=EXAMPLES_PATH / "param") as path:
        yield path


@fixture
def testdata(prjroot):
    """Add access to ``testdata``."""
    with _env(prjroot, path=TESTDATA_PATH) as path:
        yield path


@fixture
def tests(prjroot):
    """Add access to ``tests``."""
    with _env(prjroot, path=TESTS_PATH.parent) as path:
        yield path


@fixture
def examples_path(prjroot):
    """Add access to ``examples``."""
    yield EXAMPLES_PATH


@fixture
def uartcorefile(prjroot):
    """UART Core File."""
    uartcorefile = prjroot / "uart_lib" / "uart" / "rtl" / "uart_core.sv"
    uartcorefile.parent.mkdir(parents=True, exist_ok=True)
    uartcorefile.touch()
    yield
