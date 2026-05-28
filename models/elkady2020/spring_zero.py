##################################################################################################################
# Spring_Zero
#                                                                                       
# SubRoutine to construct a rotational spring with a very low stiffness                                                                 
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

def spring_zero(spring_id: int, node_i: int, node_j: int) -> None:
    """
    Construct a rotational spring with a very low stiffness.

    Args:
        spring_id: Spring ID / Element Tag
        node_i: Node i ID
        node_j: Node j ID
    """
    # Note: Requires a stiff material (e.g. tag 99) and a zero/low stiffness material (e.g. tag 9)
    ops.element('zeroLength', spring_id, node_i, node_j, '-mat', 99, 99, 9, '-dir', 1, 2, 6)
