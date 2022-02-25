# coding: utf-8
"""Provide interfaces for dealing with faces, patches, and boundaries."""

from __future__ import annotations

from typing import Sequence

import tetris.constants
import tetris.io
from tetris.blockmesh.geometry import Geometry
from tetris.blockmesh.vertex import Vertex
from tetris.typing import BlockMeshElement


class Face(BlockMeshElement):
    """Define a blockMesh face entry."""

    def __init__(self, vertices: Sequence[Vertex], geometry: Geometry) -> None:
        self.vertices = vertices
        self.geometry = geometry

    def write(self) -> str:
        return (
            f"project {tetris.io.tetris2foam([v.name for v in self.vertices])}"
            f" {tetris.io.tetris2foam(self.geometry.name)}"
        )


class Patch(BlockMeshElement):
    """Define a blockMesh patch entry."""

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

    def __init__(self, name: str, type: str) -> None:
        self.name = name
        self.type = type

    def write(self) -> str:
        """Write the patch in OpenFOAM style."""
        return f"defaultPatch {{ name {self.name}}}; type {self.type} }}"


class PatchPair(BlockMeshElement):
    """Define a blockMesh mergePatchPair entry."""

    def __init__(self, master: Patch, slave: Patch) -> None:
        self.master = master
        self.slave = slave

    def write(self) -> str:
        """Write the patch pair in OpenFOAM style."""
        return f"{tetris.io.tetris2foam([self.master.name, self.slave.name])}"
