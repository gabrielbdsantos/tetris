# coding: utf-8
"""A minimal Python wrapper around OpenFOAM's blockMesh."""

from .elements import (
    ArcMidEdge,
    ArcOriginEdge,
    Block,
    LineEdge,
    Patch,
    PatchPair,
    PolyLineEdge,
    SplineEdge,
    Vertex,
)
from .mesh import Mesh

__version__ = "0.1.0"
