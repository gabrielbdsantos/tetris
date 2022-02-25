# coding: utf-8
"""Define type hints for being used accross the module."""

from __future__ import annotations

from abc import ABC, abstractmethod, abstractproperty
from typing import TYPE_CHECKING, List, Tuple, Type, Union

import numpy as np
from numpy.typing import NDArray

if TYPE_CHECKING:
    from tetris.elements import Vertex

Vector = Union[List[np.floating], Tuple[np.floating], NDArray[np.floating]]


class BlockMeshElement(ABC):
    """Base class for blockMesh elements."""

    @classmethod
    def __init_subclass__(cls: Type[BlockMeshElement]) -> None:
        cls.id: int = -1

    @abstractmethod
    def write(self) -> str:
        """Output the current element in OpenFOAM style."""
        ...


class Edge(BlockMeshElement):
    """Base class for edge objects."""

    def __init__(self, v0: Vertex, v1: Vertex) -> None:
        # Check whether the vertices are at the same location.
        if v0 == v1:
            raise ValueError(
                "Zero-length edge. Vertices are at the same point in space."
            )

        self.v0 = v0
        self.v1 = v1

    @abstractproperty
    def type(self) -> str:
        """The edge type."""
        ...

    @abstractmethod
    def invert(self) -> Edge:
        """Invert the edge direction."""
        ...

    def __getitem__(self, index: int) -> Vertex:
        return [self.v0, self.v1][index]
