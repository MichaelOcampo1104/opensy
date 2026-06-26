

# Notes:
In this problem we will assign the same material properties to the slope and the foundation. Periodic boundaries will be created on the left and the right boundaries. No water at the toe of the slope. Total stress analysis.
# To do
- [x] Make a simple slope with foundation layer in Gmsh.
- [x] Assign appropriate physical tags for easy identification when assigning boundary conditions in OpenSees.
- [x] Python script to read the nodes and elements.
- [x] Script to read ndMaterial from a ``.csv`` file and assign to elements based on Gmsh physical tags.
- [x] Analysis.
- [ ] Script to plot horizontal displacements with time, plot displacement at top of the slope, mid-slope, toe of the slope and a point on the slope layer away from the slope. Nodes: Top of slope: 6, bottom of slope: 5, Middle of the slope: 80, Away from the slope: 99
- [ ] Script to plot the horizontal accelerations with time at the four nodes above.
- [ ] Script to write displacements to ``.vtk`` file.
- [ ] Script to write desired output to ``.vtk`` file.


# Periodic boundary condition
The outer regions both on the left and right are periodic boundaries. How is a periodic boundary defined?
For the element in the periodic boundary use the same material in a given layer the periodic is defined but increase the element size to 10000.0.
fixity: 0 1 for the right most bottom periodic boundary node
fixity: 0 1 for right most bottom layer node
EqualDOF for the above two in dir [1, 2]
EqualDOF for left and right periodic boundary dir [1]
