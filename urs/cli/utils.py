"""
CLI Validation Utilities
========================
Contains utilities for Pydantic CLI argument validation.
"""

from enum import Enum
from typing import Any, Dict, List, Type


class DebuggableEnum(Enum):
    """
    This class contains helper methods for Python `Enum`s to make it easier to
    view or access Enum key, value pairs.
    """

    @classmethod
    def list(cls: Type["DebuggableEnum"]) -> List[Any]:
        """
        Returns a `List[Any]` of all variant values.

        :param Type[DebuggableEnum] cls: A class that inherits `DebuggableEnum`.

        :returns: A `List[Any]` of all `Enum` variants.
        :rtype: `List[Any]`
        """

        return list(map(lambda variant: variant.value, cls))

    @classmethod
    def dict(cls: Type["DebuggableEnum"]) -> Dict[str, Any]:
        """
        Returns a `Dict[str, Any]` of all variant key, value pairs.

        :param Type[DebuggableEnum] cls: A class that inherits `DebuggableEnum`.

        :returns: A `Dict[str, Any]` of all `Enum` key, value pairs.
        """

        return {variant.name: variant.value for variant in cls}
