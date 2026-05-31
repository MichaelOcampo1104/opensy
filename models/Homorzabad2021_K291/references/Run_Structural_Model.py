# This script configures and run the opensees model.

# Configuring the OpenSees Model
# Strand area -------------------------------------------------------------
Apts = Strand_Area

# Fuse rotational spring yield strength(10000-45000)N ---------------------
Fuse_Yield = V2

# Element Sections --------------------------------------------------------
VS1 = np.int(V_Sections[0,0])
VS2 = np.int(V_Sections[1,0])
VS3 = np.int(V_Sections[2,0])
VS4 = np.int(V_Sections[3,0])
VS5 = np.int(V_Sections[4,0])
VS6 = np.int(V_Sections[5,0])
VS7 = np.int(V_Sections[6,0])
VS8 = np.int(V_Sections[7,0])
VS9 = np.int(V_Sections[8,0])
VS10 = np.int(V_Sections[9,0])
VS11 = np.int(V_Sections[10,0])
VS12 = np.int(V_Sections[11,0])
# Runing the model with Variables------------------------------------
exec(open("Structural Model/Structural_model.py").read())
