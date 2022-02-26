# coding: utf-8
"""Define type hints for being used accross the module."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Tuple, Type, Union

from numpy import floating
from numpy.typing import NDArray

Vector = Union[List[floating], Tuple[floating], NDArray[floating]]


class BlockMeshElement(ABC):
    """Base class for blockMesh elements."""

    @classmethod
    def __init_subclass__(cls: Type[BlockMeshElement]) -> None:
        """Initiate the subclass with a generic id."""
        cls.id: int = -1

    @abstractmethod
    def write(self) -> str:
        """Output the current element in OpenFOAM style."""
        ...
