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
"""Test Path Utilities."""

import os
import re
from pathlib import Path
from unittest import mock

from contextlib_chdir import chdir
from pytest import raises

import ucdp as u


def test_improved_glob(tmp_path):
    """Test improved_glob."""
    sub = tmp_path / "sub"
    sub.mkdir()
    song = tmp_path / "song.txt"
    song.touch()
    song2 = tmp_path / "song2.txt"
    song2.touch()
    subsong = sub / "song.txt"
    subsong.touch()
    nothing = tmp_path / "nothing.txt"

    # existing
    assert tuple(u.improved_glob("song.txt", basedir=tmp_path)) == (song,)
    assert tuple(u.improved_glob("sub/song.txt", basedir=tmp_path)) == (subsong,)

    # not existing one - do not clear
    assert tuple(u.improved_glob("song.txt")) == (Path("song.txt"),)
    assert tuple(u.improved_glob("nothing.txt", basedir=tmp_path)) == (nothing,)

    # glob
    assert tuple(u.improved_glob("song*.txt", basedir=tmp_path)) == (song, song2)

    # recursive
    assert tuple(u.improved_glob("**/*.txt", basedir=tmp_path)) == (song, song2, subsong)


def test_improved_glob_env(tmp_path):
    """Test improved_glob with Env."""
    sub = tmp_path / "sub"
    sub.mkdir()
    song = tmp_path / "song.txt"
    song.touch()
    song2 = tmp_path / "song2.txt"
    song2.touch()
    subsong = sub / "song.txt"
    subsong.touch()

    # existing songs
    with mock.patch.dict(os.environ, {"SUB": str(sub), "TMP": str(tmp_path)}):
        assert tuple(u.improved_glob("${SUB}/song.txt")) == (Path("${SUB}/song.txt"),)

        # glob
        assert tuple(u.improved_glob("${SUB}/song*.txt")) == (Path("${SUB}/song.txt"),)
        assert tuple(u.improved_glob("${SUB}/../song*.txt")) == (
            Path("${SUB}/../song.txt"),
            Path("${SUB}/../song2.txt"),
        )
        assert tuple(u.improved_glob("${TMP}/song*.txt")) == (
            Path("${TMP}/song.txt"),
            Path("${TMP}/song2.txt"),
        )

        # recursive
        assert tuple(u.improved_glob("${TMP}/**/*.txt")) == (
            Path("${TMP}/song.txt"),
            Path("${TMP}/song2.txt"),
            Path("${TMP}/sub/song.txt"),
        )


def test_improved_resolve(tmp_path):
    """Improved Resolve."""
    sub = tmp_path / "sub"
    sub.mkdir()
    song = tmp_path / "song.txt"
    song.touch()
    song2 = tmp_path / "song2.txt"
    song2.touch()
    subsong = sub / "song.txt"
    subsong.touch()
    nothing = tmp_path / "nothing.txt"

    assert u.improved_resolve(Path("song.txt"), basedir=tmp_path) == song
    assert u.improved_resolve(Path("song.txt"), basedir=tmp_path, strict=True) == song

    assert u.improved_resolve(Path("nothing.txt"), basedir=tmp_path) == nothing
    with raises(FileNotFoundError):
        u.improved_resolve(Path("nothing.txt"), basedir=tmp_path, strict=True)

    with chdir(sub):
        assert u.improved_resolve(Path("song.txt")) == subsong


def test_improved_resolve_env(tmp_path):
    """Improved Resolve with environment variables."""
    env1 = tmp_path / "env1"
    env1.mkdir()
    env2 = tmp_path / "env2"
    song1 = env1 / "song.txt"
    song1.touch()
    song2 = env2 / "song.txt"

    with mock.patch.dict(os.environ, {"ENV1": str(env1), "ENV2": str(env2)}):
        # defined and existing env path
        assert u.improved_resolve(Path("${ENV1}/song.txt")) == Path("${ENV1}") / "song.txt"
        assert u.improved_resolve(Path("${ENV1}/song.txt"), replace_envvars=True) == song1
        assert u.improved_resolve(Path("${ENV1}/song.txt"), replace_envvars=True, strict=True) == song1
        with raises(FileNotFoundError, match=re.escape("${ENV1}/song.txt")):
            u.improved_resolve(Path("${ENV1}/song.txt"), strict=True)

        # defined and not existing env path
        assert u.improved_resolve(Path("${ENV2}/song.txt")) == Path("${ENV2}") / "song.txt"
        assert u.improved_resolve(Path("${ENV2}/song.txt"), replace_envvars=True) == song2
        with raises(FileNotFoundError, match=re.escape(str(env2))):
            u.improved_resolve(Path("${ENV2}/song.txt"), replace_envvars=True, strict=True)
        with raises(FileNotFoundError, match=re.escape("${ENV2}/song.txt")):
            u.improved_resolve(Path("${ENV2}/song.txt"), strict=True)

        # not defined env path
        assert u.improved_resolve(Path("${ENV3}/song.txt")) == Path("${ENV3}") / "song.txt"
        assert (
            u.improved_resolve(Path("${ENV3}/song.txt"), replace_envvars=True)
            == Path().resolve() / Path("${ENV3}") / "song.txt"
        )
        with raises(FileNotFoundError, match=re.escape("${ENV3}")):
            u.improved_resolve(Path("${ENV3}/song.txt"), replace_envvars=True, strict=True)
        with raises(FileNotFoundError, match=re.escape("${ENV3}/song.txt")):
            u.improved_resolve(Path("${ENV3}/song.txt"), strict=True)


def test_use_envvars(tmp_path):
    """Test Use Envvars."""
    env1 = tmp_path / "env1"
    env2 = tmp_path / "env2"
    env2sub = env2 / "sub"
    env3 = tmp_path / "env3"
    other = tmp_path / "other"
    envvarnames = ("ENV1", "env2sub", "env2", "env3")
    with mock.patch.dict(os.environ, {"ENV1": str(env1), "env2sub": str(env2sub), "env2": str(env2)}):
        assert u.use_envvars(other, envvarnames) == other

        # defined and existing env path
        assert u.use_envvars(env1, envvarnames) == Path("${ENV1}")
        assert u.use_envvars(env1 / "file.txt", envvarnames) == Path("${ENV1}") / "file.txt"

        # defined and not existing env path
        assert u.use_envvars(env2, envvarnames) == Path("${env2}")
        assert u.use_envvars(env2sub, envvarnames) == Path("${env2sub}")

        # not defined
        assert u.use_envvars(env3, envvarnames) == env3

        assert u.use_envvars(Path(), envvarnames) == Path()


def test_startswith_envvar(tmp_path):
    """Test startswith_envvar."""
    env1 = tmp_path / "env1"
    env1.mkdir()
    env2 = tmp_path / "env2"
    with mock.patch.dict(os.environ, {"env1": str(env1), "env2": str(env2)}):
        assert u.startswith_envvar(env1) == (None, env1)

        # defined and existing env path
        assert u.startswith_envvar(Path("$env1")) == ("env1", Path())
        assert u.startswith_envvar(Path("$env1") / "sub") == ("env1", Path("sub"))
        assert u.startswith_envvar(Path("$env1") / "sub", strict=True) == ("env1", Path("sub"))
        assert u.startswith_envvar(Path("$env1") / "sub", barename=True) == ("env1", Path("sub"))

        assert u.startswith_envvar(Path("${env1}")) == ("{env1}", Path())
        assert u.startswith_envvar(Path("${env1}") / "sub") == ("{env1}", Path("sub"))
        assert u.startswith_envvar(Path("${env1}"), barename=True) == ("env1", Path())
        assert u.startswith_envvar(Path("${env1}") / "sub", barename=True) == ("env1", Path("sub"))

        # defined and not existing env path
        assert u.startswith_envvar(Path("$env2")) == ("env2", Path())
        assert u.startswith_envvar(Path("$env2") / "sub") == ("env2", Path("sub"))
        with raises(FileNotFoundError):
            u.startswith_envvar(Path("$env2") / "sub", strict=True)

        # undefined env path
        assert u.startswith_envvar(Path("$env3")) == ("env3", Path())
        assert u.startswith_envvar(Path("$env3") / "sub") == ("env3", Path("sub"))
        with raises(FileNotFoundError):
            u.startswith_envvar(Path("$env3") / "sub", strict=True)
