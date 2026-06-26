// Gmsh project created on Thu Mar 26 16:59:55 2020
gridsize = 1;

H = 10;
// Points of the slope
Point(1) = {0, 0, 0, gridsize};
Point(2) = {3.2 * H, 0, 0, gridsize};
Point(3) = {1.2 * H, H, 0, gridsize};
Point(4) = {0, H, 0, gridsize};
Point(5) = {0, -0.5 * H, gridsize};
Point(6) = {3.2 * H, -0.5 * H, gridsize};
Point(7) = {5.2 * H, -0.5 * H, gridsize};
Point(8) = {5.2 * H, 0, gridsize};

// Lines
Line(1) = {1, 2};
Line(2) = {2, 3};
Line(3) = {3, 4};
Line(4) = {1, 4};
Line(5) = {5, 1};
Line(6) = {5, 6};
Line(7) = {6, 7};
Line(8) = {7, 8};
Line(9) = {8, 2};
Line(10) = {6, 2};

//+
Curve Loop(1) = {1, 2, 3, -4};
//+
Plane Surface(1) = {1};
//+
Curve Loop(2) = {5, 1, -10, -6};
//+
Plane Surface(2) = {2};
//+
Curve Loop(3) = {7, 8, 9, -10};
//+
Plane Surface(3) = {3};
//+
Transfinite Curve {1} = 21 Using Progression 1;
Transfinite Curve {2} = 21 Using Progression 1;
Transfinite Curve {3} = 21 Using Progression 1;
Transfinite Curve {4} = 21 Using Progression 1;

Transfinite Curve {5} = 11 Using Progression 1;
Transfinite Curve {6} = 21 Using Progression 1;
Transfinite Curve {10} = 11 Using Progression 1;
Transfinite Curve {7} = 11 Using Progression 1;
Transfinite Curve {8} = 11 Using Progression 1;
Transfinite Curve {9} = 11 Using Progression 1;
//+
Transfinite Surface {1};
//+
Transfinite Surface {2};
//+
Transfinite Surface {3};
//+
Recombine Surface {1};
//+
Recombine Surface {2};
//+
Recombine Surface {3};
