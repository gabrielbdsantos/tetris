# Tetris

A Python module to create structured meshes with blockMesh.

### Background

blockMesh is a great meshing tool --- in my _humble_ opinion, one of the best.
It is at the same time simple and robust, enabling the user to create
structured meshes of almost everything. The downside: it can be really
complicated and --- sometimes boring --- to compute the coordinates of several
vertices, set the correct vertex sequence that defines each one of the blocks,
compute the number of elements and grading level that results in the desired
cell size, and etc. On top of that, complex geometric features are usually only
feasible via splines (see [this section][tableedges] in the blockMesh
documentation), which are defined by a complex set of spatial coordinates that
are quasi impossible to type in manually.

So, why not integrate blockMesh with a user-friendly programming language like
Python?

Within Python we can easily manipulate points and edges, and then group them
into various blockMesh elements: vertices, blocks, boundaries, edges (splines,
arcs, polyLines, etc.), patches, and mergePatchPairs. This is what Tetris is
about.

### Philosophy

As the name suggests, the principle behind Tetris comes from the famous video
game. Creating a mesh _block by block_ reduces the changes of making some
mistakes, like inside-out blocks, non-matching block cell numbers or gradings,
etc.

### Planned features

* [ ] Integration with a visualization tool.<br>
  Using something like [PyVista][pyvista] or [K3D-Jupyter][k3djupyter] would
  allow to plot and inspect vertices, edges, and blocks without ever leaving
  Jupyter Lab/Notebook;

* [ ] Auto cell matching

---

### License

Tetris is licensed under the MIT License.

Copyright (c) 2020 Gabriel B. Santos


[blockmesh]: https://cfd.direct/openfoam/user-guide/blockMesh/
[tableedges]: https://cfd.direct/openfoam/user-guide/v8-blockMesh/#x26-1880112
[m4]: https://www.gnu.org/software/m4/m4.html
[numpy]: https://numpy.org
[pyvista]: https://pyvista.org
[k3djupyter]: https://github.com/K3D-tools/K3D-jupyter
