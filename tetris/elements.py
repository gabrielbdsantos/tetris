# coding: utf-8
"""Provide python-equivalent blockMesh elements."""

from __future__ import annotations

import copy
from typing import Collection, Union

import numpy as np
from numpy.typing import NDArray

import tetris.constants
import tetris.io
import tetris.utils
from tetris.typing import BlockMeshElement, Vector


class Vertex(BlockMeshElement):
    """Define a blockMesh vertex entry."""

    __slots__ = ["coords"]

    def __init__(self, *args: Vector) -> None:
        try:
            # Append three zeros to args, and then select the first three
            # elements of the resulting array.
            self.coords: NDArray[np.floating] = np.pad(
                np.asfarray(args).flatten(), (0, 3)
            )[:3]
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
    ) -> NDArray[np.floating]:
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

        return tetris.utils.rotate3D(
            self.coords, yaw, pitch, roll, origin, degrees
        )

    def write(self) -> str:
        """Write the coordinates in OpenFOAM style.

        Returns
        -------
        str
            A rendered representation of the current Vertex instance in
            OpenFOAM style.
        """
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


class Edge(BlockMeshElement):
    """Define a blockMesh edge entry."""

    __slots__ = ["v0", "v1", "__points", "type"]

    def __init__(
        self,
        v0: Vertex,
        v1: Vertex,
        points: NDArray[np.floating] = np.array([]),
        type: str = None,
    ) -> None:
        # Check whether the vertices are at the same location.
        if v0 == v1:
            raise ValueError(
                "Zero-length edge. Vertices are at the same point in space."
            )

        self.v0 = v0
        self.v1 = v1
        self.points = points
        self.type = type

    @property
    def points(self) -> np.ndarray:
        """Define a list of points defining the edge."""
        return self.__points

    @points.setter
    def points(self, points: np.ndarray) -> None:
        # Let us work with numpy.array insted of simple lists.
        self.__points = np.array(points, dtype="float64")

        # The points list is empty. No need to go any further.
        if self.__points.size == 0:
            self.type = None
            return

        # Well, the code reached here, we then need to check whether the
        # provided list is correct; i.e., the points list must have a shape of
        # (N, 3), where x denotes any positive integer. Summarizing, the points
        # list must be a list of three-dimensional coordinates.
        if self.__points.shape[-1] != 3 or self.__points.ndim != 2:
            raise TypeError(
                "Incorrect points list. Please see the docstrings"
                " for information on how to define the points list."
            )

        # To check the collinearity of the points, we need to add the ending
        # vertices to the list of points.
        points = np.concatenate(
            (
                np.reshape(self.v0.coords, (1, 3)),
                np.array(self.points),
                np.reshape(self.v1.coords, (1, 3)),
            )
        )

        # Let us find and delete collinear points. Here, v0, v1, and v2 are
        # three consecutive points in the points list. If they are collinear,
        # the line can be represented by v0 and v2 only, eliminating the need
        # to store v1 as well.
        to_delete = []
        for i, (v0, v1, v2) in enumerate(
            zip(points[0:-2], points[1:-1], points[2:-0])
        ):
            if tetris.utils.is_collinear(v0, v1, v2):
                to_delete.append(i + 1)

        # `axis = 0` is needed to get a two-dimensional array, maintaining
        # consistence.
        np.delete(points, to_delete, axis=0)

        # As we added both vertices to the points list for checking for
        # collinear points, we now need to exclude the first and last entries
        # in `points`.
        self.__points = points[1:-1]

        # Finally, if the points list is empty, then we have a straight line
        # between v0 and v1. Thereby, we must change the `type` of the current
        # instance to `None`.
        if self.__points.size == 0:
            self.type = None

    def length(self) -> float:
        """Compute the edge length."""
        # If the edge has a type `None` (i.e., it is a straight line, then
        # return the distance between v0 and v1.
        if self.type is None:
            return tetris.utils.distance(self.v0, self.v1)

        # If the points list is not empty, we need to add both vertices to the
        # points list for computing the edge length. So, we prepend v0 and
        # append v1.
        points = np.concatenate(
            (
                np.reshape(self.v0.coords, (1, 3)),
                np.array(self.points),
                np.reshape(self.v1.coords, (1, 3)),
            )
        )

        # And lastly we compute the distance between the various consecutive
        # points in the list. The resulting values are all added together,
        # yielding the edge length.
        return tetris.utils.distance(points[:-1], points[1:])

    def invert(self) -> Edge:
        """Invert the edge direction."""
        return Edge(self.v1, self.v0, points=self.points[::-1], type=self.type)

    def write(self) -> str:
        """Write the edge in OpenFOAM style.

        Returns
        -------
        str
            A rendered representation of the current Edge instance in OpenFOAM
            style.
        """
        if self.type != "arc":
            points = (
                [self.v0.coords.tolist()]
                + self.points.tolist()
                + [self.v1.coords.tolist()]
            )
        else:
            points = self.points[0].tolist()

        return (
            f"{self.type} {self.v0.name} {self.v1.name} "
            f"{tetris.io.tetris2foam(points)}"
        )

    # Make the class subscriptable
    def __getitem__(self, index: int) -> Vertex:
        return [self.v0, self.v1][index]


class Patch(BlockMeshElement):
    """Define a blockMesh patch entry."""

    __slots__ = ["name", "faces", "type"]

    def __init__(self, name: str, type: str, faces: list) -> None:
        self.name = name
        self.faces = faces
        self.type = type

    def write(self) -> str:
        """Write the patch in OpenFOAM style."""
        ids = [[f.id for f in face] for face in self.faces]
        return f"{self.type} {self.name} {tetris.io.tetris2foam(ids)}"

    # Make the class subscriptable
    def __getitem__(self, index: int) -> list:
        return self.faces[index]


class PatchPair(BlockMeshElement):
    """Define a blockMesh mergePatchPair entry."""

    __slots__ = ["master", "slave"]

    def __init__(self, master: Patch, slave: Patch) -> None:
        self.master = master
        self.slave = slave

    def write(self) -> str:
        """Write the patch pair in OpenFOAM style."""
        return f"{tetris.io.tetris2foam([self.master.name, self.slave.name])}"


class Block(BlockMeshElement):
    """Define a blockMesh entry for hexahedral blocks."""

    __slots__ = [
        "vertices",
        "edges",
        "faces",
        "patches",
        "__grading",
        "__grading_type",
        "__ncells",
        "cellZone",
        "description",
    ]

    def __init__(self) -> None:
        self.vertices: list[Vertex] = []
        self.edges: list[Edge] = []
        self.faces: dict[int, list[Vertex]] = {}
        self.patches: list[Patch] = []

        self.grading = [1, 1, 1]
        self.ncells = np.ones(3)
        self.cellZone: str = ""

        self.description: str = ""

    @property
    def name(self) -> str:
        """Get the block name."""
        return f"b{self.id}"

    @property
    def ncells(self) -> NDArray[np.integer]:
        """Get the number of cells on each axis."""
        return self.__ncells

    @ncells.setter
    def ncells(self, value: Vector) -> None:
        # Since `value` can be a list, tuple, or numpy.array, we must provide a
        # solution for all cases. Instead of using a series of if/else clauses,
        # it may be more interesting to convert `value` to numpy.array and then
        # reshape it into what we want.
        self.__ncells = np.asarray(value).reshape(3).astype(np.integer)

    @property
    def grading(self):
        """Get the block grading on each axis/edge."""
        return self.__grading

    @grading.setter
    def grading(self, value: list) -> None:
        # For now, value must be either a list or a tuple
        if not isinstance(value, (list, tuple)):
            raise TypeError(
                "The block grading must be expressed as either a"
                "a list or a tuple."
            )

        # If value has three elements, then we adopt the simpleGrading approach
        if len(value) == 3:
            # Copy value so grading levels may be changed freely later.
            self.__grading = copy.deepcopy(value)
            self.__grading_type = "simple"
            return

        # Otherwise, the block uses the 'edgeGrading' approach, which requires
        # a grading level for each one of the edges. Thus, the grading array
        # must be of size 12.
        if len(value) == 12:
            # We copy the value linked grading levels may be changed freely
            self.__grading = copy.deepcopy(value)
            self.__grading_type = "edge"
            return

        # If we reach here, the number of elements passed are wrong. So, let's
        # throw an error
        raise ValueError(
            "The number of elements defining the grading must be"
            "either 3 (simpleGrading) or 12 (edgeGrading)"
        )

    def set_vertices(self, vertices: Collection[Vertex]) -> None:
        """Create a block from a list of vertices."""
        # Check whether the list have eight items.
        if len(vertices) != 8:
            raise ValueError("Incorrect number of vertices. Expected 8")

        # Clear the list of vertices and assign the given one
        self.vertices = []
        for vertex in vertices:
            self.vertices.append(vertex)

        # Clear the list of edges and assign an Edge instance for each edge
        self.edges = []
        for edges_on_axis in tetris.constants.EDGES_ON_AXIS:
            for v0, v1 in edges_on_axis:
                self.edges.append(Edge(self.vertices[v0], self.vertices[v1]))

    def set_edge(
        self, v0: Vertex, v1: Vertex, points: np.ndarray, type: str = "spline"
    ) -> None:
        """Define a new edge."""
        # Check whether there is already an edge defined for the given
        # vertices.
        for i, edge in enumerate(self.edges):
            if {edge.v0, edge.v1} == {v0, v1}:
                self.edges[i] = Edge(v0, v1, points, type)
                break
        else:
            self.edges.append(Edge(v0, v1, points, type))

    def get_face(self, face: str) -> tuple[Vertex, ...]:
        """List the vertices ids for the given face label.

        Parameters
        ----------
        face : str
            The face label: right, left, top, bottom, front, or back.

        Returns
        -------
        tuple
            A tuple of vertex ids that describe the given face label. The
            list is ordered to yield an outward-pointing face.
        """
        return tuple(
            [self.vertices[id] for id in tetris.constants.FACE_MAPPING[face]]
        )

    def get_edge_by_vertex(
        self, v0: Union[Vertex, int], v1: Union[Vertex, int]
    ) -> Edge:
        """Get the Edge defined by the local vertices v0 and v1.

        Parameters
        ----------
        v0 : int, Vertex
            The local Vertex id or instance.
        v1 : int, Vertex
            The local Vertex id or instance.

        Returns
        -------
        Edge
            The edge defined by the two vertices.
        """
        if not isinstance(v0, Vertex):
            v0 = self.vertices[v0]

        if not isinstance(v1, Vertex):
            v1 = self.vertices[v1]

        edge = [e for e in self.edges if {e.v0, e.v1} == {v0, v1}][0]
        return edge if edge.v0 == v0 else edge.invert()

    def write(self) -> str:
        """Write the block in OpenFOAM style.

        Returns
        -------
        str
            OpenFOAM entry for hex blocks.
        """
        return (
            f"name {self.name} "
            f"hex ({' '.join([str(v.name) for v in self.vertices])})"
            f"{' ' + self.cellZone if self.cellZone else ''}"
            f" {tetris.io.tetris2foam(self.ncells.tolist())}"
            f" {self.__grading_type}Grading"
            f" {tetris.io.tetris2foam(self.grading)}"
            f"{tetris.io.comment(self.description)}"
        )

    # Make the class subscriptable
    def __getitem__(self, index: int) -> Vertex:
        return self.vertices[index]
