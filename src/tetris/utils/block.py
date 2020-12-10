# coding: utf-8
"""Utilities for creating block elements."""

import numpy as np


def ncells_simple(cell_size, edge_length):
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
