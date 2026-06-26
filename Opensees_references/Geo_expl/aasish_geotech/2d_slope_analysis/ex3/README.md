# Notes:
In this problem we will assign the same material properties to the slope and the foundation. Periodic boundaries will be created on the left and the right boundaries. No water at the toe of the slope. Total stress analysis.
# To do
- [ ] Trace the slope in LibreCAD and obtain the coordinates for the slope.
- [ ] Convert the coordinates from LibreCAD paper units to physical units. Identify nodes corresponding to the obtained coordinates and compute distances for scale.
- [ ] Make the model of the slope in Gmsh.
- [ ] Assign appropriate physical tags for easy identification when assigning boundary conditions in OpenSees.
- [ ] Python script to read the nodes and elements.
- [ ] Script to read ndMaterial from a ``.csv`` file and assign to elements based on Gmsh physical tags.
- [ ] Analysis.
- [ ] Script to write desired output to ``.vtk`` file.
