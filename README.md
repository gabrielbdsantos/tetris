# Tetris

A Python module for creating structured meshes with blockMesh.

## Contents

* [Why Python?](#why-python%3F)
* [What can Tetris do?](#what-can-tetris-do%3F)
* [License](#license)

## Why Python?

[blockMesh][blockmesh] is for sure a great meshing tool. In my humble opinion,
one of the best. It is at the same time simple and robust, enabling the user to
create a wide range of meshes. However, it can be really complicated and boring
to compute the coordinates of several vertices, set the correct vertex sequence
for all block, set the correct number of elements to get the desired cell size,
and etc. On top of that, complex geometries are usually achieved via
[splines][tableedges], which demand external tools to be calculated. Then, why
not use Python to do all this?

Integrating Python into the meshing process can make everything a little bit
easier, reducing the time necessary to achieved what you want. It also
facilitates the process of creating parametric meshes for grid convergence
analysis and optimization studies. I know that someone will argue that [m4][m4]
does the same thing; but _really_...?

So, back to what matters, the great advantage of Python is [Numpy][numpy],
which makes really ease to perform operations of linear algebra and analytical
geometry. Additionally, Python offers a wide range of libraries and modules to
load and manipulate all kinds of data (e.g., `.stl` files, `.csv` data, etc.).
These two features together enable the creation of complex meshes within only a
fraction of what it would take to create the same mesh using only `blockMesh`
and `m4`.

## What can Tetris do?

Well, have you ever played tetris? If not, google it! If yes, then you already
have the answer. For me, meshing is somehow like playing tetris. I don't know
you, but I never try to create the whole mesh at once. Instead, I create one
block at a time until I get the mesh I want. Therefore, I started coding
Tetris, always keeping this concept in mind.

If you like to create everything at once, well... good luck! Perhaps Tetris
will serve you as well. But if anything goes wrong while running `blockMesh`,
the debugging process can be really harsh on you. So, my two cents on this
subject are: _create a block at a time_, and you won't regret it.

## License

This project is licensed under the MIT License.

Copyright (c) 2020 Gabriel B. Santos

You should have received a copy
of the MIT License along with this source code. If not, see
<https://mit-license.org>.

[blockmesh]: https://cfd.direct/openfoam/user-guide/blockMesh/
[tableedges]: https://cfd.direct/openfoam/user-guide/v8-blockMesh/#x26-1880112
[m4]: https://www.gnu.org/software/m4/m4.html
[numpy]: https://numpy.org
