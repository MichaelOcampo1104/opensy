// Gmsh project created on Thu Mar 26 16:59:55 2020
gridsize = 1;

// Left periodic boundary
Point(1) = {-60.960, -68.580, 0, gridsize};
Point(2) = {0.0, -68.580, 0, gridsize};
Point(3) = {0.0, 4.877, 0, gridsize};
Point(4) = {-60.960, 4.877, 0, gridsize};
// between periodic boundary and slope
Point(5) = {158.490, -68.580, 0, gridsize};
Point(6) = {158.490, -12.802, 0, gridsize};
Point(7) = {158.490, 4.877, 0, gridsize};
//slope
Point(8) = {266.70, 4.877, 0.0, gridsize};
Point(9) = {284.988, 0.000, 0.0, gridsize};
Point(10) = {361.188, -12.802, 0.0, gridsize};
Point(11) = {266.70, -12.802, 0.0, gridsize};
Point(12) = {266.70, -68.580, 0.0, gridsize};
// between the slope and the right periodic boundary
Point(13) = {483.108, -12.802, 0.0, gridsize};
Point(14) = {483.108, -68.580, 0.0, gridsize};
Point(15) = {361.188, -68.580, 0.0, gridsize};
// right periodic boundary
Point(16) = {544.068,-12.802, 0.0, gridsize};
Point(17) = {544.068, -68.580, 0.0, gridsize};

// Periodic boundary
Line(1) = {1, 2};
Line(2) = {2, 3};
Line(3) = {3, 4};
Line(4) = {1, 4};
// between periodic boundary and slope
Line(5) = {2, 5};
Line(6) = {5, 6};
Line(7) = {6, 7};
Line(8) = {7, 3};
// slope
Line(9) = {8, 7};
Line(10) = {9, 8};
Line(11) = {10, 9};
Line(12) = {6, 11};
Line(13) = {11, 8};
Line(14) = {5, 12};
Line(15) = {12, 11};
Line(16) = {11, 10};
// between the slope and right periodic boundary
Line(17) = {12, 15};
Line(18) = {15, 10};
Line(19) = {15, 14};
Line(20) = {14, 13};
Line(21) = {13, 10};
// right periodic boundary
Line(22) = {14, 17};
Line(23) = {17, 16};
Line(24) = {16, 13};

// Plane surfaces
Curve Loop(1) = {1, 2, 3, -4};
Plane Surface(1) = {1};
Curve Loop(2) = {5, 6, 7, 8, -2};
Plane Surface(2) = {2};
Curve Loop(3) = {14, 15, -12, -6};
Plane Surface(3) = {3};
Curve Loop(4) = {12, 13, 9, -7};
Plane Surface(4) = {4};
Curve Loop(5) = {16, 11, 10, -13};
Plane Surface(5) = {5};
Curve Loop(6) = {17, 18, -16, -15};
Plane Surface(6) = {6};
Curve Loop(7) = {19, 20, 21, -18};
Plane Surface(7) = {7};
Curve Loop(8) = {22, 23, 24, -20};
Plane Surface(8) = {8};

// Transfinite curve
Transfinite Curve {1} = 10 Using Progression 1;
Transfinite Curve {2} = 10 Using Progression 1;
Transfinite Curve {3} = 10 Using Progression 1;
Transfinite Curve {4} = 10 Using Progression 1;
Transfinite Curve {5} = 10 Using Progression 1;
Transfinite Curve {6} = 10 Using Progression 1;
Transfinite Curve {7} = 10 Using Progression 1;
Transfinite Curve {8} = 10 Using Progression 1;
Transfinite Curve {14} = 10 Using Progression 1;
Transfinite Curve {15} = 10 Using Progression 1;
Transfinite Curve {12} = 10 Using Progression 1;
Transfinite Curve {13} = 10 Using Progression 1;
Transfinite Curve {9} = 10 Using Progression 1;
Transfinite Curve {17} = 10 Using Progression 1;
Transfinite Curve {18} = 10 Using Progression 1;
Transfinite Curve {16} = 10 Using Progression 1;
Transfinite Curve {11} = 10 Using Progression 1;
Transfinite Curve {10} = 10 Using Progression 1;
Transfinite Curve {19} = 10 Using Progression 1;
Transfinite Curve {20} = 10 Using Progression 1;
Transfinite Curve {21} = 10 Using Progression 1;
Transfinite Curve {22} = 10 Using Progression 1;
Transfinite Curve {23} = 10 Using Progression 1;
Transfinite Curve {24} = 10 Using Progression 1;

// Transfinite surface
Transfinite Surface {1};
Transfinite Surface {2};
Transfinite Surface {3};
Transfinite Surface {4};
Transfinite Surface {6};
Transfinite Surface {5};
Transfinite Surface {7};
Transfinite Surface {8};

// Recombine for structured mesh
Recombine Surface {1};
Recombine Surface {2};
Recombine Surface {3};
Recombine Surface {4};
Recombine Surface {6};
Recombine Surface {5};
Recombine Surface {7};
Recombine Surface {8};
