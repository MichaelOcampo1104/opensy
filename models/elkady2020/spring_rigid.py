##################################################################################################################
# Spring_Rigid
#                                                                                       
# SubRoutine to construct a rotational spring with a very large stiffness                                                                 
#
##################################################################################################################
#
# Input Arguments:
#------------------
#  SpringID  			Spring ID
#  NodeI				Node i ID
#  NodeJ				Node j ID
#
# Written by: Dr. Ahmed Elkady, University of Southampton, UK
#
##################################################################################################################

import openseespy.opensees as ops

def spring_rigid(spring_id: int, node_i: int, node_j: int) -> None:
    """
    Construct a rotational spring with a very large stiffness.

    Args:
        spring_id: Spring ID / Element Tag
        node_i: Node i ID
        node_j: Node j ID
    """
    # Note: Requires a highly stiff material (e.g. tag 99) to be defined previously
    ops.element('zeroLength', spring_id, node_i, node_j, '-mat', 99, 99, 99, '-dir', 1, 2, 6, '-doRayleigh', 1)
