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
"""Configuration."""

import datetime
import hashlib
from typing import ClassVar

from .consts import PAT_OPT_IDENTIFIER
from .object import Field, LightObject, PosArgs


class AConfig(LightObject):
    """
    Configuration Container.

    Args:
        name: Configuration name, used as suffix of the generated module.

    A configuration is nothing more than a recipe how to assemble a module:

    * if a specific option should be built-in or not
    * how many instances or which instances should be created

    A configuration **MUST** have at least a name.

    Due to the frozen instance approach, configurations have to be implemented
    via `u.field()`.

    ??? Example "AConfig Examples"
        Create a Config.

            >>> import ucdp as u
            >>> class MyConfig(u.AConfig):
            ...
            ...     base_addr: u.Hex # required without default
            ...     ram_size: u.Bytesize
            ...     rom_size: u.Bytesize|None = None
            ...     feature: bool = False

        To create 1st variant

            >>> variant0  = MyConfig(name='variant0', base_addr=4*1024, ram_size='16kB')
            >>> variant0
            MyConfig('variant0', base_addr=Hex('0x1000'), ram_size=Bytesize('16 KB'))
            >>> variant0.base_addr
            Hex('0x1000')
            >>> variant0.ram_size
            Bytesize('16 KB')
            >>> variant0.rom_size
            >>> variant0.feature
            False
            >>> variant0.hash
            'd0cf21ab30478424'

        To create 2nd variant

            >>> for name, value in variant0:
            ...     name, value
            ('name', 'variant0')
            ('modname', '')
            ('base_addr', Hex('0x1000'))
            ('ram_size', Bytesize('16 KB'))
            ('rom_size', None)
            ('feature', False)

            >>> variant1  = MyConfig('variant1', base_addr=8*1024, rom_size="2KB", ram_size="4KB", feature=True)
            >>> variant1
            MyConfig('variant1', base_addr=Hex('0x2000'), ram_size=Bytesize('4 KB'), rom_size=Bytesize('2 KB'), ...)
            >>> variant1.base_addr
            Hex('0x2000')
            >>> variant1.ram_size
            Bytesize('4 KB')
            >>> variant1.rom_size
            Bytesize('2 KB')
            >>> variant1.feature
            True
            >>> variant1.hash
            'eb8052ba0b38cc3f'

        To create another variant based on an existing:

            >>> variant2 = variant1.new(name='variant2', rom_size='8KB')
            >>> variant2
            MyConfig('variant2', base_addr=Hex('0x2000'), ram_size=Bytesize('4 KB'), rom_size=Bytesize('8 KB'), ...)
            >>> variant2.base_addr
            Hex('0x2000')
            >>> variant2.ram_size
            Bytesize('4 KB')
            >>> variant2.rom_size
            Bytesize('8 KB')
            >>> variant2.feature
            True
            >>> variant2.hash
            'd8704dd8163a5ecc'

    ???+ bug "Todo"
        * fix name type
    """

    name: str = Field(pattern=PAT_OPT_IDENTIFIER, default="")
    """Configuration Name."""

    modname: str = Field(pattern=PAT_OPT_IDENTIFIER, default="")
    """Enforced Module Name."""

    _posargs: ClassVar[PosArgs] = ("name",)
    _hash_excludes: ClassVar[set[str]] = set()

    def __init__(self, name: str = "", **kwargs):
        super().__init__(name=name, **kwargs)  # type: ignore[call-arg]

    @property
    def is_default(self) -> bool:
        """Return `true` if configuration just contains default values."""
        exclude = self.__class__._hash_excludes
        return not self.model_dump(exclude_unset=True, exclude_defaults=True, exclude=exclude)

    @property
    def hash(self) -> str:
        """Unique Configuration Hash."""
        exclude = self.__class__._hash_excludes
        hashdata = self.model_dump(exclude=exclude)
        for key, value in self.__dict__.items():
            if key not in hashdata:
                continue
            if isinstance(value, AConfig):
                hashdata[key] = value.hash
            if isinstance(value, tuple):
                items = list(value)
                for idx, item in enumerate(items):
                    if isinstance(item, AConfig):
                        items[idx] = item.hash
                hashdata[key] = tuple(items)
        return hashlib.sha256(str(hashdata).encode("utf-8")).hexdigest()[:16]

    @property
    def unique_name(self) -> str:
        """Unique Configuration Hash."""
        return self.hash


BaseConfig = AConfig
"""BaseConfig"""


class AVersionConfig(AConfig):
    """
    Version Configuration Container.

    Attributes:
        title: Title.
        version: Version
        timestamp: Timestamp

    ??? Example "AVersionConfig Examples"
        Create a Config.

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
            >>> version.hash
            'e98d9954882a5081'

            >>> for name, value in version:
            ...     name, value
            ('name', 'my')
            ('modname', '')
            ('title', 'Title')
            ('version', '1.2.3')
            ('timestamp', datetime.datetime(2020, 10, 17, 23, 42))
            ('mem_baseaddr', Hex('0x12340000'))

        Title, version and timestamp do not affect the hash

        >>> title = "Title"
        >>> version = "Version"
        >>> timestamp0 = datetime.datetime(2020, 10, 17, 23, 42)
        >>> timestamp1 = datetime.datetime(2020, 10, 17, 23, 43)
        >>> MyVersionConfig(mem_baseaddr=0x12340000, title=title, version=version, timestamp=timestamp0).hash
        '5b23b35be0ab5615'
        >>> MyVersionConfig(mem_baseaddr=0x12340000, title=title, version=version, timestamp=timestamp1).hash
        '5b23b35be0ab5615'

    """

    _hash_excludes: ClassVar[set[str]] = {"title", "version", "timestamp"}

    title: str
    version: str
    timestamp: datetime.datetime
