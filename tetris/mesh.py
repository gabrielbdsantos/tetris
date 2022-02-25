# coding: utf-8
"""Interface for registering blockMesh elements in a mesh instance."""

from __future__ import annotations

import pathlib
from typing import Dict, List

from jinja2 import Template

from tetris.elements import Block, GenericEdge, Patch, PatchPair, Vertex
from tetris.template import BLOCKMESHDICT_TEMPLATE


class Mesh:
    """Provide a mesh object interface that outputs a blockMeshDict."""

    __slots__ = [
        "ids",
        "scale",
        "vertices",
        "blocks",
        "edges",
        "patches",
        "merge_patch_pairs",
    ]

    def __init__(self) -> None:
        self.ids: Dict[str, int] = {
            "vertex": 0,
            "block": 0,
            "patch": 0,
            "edge": 0,
        }
        self.scale: int = 1
        self.vertices: List[Vertex] = []
        self.blocks: List[Block] = []
        self.edges: List[GenericEdge] = []
        self.patches: List[Patch] = []
        self.merge_patch_pairs: List[PatchPair] = []

    def add_block(self, element: Block) -> None:
        """Register a new block to the mesh."""
        if not isinstance(element, Block):
            raise TypeError(f"{element} is not a Block.")

        for vertex in element.vertices:
            self.add_vertex(vertex)

        for edge in element.edges:
            self.add_edge(edge)

        if element.id < 0:
            self.blocks.append(element)
            self.blocks[-1].id = self.ids["block"]
            self.ids["block"] += 1

    def add_edge(self, edge: GenericEdge) -> None:
        """Register a new edge to the mesh."""
        # If the edge type is undefined, we have a simple straight line. No
        # need for registering it to the mesh.
        if edge.type is None:
            return

        # Register the vertices defining the extremities if not already
        # registered
        for vertex in [edge.v0, edge.v1]:
            self.add_vertex(vertex)

        # TODO:
        #   For now, no check is done to verify whether the inverse edge is
        #   already defined. It makes no sense to have two edges defining the
        #   same curve -- or even worse, defining different curves --, which
        #   would crash blockMesh. So, future versions could (should?) perform
        #   some kind of verification.
        if edge.id < 0:
            self.edges.append(edge)
            self.edges[-1].id = self.ids["edge"]
            self.ids["edge"] += 1
            return

    def add_vertex(self, vertex: Vertex) -> None:
        """Register a new vertex to the mesh."""
        if vertex.id < 0:
            self.vertices.append(vertex)
            self.vertices[-1].id = self.ids["vertex"]
            self.ids["vertex"] += 1

    def add_patch(self, patch: Patch) -> None:
        """Register a new patch to the mesh."""
        if patch.id < 0:
            self.patches.append(patch)
            self.patches[-1].id = self.ids["patch"]
            self.ids["patch"] += 1

    def add_mergePatchPairs(self, master: Patch, slave: Patch) -> None:
        """Merge the slave patch into the master patch."""
        # If master and slave are not yet registered to the mesh instance,
        # register them now.
        self.add_patch(master)
        self.add_patch(slave)

        # Create a PatchPair instance and register it to the mesh instance.
        self.merge_patch_pairs.append(PatchPair(master, slave))

    def write(
        self,
        filename: str,
        template: str = BLOCKMESHDICT_TEMPLATE,
        header: str = "",
        footer: str = "",
    ) -> None:
        """Write the rendered blockMeshDict to file."""
        with open(pathlib.Path(filename).resolve(), "w+") as file:
            file.write(
                self._render(template=template, header=header, footer=footer)
            )

    def print(
        self,
        template: str = BLOCKMESHDICT_TEMPLATE,
        header: str = "",
        footer: str = "",
    ) -> None:
        """Print the rendered blockMeshDict to screen."""
        print(self._render(template=template, header=header, footer=footer))

    def _render(
        self, template: str, header: str = "", footer: str = ""
    ) -> str:
        """Render a blockMeshDict template using Jinja2."""
        from tetris import __version__ as TETRIS_VERSION

        render = Template(template).render(
            header=header,
            footer=footer,
            version=TETRIS_VERSION,
            scale=self.scale,
            vertices=self.vertices,
            blocks=self.blocks,
            edges=[edge for edge in self.edges if edge.type != "line"],
            patches=self.patches,
            mergePatchPairs=self.merge_patch_pairs,
        )

        return render
