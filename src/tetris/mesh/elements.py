# coding: utf-8
"""Python-equivalent blockMesh elements."""

import copy
import numpy as np

from ..utils.math import distance, is_collinear
from .io import comment, list2foam


class Element(object):
    """Base class for blockMesh elements."""

    def __init__(self):
        pass

    def write(self):
        """Output the current element in OpenFOAM style."""
        return None


class Vertex(Element):
    """Define a blockMesh vertex entry."""

    def __init__(self, *args):
        try:
            # Convert the arguments to numpy.ndarray.
            _args = np.array(args, dtype='float64')

            # np.pad appends three zeros to the _args array, and we then select
            # the first three elements of the resulting array. If _args is
            # smaller than three, _args is filled with zeros for the missing
            # elements. Otherwise, _args itself is returned.
            #
            # np.reshape is used to force a one-dimesional array with three
            # elements. Anything different than that will raise an error.
            self.coords = np.pad(
                np.reshape(_args, _args.shape[-1]), (0, 3)
            )[:3]
        except (TypeError, ValueError):
            raise ValueError("Invalid argument. Please, see the docstrings "
                             "for details on how to declare the coordinates.")

        # An ID is assigned when registering the Vertex instance to the mesh.
        # It is also an easier way to monitor whether a Vertex has been already
        # registered to the mesh.
        self.id = None

    def write(self):
        """Write the coordinates in OpenFOAM style.

        Returns
        -------
        str
            A rendered representation of the current Vertex instance in
            OpenFOAM style.
        """
        v = self.coords
        return (f"({v[0]:.6f} {v[1]:.6f} {v[2]:.6f}){comment(self.id)}")

    # Make the class subscriptable
    def __getitem__(self, index):
        return self.coords[index]

    # Let's overload some operators so we may use the Vertex class in a more
    # pythonic way.
    def __neg__(self):
        return Vertex(-self.coords)

    def __eq__(self, other):
        if not isinstance(other, Vertex):
            other = Vertex(other)

        return all(self.coords == other.coords)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __add__(self, other):
        # When adding to Vertex instances, we just need to add each one's
        # coordinates since Vertex.coords is stored as numpy.ndarray.
        if isinstance(other, Vertex):
            return Vertex(self.coords + other.coords)

        # If `other` is an instance of numpy.ndarray, we can simply add
        # `self.coords` to it. It could be wise to check whether `other` and
        # `self.coords` have the same shape. However, as we enforce a (3,)
        # shape for Vertex coordinates, anything different than that will raise
        # an error. Just for the record, we are fine with that.
        if isinstance(other, np.ndarray):
            return Vertex(self.coords + other)

        # If 'other' is a list or tuple, we first convert it to numpy.ndarray
        # and then add it to 'self.coords'. Again, we perform no checks to
        # verify the list or tuple content and its dimensions.
        if isinstance(other, (list, tuple,)):
            return Vertex(self.coords + np.array(other, dtype='float64'))

        # If 'other' is simply an integer or float, we add it to 'self.coord'.
        if isinstance(other, (int, float)):
            return Vertex(self.coords + other)

        # Case none of the above clauses are satisfied, then we have an error.
        # Let's warn the user about that.
        raise ArithmeticError("Vertex can only be added to another Vertex or"
                              " Numpy array of same shape.")

    def __sub__(self, other):
        # Any decisions here are just a copy-paste version of the addition
        # operator. Thus, please refer to `__add__` for more details.
        if isinstance(other, Vertex):
            return Vertex(self.coords - other.coords)

        if isinstance(other, np.ndarray):
            return Vertex(self.coords - other)

        if isinstance(other, (list, tuple,)):
            return Vertex(self.coords + np.array(other, dtype='float64'))

        if isinstance(other, (int, float)):
            return Vertex(self.coords - other)

        raise ArithmeticError("Vertex can only be subtracted from another"
                              " Vertex or Numpy array of same shape.")

    def __mul__(self, other):
        if isinstance(other, (int, float,)):
            return Vertex(other * self.coords)

        raise ArithmeticError("Vertex can only be multiplied by an integer or"
                              " float.")

    def __truediv__(self, other):
        # Don't need to check whether `other` is zero. In such case, Python
        # itself will raise a ZeroDivisionError.
        if isinstance(other, (int, float,)):
            return Vertex(self.coords / other)

        raise ArithmeticError("Vertex can only be divided by an integer or"
                              " float.")

    # Use the already overloaded operators for the reflected operators and
    # augmented arithmetic assignments.
    __radd__ = __iadd__ = __add__
    __rsub__ = __isub__ = __sub__
    __rmul__ = __imul__ = __mul__
    __rtruediv__ = __itruediv__ = __truediv__

    # Overloading the __eq__ operator leads to a TypeError when trying to hash
    # instances of the Vertex class. Hence, to retain the implementation of
    # __hash__ from the parent class, the intepreter must be told to do so
    # explicitly by setting __hash__ as following
    __hash__ = Element.__hash__


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
        # (N, 3), where x denotes any positive integer. Summarizing, the points
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

    def length(self):
        """Compute the edge length."""
        # If the edge has a type `None` (i.e., it is a straight line, then
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

        # And lastly we compute the distance between the various consecutive
        # points in the list. The resulting values are all added together,
        # yielding the edge length.
        return distance(points[:-1], points[1:])

    def inverse_direction(self):
        """Return an Edge instance in the inverse direction."""
        return Edge(self.v1, self.v0, points=self.points[::-1], type=self.type)

    def write(self):
        """Write the edge in OpenFOAM style.

        Returns
        -------
        str
            A rendered representation of the current Edge instance in OpenFOAM
            style.
        """
        if self.type != 'arc':
            points = ([self.v0.coords.tolist()] + self.points.tolist() +
                      [self.v1.coords.tolist()])
        else:
            points = self.points[0].tolist()

        return f"{self.type} {self.v0.id} {self.v1.id} {list2foam(points)}"

    # Make the class subscriptable
    def __getitem__(self, index):
        return self.vertices[index]


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

    # Make the class subscriptable
    def __getitem__(self, index):
        return self.faces[index]


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
        self.ncells = [1, 1, 1]
        self.cellZone = ""

        self.description = None
        self.id = None

    # Properties
    # -------------------------------------------------------------------------
    @property
    def ncells(self):
        """Get the number of cells on each axis."""
        return self.__ncells

    @ncells.setter
    def ncells(self, value):
        # Since `value` can be a list, tuple, or numpy.array, we must provide a
        # solution for all cases. Instead of using a series of if/else clauses,
        # it may be more interesting to convert `value` to numpy.array and then
        # reshape it into what we want.
        self.__ncells = np.reshape(np.array(value, dtype=int), (3))

    @property
    def grading(self):
        """Get the block grading on each axis/edge."""
        return self.__grading

    @grading.setter
    def grading(self, value):
        # For now, value must be either a list or a tuple
        if not isinstance(value, (list, tuple)):
            raise TypeError('The block grading must be expressed as either a'
                            f'a list or a tuple. A {type(value)} was given.')

        # If value has three elements, then we adopt the simpleGrading approach
        if len(value) == 3:
            # We copy the value linked grading levels may be changed freely
            self.__grading = copy.deepcopy(value)
            self.__grading_type = 'simple'
            return

        # Otherwise, the block uses the 'edgeGrading' approach, which requires
        # a grading level for each one of the edges. Thus, the grading array
        # must be of size 12.
        if len(value) == 12:
            # We copy the value linked grading levels may be changed freely
            self.__grading = copy.deepcopy(value)
            self.__grading_type = 'edge'
            return

        # If we reach here, the number of elements passed are wrong. So, let's
        # throw an error
        raise ValueError('The number of elements defining the grading must be'
                         'either 3 (simpleGrading) or 12 (edgeGrading)')

    # Setters
    # -------------------------------------------------------------------------
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
        # Check whether there is already an edge defined for the given
        # vertices.
        for i, edge in enumerate(self.edges):
            if {edge.v0, edge.v1} == {v0, v1}:
                self.edges[i] = Edge(v0, v1, points, type)
                break
        else:
            self.edges.append(Edge(v0, v1, points, type))

    def set_cell_size(self, value, axis=None):
        """Set a homogeneous cell count to obtain the given cell size."""
        from ..utils.math import distance
        from ..utils.block import ncells_simple

        if axis is not None:
            id0, id1 = self.EDGES_ON_AXIS[axis][0]
            self.ncells[axis] = ncells_simple(
                value, self.get_edge_by_vertex(id0, id1).length()
            )
            return

        self.ncells = [
            ncells_simple(value, distance(self.vertices[0], self.vertices[1])),
            ncells_simple(value, distance(self.vertices[0], self.vertices[3])),
            ncells_simple(value, distance(self.vertices[0], self.vertices[4])),
        ]

    # Getters
    # -------------------------------------------------------------------------
    def get_cell_size(self, v0, v1):
        """Get the cell size along the edge v0--v1.

        Parameters
        ----------
        v0 : int, Vertex
            Vertex instance or id.
        v1 : int, Vertex
            Vertex instance or id.

        Returns
        -------
        float
            The cell size along the edge v0--v1.
        """
        # Get the edge to which the vertices v0 and v1 belong.
        edge = self.get_edge_by_vertex(v0, v1)

        # Get in which axis the edge lays
        def edge_on_axis():
            nonlocal self, edge, v0, v1
            for i, axis in enumerate(self.EDGES_ON_AXIS):
                for id0, id1 in axis:
                    _v0 = self.vertices[id0]
                    _v1 = self.vertices[id1]
                    if {_v0, _v1} == {edge.v0, edge.v1}:
                        return i

        return edge.length() / self.ncells[edge_on_axis()]

    def get_face_ids(self, face=None):
        """Get a list the vertex ids for the given face label.

        Parameters
        ----------
        face : str
            The face label: right, left, top, bottom, front, or back.

        Returns
        -------
        list
            List of vertex ids that describe the given face label. The
            list is ordered to yield an outward-pointing face.
        """
        if face in self.FACE_MAPPING.keys():
            return [self.vertices[i] for i in self.FACE_MAPPING[face]]

    def get_edge_by_vertex(self, v0, v1):
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

        for edge in self.edges:
            if {edge.v0, edge.v1} == {v0, v1}:
                return edge if edge.v0 == v0 else edge.inverse_direction()

    def write(self):
        """Write the block in OpenFOAM style.

        Returns
        -------
        str
            OpenFOAM entry for hex blocks.
        """
        return (
            f"hex ({' '.join([str(v.id) for v in self.vertices])})"
            f"{' ' + self.cellZone if self.cellZone else ''}"
            f" {list2foam(self.ncells.tolist())}"
            f" {self.__grading_type}Grading {list2foam(self.grading)}"
            f"{comment(self.description)}"
        )

    # Make the class subscriptable
    def __getitem__(self, index):
        return self.vertices[index]
