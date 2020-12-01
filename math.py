# coding: utf-8
"""Provide mathematical utilities for Tetris."""

import numpy as np


def normL2(vector):
    """Return the norm L2 of a given vector."""
    return np.linalg(vector)


def unit_vector(vector):
    """Return an unit vector on the same direction of the given vector."""
    return vector / normL2(vector)


def normal_unit_vector(p1, p2, inverse=False):
    """Return a normal unit vector."""
    sig = -1 if inverse else 1
    return unit_vector(sig * np.array([-(p2[1] - p1[1]), (p2[0] - p1[0])]))


def rotation3D(p1, p2, yaw=0, pitch=0, roll=0, rotate_about=None,
               in_rad=False):
    """Perform general rotation in three-dimensional euclidean space."""
    c, s = np.cos, np.sin
    p1, p2 = np.array(p1), np.array(p2)

    if rotate_about is None:
        rotate_about = p1

    if not in_rad:
        yaw = np.deg2rad(yaw)
        pitch = np.deg2rad(pitch)
        roll = np.deg2rad(roll)

    matrix_yaw = np.array([[c(yaw), -s(yaw), 0],
                           [s(yaw),  c(yaw), 0],
                           [0,       0,      1]])
    matrix_pitch = np.array([[c(pitch),  0, s(pitch)],
                             [0,         1,        0],
                             [-s(pitch), 0, c(pitch)]])
    matrix_roll = np.array([[1,       0,        0],
                            [0, c(roll), -s(roll)],
                            [0, s(roll),  c(roll)]])

    rotation_matrix = np.matmul(matrix_yaw, matrix_pitch, matrix_roll)

    _p1 = (rotation_matrix * (p1 - rotate_about)).sum(1)
    _p2 = (rotation_matrix * (p2 - rotate_about)).sum(1)

    return (_p1, _p2) + rotate_about


def ncells_simple(first_cell_size, edge_length):
    """Return the cell count based on: first cell size and edge length."""
    return int(np.ceil(edge_length / first_cell_size))
