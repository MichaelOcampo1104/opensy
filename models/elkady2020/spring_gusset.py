##################################################################################################################
# Spring_Gusset.tcl
#
# SubRoutine to construct a rotational spring with a bilinear repsonse for the gusset plate.
#
# References: 
#--------------	
# Hsiao, P-C., Lehman, D. E. and Roeder, C. W. (2013). "A Model to Simulate Special Concentrically Braced Frames 
# 	Beyond Brace Fracture." Earthquake Eng. & Structural Dynamics 42(2).
#
##################################################################################################################
#
# Input Arguments:
#------------------
# SpringID  Spring ID
# NodeI    	Node i ID 
# NodeJ    	Node j ID 
# E        	Young's modulus
# fy       	Expected yield strength
# Lb	   	Gusset plate average buckling length
# tp       	Gusset plate thickness
# Lc	   	Brace-to-Gusset connection length
# d_Brace  	Brace Depth/Height/Diameter
# matTag   	Material ID
#
# Written by: Dr. Ahmed Elkady, University of Southampton, UK
#
##################################################################################################################

import openseespy.opensees as ops
import math

def spring_gusset(SpringID, NodeI, NodeJ, E, fy, Lb, tp, Lc, d_Brace, matTag):
    """
    SubRoutine to construct a rotational spring with a bilinear response for the gusset plate.
    Ref: Hsiao, P-C., Lehman, D. E. and Roeder, C. W. (2013)
    
    NOTE: This function references a material tag '99' for translational DOFs. 
    Ensure that uniaxialMaterial 99 (typically a very stiff material like Elastic) 
    is defined in your main script before calling this function.
    """
    
    pi = math.pi                             # Definition of Pi (kept for consistency)
    Ww = d_Brace + 2.0 * Lc                  # Whitmore Width
    I = (Ww * (tp ** 3)) / 12.0              # Moment of Inertia 
    Z = (Ww * (tp ** 2)) / 6.0               # Plastic Modulus 
    My = Z * fy                              # Plastic Moment 
    Krot = (E * I) / Lb                      # Flexural Stiffness
    b = 0.01

    # Define the Steel02 material for the gusset out-of-plane rotation
    ops.uniaxialMaterial('Steel02', matTag, My, Krot, b, 20, 0.925, 0.15, 0.0005, 0.01, 0.0005, 0.01)

    # Construct the zeroLength element
    # Couples translational DOFs (1 and 2) with material 99, and rotational DOF (6) with matTag
    ops.element('zeroLength', SpringID, NodeI, NodeJ, 
                '-mat', 99, 99, matTag, 
                '-dir', 1, 2, 6, 
                '-doRayleigh', 1)
