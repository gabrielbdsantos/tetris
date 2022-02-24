# coding: utf-8
"""Define type hints for being used accross the module."""

from typing import List, Tuple, Union

from numpy import floating
from numpy.typing import NDArray

Vector = Union[List[floating], Tuple[floating], NDArray[floating]]


class BlockMeshElement:
    """Base class for blockMesh elements."""

    def write(self):
        """Output the current element in OpenFOAM style."""
        pass
