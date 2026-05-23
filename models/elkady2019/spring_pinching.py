##################################################################################################################
# Spring_Pinching
#                                    
# SubRoutine to construct a rotational spring with deteriorating pinched response representing the moment-rotation 
# behaviour of beams that are part of conventional shear-tab connections.
#  
# The subroutine also considers modeling uncertainty based on the logarithmic standard deviations specified by the user.
#
# References: 
#--------------	
# Elkady, A. and D. G. Lignos (2015). "Effect of Gravity Framing on the Overstrength and Collapse Capacity of Steel
# 	 Frame Buildings with Perimeter Special Moment Frames." Earthquake Eng. & Structural Dynamics 44(8).
#
##################################################################################################################
#
# Input Arguments:
#------------------
# SpringID		Spring ID
# NodeI			Node i ID
# NodeJ			Node j ID
# Mp			Effective plastic strength of the gravity beam
# gap			Gap distance between beam end and column flange
# ResponseID	0 --> Bare Shear Connection
#				1 --> Composite Shear Connection
#				2 --> Composite Shear Connection with Stiffeneing due to Binding
#
# Written by: Dr. Ahmed Elkady, University of Southampton, UK
# 
##################################################################################################################

import openseespy.opensees as ops
def spring_pinching(
    spring_id: int, node_i: int, node_j: int,
    M_p: float, gap: float, response_id: int
) -> None:
    """
    Construct a rotational spring with deteriorating pinched response representing the moment-rotation
    behaviour of beams that are part of conventional shear-tab connections.
    Args:
        spring_id: Spring ID / Element Tag
        node_i: Node i ID
        node_j: Node j ID
        M_p: Effective plastic strength of the gravity beam
        gap: Gap distance between beam end and column flange
        response_id: 0 for Bare Shear Connection, 1 for Composite Shear Connection,
                        2 for Composite Shear Connection with Stiffening due to Binding
    """

    if response_id == 0:
        M_max_pos = 0.121 * M_p
        M_max_neg = 0.121 * M_p
        M1_P, M1_N = 0.521 * M_max_pos, -0.521 * M_max_neg
        M2_P, M2_N = 0.967 * M_max_pos, -0.967 * M_max_neg
        M3_P, M3_N = 1.000 * M_max_pos, -1.000 * M_max_neg
        M4_P, M4_N = 0.901 * M_max_pos, -0.901 * M_max_neg
        Th_1_P, Th_1_N = 0.0045, -0.0045
        Th_2_P, Th_2_N = 0.0465, -0.0465
        Th_3_P, Th_3_N = 0.0750, -0.0750
        Th_4_P, Th_4_N = 0.1000, -0.1000
        rDispP, rDispN = 0.57, 0.57
        rForceP, rForceN = 0.40, 0.40
        uForceP, uForceN = 0.05, 0.05
        gK1 = gD1 = gF1 = 0.0
        gK2 = gD2 = gF2 = 0.0
        gK3 = gD3 = gF3 = 0.0
        gK4 = gD4 = gF4 = 0.0
        gKLim, gDLim, gFLim = 0.2, 0.1, 0.0
        gE = 10.0
        dmgType = "energy"
        Th_U_P = gap + 0.000
        Th_U_N = -gap - 0.000

    elif response_id == 1:
        M_max_pos = 0.35 * M_p
        M_max_neg = 0.64 * 0.35 * M_p
        M1_P, M1_N = 0.250 * M_max_pos, -0.250 * M_max_pos
        M2_P, M2_N = 1.000 * M_max_pos, -1.000 * M_max_neg
        M3_P, M3_N = 1.001 * M_max_pos, -1.001 * M_max_neg
        M4_P, M4_N = 0.530 * M_max_pos, -0.540 * M_max_neg
        Th_1_P, Th_1_N = 0.0042, -0.0042
        Th_2_P, Th_2_N = 0.0200, -0.0110
        Th_3_P, Th_3_N = 0.0390, -0.0300
        Th_4_P, Th_4_N = 0.0400, -0.0550
        rDispP, rDispN = 0.40, 0.50
        rForceP, rForceN = 0.13, 0.53
        uForceP, uForceN = 0.01, 0.05
        gK1 = gD1 = gF1 = 0.0
        gK2 = gD2 = gF2 = 0.0
        gK3 = gD3 = gF3 = 0.0
        gK4 = gD4 = gF4 = 0.0
        gKLim, gDLim, gFLim = 0.30, 0.05, 0.05
        gE = 10.0
        dmgType = "energy"
        Th_U_P = gap + 0.000
        Th_U_N = -gap - 0.000

    elif response_id == 2:
        M_max_pos = 0.35 * M_p
        M_max_neg = 0.49 * 0.35 * M_p
        M1_P, M1_N = 0.250 * M_max_pos, -1.000 * M_max_neg
        M2_P, M2_N = 1.000 * M_max_pos, -1.001 * M_max_neg
        M3_P, M3_N = 1.001 * M_max_pos, -2.353 * M_max_neg
        M4_P, M4_N = 0.530 * M_max_pos, -2.350 * M_max_neg
        Th_1_P, Th_1_N = 0.0042, -0.0080
        Th_2_P, Th_2_N = 0.0200, -1.0 * gap
        Th_3_P, Th_3_N = 0.0390, -1.0 * gap - 0.015
        Th_4_P, Th_4_N = 0.0400, -1.0 * gap - 0.040
        rDispP, rDispN = 0.40, 0.50
        rForceP, rForceN = 0.13, 0.53
        uForceP, uForceN = 0.01, 0.05
        gK1 = gD1 = gF1 = 0.0
        gK2 = gD2 = gF2 = 0.0
        gK3 = gD3 = gF3 = 0.0
        gK4 = gD4 = gF4 = 0.0
        gKLim, gDLim, gFLim = 0.30, 0.05, 0.05
        gE = 10.0
        dmgType = "energy"
        Th_U_P = gap + 0.040
        Th_U_N = -gap - 0.040

    dummy_id = 12 * spring_id

    ops.uniaxialMaterial(
        'Pinching4', dummy_id,
        M1_P, Th_1_P, M2_P, Th_2_P, M3_P, Th_3_P, M4_P, Th_4_P,
        M1_N, Th_1_N, M2_N, Th_2_N, M3_N, Th_3_N, M4_N, Th_4_N,
        rDispP, rForceP, uForceP, rDispN, rForceN, uForceN,
        gK1, gK2, gK3, gK4, gKLim, gD1, gD2, gD3, gD4, gDLim,
        gF1, gF2, gF3, gF4, gFLim, gE, dmgType
    )

    ops.uniaxialMaterial('MinMax', spring_id, dummy_id, '-min', Th_U_N, '-max', Th_U_P)

    # Note: Requires material 99 to be defined previously
    ops.element('zeroLength', spring_id, node_i, node_j, '-mat', 99, 99, spring_id, '-dir', 1, 2, 6)

    if response_id == 2:
        # Stiffening Spring
        Esc = M_max_pos / Th_2_P
        My = 0.71 * M_max_pos
        eta = 0.0001
        damage = "damage"

        spring_id_2 = spring_id + 8
        dummy_id_2 = spring_id_2 + 1

        ops.uniaxialMaterial('ElasticPPGap', dummy_id_2, Esc, My, gap, eta, damage)
        ops.uniaxialMaterial('MinMax', spring_id_2, dummy_id_2, '-max', gap + 0.040)

        ops.element('zeroLength', spring_id_2, node_i, node_j, '-mat', 99, 99, spring_id_2, '-dir', 1, 2, 6)
