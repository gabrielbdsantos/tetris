# coding: utf-8
# pyright: reportUnboundVariable=false
"""Input--Output functionalities."""

from typing import Any, Sequence

from numpy import ndarray

def comment(string: Any) -> str:
    """Output `string` as a comment in OpenFOAM C++ style."""
    if string not in [None, ""]:
        return f" // {string}"
    return ""


def printif(string: str, pre_sep: str = " ", post_sep: str = " ") -> str:
    """Print `string` if `string` is not null."""
    if string not in [None, ""]:
        return f"{pre_sep}{string}{post_sep}"
    return ""


def list2foam(lst: Sequence[Any]) -> str:
    """Translate nested Python lists into OpenFOAM lists."""
    from .elements import Vertex

    if isinstance(
        lst[0],
        (
            str,
            float,
            int,
        ),
    ):
        s = f"{str(lst[0])}"
    elif isinstance(
        lst[0],
        (
            tuple,
            list,
        ),
    ):
        s = f"{list2foam(lst[0])}"
    elif isinstance(lst[0], Vertex):
        s = f"{lst[0].write()}"

    for i in lst[1:]:
        if isinstance(
            i,
            (
                str,
                float,
                int,
            ),
        ):
            s += f" {str(i)}"
        elif isinstance(
            i,
            (
                tuple,
                list,
            ),
        ):
            s += f" {list2foam(i)}"
        elif isinstance(i, Vertex):
            s += f" {i.write()}"

    return f"({s})"


def tetris2foam(element: Any) -> str:
    """Translate Tetris objects into OpenFOAM style."""
    from numpy import ndarray

    from .elements import Block, Edge, Patch, PatchPair, Vertex

    if isinstance(element, str):
        return str2foam(element)
    elif isinstance(element, int):
        return int2foam(element)
    elif isinstance(element, float):
        return float2foam(element)
    elif isinstance(element, (list, tuple)):
        return lst2foam(element)
    elif isinstance(element, ndarray):
        return numpy2foam(element)
    elif isinstance(element, (Vertex, Edge, Patch, PatchPair, Block)):
        return f"{element.write()}"

    raise TypeError(f"Could not print {element}")


def str2foam(value: str) -> str:
    """Translate Python strings to OpenFOAM style."""
    return f"{value}"


def int2foam(value: int, show_sign: bool = False) -> str:
    """Translate Python integer to OpenFOAM style."""
    sign = "+" if show_sign else ""
    return f"{value:{sign}}"


def float2foam(
    value: float,
    show_sign: bool = False,
    precision: str = ".6",
    type: str = "f",
) -> str:
    """Translate Python float to OpenFOAM style."""
    sign = "+" if show_sign else ""
    return f"{value:{sign}{precision}{type}}"


def lst2foam(value: Sequence[Any], sep: str = " ") -> str:
    """Translate Python list to OpenFOAM style."""
    r = sep.join([tetris2foam(v) for v in value])
    return f"({r})"


def numpy2foam(value: ndarray, sep: str = " ") -> str:
    """Translate Numpy array to OpenFOAM style."""
    return lst2foam(value.tolist(), sep)
