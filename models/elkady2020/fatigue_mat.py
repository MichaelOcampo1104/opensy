##################################################################################################################
# FatigueMat.py
#
# SubRoutine to construct a Steel02 material masked with a Fatigue material to simulate ductile fracture in steel braces.
#
# References: 
#--------------	
# Karamanchi, E. and Lignos, D. G. (2014). "Computational Approach for Collapse Assessment of Concentrically Braced 
#	Frames in Seismic Regions." ASCE Journal of Structural Engineering: 140.
#
##################################################################################################################
#
# Input Arguments:
#------------------
# matID      	Material ID
# SecType     	The brace cross-section type
# 				1 --> Rectangular HSS section
#				2 --> Circular HSS section
#				3 --> Wide-flange section
# fy       		Expected yield strength
# E         	Young's modulus
# L 		  	Brace length
# ry     		Cross-section weak-axis radius of gyration
# wt    		Cross-section width-to-thickness ratio
# ht 			Cross-section height
# bt 			Cross-section width
#
# Written by: Dr. Ahmed Elkady, University of Southampton, UK
#
##################################################################################################################

import openseespy.opensees as ops

def fatigue_mat(matID, SecType, fy, E, L, ry, wt, ht, bt):
    """
    SubRoutine to construct a Steel02 material masked with a Fatigue material 
    to simulate ductile fracture in steel braces.
    Ref: Karamanchi, E. and Lignos, D. G. (2014)
    """
    
    matFatigue = matID + 1

    # 1. Rectangular HSS Section
    if SecType == 1:
        b = 0.001       # Strain Hardening Ratio
        R0 = 22.0       # Control the Transition from Elastic to Plastic Branches
        cR1 = 0.925     # Recommended Values: R0=10~20, cR1=0.925, cR2=0.15
        cR2 = 0.25
        # Isotropic Hardening Parameters
        a1 = 0.03       # Compression yield envelope scaling
        a2 = 1.0
        a3 = 0.02       # Tension yield envelope scaling
        a4 = 1.0
        m = -0.300      # Slope of Coffin-Manson curve in log-log space
        E0 = 0.291 * ((L / ry) ** -0.484) * (wt ** -0.613) * ((E / fy) ** 0.303)

    # 2. Round HSS Section
    elif SecType == 2:
        b = 0.005       # Strain Hardening Ratio
        R0 = 24.0       # Control the Transition from Elastic to Plastic Branches
        cR1 = 0.925
        cR2 = 0.25
        # Isotropic Hardening Parameters
        a1 = 0.02
        a2 = 1.0
        a3 = 0.02
        a4 = 1.0
        m = -0.300      # Slope of Coffin-Manson curve in log-log space
        E0 = 0.748 * ((L / ry) ** -0.399) * (wt ** -0.628) * ((E / fy) ** 0.201)

    # 3. Wide-Flange Section
    elif SecType == 3:
        b = 0.001       # Strain Hardening Ratio
        R0 = 20.0       # Control the Transition from Elastic to Plastic Branches
        cR1 = 0.925
        cR2 = 0.25
        # Isotropic Hardening Parameters
        a1 = 0.02
        a2 = 1.0
        a3 = 0.02
        a4 = 1.0
        m = -0.300      # Slope of Coffin-Manson curve in log-log space
        E0 = 0.0391 * ((L / ry) ** -0.234) * (bt ** -0.169) * (ht ** -0.065) * ((E / fy) ** 0.351)
        
    else:
        raise ValueError(f"Invalid SecType: {SecType}. Must be 1, 2, or 3.")

    # 2. Amplify strain capacity if an elastic model is being built (large fy override)
    if fy > 3000.0:
        E0 = 100.0

    # 3. Define the OpenSees Materials
    # Base Steel02 material
    ops.uniaxialMaterial('Steel02', matID, fy, E, b, R0, cR1, cR2, a1, a2, a3, a4)
    
    # Wrapper Fatigue material
    ops.uniaxialMaterial('Fatigue', matFatigue, matID, '-E0', E0, '-m', m)
