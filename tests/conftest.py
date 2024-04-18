"""Pytest Configuration and Fixtures."""

from pathlib import Path

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
