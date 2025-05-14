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

"""Constants."""

import re
import sys
from pathlib import Path
from typing import Literal

AUTO: str = "auto"
"""AUTO."""

PAT_IDENTIFIER: str = r"^[a-zA-Z]([a-zA-Z_0-9]*[a-zA-Z0-9])?$"
"""Pattern for Identifier."""

RE_IDENTIFIER = re.compile(PAT_IDENTIFIER)
"""Regular Expression for Identifier."""

PAT_OPT_IDENTIFIER: str = r"^([a-zA-Z]([a-zA-Z_0-9]*[a-zA-Z0-9])?)?$"
"""Pattern for Optional Identifier."""

PAT_IDENTIFIER_LOWER: str = r"^[a-z]([a-z_0-9]*[a-z0-9])?$"
"""Pattern for Identifier."""

UPWARDS: str = ".."
"""UPWARDS."""

Gen = Literal["no", "inplace", "full", "custom"]
"""Gen."""

PATH = Path(__file__).parent

PKG_PATHS = {sys.prefix, sys.base_prefix}
