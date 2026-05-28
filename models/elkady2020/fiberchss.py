##################################################################################################################
# FiberCHSS.py
#
# SubRoutine to construct a fiber section: Circular HSS section  
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
#
# Written by: Dr. Ahmed Elkady, University of Southampton, UK
#
##################################################################################################################
import openseespy.opensees as ops

def fiber_chss(secID, matID, d, t, nfdy, nfty):
    """
    SubRoutine to construct a fiber section: Circular HSS section  
    """
    intRad = (d / 2.0) - t
    extRad = d / 2.0

    # 1. Initialize the fiber section with torsional stiffness (GJ)
    ops.section('fiberSec', secID, '-GJ', 1.e10)
    
    # 2. Define the circular patch
    # Syntax: ops.patch('circ', matTag, numSubdivCirc, numSubdivRad, yCenter, zCenter, intRad, extRad, startAng, endAng)
    # Note: Kept the exact variable assignment order from your original TCL script.
    ops.patch('circ', matID, nfdy, nfty, 0.0, 0.0, extRad, intRad, 360.0, 0.0)
