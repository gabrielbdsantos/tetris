# coding: utf-8
"""Provide interfaces for manipulating vertices."""

from __future__ import annotations

from typing import Union

import numpy as np

import tetris.io
import tetris.utils
from tetris.blockmesh.geometry import Geometry
from tetris.typing import BlockMeshElement, Vector


class Vertex(BlockMeshElement):
    """Define a blockMesh vertex entry."""

    def __init__(self, *args: Vector) -> None:
        try:
            # Append three zeros to args, and then select the first three
            # elements of the resulting array.
            self.coords = np.pad(np.asfarray(args).flatten(), (0, 3))[:3]
        except (TypeError, ValueError):
            raise ValueError(
                "Invalid arguments. Please, see the docstrings "
                "for details on how to declare the coordinates."
            )

    @property
    def name(self) -> str:
        """Get the vertex name."""
        return f"v{self.id}"

    def move(self, vector: Union[Vector, int, float]) -> None:
        """Move the vertex.

        Parameters
        ----------
        vector: int, float, vector
            The translation vector.
        """
        self.coords += tetris.utils.to_array(vector)

    def rotate(
        self,
        yaw: float = 0,
        pitch: float = 0,
        roll: float = 0,
        origin: Union[Vertex, Vector] = np.zeros(3),
        degrees: bool = True,
    ) -> Vertex:
        """Rotate the vertex around a reference point.

        Parameters
        ----------
        yaw: float
            Rotation angle about the z axis.
        pitch: float
            Rotation angle about the y axis.
        roll: float
            Rotation angle about the x axis.
        origin: np.ndarray
            The point about which rotation is done.
        degrees: bool
            Interpret angles as in degrees rather than radians.

        Return
        ------
        Vertex
            A new vertex instance.
        """
        origin = np.asarray(
            origin.coords if isinstance(origin, Vertex) else origin
        )

        return Vertex(
            tetris.utils.rotate3D(
                self.coords, yaw, pitch, roll, origin, degrees
            )
        )

    def write(self) -> str:
        """Write the coordinates in OpenFOAM style."""
        v = self.coords

        return f"name {self.name} ({v[0]:.6f} {v[1]:.6f} {v[2]:.6f})"

    # Make the class subscriptable.
    def __getitem__(self, index: int) -> float:
        return self.coords[index]

    # Let's overload some operators so we can use the Vertex class in a more
    # pythonic way.
    def __neg__(self) -> Vertex:
        return Vertex(-self.coords)

    def __eq__(self, other: Union[Vertex, Vector]) -> bool:
        return all(self.coords == tetris.utils.to_array(other))

    def __ne__(self, other: Union[Vertex, Vector]) -> bool:
        return not self.__eq__(other)

    # For the next methods (add, sub, mul, and truediv), we adopt a little
    # trick. Instead of using a cascade of if-else statements to check the
    # argument type, we take advantage of numpy arrays. It is easier on the
    # eyes to convert to a numpy array and then perform the desired operation.
    def __add__(self, other: Union[Vertex, Vector, int, float]) -> Vertex:
        return Vertex(self.coords + tetris.utils.to_array(other))

    def __sub__(self, other: Union[Vertex, Vector, int, float]) -> Vertex:
        return Vertex(self.coords - tetris.utils.to_array(other))

    def __mul__(self, other: Union[Vertex, Vector, int, float]) -> Vertex:
        return Vertex(self.coords * tetris.utils.to_array(other))

    def __truediv__(self, other: Union[Vertex, Vector, int, float]) -> Vertex:
        return Vertex(self.coords / tetris.utils.to_array(other))

    # Use the already overloaded operators for both the reflected operators and
    # augmented arithmetic assignments.
    __radd__ = __iadd__ = __add__
    __rsub__ = __isub__ = __sub__
    __rmul__ = __imul__ = __mul__
    __rtruediv__ = __itruediv__ = __truediv__

    # Overloading the __eq__ operator leads to a TypeError when trying to hash
    # instances of the Vertex class. Hence, to retain the implementation of
    # __hash__ from the parent class, the intepreter must be told to do so
    # explicitly by setting __hash__ as following
    __hash__ = BlockMeshElement.__hash__  # type: ignore


class ProjectVertex(Vertex):
    """Define a projected vertex onto a surface."""

    def __init__(self, coords: Vector, geometries: list[Geometry]) -> None:
        super().__init__(coords)
        self.geometries = geometries

    def write(self) -> str:
        v = self.coords

        return (
            f"name {self.name} project ({v[0]:.6f} {v[1]:.6f} {v[2]:.6f})"
            f" {tetris.io.tetris2foam([x.name for x in self.geometries])}"
        )
