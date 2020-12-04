# coding: utf-8
"""Provide Python-equivalent blockMesh elements."""

import os

import numpy as np
from jinja2 import Template

from .io import PATH_HERE, comment, list2foam
from .math import distance, is_collinear


class Element(object):
    """Base class for blockMesh elements."""

    def __init__(self):
        pass

    def write(self):
        """Output element in OpenFOAM style."""
        return None


class Vertex(Element):
    """Define a blockMesh vertex entry."""

    def __init__(self, *args):
        try:
            _args = np.array(args, dtype='float64')
            _args = np.reshape(_args, (_args.shape[-1],))
            self.coords = np.pad(_args, [0, int(3 - _args.shape[0])],
                                 'constant', constant_values=(0))
        except (TypeError, ValueError):
            raise ValueError("Invalid argument. Please, see the docstrings"
                             " for more details on how to declare the"
                             " coordinates.")

        self.id = None

    def write(self):
        """Write the coordinates in OpenFOAM style."""
        v = self.coords
        return (f"({v[0]:.6f} {v[1]:.6f} {v[2]:.6f}){comment(self.id)}")

    # Let us overload some operators so we may use the Vertex class in a more
    # pythonic way
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

        raise ArithmeticError("Unsupported operation. Vertex can only be"
                              " subtracted from other Vertex or Numpy array of"
                              " same shape.")

    def __mul__(self, other):
        """Overload the multiplication operator."""
        if isinstance(other, (int, float,)):
            return Vertex(*[x for x in (other * self.coords)])

        raise ArithmeticError("Unsupported operation. Vertex can only be"
                              " multiplied by a number.")

    def __truediv__(self, other):
        """Overload true division."""
        # Don't need to check whether `other` is zero. In such case, Python
        # itself will raise a ZeroDivisionError.
        if isinstance(other, (int, float,)):
            return Vertex(*[x for x in (self.coords / other)])

        raise ArithmeticError("Unsupported operation. Vertex can only be"
                              " divided by a number.")

    # Use the already overloaded operators for the reflected ones and augmented
    # arithmetic assignments
    __radd__ = __iadd__ = __add__
    __rsub__ = __isub__ = __sub__
    __rmul__ = __imul__ = __mul__
    __rtruediv__ = __itruediv__ = __truediv__


class Edge(Element):
    """Define a blockMesh edge entry."""

    def __init__(self, v0=None, v1=None, points=[], type=None):
        # Check whether the vertices are the same.
        if np.alltrue(v0.coords == v1.coords):
            raise ValueError("Zero-length edge. Vertices are at the same point"
                             " in space.")

        self.v0 = v0
        self.v1 = v1
        self.points = points
        self.type = type
        self.id = None

    @property
    def points(self):
        """Define a list of points defining the edge."""
        return self.__points

    @points.setter
    def points(self, points):
        # Let us work with numpy.array insted of simple lists.
        self.__points = np.array(points, dtype='float64')

        # The points list is empty. No need to go any further.
        if self.__points.size == 0:
            self.type = None
            return

        # Well, the code reached here, we then need to check whether the
        # provided list is correct; i.e., the points list must have a shape of
        # (x,3,), where x denotes any positive integer. Summarizing, the points
        # list must be a list of three-dimensional coordinates.
        if self.__points.shape[-1] != 3 or self.__points.ndim != 2:
            raise TypeError("Incorrect points list. Please see the docstrings"
                            " for more information on how to define the points"
                            " list.")

        # To check the collinearity of the points, we need to add the ending
        # vertices to the list of points.
        points = np.concatenate((
            np.reshape(self.v0.coords, (1, 3)),
            np.array(self.points),
            np.reshape(self.v1.coords, (1, 3))
        ))

        # Let us find and delete collinear points. Here, v0, v1, and v2 are
        # three consecutive points in the points list. If they are collinear,
        # the line can be represented by v0 and v2 only, eliminating the need
        # to store v1 as well.
        to_delete = []
        for i, (v0, v1, v2) in enumerate(zip(points[0:-2], points[1:-1],
                                             points[2:-0])):
            if is_collinear(v0, v1, v2):
                to_delete.append(i + 1)

        # `axis = 0` is needed to get a two-dimensional array, maintaining
        # consistence.
        np.delete(points, to_delete, axis=0)

        # As we added both vertices to the points list for checking for
        # collinear points, we now need to disregard them, excluding the
        # first and last entries in `points`.
        self.__points = points[1:-1]

        # Finally, if the points list is empty, then we have a straight line
        # between v0 and v1. Thereby, we must change the `type` of the current
        # instance to `None`.
        if self.__points.size == 0:
            self.type = None

    @property
    def length(self):
        """Compute the length of the edge."""
        # If the edge is a straight line (i.e., it has a type `None`), then
        # return the distance between v0 and v1.
        if self.type is None:
            return distance(self.v0, self.v1)

        # If the points list is not empty, we need to add both vertices to the
        # points list for computing the edge length. So, we prepend v0 and
        # append v1.
        points = np.concatenate((
            np.reshape(self.v0.coords, (1, 3)),
            np.array(self.points),
            np.reshape(self.v1.coords, (1, 3))
        ))

        return distance(points[:-1], points[1:])

    def write(self):
        """Write the edge in OpenFOAM style."""
        points = ([self.v0.coords.tolist()] + self.points.tolist() +
                  [self.v1.coords.tolist()])
        return f"{self.type} {self.v0.id} {self.v1.id} {list2foam(points)}"


class Boundary(Element):
    """Define a blockMesh boundary entry."""

    pass


class Patch(Element):
    """Define a blockMesh patch entry."""

    def __init__(self, faces=None, boundary_type=None, name=None):
        self.name = name
        self.faces = faces
        self.boundary_type = boundary_type
        self.id = None

    def write(self):
        """Write the patch in OpenFOAM style."""
        ids = [[f.id for f in face] for face in self.faces]
        return f"{self.boundary_type} {self.name} {list2foam(ids)}"


class PatchPair(Element):
    """Define a blockMesh mergePatchPair entry."""

    def __init__(self, master, slave):
        self.master = master
        self.slave = slave
        self.id = None

    def write(self):
        """Write the patch pair in OpenFOAM style."""
        return f"{list2foam([self.master.name, self.slave.name])}"


class Block(Element):
    """Define a blockMesh block entry."""

    # Sequence of vertices that yield an outward-pointing face
    # Check https://cfd.direct/openfoam/user-guide/blockMesh/#x26-1850174 for
    # more information on how vertices are labeled.
    FACE_MAPPING = {
        'bottom': (0, 3, 2, 1),
        'top': (4, 5, 6, 7),
        'right': (1, 2, 6, 5),
        'left': (3, 0, 4, 7),
        'front': (0, 1, 5, 4),
        'back': (2, 3, 7, 6)
    }

    # List of edges on each direction, following the notation on
    # https://cfd.direct/openfoam/user-guide/blockMesh/#x26-1850174
    EDGES_ON_AXIS = (
        ([0, 1], [2, 3], [6, 7], [4, 5]),  # x1
        ([0, 3], [1, 2], [5, 6], [4, 7]),  # x2
        ([0, 4], [1, 5], [2, 6], [3, 7]),  # x3
    )

    def __init__(self):
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

    def set_vertices(self, vertices):
        """Create a block from a list of vertices."""
        # Check whether the list of vertices is a `list` or `tuple`
        if not isinstance(vertices, (list, tuple,)):
            raise TypeError("List of vertices should be a list or tuple.")

        # Check whether the list have eight items. Anything different than this
        # is not acceptable.
        if len(vertices) != 8:
            raise ValueError("Incorrect number of vertices. Expected 8"
                             " vertices")

        # Clear the list of vertices and assign the given one
        self.vertices = []
        for i, vertex in enumerate(vertices):
            self.vertices.append(vertex)

        # Clear the list of edges and assign an Edge instance for each edge
        self.edges = []
        for edges_on_axis in self.EDGES_ON_AXIS:
            for v0, v1 in edges_on_axis:
                self.edges.append(Edge(self.vertices[v0], self.vertices[v1]))

    def set_edge(self, v0, v1, points, type='spline'):
        """Define a new edge."""
        # Check whether there is already a edge defined between the given
        # vertices.
        for i, edge in enumerate(self.edges):
            if len(set((edge.v0, edge.v1)) & set((v0, v1))) == 2:
                self.edges[i] = Edge(v0, v1, points, type)
                break
        else:
            self.edges.append(Edge(v0, v1, points, type))

    def get_face_ids(self, face=None):
        """Return a list of vertex ids for the given face label."""
        if face in self.FACE_MAPPING.keys():
            return [self.vertices[i] for i in self.FACE_MAPPING[face]]

    def write(self):
        """Write the block in OpenFOAM style."""
        return (
            f"hex ({' '.join([str(v.id) for v in self.vertices])})"
            f"{' ' + self.cellZone if self.cellZone else ''}"
            f" {list2foam(self.ncells)}"
            f" {self.grading_type}Grading {list2foam(self.grading)}"
            f"{comment(self.description)}"
        )


class Mesh():
    """Provide an interface for blockMeshDict."""

    def __init__(self):
        self.ids = {"vertex": 0, "block": 0, "patch": 0, "edge": 0}
        self.scale = 1
        self.vertices = []
        self.blocks = []
        self.edges = []
        self.boundaries = []
        self.patches = []
        self.merge_patch_pairs = []

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
        # If true, we have a simple straight line.  No need for registering it
        # to the mesh.
        if edge.type is None:
            return

        # Register the vertices defining edge extremities if not already
        # registered
        for vertex in [edge.v0, edge.v1]:
            self.add_vertex(vertex)

        # If edge.id is None, then the vertex was not registered before.
        #
        # TODO:
        #   For now, no check is done to verify whether the inverse edge is
        #   already defined. It makes no sense to have two edges defining the
        #   same curve -- or even worse, defining different curves, which would
        #   crash blockMesh. So, future versions could (should?) perform some
        #   kind of verification
        if edge.id is None:
            self.edges.append(edge)
            self.edges[-1].id = self.ids["edge"]
            self.ids["edge"] += 1
            return

        # for i, e in enumerate(self.edges):
        #     if len(set((edge.v0, edge.v1)) & set((e.v0, e.v1))) == 2:
        #         print("Edge already set. This operation will override it.")
        #         edge.id = self.edges[i].id
        #         self.edges[i] = edge

    def add_vertex(self, vertex):
        """Register a new vertex to the mesh."""
        if vertex.id is None:
            self.vertices.append(vertex)
            self.vertices[-1].id = self.ids["vertex"]
            self.ids["vertex"] += 1

    def add_patch(self, patch):
        """Register a new patch to the mesh."""
        if patch.id is None:
            self.patches.append(patch)
            self.patches[-1].id = self.ids["patch"]
            self.ids["patch"] += 1

    def add_boundary(self, boundary):
        """Register a new boundary to the mesh."""
        raise NotImplementedError("Sorry. Yet to implement.")

    def add_mergePatchPairs(self, master, slave):
        """Merge the target patch into master."""
        self.merge_patch_pairs.append(PatchPair(master, slave))

    def write(self, output_filename,
              template=os.path.join(PATH_HERE, 'assets/blockMeshDict')):
        """Write the rendered blockMeshDict to disk."""
        with open(output_filename, 'w+') as f:
            f.write(self.__render(template=template))

    def print(self,
              template=os.path.join(PATH_HERE, 'assets/blockMeshDict')):
        """Print the rednered blockMeshDict to screen."""
        print(self.__render(template=template))

    def __render(self, template):
        """Render the Jinja2 blockMeshDict template."""
        with open(template) as t:
            dict_template = Template(t.read())

        render = dict_template.render(scale=self.scale,
                                      vertices=self.vertices,
                                      blocks=self.blocks,
                                      edges=self.edges,
                                      patches=self.patches,
                                      mergePatchPairs=self.merge_patch_pairs)

        return render
