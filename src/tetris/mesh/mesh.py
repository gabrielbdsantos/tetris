# coding: utf-8
"""Interface for registering blockMesh elements in a mesh instance."""

from jinja2 import Template

from .elements import Block, PatchPair
from .io import BLOCKMESHDICT_TEMPLATE


class Mesh():
    """Provide a mesh object interface that outputs a blockMeshDict."""

    def __init__(self):
        self.ids = {"vertex": 0, "block": 0, "patch": 0, "edge": 0}
        self.scale = 1
        self.vertices = []
        self.blocks = []
        self.edges = []
        self.boundaries = []
        self.patches = []
        self.merge_patch_pairs = []

    def add_block(self, element):
        """Register a new block to the mesh."""
        if not isinstance(element, Block):
            raise TypeError(f"{element} is not a Block.")

        for vertex in element.vertices:
            self.add_vertex(vertex)

        for edge in element.edges:
            self.add_edge(edge)

        if element.id is None:
            self.blocks.append(element)
            self.blocks[-1].id = self.ids["block"]
            self.ids["block"] += 1

    def add_edge(self, edge):
        """Register a new edge to the mesh."""
        # If true, we have a simple straight line.  No need for registering it
        # to the mesh.
        if edge.type is None:
            return

        # Register the vertices defining edge extremities if not already
        # registered
        for vertex in [edge.v0, edge.v1]:
            self.add_vertex(vertex)

        # If edge.id is None, then the vertex was not registered before.
        #
        # TODO:
        #   For now, no check is done to verify whether the inverse edge is
        #   already defined. It makes no sense to have two edges defining the
        #   same curve -- or even worse, defining different curves, which would
        #   crash blockMesh. So, future versions could (should?) perform some
        #   kind of verification.
        if edge.id is None:
            self.edges.append(edge)
            self.edges[-1].id = self.ids["edge"]
            self.ids["edge"] += 1
            return

        # Code commented as a result of the TODO in the previous comment.
        # for i, e in enumerate(self.edges):
        #     if len(set((edge.v0, edge.v1)) & set((e.v0, e.v1))) == 2:
        #         print("Edge already set. This operation will override it.")
        #         edge.id = self.edges[i].id
        #         self.edges[i] = edge

    def add_vertex(self, vertex):
        """Register a new vertex to the mesh."""
        if vertex.id is None:
            self.vertices.append(vertex)
            self.vertices[-1].id = self.ids["vertex"]
            self.ids["vertex"] += 1

    def add_patch(self, patch):
        """Register a new patch to the mesh."""
        if patch.id is None:
            self.patches.append(patch)
            self.patches[-1].id = self.ids["patch"]
            self.ids["patch"] += 1

    def add_boundary(self, boundary):
        """Register a new boundary to the mesh."""
        raise NotImplementedError("Sorry. Yet to implement.")

    def add_mergePatchPairs(self, master, slave):
        """Merge the slave patch into the master patch."""
        # If master and slave are not registered to the Mesh instance yet, we
        # do it now.
        self.add_patch(master)
        self.add_patch(slave)

        # Create a PatchPair instance and register it to the mesh instance.
        self.merge_patch_pairs.append(PatchPair(master, slave))

    def write(self, output_filename, template=BLOCKMESHDICT_TEMPLATE):
        """Write the rendered blockMeshDict to disk."""
        with open(output_filename, 'w+') as f:
            f.write(self.__render(template=template))

    def print(self, template=BLOCKMESHDICT_TEMPLATE):
        """Print the rednered blockMeshDict to screen."""
        print(self.__render(template=template))

    def __render(self, template):
        """Render the Jinja2 blockMeshDict template."""
        with open(template) as t:
            dict_template = Template(t.read())

        render = dict_template.render(scale=self.scale,
                                      vertices=self.vertices,
                                      blocks=self.blocks,
                                      edges=self.edges,
                                      patches=self.patches,
                                      mergePatchPairs=self.merge_patch_pairs)

        return render
