# coding: utf-8
"""Provide Python-equivalent blockMesh elements."""

import os
import numpy as np
from jinja2 import Template
from .io import PATH_HERE, comment, list2foam


class Base(object):
    """Base class for mesh elements."""

    def __init__(self):
        pass

    def write(self):
        """Output element in OpenFOAM style."""
        return None


class Vertex(Base):
    """Define a vertex in a three-dimensional euclidean space."""

    def __init__(self, x1, x2, x3):
        self.coords = np.array([x1, x2, x3], dtype='float64')
        self.id = None

    def write(self):
        """Write the coordinates in OpenFOAM style."""
        v = self.coords
        return (f"({v[0]:.6f} {v[1]:.6f} {v[2]:.6f}){comment(self.id)}")

    def __neg__(self):
        """Overload the negation operator."""
        return Vertex(*(-self.coords))

    def __add__(self, other):
        """Overload the addition operator."""
        if isinstance(other, Vertex):
            return Vertex(*[x for x in (self.coords + other.coords)])

        if isinstance(other, np.ndarray):
            if other.shape == self.coords.shape:
                return Vertex(*[x for x in (self.coords + other)])

        if isinstance(other, (list, tuple,)):
            if len(other) == 3:
                return Vertex(*[x for x in (self.coords + np.array(other))])

        if isinstance(other, (int, float)):
            return Vertex(*[x for x in (self.coords + other)])

        raise ArithmeticError("Vertex can only be added to other Vertex or"
                              " Numpy array of same shape.")

    def __sub__(self, other):
        """Overload the subtraction operator."""
        if isinstance(other, Vertex):
            return Vertex(*[x for x in (self.coords - other.coords)])

        if isinstance(other, np.ndarray):
            if other.shape == self.coords.shape:
                return Vertex(*[x for x in (self.coords - other)])

        if isinstance(other, (int, float)):
            return Vertex(*[x for x in (self.coords - other)])

        raise ArithmeticError("Vertex can only be subtracted from other Vertex"
                              " or Numpy array of same shape.")

    def __mul__(self, other):
        """Overload the multiplication operator."""
        if isinstance(other, (int, float,)):
            return Vertex(*[x for x in (other * self.coords)])

        raise ArithmeticError("Vertex can only be multiplied by a number.")

    def __truediv__(self, other):
        """Overload true division."""
        # Don't need to check whether `other` is zero. In such case, Python
        # itself will raise a ZeroDivisionError.
        if isinstance(other, (int, float,)):
            return Vertex(*[x for x in (self.coords / other)])

        raise ArithmeticError("Vertex can only be divided by a number.")

    # Reflected operators
    def __radd__(self, other):
        """Overload the reflected addition operator."""
        return self.__add__(other)

    def __rsub__(self, other):
        """Overload the reflected subtraction operator."""
        return self.__sub__(other)

    def __rmul__(self, other):
        """Overload the reflected multiplication operator."""
        return self.__mul__(other)

    def __rtruediv__(self, other):
        """Overload the reflected division operator."""
        return self.__truediv__(other)

    # Augmented arithmetic assignments
    def __iadd__(self, other):
        """Overload the augmented addition assignment."""
        return self.__add__(other)

    def __isub__(self, other):
        """Overload the augmented subtraction assignment."""
        return self.__sub__(other)

    def __imul__(self, other):
        """Overload the augmented multiplication assignment."""
        return self.__mul__(other)

    def __itruediv__(self, other):
        """Overload the augmented division assignment."""
        return self.__truediv__(other)


class Edge(Base):
    """Define an edge in a three-dimensional euclidian space."""

    def __init__(self, v1=None, v2=None, points=None, type="spline"):
        self.v1 = v1
        self.v2 = v2
        self.points = points
        self.type = "spline"
        self.id = None

    def write(self):
        """Write the edge in OpenFOAM style."""
        points = [list(self.v1.coords)] + self.points + [list(self.v2.coords)]
        return f"{self.type} {self.v1.id} {self.v2.id} {list2foam(points)}"


class Patch(Base):
    """Define a face in a three-dimensional euclidian space."""

    def __init__(self, edges=None, btype=None):
        self.edges = edges
        self.btype = btype
        self.mapping = True
        self.id = None


class Block(Base):
    """Define a block in a three-dimensional euclidian space."""

    # Sequence of vertices that yield an outward-pointing face
    FACE_MAPPING = {
        'bottom': (0, 3, 2, 1),
        'top': (4, 5, 6, 7),
        'right': (2, 3, 6, 5),
        'left': (3, 0, 4, 7),
        'front': (0, 1, 5, 4),
        'back': (2, 3, 7, 6)
    }

    # List of edges on each direction. It follows the notation on
    # https://cfd.direct/openfoam/user-guide/blockMesh/#x26-1850174
    EDGES_ON_AXIS = (
        ([0, 1], [2, 3], [6, 7], [4, 5]),  # x1 = 0
        ([0, 3], [1, 2], [5, 6], [4, 7]),  # x2 = 1
        ([0, 4], [1, 5], [2, 6], [3, 7]),  # x3 = 2
    )

    def __init__(self):
        # List of 8 Vertex objects
        self.vertices = []
        self.edges = []
        self.faces = {}
        self.patches = []

        self.grading = [1, 1, 1]
        self.grading_type = 'simple'
        self.ncells = [1, 1, 1]
        self.cellZone = ""

        self.description = None
        self.id = None
        self.valid = False

    def set_vertices(self, vertices):
        """Create a block from a list of vertices."""
        if not isinstance(vertices, (list, tuple,)):
            raise TypeError("List of vertices should be a list or tuple.")

        if len(vertices) != 8:
            raise ValueError("Incorrect number of vertices. Expected 8"
                             " vertices")

        self.vertices = []
        self.valid = False

        for i, vertex in enumerate(vertices):
            self.vertices.append(vertex)

        self.valid = True

    def set_edge(self, v1, v2, points, type="spline"):
        """Set a new edge feature."""
        for i, edge in enumerate(self.edges):
            if len(set((edge.v1, edge.v2)) & set((v1, v2))) == 2:
                print("Edge already set. This operation will override it.")
                self.edges[i].v1 = v1
                self.edges[i].v2 = v2
                self.edges[i].points = points
                self.edges[i].type = type
                return

        self.edges.append(Edge(v1, v2, points))

    def write(self):
        """Write the block in OpenFOAM style."""
        return (
            f"hex ({' '.join([str(v.id) for v in self.vertices])})"
            f"{' ' + self.cellZone if self.cellZone else ''}"
            f" {list2foam(self.ncells)}"
            f" {self.grading_type}Grading {list2foam(self.grading)}"
            f"{comment(self.description)}"
        )


class Mesh(Base):
    """Define a new structure mesh."""

    def __init__(self):
        self.ids = {"vertex": 0, "block": 0, "patch": 0, "edge": 0}
        self.scale = 1
        self.vertices = []
        self.blocks = []
        self.edges = []
        self.boundaries = []
        self.patches = []

    def add_block(self, element):
        """Register a new block to the mesh."""
        if not isinstance(element, Block):
            raise TypeError(f"{element} is not a Block.")

        for vertex in element.vertices:
            self.add_vertex(vertex)

        for edge in element.edges:
            self.add_edge(edge)

        if element.id is None:
            self.blocks.append(element)
            self.blocks[-1].id = self.ids["block"]
            self.ids["block"] += 1

    def add_edge(self, edge):
        """Register a new edge to the mesh."""
        for vertex in [edge.v1, edge.v2]:
            self.add_vertex(vertex)

        for i, e in enumerate(self.edges):
            if len(set((edge.v1, edge.v2)) & set((e.v1, e.v2))) == 2:
                print("Edge already set. This will override it.")
                edge.id = self.edges[i].id
                self.edges[i] = edge
                return

        if edge.id is None:
            self.edges.append(edge)
            self.edges[-1].id = self.ids["edge"]
            self.ids["edge"] += 1

    def add_vertex(self, vertex):
        """Register a new vertex to the mesh."""
        if vertex.id is None:
            self.vertices.append(vertex)
            self.vertices[-1].id = self.ids["vertex"]
            self.ids["vertex"] += 1

    def write(self, output=None,
              template=os.path.join(PATH_HERE, 'assets/blockMeshDict')):
        """Write the resulting blockMeshDict using a Jinja2 template."""
        with open(template) as t:
            dict_template = Template(t.read())

        render = dict_template.render(scale=self.scale, vertices=self.vertices,
                                      blocks=self.blocks, edges=self.edges)

        if output is None:
            print(render)
        else:
            with open(output, 'w+') as f:
                f.write(render)
