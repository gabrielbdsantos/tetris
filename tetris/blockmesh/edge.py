# coding: utf-8
"""Provide interfaces for dealing with blockMesh edges."""

from __future__ import annotations

from abc import abstractmethod, abstractproperty
from typing import Sequence

import numpy as np

import tetris.io
from tetris.blockmesh.geometry import Geometry
from tetris.blockmesh.vertex import Vertex
from tetris.typing import BlockMeshElement, NDArray


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


class LineEdge(Edge):
    """Define a simple straight edge."""

    def __init__(self, v0: Vertex, v1: Vertex) -> None:
        super().__init__(v0, v1)

    @property
    def type(self) -> str:
        return "line"

    def invert(self) -> LineEdge:
        return LineEdge(self.v1, self.v0)

    def write(self) -> str:
        return f"{self.type} {self.v0.name} {self.v1.name}"


class ArcEdge(Edge):
    """Base class for arc edges."""

    @property
    def type(self) -> str:
        return "arc"


class ArcMidEdge(ArcEdge):
    """Define an arc edge based on a mid point."""

    def __init__(
        self,
        v0: Vertex,
        v1: Vertex,
        point: NDArray[np.floating],
    ) -> None:
        super().__init__(v0, v1)
        self.point = point

    def invert(self) -> ArcMidEdge:
        return ArcMidEdge(self.v1, self.v0, self.point)

    def write(self) -> str:
        return (
            f"{self.type} {self.v0.name} {self.v1.name} "
            f"{tetris.io.tetris2foam(self.point)}"
        )


class ArcOriginEdge(ArcEdge):
    """Define an arc edge based on the circle origin."""

    def __init__(
        self,
        v0: Vertex,
        v1: Vertex,
        origin: NDArray[np.floating],
        factor: float = 1.0,
    ) -> None:
        super().__init__(v0, v1)
        self.origin = origin
        self.factor = factor

    def invert(self) -> ArcOriginEdge:
        return ArcOriginEdge(self.v1, self.v0, self.origin, self.factor)

    def write(self) -> str:
        return (
            f"{self.type} {self.v0.name} {self.v1.name} origin {self.factor} "
            f"{tetris.io.tetris2foam(self.origin)}"
        )


class SequenceEdge(Edge):
    """Base class for edges defined by a sequence of points."""

    def __init__(
        self, v0: Vertex, v1: Vertex, points: Sequence[NDArray[np.floating]]
    ) -> None:
        super().__init__(v0, v1)
        self.points = points

    def invert(self) -> SequenceEdge:
        return self.__class__(self.v1, self.v0, self.points[::-1])

    def write(self) -> str:
        return (
            f"{self.type} {self.v0.name} {self.v1.name} "
            f"{tetris.io.tetris2foam(self.points)}"
        )


class SplineEdge(SequenceEdge):
    """Define a spline edge."""

    @property
    def type(self) -> str:
        return "spline"


class BSplineEdge(SequenceEdge):
    """Define a B-spline edge."""

    @property
    def type(self) -> str:
        return "BSpline"


class PolyLineEdge(SequenceEdge):
    """Define a poly line edge."""

    @property
    def type(self) -> str:
        return "polyLine"


class ProjectEdge(Edge):
    """Define a projected (body-fitted) edge."""

    def __init__(
        self, v0: Vertex, v1: Vertex, surfaces: Sequence[Geometry]
    ) -> None:
        super().__init__(v0, v1)
        self.surfaces = surfaces

    @property
    def type(self) -> str:
        return "project"

    def invert(self) -> ProjectEdge:
        return ProjectEdge(self.v1, self.v0, self.surfaces)

    def write(self) -> str:
        return (
            f"{self.type} {self.v0.name} {self.v1.name} "
            f"{tetris.io.tetris2foam([surf.name for surf in self.surfaces])}"
        )
