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
"""Configuration."""
import datetime
import hashlib
from pathlib import Path

from humannum import Hex, hex_

from ..attrs import asdict, define, evolve, field
from ..nameutil import validate_identifier
from ..util import opt


def config(maybe_cls=None, **kwargs):
    """Configuration Decorator - see :any:`BaseConfig`."""
    return define(maybe_cls, frozen=True, repr=False, **kwargs)


@config
class BaseConfig:
    """Base Class for all Configurations."""

    name: str = ""

    def __repr__(self):
        return f"{self.__class__.__qualname__}({self.name!r})"

    def new(self, **kwargs) -> "BaseConfig":
        """Return A Copy With Updated Attributes."""
        return evolve(self, **kwargs)

    def iter_overview(self):
        """Iterate Overview."""
        yield from asdict(self, recurse=False).items()


@config
class AConfig(BaseConfig):
    """
    Configuration Container.

    Args:
        name (str): Configuration name, used as suffix of the generated module.

    A configuration is nothing more than a receipe how to assemble a module:

    * if a specific option should be built-in or not
    * how many instances or which instances should be created

    A configuration **MUST** have at least a name.

    Due to the frozen instance approach, configurations have to be implemented
    via `ucdp.field()`.

    Example:

    >>> import ucdp
    >>> from humannum import bytes_, hex_
    >>> @ucdp.config
    ... class MyConfig(ucdp.AConfig):
    ...
    ...     mem_baseaddr = ucdp.field(converter=hex_) # required without default
    ...     ram_size = ucdp.field(converter=bytes_, default="256 KB")  # required with default
    ...     rom_size = ucdp.field(converter=opt(bytes_), default=None)  # optional
    ...     feature: bool = ucdp.field(default=False) # boolean

    >>> variant0  = MyConfig('variant0', 4*1024)
    >>> variant0
    MyConfig('variant0')
    >>> variant0.mem_baseaddr
    Hex('0x1000')
    >>> variant0.ram_size
    Bytes('256 KB')
    >>> variant0.rom_size
    >>> variant0.feature
    False

    >>> for name, value in variant0.iter_overview():
    ...     name, value
    ('name', 'variant0')
    ('mem_baseaddr', Hex('0x1000'))
    ('ram_size', Bytes('256 KB'))
    ('rom_size', None)
    ('feature', False)

    >>> variant1  = MyConfig('variant1', 8*1024, rom_size="2KB", ram_size="4KB", feature=True)
    >>> variant1
    MyConfig('variant1')
    >>> variant1.mem_baseaddr
    Hex('0x2000')
    >>> variant1.ram_size
    Bytes('4 KB')
    >>> variant1.rom_size
    Bytes('2 KB')
    >>> variant1.feature
    True

    To create another variant based on an existing:

    >>> variant2 = variant1.new(name='variant2', rom_size='8KB')
    >>> variant2
    MyConfig('variant2')
    >>> variant2.mem_baseaddr
    Hex('0x2000')
    >>> variant2.ram_size
    Bytes('4 KB')
    >>> variant2.rom_size
    Bytes('8 KB')
    >>> variant2.feature
    True
    """

    name: str = field()

    @name.validator  # type: ignore
    def _name_validator(self, attribute, value):
        # pylint: disable=unused-argument
        validate_identifier(value)


@config
class AUniqueConfig(BaseConfig):

    """
    A Unique Configuration.

    The configuration name is automatically derived from the attribute values.

    >>> import ucdp
    >>> import datetime
    >>> from typing import Tuple
    >>> @ucdp.config
    ... class MyUniqueConfig(ucdp.AUniqueConfig):
    ...     mem_baseaddr: int = ucdp.field(converter=hex_)
    ...     width: int = ucdp.field(default=32)
    ...     feature: bool = ucdp.field(default=False)
    ...     coeffs: Tuple[int, ...] = ucdp.field(factory=tuple)

    >>> config = MyUniqueConfig(
    ...     mem_baseaddr=0x12340000,
    ... )
    >>> config.name
    'aa440a0fab478a72'

    >>> for name, value in config.iter_overview():
    ...     name, value
    ('mem_baseaddr', Hex('0x12340000'))
    ('width', 32)
    ('feature', False)
    ('coeffs', ())

    >>> config = MyUniqueConfig(
    ...     mem_baseaddr=0x12340000,
    ...     coeffs=(1,2,3),
    ... )
    >>> config.name
    '087561fbb5f4aaac'
    """

    @property
    def name(self):
        """Assembled name from configuration values."""
        parts = []
        for value in asdict(self, recurse=False).values():
            if isinstance(value, bool):
                value = int(value)
            parts.append(str(value).replace(" ", ""))
        return hashlib.sha256("_".join(parts).encode("utf-8")).hexdigest()[:16]


@config
class AVersionConfig(AConfig):

    """
    Version Configuration Container.

    >>> import ucdp
    >>> import datetime
    >>> @ucdp.config
    ... class MyVersionConfig(ucdp.AVersionConfig):
    ...     mem_baseaddr = ucdp.field(converter=hex_) # required without default

    >>> version = MyVersionConfig(
    ...     'my',
    ...     title="Title",
    ...     version="1.2.3",
    ...     timestamp=datetime.datetime(2020, 10, 17, 23, 42),
    ...     rand=0x65DDB0631,
    ...     file=__file__,
    ...     mem_baseaddr=0x12340000
    ... )
    >>> version.name
    'my'
    >>> version.title
    'Title'
    >>> version.timestamp
    datetime.datetime(2020, 10, 17, 23, 42)
    >>> version.rand
    Hex('0x65DDB0631')
    >>> version.mem_baseaddr
    Hex('0x12340000')

    >>> for name, value in version.iter_overview():
    ...     name, value
    ('name', 'my')
    ('title', 'Title')
    ('version', '1.2.3')
    ('timestamp', datetime.datetime(2020, 10, 17, 23, 42))
    ('mem_baseaddr', Hex('0x12340000'))
    """

    title: str = field(kw_only=True)
    version: str = field(kw_only=True)
    timestamp: datetime.datetime = field(kw_only=True)
    rand: Hex = field(kw_only=True, converter=opt(hex_))
    file: Path = field(kw_only=True)

    def iter_overview(self):
        """Iterate Overview."""
        for name, value in asdict(self, recurse=False).items():
            if name in ("rand", "file"):
                continue
            yield name, value
