# coding: utf-8
"""Input--Output functionalities."""

import os.path

PATH_HERE = os.path.abspath(os.path.dirname(__file__))
BLOCKMESHDICT_TEMPLATE = os.path.abspath(
    os.path.join(PATH_HERE, r'../../../assets/blockMeshDict')
)


def comment(string):
    """Output `string` as a comment in OpenFOAM C++ style."""
    if string not in [None, ""]:
        return f" // {string}"
    return ""


def printif(string, pre_sep=' ', post_sep=' '):
    """Print `string` if `string` is not null."""
    if string not in [None, ""]:
        return f"{pre_sep}{string}{post_sep}"
    return ""


def list2foam(lst):
    """Translate nested Python lists into OpenFOAM lists."""
    from ..mesh.elements import Vertex

    if isinstance(lst[0], (str, float, int,)):
        s = f"{str(lst[0])}"
    elif isinstance(lst[0], (tuple, list,)):
        s = f"{list2foam(lst[0])}"
    elif isinstance(lst[0], Vertex):
        s = f"{lst[0].write()}"

    for i in lst[1:]:
        if isinstance(i, (str, float, int,)):
            s += f" {str(i)}"
        elif isinstance(i, (tuple, list,)):
            s += f" {list2foam(i)}"
        elif isinstance(i, Vertex):
            s += f" {i.write()}"

    return f"({s})"


def tetris2foam(element):
    """Translate Tetris objects into OpenFOAM style."""
    pass


def str2foam(value):
    """Translate Python strings to OpenFOAM style."""
    return f"{value}"


def int2foam(value, show_sign=False):
    """Translate Python integer to OpenFOAM style."""
    sign = '+' if show_sign else ''
    return f"{value:{sign}}"


def float2foam(value, show_sign=False, precision='.6', type='f'):
    """Translate Python float to OpenFOAM style."""
    sign = '+' if show_sign else ''
    return f"{value:{sign}{precision}{type}}"


def lst2foam(value, sep=' '):
    """Translate Python list to OpenFOAM style."""
    r = sep.join([tetris2foam(v) for v in value])
    return f"({r})"


# We can use the same function for lists and tuples.
tuple2foam = list2foam
