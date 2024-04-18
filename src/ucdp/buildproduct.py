"""Build."""

from abc import abstractmethod
from typing import Any

from .object import Object


class ABuildProduct(Object):
    """Product Mixin which builts itself via `_build`."""

    @abstractmethod
    def _build(self) -> None:
        """Build."""

    def model_post_init(self, __context: Any) -> None:
        """Run Build."""
        self._build()
