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

"""
Configurable Module.
"""

from .config import BaseConfig
from .modbase import BaseMod
from .modbasetop import BaseTopMod
from .modutil import get_topmodname
from .nameutil import join_names


class AConfigurableMod(BaseTopMod):
    """
    A Module Which Is Assembled According To A Receipe ([AConfig][ucdp.config.AConfig]).

    See : for arguments, attributes and details.

    Additionally the config has to be provided at instantiation.
    A [AConfigurableMod][ucdp.modconfigurable.AConfigurableMod] may define a `default_config`
    which is taken if no `config` is provided at instantiaion.

    All module parameter, local parameter, ports, signals and submodules
    **MUST** be added and created within the `_build` method depending on the config.


    .. attention:: It is forbidden to implement `add` methods or any other *tailored* functionality.
                   Use a tailored module instead!

    Configurable modules are located next to the python file and use the configuration name in the module name.

    Attributes:
        config:

    ??? Example "AConfigurableMod Example"
            Basics:

            >>> import ucdp as u
            >>> class MyConfig(u.AConfig):
            ...
            ...     feature: bool = False

            >>> class ProcMod(u.AConfigurableMod):
            ...
            ...     config: MyConfig = MyConfig('default')
            ...
            ...     def _build(self) -> None:
            ...         if self.config.feature:
            ...             self.add_port(u.UintType(8), "feature_i")
            ...             self.add_port(u.UintType(8), "feature_o")
            ...         else:
            ...             self.add_port(u.UintType(8), "default_o")

            >>> my = ProcMod()
            >>> my.modname
            'proc_default'
            >>> my.ports
            Idents([Port(UintType(8), 'default_o', direction=OUT)])

            >>> my = ProcMod(config=MyConfig('other', feature=True))
            >>> my.modname
            'proc_other'
            >>> my.ports
            Idents([Port(UintType(8), 'feature_i', direction=IN), Port(UintType(8), 'feature_o', direction=OUT)])
    """

    config: BaseConfig

    def __init__(self, parent: BaseMod | None = None, name: str | None = None, **kwargs):
        if "config" not in kwargs and parent is not None:
            raise ValueError("'config' is required if 'parent' is given")
        super().__init__(parent=parent, name=name, **kwargs)  # type: ignore[call-arg]

    @property
    def modname(self) -> str:
        """Module Name."""
        config = self.config
        name = config.name
        if not name and "config" in self.model_fields_set and not config.is_default:
            name = config.hash
        return join_names(self.basename, name)

    @property
    def topmodname(self) -> str:
        """Top Module Name."""
        return get_topmodname(self.__class__)
