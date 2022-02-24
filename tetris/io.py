# coding: utf-8# pyright: reportUnboundVariable=false
"""Input--Output functionalities."""

from __future__ import annotations

from typing import Any, Sequence, Union

from numpy import ndarray

from tetris.typing import BlockMeshElement


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


def str2foam(value: str) -> str:
    """Translate Python strings to OpenFOAM style."""
    return f"{value}"


def number2foam(
    value: Union[int, float],
    show_sign: bool,
    precision: str = "",
    type: str = "f",
) -> str:
    """Translate Python numbers to OpenFOAM style."""
    sign = "+" if show_sign else ""
    return f"{value:{sign}{precision}{type}}"


def int2foam(value: int, show_sign: bool = False) -> str:
    """Translate Python integer to OpenFOAM style."""
    return number2foam(value, show_sign, precision=".0")


def float2foam(value: float, show_sign: bool = False) -> str:
    """Translate Python float to OpenFOAM style."""
    return number2foam(value, show_sign, precision=".6", type="f")


def sequence2foam(value: Sequence[Any], sep: str = " ") -> str:
    """Translate Python list to OpenFOAM style."""
    r = sep.join([tetris2foam(v) for v in value])
    return f"({r})"


def numpy2foam(value: ndarray, sep: str = " ") -> str:
    """Translate Numpy array to OpenFOAM style."""
    return sequence2foam(value.tolist(), sep)


def blockMeshElement2foam(value: BlockMeshElement) -> str:
    """Call the write method of the Element."""
    return value.write()


def tetris2foam(element: Any) -> str:
    """Translate Tetris objects into OpenFOAM style."""

    translate_types = {
        str: str2foam,
        int: int2foam,
        float: float2foam,
        list: sequence2foam,
        tuple: sequence2foam,
        ndarray: numpy2foam,
        BlockMeshElement: blockMeshElement2foam,
    }

    if (element_type := type(element)) in translate_types:
        return translate_types[element_type](element)

    raise TypeError(f"Could not print {element} of type {element_type}")
