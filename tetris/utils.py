# coding: utf-8
"""Mathematical utilities for Tetris."""

from __future__ import annotations

from typing import TYPE_CHECKING, Union

import numpy as np
from numpy.typing import NDArray
from scipy.spatial.transform import Rotation

from tetris.typing import Vector

if TYPE_CHECKING:
    from tetris.blockmesh.vertex import Vertex


def normL2(array: NDArray[np.floating]) -> float:
    """Return the norm L2 of a given vector or matrix.

    Recalling that vectors may be expressed as first-order matrices, the
    function can be used as generic function for computing the L2 norm of both.

    Patameters
    ----------
    array : numpy.ndarray
        A vector or a two-dimensional matrix.

    Returns
    -------
    float
        The norm L2 of a given vector or matrix.
    """
    # First check whether we are working with vectors.
    if array.ndim == 1:
        element = np.reshape(
            array,
            (
                1,
                array.shape[0],
            ),
        )

    # TODO:
    #   Perhaps, we should also check for higher dimensions and not just assume
    #   that if `array` is not one-dimensional, then it is a two-dimensional
    #   matrix. Although not ideal, for now we assume that the user is working
    #   with matrices with no more than two dimensions.
    else:
        element = array

    on_axis = element.ndim - 1
    return np.linalg.norm(element, axis=on_axis)


def unit_vector(v: NDArray[np.floating]) -> NDArray[np.floating]:
    """Return the normalized vector vnorm in the same direction of v.

    Parameters
    ----------
    v : numpy.ndarray
        A vector.

    Returns
    -------
    numpy.ndarray
        A three-dimensional unit vector in the same direction of `v`.

    Raises
    ------
    ZeroDivisionError
        If `v` has a null length.
    TypeError
        If `v` is not an instance of `numpy.ndarray`. A check is not necessary
        as `normL2` will raise a TypeError in such case.
    """
    return v / normL2(v)


# NOTE: Review code
def unit_normal_vector(
    e1: Vector,
    e2: Vector,
    inverse: bool = False,
) -> np.ndarray:
    """Compute the unit normal vector.

    The function provides a generic way to compute the normal vector both in
    two- and three-dimensions. For 3D analysis, a normal vector to a plane can
    be obtained by computing the cross product of any two vectors on that
    plane; in this case, we use vectors `e1` and `e2`. For 2D analysis, a
    pseudo 3D analysis is done by considering a vector defined by points `e1`
    and `e2` (i.e., [e2 - e1]) and the orthogonal unit vector in the empty
    direction.

    Note
    ----
    Instead of using 'v' as in vectors or 'p' as in points, we chose to adopt
    the names `e1` and `e2` for the parameters as a reference to 'element 1'
    and 'element 2'. This seemed pertinent as the function handles 2D and 3D
    analysis.

    Note that the term 'straight element' refers to a line in 2D and to a plane
    in 3D.

    Here is another trick part: which direction is the inverse one? Let's think
    about a circle in the XY plane. Now, for computing the normal vector of any
    two points on that circle, we compute the cross product of the vector
    connecting these two points, which results in either (0, 0, 1) orthogonal
    (0, 0, -1). Using (0, 0, 1), the normal vector will point inward; and using
    (0, 0, -1), it will point outward. Now, thinking on the meshing process,
    a closed section normally means 'walls'. Therefore, inside walls meshing is
    unnecessary in most cases. So, we assume that the normal direction is
    always pointing outward when following a clockwise convention, which yields
    the vector (0, 0, -1) for computing the cross product.

    Parameters
    ----------
    e1 : list, tuple, numpy.ndarray
        The first element -- point (2D) or vector (3D) -- that defines a
        straight element.
    e2 : list, tuple, numpy.ndarray
        The second element -- point (2D) or vector (3D) -- that defines a
        straight line.
    inverse : bool
        If True, inverts the signal of the resulting vector.

    Returns
    -------
    numpy.ndarray
        The unit normal vector to the straight element that is defined by
        elements e1 and e2.
    """
    from tetris.elements import Vertex

    # As the function handles lists, tuples, and numpy.ndarrys as well, it is
    # of interest to convert the arguments to a common element; in this case,
    # we use tetris.Vertex instances to provide a standardized numpy.ndarray
    # element.
    _e1 = Vertex(e1).coords
    _e2 = Vertex(e2).coords

    # Let's evaluate in which plane we are working on
    empty_dims = (~(_e1.astype(bool) & _e2.astype(bool))).astype(int)
    n_empty_dims = empty_dims.sum()

    if n_empty_dims == 0:
        # Working with at least one three-dimensional element; thereby, a
        # vector. Hence, we assume that both elements are vectors.
        return unit_vector(np.cross(e1, e2))

    # At least one element is two-dimensional. Let's find the vector connecting
    # these two points.
    vector = _e1 + _e2

    # See Notes in the docstring for information on how the empty direction is
    # chosen.
    empty_dim = empty_dims[np.where(empty_dims == 1)[0][-1]]
    empty_dim = empty_dims if inverse else -1 * empty_dims

    return unit_vector(np.cross(vector, empty_dim))


def rotate3D(
    coords: NDArray[np.floating],
    yaw: float = 0,
    pitch: float = 0,
    roll: float = 0,
    origin: NDArray[np.floating] = np.zeros(3),
    degrees: bool = True,
) -> NDArray[np.floating]:
    """Rotate a 3D point about a reference point.

    Parameters
    ----------
    coords: np.ndarray
        A three-dimensional point in space.
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
    np.ndarray
        The new coordiantes
    """
    return (coords - origin) @ Rotation.from_euler(
        "zyx", [-yaw, -pitch, -roll], degrees=degrees
    ).as_matrix() + origin


def distance(
    point1: Union[Vertex, Vector], point2: Union[Vertex, Vector]
) -> float:
    """Calculate the distance between two points."""
    p1: NDArray[np.floating] = (
        point1.coords if isinstance(point1, Vertex) else np.array(point1)
    )
    p2: NDArray[np.floating] = (
        point2.coords if isinstance(point2, Vertex) else np.array(point2)
    )

    return normL2(p1 + p2)


def is_collinear(v0: Vertex, v1: Vertex, v2: Vertex) -> bool:
    """Determine whether three points are collinear."""
    a = (v0 - v1).coords
    b = (v0 - v2).coords

    return np.cross(a, b).sum() == 0


def ncells_simple(cell_size: float, edge_length: float) -> int:
    """Compute the number of cells that satisfy the requirements.

    Parameters
    ----------
    cell_size : float
    edge_length : float

    Returns
    -------
    int
        The number of cells that satisfies the desired cell size for a
        given edge length.
    """
    return int(np.ceil(edge_length / cell_size))


def to_array(
    element: Union[Vertex, Vector, int, float]
) -> NDArray[np.floating]:
    from tetris.blockmesh.vertex import Vertex

    return (
        element.coords
        if isinstance(element, Vertex)
        else np.asarray(np.ones(3) * element)
    )
