# Slope Stability Analysis
These are my efforts to use OpenSees for slope stability analysis. Here I have tried to solve some of the problems defined in Griffiths and Lane (1999). I have very limited knowledge of both Finite Element Method (FEM) and OpenSees, so if anyone has a better way, please let me know by leaving comments in the issues. I will  try to solve all the problems in the paper and upload them as I complete them, without a timeline.

I will have to mention outright that this is not a tutorial; it does not contain detailed step-by-step instructions. One needs to have a certain proficiency with Python and an innate desire to learn because it may require learning new things. But I do hope if anyone is interested, and is ready to spend the time, this might make the journey less arduous, because I have listed and minimally demonstrated the use of some helpful tools.

I have used all opensource softwares under Windows 10 for this purpose. I think they are available for Linux too but I currently I do not have a separate Linux system so I am just guessing here.

The mesh was generated using Gmsh, a wonderful opensource tool for meshing. I have included the ``.geo`` defining the geometry and mesh properties. You would have to learn some Gmsh. There are tutorials online which are helpful. Here again, I have limited knowledge and I learnt it in the same way. In Gmsh create physical tags for everything, such as the boundary conditions and the layers. Both the ``.geo`` file and the mesh file ``.msh`` are in the ``gmsh`` directory.

I then used meshio to read the Gmsh mesh file and write the nodes and element connectivities to separate files. These files are located in the ``gmsh`` directory with ``_nodes`` and ``_elements`` in their filenames. These files are read when creating the model in OpenSeesPy.

The output of the analysis are written in the ``data`` directory. Each Factor of Safety (FS) analysis has its own directory where the output for that particular analysis is written. OpenSees does not have Mohr-Coulomb material model so I used Drucker-Prager with everything set to ``0`` (zero) except ``rho`` and ``sigma_y``. The conversion from Mohr-Coulomb to Drucker Prager was done using relationships, which can be found in Wikipedia or in the OpenSees documentation.

After the analysis I again used meshio to write node and element values in ``.vtk`` format so that I could visualize nodal displacements and elemental stresses and strains in Paraview. Opensees has ``PVD`` writer for nodal displacements but I wanted to include stresses and strains too. Here again I have no special knowledge, I just completed a few tutorials and used the search engine.

As mentioned previously, I have very limited knowledge of both FEM and OpenSees so the way I visualize elemental stresses and strains are by averaging the values at four integration points (2D quad elements). It should be understood that this gives the values at the centroids. Stresses and strains vary over the element. If the mesh is fine enough it might not be a bad way of visualizing these quantities. As I understand, there is no way to make VTK read and display integration point values, so I averaged and passed them as elemental values.

The workflow may not be optimal and no effort was made in that direction, obviously due to lack of expertise. If after reading this you can recommend any improvements in any of the steps please feel free to leave comments in the issues.  


# Requirements
Some additional requirements and resources (which come to mind now) are:

1. [Gmsh](http://gmsh.info/)
2. [Paraview](https://www.paraview.org/)
3. [meshio](https://github.com/nschloe/meshio)
4. [Gmsh tutorials](https://gitlab.onelab.info/gmsh/gmsh/-/blob/master/tutorial/t1.geo)
5. [Gmsh tutorials](https://www.youtube.com/watch?v=1A-b84kloFs)
6. [gmshtranslator](http://joseabell.com/)
