# coding: utf-8
"""Define type hints for being used accross the module."""

from abc import ABC, abstractmethod
from typing import List, Tuple, Union

from numpy import floating
from numpy.typing import NDArray

Vector = Union[List[floating], Tuple[floating], NDArray[floating]]


class BlockMeshElement(ABC):
    """Base class for blockMesh elements."""

    @abstractmethod
    def write(self) -> str:
        """Output the current element in OpenFOAM style."""
        ...
