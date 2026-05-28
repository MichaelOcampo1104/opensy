##################################################################################################################
# Spring_IMK
#                                                                                       
# SubRoutine to construct a rotational spring representing the moment-rotation behaviour of steel beam-columns  
# and beams that are part of fully-restrained beam-to-column connections.                                                                 
#  
# The subroutine also considers modeling uncertainty based on the logarithmic standard deviations specified by the user.
#
# References: 
#--------------	
# Lignos, D. G. and H. Krawinkler (2011). "Deterioration Modeling of Steel Components in Support of Collapse 
# 	Prediction of Steel Moment Frames under Earthquake Loading." Journal of Structural Engineering 137(11).	
#
# Elkady, A. and D. G. Lignos (2014). "Modeling of the Composite Action in Fully Restrained Beam-to-Column
# 	Connections: ‎Implications in the Seismic Design and Collapse Capacity of Steel Special Moment Frames." 
# 	Earthquake Eng. & Structural Dynamics 43(13).
#
# Lignos, D. G., et al. (2019). "Proposed Updates to the ASCE 41 Nonlinear Modeling Parameters for Wide-Flange
#	 Steel Columns in Support of Performance-based Seismic Engineering." Journal of Structural Engineering 145(9).
#
##################################################################################################################
#
# Input Arguments:
#------------------
#  SpringID  			Spring ID
#  NodeI				Node i ID
#  NodeJ				Node j ID
#  E         			Young's modulus
#  Fy        			Yield stress
#  Ix        			Moment of inertia of section
#  d         			Section depth
#  htw        			Web slenderness ratio
#  bftf        			Flange slenderness ratio
#  L         			Member Length
#  Ls         			Shear Span
#  Lb        			Unbraced length
#  My        			Effective Yield Moment
#  PgPye        		Axial load ratio due to gravity
#  CompositeFlag		FLAG for Composite Action Consideration: 0 --> Ignore   Composite Effect   
# 															 	 1 --> Consider Composite Effect
#  ConnectionType		Type of Connection: 0 --> Reduced     Beam Section  
# 											1 --> Non-Reduced Beam Section    
# 											2 --> Column Section   
#  Units				Unsed Units: 1 --> millimeters and MPa     
#								 	 2 --> inches and ksi
#
# Written by: Dr. Ahmed Elkady, University of Southampton, UK
#
##################################################################################################################
import openseespy.opensees as ops

def spring_imk(
    spring_id: int, node_i: int, node_j: int,
    E: float, Fy: float, Ix: float, d: float, htw: float, bftf: float, ry: float,
    L: float, Ls: float, Lb: float, My: float, PgPye: float,
    composite_flag: int, connection_type: int
) -> None:
    """
    Construct a rotational spring representing the moment-rotation behaviour of steel beam-columns
    and beams that are part of fully-restrained beam-to-column connections.

    Args:
        spring_id: Spring ID / Element Tag
        node_i: Node i ID
        node_j: Node j ID
        E: Young's modulus
        Fy: Yield stress (MPa)
        Ix: Moment of inertia of section
        d: Section depth
        htw: Web slenderness ratio
        bftf: Flange slenderness ratio
        ry: Radius of gyration about y-axis
        L: Member Length
        Ls: Shear Span
        Lb: Unbraced length
        My: Effective Yield Moment
        PgPye: Axial load ratio due to gravity
        composite_flag: 0 to Ignore Composite Effect, 1 to Consider Composite Effect
        connection_type: 0 for Reduced Beam Section, 1 for Non-Reduced Beam Section, 2 for Column Section
    """
    n = 10.0

    # Unit conversion factors (assuming N, mm, MPa system)
    c1 = 1.0
    c2 = 1.0
    c3 = 25.4
    c4 = 1.0   # 1.0 assumes Fy is in MPa (matches Fy / 355 MPa)

    K = (n + 1.0) * 6.0 * E * Ix / L

    if connection_type == 0:
        # Rotational capacities calculated using Lignos and Krawinkler (2009) RBS equations
        theta_p = 0.19 * (htw**-0.314) * (bftf**-0.100) * ((Lb/ry)**-0.185) * ((Ls/d)**0.113) * ((c1 * d/533)**-0.760) * ((c2 * Fy * c4/355)**-0.070)
        theta_pc = 9.52 * (htw**-0.513) * (bftf**-0.863) * ((Lb/ry)**-0.108) * ((c2 * Fy * c4/355)**-0.360)
        Lmda = 585 * (htw**-1.140) * (bftf**-0.632) * ((Lb/ry)**-0.205) * ((c2 * Fy * c4/355)**-0.391)

        # FOR BARE STEEL BEAM
        if composite_flag == 0:
            MyPMy, MyNMy = 1.0, 1.0
            McMyP, McMyN = 1.1, 1.1

            theta_y = My / (6.0 * E * Ix / L)
            theta_p = theta_p - (McMyP - 1.0) * My / (6.0 * E * Ix / L)
            theta_pc = theta_pc + theta_y + (McMyP - 1.0) * My / (6.0 * E * Ix / L)

            theta_p_P = theta_p_N = theta_p
            theta_pc_P = theta_pc_N = theta_pc
            theta_u = 0.2

            D_P = D_N = 1.0
            Res_P = Res_N = 0.4
            c = 1.0

        # FOR COMPOSITE BEAM
        elif composite_flag != 0:
            MyPMy, MyNMy = 1.35, 1.25
            McMyP, McMyN = 1.30, 1.05

            theta_y = My / (6.0 * E * Ix / L)
            theta_p_p = theta_p - (McMyP - 1.0) * My / (6.0 * E * Ix / L)
            theta_p_n = theta_p - (McMyN - 1.0) * My / (6.0 * E * Ix / L)
            theta_pc_p = theta_pc + theta_y + (McMyP - 1.0) * My / (6.0 * E * Ix / L)
            theta_pc_n = theta_pc + theta_y + (McMyN - 1.0) * My / (6.0 * E * Ix / L)

            theta_p_P = 1.80 * theta_p_p
            theta_p_N = 0.95 * theta_p_n
            theta_pc_P = 1.35 * theta_pc_p
            theta_pc_N = 0.95 * theta_pc_n
            theta_u = 0.2

            D_P, D_N = 1.15, 1.0
            Res_P, Res_N = 0.3, 0.2
            c = 1.0

    elif connection_type == 1:
        # Rotational capacities calculated using Lignos and Krawinkler (2009) other-than-RBS equations
        if d > c3 * 21.0:
            theta_p = 0.318 * (htw**-0.550) * (bftf**-0.345) * ((Lb/ry)**-0.023) * ((Ls/d)**0.090) * ((c1 * d/533)**-0.330) * ((c2 * Fy * c4/355)**-0.130)
            theta_pc = 7.500 * (htw**-0.610) * (bftf**-0.710) * ((Lb/ry)**-0.110) * ((c1 * d/533)**-0.161) * ((c2 * Fy * c4/355)**-0.320)
            Lmda = 536 * (htw**-1.260) * (bftf**-0.525) * ((Lb/ry)**-0.130) * ((c2 * Fy * c4/355)**-0.291)
        else:
            theta_p = 0.0865 * (htw**-0.360) * (bftf**-0.140) * ((Ls/d)**0.340) * ((c1 * d/533)**-0.721) * ((c2 * Fy * c4/355)**-0.230)
            theta_pc = 5.6300 * (htw**-0.565) * (bftf**-0.800) * ((c1 * d/533)**-0.280) * ((c2 * Fy * c4/355)**-0.430)
            Lmda = 495 * (htw**-1.340) * (bftf**-0.595) * ((c2 * Fy * c4/355)**-0.360)

        # FOR BARE STEEL BEAM
        if composite_flag == 0:
            MyPMy, MyNMy = 1.0, 1.0
            McMyP, McMyN = 1.1, 1.1

            theta_y = My / (6.0 * E * Ix / L)
            theta_p = theta_p - (McMyP - 1.0) * My / (6.0 * E * Ix / L)
            theta_pc = theta_pc + theta_y + (McMyP - 1.0) * My / (6.0 * E * Ix / L)

            theta_p_P = theta_p_N = theta_p
            theta_pc_P = theta_pc_N = theta_pc
            theta_u = 0.2

            D_P = D_N = 1.0
            Res_P = Res_N = 0.4
            c = 1.0

        # FOR COMPOSITE BEAM
        elif composite_flag != 0:
            MyPMy, MyNMy = 1.35, 1.25
            McMyP, McMyN = 1.30, 1.05

            theta_y = My / (6.0 * E * Ix / L)
            theta_p_p = theta_p - (McMyP - 1.0) * My / (6.0 * E * Ix / L)
            theta_p_n = theta_p - (McMyN - 1.0) * My / (6.0 * E * Ix / L)
            theta_pc_p = theta_pc + theta_y + (McMyP - 1.0) * My / (6.0 * E * Ix / L)
            theta_pc_n = theta_pc + theta_y + (McMyN - 1.0) * My / (6.0 * E * Ix / L)

            theta_p_P = 1.80 * theta_p_p
            theta_p_N = 0.95 * theta_p_n
            theta_pc_P = 1.35 * theta_pc_p
            theta_pc_N = 0.95 * theta_pc_n
            theta_u = 0.2

            D_P, D_N = 1.15, 1.00
            Res_P, Res_N = 0.3, 0.2
            c = 1.0

    elif connection_type == 2:
        # Rotational capacities calculated using Lignos et al. (2019) column regression equations for monotonic
        theta_p = 294 * (htw**-1.700) * ((Lb/ry)**-0.700) * ((1.0 - PgPye)**1.600)
        theta_pc = 90 * (htw**-0.800) * ((Lb/ry)**-0.800) * ((1.0 - PgPye)**2.500)

        if theta_p > 0.20: theta_p = 0.2
        if theta_pc > 0.30: theta_pc = 0.3

        if PgPye <= 0.35:
            Lmda = 25500 * (htw**-2.140) * ((Lb/ry)**-0.530) * ((1.0 - PgPye)**4.920)
        else:
            Lmda = 268000 * (htw**-2.300) * ((Lb/ry)**-1.300) * ((1.0 - PgPye)**1.190)

        if PgPye <= 0.2:
            My = (1.15 / 1.1) * My * (1.0 - PgPye / 2.0)
        else:
            My = (1.15 / 1.1) * My * (9.0 / 8.0) * (1.0 - PgPye)

        McMy = 12.5 * (htw**-0.200) * ((Lb/ry)**-0.400) * ((1.0 - PgPye)**0.400)
        if McMy < 1.0: McMy = 1.0
        if McMy > 1.3: McMy = 1.3

        MyPMy, MyNMy = 1.0, 1.0
        McMyP = McMyN = McMy

        theta_y = My / (6.0 * E * Ix / L)
        theta_p = theta_p - (McMyP - 1.0) * My / (6.0 * E * Ix / L)
        theta_pc = theta_pc + theta_y + (McMyP - 1.0) * My / (6.0 * E * Ix / L)

        theta_p_P = theta_p_N = theta_p
        theta_pc_P = theta_pc_N = theta_pc
        theta_u = 0.15

        D_P = D_N = 1.0
        Res_P = Res_N = 0.5 - 0.4 * PgPye
        c = 1.0

    My_P = MyPMy * My
    My_N = MyNMy * My

    # Cyclic deterioration parameters
    if connection_type == 2:
        L_S = Lmda
        L_C = 0.9 * Lmda
        L_A = Lmda
        L_K = 0.9 * Lmda
    else:
        L_S = L_C = L_A = L_K = Lmda

    c_S = c_C = c_A = c_K = c

    # IMKBilin material model (updated version of the Bilin model)
    ops.uniaxialMaterial(
        'IMKBilin', spring_id, K,
        theta_p_P, theta_pc_P, theta_u, My_P, McMyP, Res_P,
        theta_p_N, theta_pc_N, theta_u, My_N, McMyN, Res_N,
        L_S, L_C, L_K, c_S, c_C, c_K, D_P, D_N
    )

    # Note: Requires material 99 to be defined previously
    ops.element('zeroLength', spring_id, node_i, node_j, '-mat', 99, 99, spring_id, '-dir', 1, 2, 6, '-doRayleigh', 1)
