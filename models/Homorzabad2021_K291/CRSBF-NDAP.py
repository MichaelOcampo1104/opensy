import numpy as np
import matplotlib.pyplot as plt
import openseespy.opensees as ops
import os
import pathlib
import time

tic = time.perf_counter()
# Set the directory
project_directory = pathlib.Path("Directory")
os.chdir(project_directory)

# Set/load parameters -------------------------------------------------
f_y = 350e6;         # Steel yield stress, Pa
E_steel = 2.05e11;   # Steel young modulus, Pa
L_r = 4.71*(E_steel/f_y)**0.5; #kl/r limit
Strand_Area_Mat=np.array([[890.28],[1109.6],[1184.52],[1381.94],[1579.36],[1664.4],[1941.8],[2219.2]], ndmin=2)*1.0e-6; # Strand area values
# Section_Mat (Section number, A, I, r, S, Aw)
Section_Mat = np.loadtxt('Section_Mat.txt', ndmin=2)
# Element_Mat (Element number, Element code, element type, L)
Element_Mat=np.loadtxt('Element_Mat.txt', ndmin=2)

# Set initial design variables ----------------------------------------
X = np.array([[1],[450000.0],[8],[8],[8],[8],[8],[8],[8],[8],[8],[8],[8],[8]], ndmin=2); # Initial variable vector

# Set Optimization parameters --------------------------------------------
Lambda=0.1;
R0=100.0;
Epsilon=1.0;
ni = 200; # Number of iterations

# Define variations in variables:
dX = np.array([[1.0],[10000.0],[1.0],[1.0],[1.0],[1.0],[1.0],[1.0],[1.0],[1.0],[1.0],[1.0],[1.0],[1.0]], ndmin=2)
h = np.array([[0.1],[1000.0],[0.1],[0.1],[0.1],[0.1],[0.1],[0.1],[0.1],[0.1],[0.1],[0.1],[0.1],[0.1]], ndmin=2)
Obj_Func = np.zeros((ni,1))
Sim_Var = np.zeros((14, ni)); # To save the simulated variables
Var = np.zeros((14, ni)); # To save the design variables

for n in np.arange(ni):
    Rn = R0+n/Epsilon
    Var[:,n] = X.reshape(-1); # To save the design variables
    # Obtain the objective function and simulated variable vector ---------
    exec(open("Obj_Fun.py").read())
    # Run the model -------------------------------------------------------
    exec(open("Run_Structural_Model.py").read())
    # Obtain the constraints ----------------------------------------------
    exec(open("Obj_Fun.py").read())
    X_dot = NDAP(Lambda, Rn, X, dX, h)
    X += X_dot
toc = time.perf_counter()
ElapsedTime = toc - tic
print(ElapsedTime)
plt.plot(Obj_Func)
