# This script loads OpenSees outputs and obtains the g constraint terms

Roof_Disp=np.loadtxt('Structural Model/Outputs/disp604.out')

Fuse_Shear_Deformation_1=np.loadtxt('Structural Model/Outputs/disp2011.out')
Fuse_Shear_Deformation_2=np.loadtxt('Structural Model/Outputs/disp2051.out')
Fuse_Shear_Deformation = np.concatenate((Fuse_Shear_Deformation_1,Fuse_Shear_Deformation_2), axis=0)

Strand_Force_1=np.loadtxt('Structural Model/Outputs/Strand1.out')
Strand_Force_2=np.loadtxt('Structural Model/Outputs/Strand2.out')
Strand_Force=np.concatenate((Strand_Force_1,Strand_Force_2), axis=0)


for i in np.arange(48):
    exec(f"Force{str(i+1)} = np.loadtxt('Structural Model/Outputs/Element{str(i+1)}.out')")


# Axial and flexural strength ----------------------------------------
V_c = np.zeros((48,1))
V_u = np.zeros((48,1))
Ax_Flex_Overall = np.zeros((np.size(Force1, axis=0),1))
g1 = np.zeros((48,1))
for i in np.arange(48):
    Element_Type=np.int(Element_Mat[i,2])
    Element_Length=Element_Mat[i,3]
    Section_number = np.int(V_Sections[Element_Type-1, 0])
    Section_Area = Section_Mat[Section_number-1, 1]
    A_w=Section_Mat[Section_number-1, 8]
    V_c[i,0] = 0.75*0.6*f_y*A_w
    exec('V_u[i,0] = np.absolute(Force'+str(i+1)+'[:,2]).max()')
    r = Section_Mat[Section_number-1, 3]
    S = Section_Mat[Section_number-1, 4]
    F_e = (np.pi**2.0)*E_steel/((2.0*Element_Length/r)**2)
    if (2*Element_Length/r)<=L_r:
        F_cr=(0.658**(f_y/F_e))*f_y
    else:
        F_cr=0.877*F_e;

    P_c = 0.9*F_cr*Section_Area;
    M_c = 0.9*f_y*S;
    
    for j in np.arange(np.size(Force1, axis=0)):
        exec('Pr_Pc = np.absolute(Force'+str(i+1)+'[j,1])/P_c')
        exec('P_r = np.absolute(Force'+str(i+1)+'[j,1])')
        exec('M1 = np.absolute(Force'+str(i+1)+'[j,6])')
        exec('M2 = np.absolute(Force'+str(i+1)+'[j,12])')
        M_r = max(M1,M2)
        if Pr_Pc >= 0.2:
            Ax_Flex_Overall[j,0] = P_r/P_c+8.0/9.0*M_r/M_c
        else:
            Ax_Flex_Overall[j,0] = P_r/2.0/P_c+M_r/M_c   
    g1[i,0] = np.max(Ax_Flex_Overall)-1.0
# Shear strength -----------------------------------------------------
g2 = V_u-V_c
# Story drift --------------------------------------------------------
g3 = np.absolute(Roof_Disp[:,2]).max()/24.0-0.05
# Fuse shear Deformation ---------------------------------------------
g4 = np.absolute(Fuse_Shear_Deformation[:,3]).max()/0.15-0.5
# Story Residual Drift-- ---------------------------------------------
g5 = np.absolute(Roof_Disp[-1,2])/24.0-0.01
# Strand stress -------- ---------------------------------------------
g6 = Strand_Force[:,1].max()/Apts/(1.676e9)-0.01

g = np.concatenate((g1,g2,g3.reshape(-1,1),g4.reshape(-1,1),g5.reshape(-1,1),g6.reshape(-1,1)), axis=0)
