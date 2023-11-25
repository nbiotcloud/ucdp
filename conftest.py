"""Pytest Configuration and Fixtures."""

import sys
from pathlib import Path

from pytest import fixture

EXAMPLES = Path(__file__)


@fixture
def example_simple():
    """Add access to ``examples/simple``."""
    orig = sys.path
    sys.path = [*sys.path, str(EXAMPLES / "simple")]
    yield
    sys.path = orig
