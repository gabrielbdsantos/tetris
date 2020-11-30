# coding: utf-8
"""Provide IO functionalities for Tetris."""

import os.path

PATH_HERE = os.path.abspath(os.path.dirname(__file__))


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
    from .mesh import Vertex

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
            s = f"{i.write()}"

    return f"({s})"
