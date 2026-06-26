// Gmsh project created on Thu Mar 26 16:59:55 2020
gridsize = 1;

H = 10;
// Points of the slope
Point(1) = {0, 0, 0, gridsize};
Point(2) = {3.2 * H, 0, 0, gridsize};
Point(3) = {1.2 * H, H, 0, gridsize};
Point(4) = {0, H, 0, gridsize};

// Lines
Line(1) = {1, 2};
Line(2) = {2, 3};
Line(3) = {3, 4};
Line(4) = {4, 1};

// Plane surface
Curve Loop(1) = {1, 2, 3, 4};
Plane Surface(1) = {1};

// Physical group
Physical Curve("Fix_110") = {1};
Physical Curve("Fix_100") = {4};
Physical Surface("Soil") = {1};

// Transfinite curve
Transfinite Curve {1} = 41 Using Progression 1;
Transfinite Curve {2} = 41 Using Progression 1;
Transfinite Curve {3} = 41 Using Progression 1;
Transfinite Curve {4} = 41 Using Progression 1;

// Transfinite surface
Transfinite Surface {1};

// Recombine for quad elements
Recombine Surface {1};

// Remove duplicate entities
// Coherence Mesh;

// Renumber nodes and elements in continuous sequence
// RenumberMeshNodes;
// RenumberMeshElements;
