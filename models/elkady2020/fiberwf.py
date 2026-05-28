##################################################################################################################
# FiberWF.py
#
# SubRoutine to construct a fiber section: Wide-Flange or general I-shaped section 
# 
##################################################################################################################
#
# Input Arguments:
#------------------
# secID 	Section ID 
# matID 	Material ID  
# d  		Section depth	
# bf  		Flange width	
# tf  		Flange tickness
# tw  		Web tickness
# nfdw 		Number of fibers along depth
# nftw		Number of fibers along web thickness
# nfbf		Number of fibers along flange width
# nftf		Number of fibers along flange thickness
#
# Written by: Dr. Ahmed Elkady, University of Southampton, UK
#
##################################################################################################################
import openseespy.opensees as ops

def fiber_wf(secID, matID, d, bf, tf, tw, nfdw, nftw, nfbf, nftf):
    """
    SubRoutine to construct a fiber section: Wide-Flange or general I-shaped section 
    """
    # Deduce web depth
    dw = d - 2.0 * tf
    
    # Local y-coordinates (Depth direction)
    y1 = -d / 2.0
    y2 = -dw / 2.0
    y3 = dw / 2.0
    y4 = d / 2.0
  
    # Local z-coordinates (Flange width direction)
    z1 = -bf / 2.0
    z2 = -tw / 2.0
    z3 = tw / 2.0
    z4 = bf / 2.0

    # 1. Initialize the fiber section with torsional stiffness (GJ)
    ops.section('fiberSec', secID, '-GJ', 1.e10)
    
    # 2. Define the 3 quadrilateral patches forming the I-shape
    # Format: ops.patch('quadr', matTag, numSubdivIJ, numSubdivJK, yI, zI, yJ, zJ, yK, zK, yL, zL)
    
    # Bottom Flange
    ops.patch('quadr', matID, nfbf, nftf, y1, z4, y1, z1, y2, z1, y2, z4)
    
    # Web
    ops.patch('quadr', matID, nftw, nfdw, y2, z3, y2, z2, y3, z2, y3, z3)
    
    # Top Flange
    ops.patch('quadr', matID, nfbf, nftf, y3, z4, y3, z1, y4, z1, y4, z4)
