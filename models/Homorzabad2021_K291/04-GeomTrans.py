ops.geomTransf('PDelta', 1, *[1.0,0.0,0.0]); #For columns, struts, beams and braces in y-direction
ops.geomTransf('PDelta', 2, *[0.0,-1.0,0.0]); #For beams and braces in x-direction

# print("Geometric transformations defined!")