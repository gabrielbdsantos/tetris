# coding: utf-8
"""Provide interfaces for manipulating blocks."""

from __future__ import annotations

import copy
from typing import Collection, Union

import tetris.constants
import tetris.io
import tetris.utils
from tetris.blockmesh.edge import Edge, LineEdge
from tetris.blockmesh.patch import Patch
from tetris.blockmesh.vertex import Vertex
from tetris.typing import BlockMeshElement


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
        self.edges: list[Edge] = []
        self.patches: list[Patch] = []

        self.grading = [1, 1, 1]
        self.ncells = [1, 1, 1]
        self.cellZone: str = ""

        self.description: str = ""

    @staticmethod
    def from_vertices(vertices: Collection[Vertex]) -> Block:
        """Create a block from a list of vertices."""
        # Instantiate the class
        cls = Block()
        cls.set_vertices(vertices)

        return cls

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

    def set_edge(self, edge: Edge) -> None:
        """Define a new edge."""
        ids = (
            self.vertices.index(edge.v0),
            self.vertices.index(edge.v1),
        )
        ordered_ids = tuple({*ids})

        # Are the vertices in the right order?
        # (i.e., following the OpenFOAM convention)
        right_order = ids == ordered_ids

        self.edges[tetris.constants.BLOCK_EDGES.index(ordered_ids)] = (
            edge if right_order else edge.invert()
        )

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

    def edge(self, v0: Union[Vertex, int], v1: Union[Vertex, int]) -> Edge:
        """Get the edge defined by vertices v0 and v1.

        Parameters
        ----------
        v0 : Vertex, int
            Either the vertex instance or the local vertex id.
        v1 : Vertex, int
            Either the vertex instance or the local vertex id.

        Returns
        -------
        Edge
            The edge defined by the two vertices.
        """
        id0 = v0 if isinstance(v0, int) else self.vertices.index(v0)
        id1 = v1 if isinstance(v1, int) else self.vertices.index(v1)
        ids = tuple({id0, id1})

        edge = self.edges[tetris.constants.BLOCK_EDGES.index(ids)]

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
