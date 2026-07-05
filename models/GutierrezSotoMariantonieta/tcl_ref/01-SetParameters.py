# Geometric properties------------------------------------
bw_x = 6.0; # Bay width in x direction
bw_y = 6.0; # Bay width in y direction
sh = 4.0; # Story height

# main frame elements properties--------------------------
Esf = 2.05e11; # E for frame steel frame elements
Gsf = 7.93e10; # Shear modulus for steel frame elements

AC1 = 0.013376;  # section area for strut
IC1 = 1.15373416e-4; # moment of inertia for strut
# Node mass-----------------------------------------------
M_n = 24000.0; # Node mass (kg)

#PT strand------------------------------------------------
Apts = Strand_Area; # total area of PT strands, m^2

#Fuse assembly--------------------------------------------
KvA = 2.99151e8;# Kv for fuse A
Kf1A = KvA/1000
Kf2A = KvA*1000

# print('Parameters are set!')