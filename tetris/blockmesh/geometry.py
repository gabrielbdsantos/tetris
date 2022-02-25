# coding: utf-8
"""Provide common geometry types."""

from __future__ import annotations

from abc import abstractproperty

from tetris.typing import BlockMeshElement


class Geometry(BlockMeshElement):
    """Base class for geometry objects."""

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractproperty
    def type(self) -> str:
        """Define the geometry type"""
        ...

    def __eq__(self, other: Geometry) -> bool:
        """Check whether two geometries are 'equal'."""
        return self.name == other.name


class TriSurfaceMesh(Geometry):
    """Create a geometry based on a surface file."""

    def __init__(self, name: str, file: str) -> None:
        super().__init__(name)
        self.file = file

    @property
    def type(self) -> str:
        return "triSurfaceMesh"

    def write(self) -> str:
        return f'{self.name} {{ type {self.type}; file "{self.file}"; }}'
