"""Pytest Configuration and Fixtures."""

import os
from pathlib import Path
from unittest import mock

import ucdp as u
from pytest import fixture

EXAMPLES_PATH = Path(u.__file__).parent / "examples"


@fixture
def example_simple():
    """Add access to ``examples/simple``."""
    example_path = EXAMPLES_PATH / "simple"
    with u.extend_sys_path((example_path,)):
        yield example_path


@fixture
def example_bad():
    """Add access to ``examples/bad``."""
    example_path = EXAMPLES_PATH / "bad"
    with u.extend_sys_path((example_path,)):
        yield example_path


@fixture
def example_filelist():
    """Add access to ``examples/filelist``."""
    example_path = EXAMPLES_PATH / "filelist"
    with u.extend_sys_path((example_path,)):
        yield example_path


@fixture
def example_param():
    """Add access to ``examples/param``."""
    example_path = EXAMPLES_PATH / "param"
    with u.extend_sys_path((example_path,)):
        yield example_path


@fixture
def prjroot(tmp_path):
    """Project Environment."""
    with mock.patch.dict(os.environ, {"PRJROOT": str(tmp_path)}):
        yield tmp_path


@fixture
def testdata():
    """Add access to ``testdata``."""
    path = Path(__file__).parent / "testdata"
    with u.extend_sys_path((path,)):
        yield path
