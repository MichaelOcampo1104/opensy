##################################################################################################################
# Spring_PZ
#
# SubRoutine to construct a rotational spring with a trilinear hysteretic response representative of steel 
# panel zone response                                                            
#  
# The subroutine also considers modeling uncertainty based on the logarithmic standard deviations specified by the user.
#      
# References: 
#--------------	
# Elkady, A. and D. G. Lignos (2014). "Modeling of the Composite Action in Fully Restrained Beam-to-Column
# 	Connections: ‎Implications in the Seismic Design and Collapse Capacity of Steel Special Moment Frames." 
# 	Earthquake Eng. & Structural Dynamics 43(13).
#
# Skiadopoulos, A., Elkady, A. and D. G. Lignos (2020). "Proposed Panel Zone Model for Seismic Design of 
#   Steel Moment-Resisting Frames." ASCE Journal of Structural Engineering (under review). 
#
##################################################################################################################
#
# Input Arguments:                                                                               
#------------------
# P_Elm			Element ID
# NodeI			Node i ID
# NodeJ			Node j ID
# E				Young's Modulus
# mu			Poisson's Ratio
# fy			Expected Yield Stress
# tdp			Doubler Plate(s) Thickness
# d_Col			Column Depth
# d_Beam		Beam Depth
# tf_Col		Column Flange Thickness
# bf_Col		Column Flange Width
# tw_Col		Column Web Thickness
# Ic			Column second-moment-of-interia about the strong axis
# trib			Steel deck rib depth
# ts			Concrete slab depth above the rib
# Response_ID	ID for Panel Zone Response: 0 --> Interior Steel Panel Zone with Composite Action
#											1 --> Exterior Steel Panel Zone with Composite Action
#											2 --> Bare Steel Interior/Exterior Steel Panel Zone
# transfTag		Geometric Transformation ID
#                                                                                                      
# Written by: Dr. Ahmed Elkady, University of Southampton, UK
# 
########################################################################################################

import openseespy.opensees as ops
from lognrmrand import generate_lognrmrand

# ── HELPER: PANEL ZONE SPRING ────────────────────────────────────────────────
def spring_pz(
    p_elm: int, node_i: int, node_j: int, E: float, mu: float, fy: float,
    tw_col: float, tdp: float, d_col: float, d_beam: float, tf_col: float,
    bf_col: float, ix_col: float, trib: float, ts: float, response_id: int,
    transf_tag: int, sigma_pz: list = None
) -> None:
    """Construct a rotational spring with a trilinear hysteretic response
    representative of steel panel zone response.
    """
    tpz = tw_col + tdp  # total PZ thickness
    G = E / (2.0 * (1.0 + mu))  # Shear Modulus
    # Beam's effective depth
    if response_id == 2:
        d_beam_p = d_beam
    else:
        d_beam_p = d_beam + trib + 0.5 * ts  # Effective Depth in Positive Moment
    d_beam_n = d_beam  # Effective Depth in Negative Moment

    # Stiffness Calculation
    Ks = tpz * (d_col - tf_col) * G  # PZ Stiffness: Shear Contribution
    Kb = 12.0 * E * (ix_col + tdp * ((d_col - 2.0 * tf_col)**3) / 12.0) / (d_beam**3) * d_beam  # PZ Stiffness: Bending Contribution
    Ke = (Ks * Kb) / (Ks + Kb)  # PZ Stiffness: Total
    Ksf = 2.0 * (bf_col * tf_col) * G  # Flange Stiffness: Shear Contribution
    Kbf = 2.0 * 12.0 * E * bf_col * (tf_col**3) / 12.0 / (d_beam**3) * d_beam  # Flange Stiffness: Bending Contribution
    Kef = (Ksf * Kbf) / (Ksf + Kbf)  # Flange Stiffness: Total

    ay = (0.58 * Kef / Ke + 0.88) / (1.0 - Kef / Ke)

    aw_eff_4gamma = 1.10
    aw_eff_6gamma = 1.15

    af_eff_4gamma = 0.93 * Kef / Ke + 0.015
    af_eff_6gamma = 1.05 * Kef / Ke + 0.020

    Vy = 0.577 * fy * ay * (d_col - tf_col) * tpz  # Yield Shear Force
    Vp_4gamma = 0.577 * fy * (aw_eff_4gamma * (d_col - tf_col) * tpz + af_eff_4gamma * (bf_col - tw_col) * 2.0 * tf_col)  # Plastic Shear Force @ 4 gammaY
    Vp_6gamma = 0.577 * fy * (aw_eff_6gamma * (d_col - tf_col) * tpz + af_eff_6gamma * (bf_col - tw_col) * 2.0 * tf_col)  # Plastic Shear Force @ 6 gammaY

    # Random generation of backbone parameters based on assigned uncertainty
    if sigma_pz is not None and len(sigma_pz) >= 4:
        Ke = generate_lognrmrand(Ke, sigma_pz[0])
        Vy = generate_lognrmrand(Vy, sigma_pz[1])
        Vp_4gamma = max(1.01 * Vy, generate_lognrmrand(Vp_4gamma, sigma_pz[2]))
        Vp_6gamma = max(1.01 * Vp_4gamma, generate_lognrmrand(Vp_6gamma, sigma_pz[3]))

    gamma_y = Vy / Ke
    gamma4_y = 4.0 * gamma_y
    gamma6_y = 6.0 * gamma_y

    My_P = Vy * d_beam_p
    Mp_4gamma_P = Vp_4gamma * d_beam_p
    Mp_6gamma_P = Vp_6gamma * d_beam_p

    My_N = Vy * d_beam_n
    Mp_4gamma_N = Vp_4gamma * d_beam_n
    Mp_6gamma_N = Vp_6gamma * d_beam_n

    Slope_4to6gamma_y_P = (Mp_6gamma_P - Mp_4gamma_P) / (2.0 * gamma_y)
    Slope_4to6gamma_y_N = (Mp_6gamma_N - Mp_4gamma_N) / (2.0 * gamma_y)

    # Defining the 3 Points used to construct the trilinear backbone curve
    gamma1 = gamma_y
    gamma2 = gamma4_y
    gamma3 = 100.0 * gamma_y

    M1_P = My_P
    M2_P = Mp_4gamma_P
    M3_P = Mp_4gamma_P + Slope_4to6gamma_y_P * (100.0 * gamma_y - gamma4_y)

    M1_N = My_N
    M2_N = Mp_4gamma_N
    M3_N = Mp_4gamma_N + Slope_4to6gamma_y_N * (100.0 * gamma_y - gamma4_y)

    gammaU_P = 0.3
    gammaU_N = -0.3

    dummy_id = 12 * p_elm

    # Composite Interior Steel Panel Zone
    if response_id == 0:
        ops.uniaxialMaterial("Hysteretic", dummy_id, M1_P, gamma1, M2_P, gamma2, M3_P, gamma3,
                                -M1_P, -gamma1, -M2_P, -gamma2, -M3_P, -gamma3, 0.25, 0.75, 0.0, 0.0, 0.0)
        ops.uniaxialMaterial("MinMax", p_elm, dummy_id, "-min", gammaU_N, "-max", gammaU_P)

    # Composite Exterior Steel Panel Zone
    elif response_id == 1:
        ops.uniaxialMaterial("Hysteretic", dummy_id, M1_P, gamma1, M2_P, gamma2, M3_P, gamma3,
                                -M1_N, -gamma1, -M2_N, -gamma2, -M3_N, -gamma3, 0.25, 0.75, 0.0, 0.0, 0.0)
        ops.uniaxialMaterial("MinMax", p_elm, dummy_id, "-min", gammaU_N, "-max", gammaU_P)

    # Bare Steel Interior/Exterior Steel Panel Zone
    elif response_id == 2:
        ops.uniaxialMaterial("Hysteretic", dummy_id, M1_N, gamma1, M2_N, gamma2, M3_N, gamma3,
                                -M1_N, -gamma1, -M2_N, -gamma2, -M3_N, -gamma3, 0.25, 0.75, 0.0, 0.0, 0.0)
        ops.uniaxialMaterial("MinMax", p_elm, dummy_id, "-min", gammaU_N, "-max", gammaU_P)

    ops.element("zeroLength", p_elm, node_i, node_j, "-mat", p_elm, "-dir", 6)
