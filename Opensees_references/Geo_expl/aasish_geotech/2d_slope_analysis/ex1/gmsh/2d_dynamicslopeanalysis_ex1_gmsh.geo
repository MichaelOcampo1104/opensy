// Gmsh project created on Thu Mar 26 16:59:55 2020
gridsize = 1;

H = 10;
// Points of the slope
Point(1) = {0, 0, 0, gridsize};
Point(2) = {H, 0, 0, gridsize};
Point(3) = {H, H, 0, gridsize};
Point(4) = {0, H, 0, gridsize};
Point(5) = {5.2 * H, 0, 0, gridsize};
Point(6) = {3.2 * H, H, 0, gridsize};

Point(7) = {0, -2 * H, 0, gridsize};
Point(8) = {H, -2 * H, 0, gridsize};
Point(9) = {5.2 * H, -2 * H, 0, gridsize};
Point(10) = {7.2 * H, -2 * H, 0, gridsize};
Point(11) = {7.2 * H, 0, 0, gridsize};
Point(12) = {8.2 * H, -2 * H, 0, gridsize};
Point(13) = {8.2 * H, 0, 0, gridsize};

// Lines
Line(1) = {1, 2};
Line(2) = {2, 3};
Line(3) = {3, 4};
Line(4) = {1, 4};
Line(5) = {2, 5};
Line(6) = {5, 6};
Line(7) = {6, 3};
Line(8) = {1, 7};
Line(9) = {7, 8};
Line(10) = {8, 2};
Line(11) = {8, 9};
Line(12) = {9, 5};
Line(13) = {9, 10};
Line(14) = {10, 11};
Line(15) = {11, 5};
Line(16) = {10, 12};
Line(17) = {12, 13};
Line(18) = {13, 11};

// Plane surface 
Curve Loop(1) = {1, 2, 3, -4};
Plane Surface(1) = {1};
Curve Loop(2) = {5, 6, 7, -2};
Plane Surface(2) = {2};
Curve Loop(3) = {9, 10, -1, 8};
Plane Surface(3) = {3};
Curve Loop(4) = {11, 12, -5, -10};
Plane Surface(4) = {4};
Curve Loop(5) = {13, 14, 15, -12};
Plane Surface(5) = {5};
Curve Loop(6) = {16, 17, 18, -14};
Plane Surface(6) = {6};

// Physical tags
// node for earthquake motion
Physical Point("EQ_motion") = {7};
// Lower boundary
Physical Curve("Fix_010") = {9, 11, 13, 16};
// left periodic boundary
Physical Curve("left_outer_slope_boundary") = {4};
Physical Curve("left_inner_slope_boundary") = {2};
Physical Curve("left_outer_foundation_boundary") = {8};
Physical Curve("left_inner_foundation_boundary") = {10};
// right periodic boundary
Physical Curve("right_outer_foundation_boundary") = {17};
Physical Curve("right_inner_foundation_boundary") = {14};
// Slope
Physical Surface("Slope") = {2};
Physical Surface("Foundation") = {4, 5};
// periodic boundary
Physical Surface("PeriodicBoundary_Slope") = {1};
Physical Surface("PeriodicBoundary_Foundation") = {3, 6};

// Transfinite curves
slope_discretize = 21;
Transfinite Curve {1} = 1 Using Progression 1;
Transfinite Curve {2} = slope_discretize Using Progression 1;
Transfinite Curve {3} = 1 Using Progression 1;
Transfinite Curve {4} = slope_discretize Using Progression 1;
Transfinite Curve {5} = slope_discretize Using Progression 1;
Transfinite Curve {6} = slope_discretize Using Progression 1;
Transfinite Curve {7} = slope_discretize Using Progression 1;
Transfinite Curve {8} = 21 Using Progression 1;
Transfinite Curve {9} = 1 Using Progression 1;
Transfinite Curve {10} = 21 Using Progression 1;
Transfinite Curve {11} = slope_discretize Using Progression 1;
Transfinite Curve {12} = 21 Using Progression 1;
Transfinite Curve {13} = 11 Using Progression 1;
Transfinite Curve {14} = 21 Using Progression 1;
Transfinite Curve {15} = 11 Using Progression 1;
Transfinite Curve {16} = 1 Using Progression 1;
Transfinite Curve {17} = 21 Using Progression 1;
Transfinite Curve {18} = 1 Using Progression 1;

// Transfinite surface
Transfinite Surface {1};
Transfinite Surface {2};
Transfinite Surface {3};
Transfinite Surface {4};
Transfinite Surface {5};
Transfinite Surface {6};

// Recombine for square mesh
Recombine Surface {1};
Recombine Surface {2};
Recombine Surface {3};
Recombine Surface {4};
Recombine Surface {5};
Recombine Surface {6};

// Remove duplicate entities
Coherence Mesh;

// Renumber nodes and elements in continuous sequence
RenumberMeshNodes;
RenumberMeshElements;


