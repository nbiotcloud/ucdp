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
"""Test Utilities."""
import contextlib
import logging
import os
import shutil
import subprocess
from pathlib import Path

LEARN = True

TESTDATA = Path(__file__).parent / "testdata"


@contextlib.contextmanager
def chdir(path):
    """Change Working Directory to ``path``."""
    curdir = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(curdir)


def assert_gen(genpath, refpath):
    """Compare Generated Files Versus Reference."""
    genpath.mkdir(parents=True, exist_ok=True)
    refpath.mkdir(parents=True, exist_ok=True)
    if LEARN:  # pragma: no cover
        logging.getLogger(__name__).warning("LEARNING %s", refpath)
        shutil.rmtree(refpath, ignore_errors=True)
        shutil.copytree(genpath, refpath)
    cmd = ["diff", "-r", "--exclude", "__pycache__", str(refpath), str(genpath)]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as error:  # pragma: no cover
        assert False, error.stdout.decode("utf-8")
