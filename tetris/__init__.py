# coding: utf-8
"""A minimal Python wrapper around OpenFOAM's blockMesh."""

from .elements import Block, Edge, Patch, Vertex
from .mesh import Mesh

__version__ = "0.1.0"
