#
# MIT License
#
# Copyright (c) 2024 nbiotcloud
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

from .consts import PAT_IDENTIFIER
from .object import Field, LightObject


class AConfig(LightObject):
    """
    Configuration Container.

    Args:
        name: Configuration name, used as suffix of the generated module.

    A configuration is nothing more than a receipe how to assemble a module:

    * if a specific option should be built-in or not
    * how many instances or which instances should be created

    A configuration **MUST** have at least a name.

    Due to the frozen instance approach, configurations have to be implemented
    via `u.field()`.

    Example:
        >>> import ucdp as u
        >>> class MyConfig(u.AConfig):
        ...
        ...     mem_baseaddr: u.Hex # required without default
        ...     ram_size: u.Bytes
        ...     rom_size: u.Bytes|None = None
        ...     feature: bool = False

        >>> variant0  = MyConfig(name='variant0', mem_baseaddr=4*1024, ram_size='16kB')
        >>> variant0
        MyConfig('variant0', mem_baseaddr=Hex('0x1000'), ram_size=Bytes('16 KB'))
        >>> variant0.mem_baseaddr
        Hex('0x1000')
        >>> variant0.ram_size
        Bytes('16 KB')
        >>> variant0.rom_size
        >>> variant0.feature
        False

        >>> for name, value in variant0:
        ...     name, value
        ('name', 'variant0')
        ('mem_baseaddr', Hex('0x1000'))
        ('ram_size', Bytes('16 KB'))
        ('rom_size', None)
        ('feature', False)

        >>> variant1  = MyConfig('variant1', mem_baseaddr=8*1024, rom_size="2KB", ram_size="4KB", feature=True)
        >>> variant1
        MyConfig('variant1', mem_baseaddr=Hex('0x2000'), ram_size=Bytes('4 KB'), rom_size=Bytes('2 KB'), feature=True)
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
    MyConfig('variant2', mem_baseaddr=Hex('0x2000'), ram_size=Bytes('4 KB'), rom_size=Bytes('8 KB'), feature=True)
    >>> variant2.mem_baseaddr
    Hex('0x2000')
    >>> variant2.ram_size
    Bytes('4 KB')
    >>> variant2.rom_size
    Bytes('8 KB')
    >>> variant2.feature
    True
    """

    name: str = Field(pattern=PAT_IDENTIFIER)

    _posargs: tuple[str, ...] = ("name",)

    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)


class AUniqueConfig(LightObject):
    """
    A Unique Configuration.

    The configuration name is automatically derived from the attribute values.

    >>> import ucdp as u
    >>> import datetime
    >>> from typing import Tuple
    >>> class MyUniqueConfig(u.AUniqueConfig):
    ...     mem_baseaddr: u.Hex
    ...     width: int = 32
    ...     feature: bool = False
    ...     coeffs: tuple[int, ...] = tuple()

    >>> config = MyUniqueConfig(
    ...     mem_baseaddr=0x12340000,
    ... )
    >>> config.name
    '5e813dde214238ae'

    >>> for name, value in config:
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
    '9818217751e9d3b4'
    """

    @property
    def name(self) -> str:
        """Assembled name from configuration values."""
        return hashlib.sha256(str(self.model_dump()).encode("utf-8")).hexdigest()[:16]


BaseConfig = AConfig | AUniqueConfig


class AVersionConfig(AConfig):
    """
    Version Configuration Container.

    >>> import ucdp as u
    >>> import datetime
    >>> class MyVersionConfig(u.AVersionConfig):
    ...     mem_baseaddr: u.Hex

    >>> version = MyVersionConfig(
    ...     'my',
    ...     title="Title",
    ...     version="1.2.3",
    ...     timestamp=datetime.datetime(2020, 10, 17, 23, 42),
    ...     mem_baseaddr=0x12340000
    ... )
    >>> version.name
    'my'
    >>> version.title
    'Title'
    >>> version.timestamp
    datetime.datetime(2020, 10, 17, 23, 42)
    >>> version.mem_baseaddr
    Hex('0x12340000')

    >>> for name, value in version:
    ...     name, value
    ('name', 'my')
    ('title', 'Title')
    ('version', '1.2.3')
    ('timestamp', datetime.datetime(2020, 10, 17, 23, 42))
    ('mem_baseaddr', Hex('0x12340000'))
    """

    title: str
    version: str
    timestamp: datetime.datetime
