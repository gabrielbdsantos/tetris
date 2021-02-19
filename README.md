# Tetris

A Python module to create structured meshes using blockMesh as meshing kernel.

### Background

blockMesh is a great meshing tool --- in my _humble_ opinion, one of the best.
It is at the same time simple and robust, enabling the user to create
structured meshes for almost any geometry. The downside, however: it can be
really complicated --- and sometimes boring --- to compute the coordinates of
several vertices, set the correct vertex sequence that defines each one of the
blocks, compute the number of elements and grading level that results in the
desired cell size, and etc. On top of that, complex geometric features are
usually only feasible via splines (see [this section][tableedges] in the
blockMesh documentation), which are defined by a complex set of spatial
coordinates that are quasi impossible to type in manually.

So, why not integrate blockMesh with a user-friendly programming language like
Python?

Within Python we can easily manipulate points and edges, and then group them
into various blockMesh elements: vertices, blocks, boundaries, edges (splines,
arcs, polyLines, etc.), patches, and mergePatchPairs.

This is what Tetris is about.


### Philosophy

As the name suggests, the principle behind Tetris comes from the iconic video
game. Creating a mesh _block by block_ reduces the chances of making some of
the most common mistakes, like inside-out blocks, non-matching block cell
numbers or gradings,
and etc.


### Planned features

* [ ] Include documentation

  > For now, I am only documentating the Python code via docstrings and
  > comments. Even though I am given my best to clearly reveal what the code is
  > intended for, not all users are familiarized with such features or they
  > just don't like to dig into the code. Thus, a separate docummentation would
  > be of great interest.

* [ ] Auto cell matching

* [ ] Integration with an optimization tool

  > By integrating the module with an optimization tool, it would be possible
  > to get a number of cells per block that gives the desired cell size and
  > results in a mesh with the smallest possible number of elements.

* [ ] Tests for code verification

* [ ] Include examples

* [ ] Integration with a visualization tool.

  > Using something like [PyVista][pyvista] or [K3D-Jupyter][k3djupyter]
  > would allow to plot and inspect vertices, edges, and blocks without ever
  > leaving Jupyter Lab/Notebook;


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
