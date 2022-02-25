# coding: utf-8
"""Define a collection of useful constants."""

from collections import OrderedDict

# Sequence of vertices that yield an outward-pointing face
# Check https://cfd.direct/openfoam/user-guide/blockMesh/#x26-1850174 for
# more information on how vertices are labeled.
FACE_MAPPING = OrderedDict(
    {
        "left": (3, 0, 4, 7),
        "right": (1, 2, 6, 5),
        "front": (0, 1, 5, 4),
        "back": (2, 3, 7, 6),
        "bottom": (0, 3, 2, 1),
        "top": (4, 5, 6, 7),
    }
)

FACE_IDS = (
    (3, 0, 4, 7),
    (1, 2, 6, 5),
    (0, 1, 5, 4),
    (2, 3, 7, 6),
    (0, 3, 2, 1),
    (4, 5, 6, 7),
)


# List of edges on each direction, following the notation on
# https://cfd.direct/openfoam/user-guide/blockMesh/#x26-1850174
EDGES_ON_AXIS = (
    ((0, 1), (2, 3), (6, 7), (4, 5)),  # x1
    ((0, 3), (1, 2), (5, 6), (4, 7)),  # x2
    ((0, 4), (1, 5), (2, 6), (3, 7)),  # x3
)

BLOCK_EDGES = (
    (0, 1),
    (2, 3),
    (6, 7),
    (4, 5),
    (0, 3),
    (1, 2),
    (5, 6),
    (4, 7),
    (0, 4),
    (1, 5),
    (2, 6),
    (3, 7),
)
