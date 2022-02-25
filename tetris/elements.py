# coding: utf-8
"""Provide python-equivalent blockMesh elements."""

from __future__ import annotations

import copy
from typing import Collection, Sequence, Union

import numpy as np
from numpy.typing import NDArray

import tetris.constants
import tetris.io
import tetris.utils
from tetris.typing import BlockMeshElement, GenericEdge, Vector


class Vertex(BlockMeshElement):
    """Define a blockMesh vertex entry."""

    __slots__ = ["coords"]

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


class LineEdge(GenericEdge):
    """Define a simple straight edge."""

    type = "line"

    def __init__(self, v0: Vertex, v1: Vertex) -> None:
        super().__init__(v0, v1)

    def invert(self) -> LineEdge:
        return LineEdge(self.v1, self.v0)

    def write(self) -> str:
        return f"{self.type} {self.v0.name} {self.v1.name}"


class ArcEdge(GenericEdge):
    type = "arc"


class ArcMidEdge(ArcEdge):

    __slots__ = ["point"]

    def __init__(
        self,
        v0: Vertex,
        v1: Vertex,
        point: NDArray[np.floating],
    ) -> None:
        super().__init__(v0, v1)
        self.point = point

    def write(self) -> str:
        return (
            f"{self.type} {self.v0.name} {self.v1.name} "
            f"{tetris.io.tetris2foam(self.point)}"
        )


class ArcOriginEdge(ArcEdge):

    __slots__ = ["factor"]

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

    def write(self) -> str:
        return (
            f"{self.type} {self.v0.name} {self.v1.name} origin {self.factor} "
            f"{tetris.io.tetris2foam(self.origin)}"
        )


class SequenceEdge(GenericEdge):

    __slots__ = ["points"]

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
    type = "spline"


class PolyLineEdge(SequenceEdge):
    type = "polyLine"


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


class DefaultPatch(BlockMeshElement):
    """Define a blockMesh defaultPatch entry."""

    __slots__ = ["name", "type"]

    def __init__(self, name: str, type: str) -> None:
        self.name = name
        self.type = type

    def write(self) -> str:
        """Write the patch in OpenFOAM style."""
        return f"defaultPatch {{ name {self.name}}}; type {self.type} }}"


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
        "ncells",
        "cellZone",
        "description",
    ]

    def __init__(self) -> None:
        self.vertices: list[Vertex] = []
        self.edges: list[GenericEdge] = []
        self.patches: list[Patch] = []

        self.grading = [1, 1, 1]
        self.ncells = [1, 1, 1]
        self.cellZone: str = ""

        self.description: str = ""

    @property
    def name(self) -> str:
        """Get the block name."""
        return f"b{self.id}"

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
        # Check whether the list have eight vertices.
        if len(vertices) != 8:
            raise ValueError("Incorrect number of vertices. Expected 8")

        # Set the list of vertices.
        self.vertices = [vertex for vertex in vertices]

        # Set the edges as straight lines.
        self.edges = [
            LineEdge(self.vertices[v0], self.vertices[v1])
            for v0, v1 in tetris.constants.BLOCK_EDGES
        ]

    def set_edge(self, edge: GenericEdge) -> None:
        """Define a new edge."""
        self.edges[
            tetris.constants.BLOCK_EDGES.index(tuple({edge.v0, edge.v1}))
        ] = edge

    def face(self, label: str) -> tuple[Vertex, ...]:
        """List the vertices ids for the given face label.

        Parameters
        ----------
        label : str
            The face label: right, left, top, bottom, front, or back.

        Returns
        -------
        tuple
            A tuple of vertex ids that describe the given face label. The
            list is ordered to yield an outward-pointing face.
        """
        return tuple(
            [self.vertices[id] for id in tetris.constants.FACE_MAPPING[label]]
        )

    def get_edge_by_vertex(self, v0: Vertex, v1: Vertex) -> GenericEdge:
        """Get the Edge defined by the local vertices v0 and v1.

        Parameters
        ----------
        v0 : Vertex
            The local vertex instance.
        v1 : Vertex
            The local vertex instance.

        Returns
        -------
        GenericEdge
            The edge defined by the two vertices.
        """
        id0 = self.vertices.index(v0)
        id1 = self.vertices.index(v1)

        edge = self.edges[
            tetris.constants.BLOCK_EDGES.index(tuple({id0, id1}))
        ]
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
            f" {tetris.io.tetris2foam(self.ncells)}"
            f" {self.__grading_type}Grading"
            f" {tetris.io.tetris2foam(self.grading)}"
            f"{tetris.io.comment(self.description)}"
        )

    # Make the class subscriptable
    def __getitem__(self, index: int) -> Vertex:
        return self.vertices[index]
