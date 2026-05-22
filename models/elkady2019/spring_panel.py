import openseespy.opensees as ops

# ── HELPER: PANEL ZONE SPRING (SIMPLIFIED) ───────────────────────────────────
def spring_panel(
    p_elm: int, node_i: int, node_j: int, E: float, Fy: float, tp: float,
    d_col: float, d_beam: float, tf_col: float, bf_col: float, sh_panel: float,
    response_id: int, transf_tag: int
) -> None:
    """Construct a rotational spring with a trilinear hysteretic behavior (Panel Zone Spring).
    """
    # Floor Deck Parameters for Composite Action Consideration
    ts = 102.0    # Slab Thickness Above Rib [mm]
    trib = 89.0   # Steel Deck Rib Depth [mm]

    d_beam_p = d_beam + trib + ts - 0.5 * ts  # Effective Depth in Positive Moment
    d_beam_n = d_beam                         # Effective Depth in Negative Moment

    Vy = 0.55 * Fy * d_col * tp   # Yield Shear Force
    G = E / (2.0 * (1.0 + 0.30))  # Shear Modulus
    Ke = 0.95 * G * tp * d_col    # Elastic Shear Stiffness

    gamma1_y = Vy / Ke
    gamma2_y = 4.0 * gamma1_y
    gamma3_y = 100.0 * gamma1_y

    KpP = 0.95 * G * bf_col * (tf_col * tf_col) / d_beam_p  # Plastic Stiffness
    M1yP = gamma1_y * (Ke * d_beam_p)
    M2yP = M1yP + (KpP * d_beam_p) * (gamma2_y - gamma1_y)
    M3yP = M2yP + (sh_panel * Ke * d_beam_p) * (gamma3_y - gamma2_y)

    KpN = 0.95 * G * bf_col * (tf_col * tf_col) / d_beam_n  # Plastic Stiffness
    M1yN = gamma1_y * (Ke * d_beam_n)
    M2yN = M1yN + (KpN * d_beam_n) * (gamma2_y - gamma1_y)
    M3yN = M2yN + (sh_panel * Ke * d_beam_n) * (gamma3_y - gamma2_y)

    Th_U_P = 0.3
    Th_U_N = -0.3

    dummy_id = 12 * p_elm

    # Composite Interior Steel Panel Zone
    if response_id == 0:
        ops.uniaxialMaterial("Hysteretic", dummy_id, M1yP, gamma1_y, M2yP, gamma2_y, M3yP, gamma3_y,
                                -M1yP, -gamma1_y, -M2yP, -gamma2_y, -M3yP, -gamma3_y, 0.25, 0.75, 0.0, 0.0, 0.0)
        ops.uniaxialMaterial("MinMax", p_elm, dummy_id, "-min", Th_U_N, "-max", Th_U_P)

    # Composite Exterior Steel Panel Zone
    elif response_id == 1:
        ops.uniaxialMaterial("Hysteretic", dummy_id, M1yP, gamma1_y, M2yP, gamma2_y, M3yP, gamma3_y,
                                -M1yN, -gamma1_y, -M2yN, -gamma2_y, -M3yN, -gamma3_y, 0.25, 0.75, 0.0, 0.0, 0.0)
        ops.uniaxialMaterial("MinMax", p_elm, dummy_id, "-min", Th_U_N, "-max", Th_U_P)

    # Bare Steel Interior/Exterior Steel Panel Zone
    elif response_id == 2:
        ops.uniaxialMaterial("Hysteretic", dummy_id, M1yN, gamma1_y, M2yN, gamma2_y, M3yN, gamma3_y,
                                -M1yN, -gamma1_y, -M2yN, -gamma2_y, -M3yN, -gamma3_y, 0.25, 0.75, 0.0, 0.0, 0.0)
        ops.uniaxialMaterial("MinMax", p_elm, dummy_id, "-min", Th_U_N, "-max", Th_U_P)

    ops.element("zeroLength", p_elm, node_i, node_j, "-mat", p_elm, "-dir", 6)
