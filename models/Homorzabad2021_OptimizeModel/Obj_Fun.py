#This script obtains the objective function and the Sumulated variables

# Strand area -------------------------------------------------------------
V1 = np.int(max(min(8, np.rint(X[0,0])), 1)); # To limit between 1 and 8
Strand_Area = Strand_Area_Mat[V1-1,0]

# Fuse yield strength(400-600)kN ------------------------------------------
V2 = max(min(600000.0, X[1,0]), 400000.0); # To limit between 400000 and 600000

# Element Sections --------------------------------------------------------
V_Sections = np.rint(X[2:14,0]).reshape(12,-1)
V_Sections[V_Sections>12] = 12
V_Sections[V_Sections<1] = 1

Sim_Var[:,n] = np.concatenate((np.array([[V1],[V2]], ndmin=2),V_Sections), axis=0).reshape(-1); # Variables used for simulation

# Obtaining the Objective Function-----------------------------------------
W_total = 0
for i in np.arange(602):
    Element_Type = np.int(Element_Mat[i,2])
    Element_Length = Element_Mat[i,3]
    Section_number = np.int(V_Sections[Element_Type-1, 0])
    Section_Area = Section_Mat[Section_number-1, 1]
    W_total = W_total+Element_Length*Section_Area;
    
W_max = np.sum(Element_Mat[:,3])*np.max(Section_Mat[:,1])
Strand_Area_max = np.max(Strand_Area_Mat)
Obj_Func[n,0] = 0.5*(W_total/W_max+Strand_Area/Strand_Area_max)
