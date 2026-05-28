##################################################################################################################
# FiberRHSS.py
#
# SubRoutine to construct a fiber section: Rectangular HSS section  
# 
##################################################################################################################
#
# Input Arguments:
#------------------
# secID 	Section ID 
# matID 	Material ID  
# d  		Section depth	
# t  		Tube tickness
# nfdy 		Number of fibers along depth that goes along local y axis 
# nfty 		Number of fibers along thickness that goes along local y axis
# nfdz 		Number of fibers along depth that goes along local z axis
# nftz 		Number of fibers along thickness that goes along local z axis
#
# Written by: Dr. Ahmed Elkady, University of Southampton, UK
#
##################################################################################################################
import openseespy.opensees as ops

def FiberRHSS(secID, matID, d, t, nfdy, nfty, nfdz, nftz):
    """
    SubRoutine to construct a fiber section for a Rectangular HSS section.
    
    Note: In the original script's math, the depth 'd' is utilized for both 
    the local y and z axes, which effectively configures a Square HSS.
    """
    # Deduce inner dimensions
    dw = d - 2.0 * t
    
    # Local y-coordinates
    y1 = -d / 2.0
    y2 = -dw / 2.0
    y3 = dw / 2.0
    y4 = d / 2.0
    
    # Local z-coordinates
    z1 = -d / 2.0
    z2 = -dw / 2.0
    z3 = dw / 2.0
    z4 = d / 2.0
  
    # 1. Initialize the fiber section with torsional stiffness (GJ)
    ops.section('fiberSec', secID, '-GJ', 1.e10)
    
    # 2. Define the 4 quadrilateral patches to form the hollow box
    # Format: ops.patch('quadr', matTag, numSubdivIJ, numSubdivJK, yI, zI, yJ, zJ, yK, zK, yL, zL)
    
    # Top Flange
    ops.patch('quadr', matID, nftz, nfdy, y2, z4, y2, z3, y3, z3, y3, z4)
    
    # Bottom Flange
    ops.patch('quadr', matID, nftz, nfdy, y2, z2, y2, z1, y3, z1, y3, z2)
    
    # Left Web
    ops.patch('quadr', matID, nfdz, nfty, y1, z4, y1, z1, y2, z1, y2, z4)
    
    # Right Web
    ops.patch('quadr', matID, nfdz, nfty, y3, z4, y3, z1, y4, z1, y4, z4)
