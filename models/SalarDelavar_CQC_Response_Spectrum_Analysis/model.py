# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : 2D reinforced-concrete portal frame, one bay and one storey: two 3 m columns (400 x 400 mm) and a 5 m beam
           (300 x 400 mm), both bases fixed, elastic members with Ec = 4700 sqrt(fc). The seismic input is a given response
           spectrum in the X direction (no ground-motion record), with 5 % modal damping and CQC modal combination.
UniqueID : SalarDelavar_CQC_Response_Spectrum_Analysis
Author   : Salar Delavar Ghashghaei (GitHub salardelavar/OPENSEES_SALAR); converted to the standard layout
Date     : 2026-11-26
Purpose  : Response spectrum analysis of the frame, mode by mode: the periods and participation of the first two modes, the
           column base moment of each mode, and its CQC combination. The source's spectrum is used as a list and as a Path
           time series, and the source's own numbers are reproduced as written as a check.
Ref      : py_ref/RESPONSE_SPECTRUM_ANALYSIS.py (source), PLOT_2D.py (its PLOT_2D_FRAME is not called; vis_defo gives the
           deformed shape), COVER.png (figure). OpenSees command: https://openseespydoc.readthedocs.io/en/latest/src/responseSpectrumAnalysis.html
           Source: https://github.com/salardelavar/OPENSEES_SALAR/tree/main/CONCRETE_FRAME_EXAMPLES/CQC_RESPONSE_SPECTRUM_ANALYSIS/EXAMPLE_01
Units    : N, mm, MPa  (see standards/units.py)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import os
import sys
from pathlib import Path

import numpy as np
import openseespy.opensees as ops
import opstool as opst

# models/<UniqueID>/model.py -> repository root is parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "standards"))
from units import *  # noqa: E402,F403  (N, mm, sec, MPa, m)
from vis_utils import (  # noqa: E402
    vis_curves,
    vis_defo,
    vis_loads,
    vis_model,
    vis_nodes,
    vis_pre_analysis,
)

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
ODB_TAG_LIST = 1            # main analysis: spectrum as -Tn/-Sa lists (source TEST 02), one ODB step per mode
ODB_TAG_PATH = 2            # the same analysis with the spectrum as a Path time series (source TEST 01 input)
ODB_TAG_AS_WRITTEN = 3      # the source's numbers as written (mass 500000, Sa as numbers): reproduction check
NODE_BASE_L, NODE_BASE_R = 1, 2
NODE_TOP_L, NODE_TOP_R = 3, 4
SEC_COL, SEC_BEAM = 1, 2                  # Elastic column and beam sections
INTG_COL, INTG_BEAM = 1, 2                # Lobatto beam integration of the columns and of the beam
TRANSF_LIN = 1
ELE_COL_L, ELE_COL_R, ELE_BEAM = 1, 2, 3
TS_SPECTRUM = 1                           # Path time series of the spectrum (Tn as times, Sa as values)
RSA_DIR_X = 1                             # excited DOF: X (source direction = 1)
PT_COL_BASE = 1                           # integration point 1 of a column: its first node, the base
PT_BEAM_2 = 2                             # integration point 2 of the beam: 0.17 L from node 3 (source recorder section '2')
ROUTE_LIST = "list"
ROUTE_PATH = "path"

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# All lengths in mm, forces in N, stresses in MPa = N/mm², time in s
bay_width = 5000.0 * mm                   # beam span (source bay_width)
story_height = 3000.0 * mm                # column height (source story_height)
beam_width = 300.0 * mm                   # source Bb
beam_depth = 400.0 * mm                   # source Hb
col_width = 400.0 * mm                    # source Bc
col_depth = 400.0 * mm                    # source Hc

fc = 30.0 * MPa                           # concrete compressive strength (source fc)
ec = 4700.0 * np.sqrt(fc / MPa) * MPa     # Ec = 4700 sqrt(fc), fc in MPa (source formula)

num_modes = 2                             # source NUM_MODES
num_int_points = 5                        # Lobatto integration points per element (source beamIntegration ... 5)
damping_ratio = 0.05                      # modal damping ratio (source DAMPING_RATIO; dimensionless)

# Nodal mass at nodes 3 and 4 (X and Y). The source writes mass = 500000.0 with the label [kg]. In the N-mm-s system
# 1 N·s²/mm = 1000 kg (standards/units.py 'kg' is not 1 kg), so 500000 kg = 500 N·s²/mm (AGENT.md §12j).
mass_node_si = 500000.0 / 1000.0          # 500 N·s²/mm per node (converted)
mass_node_as_written = 500000.0           # the source's value taken as N·s²/mm: reproduction check only

# Given response spectrum (source Tn and Sa lists, 103 points). The source's Sa values are in m/s²: the plateau 4.903 is
# 0.5 g in m/s² (0.5 x 9.806). Its plot label says g, which is wrong. 1 m/s² = 1000 mm/s² (units.py: m / sec**2).
tn_s = [0.0, 0.06, 0.1, 0.12, 0.18, 0.24, 0.3, 0.36, 0.4, 0.42,
        0.48, 0.54, 0.6, 0.66, 0.72, 0.78, 0.84, 0.9, 0.96, 1.02,
        1.08, 1.14, 1.2, 1.26, 1.32, 1.38, 1.44, 1.5, 1.56, 1.62,
        1.68, 1.74, 1.8, 1.86, 1.92, 1.98, 2.04, 2.1, 2.16, 2.22,
        2.28, 2.34, 2.4, 2.46, 2.52, 2.58, 2.64, 2.7, 2.76, 2.82,
        2.88, 2.94, 3.0, 3.06, 3.12, 3.18, 3.24, 3.3, 3.36, 3.42,
        3.48, 3.54, 3.6, 3.66, 3.72, 3.78, 3.84, 3.9, 3.96, 4.02,
        4.08, 4.14, 4.2, 4.26, 4.32, 4.38, 4.44, 4.5, 4.56, 4.62,
        4.68, 4.74, 4.8, 4.86, 4.92, 4.98, 5.04, 5.1, 5.16, 5.22,
        5.28, 5.34, 5.4, 5.46, 5.52, 5.58, 5.64, 5.7, 5.76, 5.82,
        5.88, 5.94, 6.0]                  # periods [s]

sa_source_m_s2 = [1.9612, 3.72628, 4.903, 4.903, 4.903, 4.903, 4.903, 4.903, 4.903, 4.6696172,
                  4.0861602, 3.6321424, 3.2683398, 2.971218, 2.7241068, 2.5142584, 2.3348086, 2.1788932, 2.0425898, 1.9229566,
                  1.8160712, 1.7199724, 1.6346602, 1.5562122, 1.485609, 1.4208894, 1.3620534, 1.3071398, 1.2571292, 1.211041,
                  1.166914, 1.1267094, 1.0894466, 1.054145, 1.0217852, 0.990406, 0.960988, 0.9335312, 0.9080356, 0.8835206,
                  0.8599862, 0.838413, 0.8168398, 0.7972278, 0.7785964, 0.759965, 0.7432948, 0.7266246, 0.710935, 0.6952454,
                  0.6805364, 0.666808, 0.6540602, 0.6285646, 0.6040496, 0.5814958, 0.5609032, 0.5403106, 0.5206986, 0.5030478,
                  0.485397, 0.4697074, 0.4540178, 0.4393088, 0.4255804, 0.411852, 0.3991042, 0.3863564, 0.3755698, 0.3638026,
                  0.353016, 0.34321, 0.333404, 0.3245786, 0.3157532, 0.3069278, 0.2981024, 0.2902576, 0.2833934, 0.2755486,
                  0.2686844, 0.2618202, 0.254956, 0.2490724, 0.2431888, 0.2373052, 0.2314216, 0.2265186, 0.220635, 0.215732,
                  0.210829, 0.205926, 0.2020036, 0.1971006, 0.1931782, 0.1892558, 0.1853334, 0.181411, 0.1774886, 0.1735662,
                  0.1706244, 0.166702, 0.1637602]   # spectral acceleration as written [m/s²]
sa_mm_s2 = [sa * m / sec**2 for sa in sa_source_m_s2]   # the same values in mm/s² for OpenSees

# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    """Reset OpenSees and create a 2D model with 3 DOFs per node (source ops.model("basic", "-ndm", 2, "-ndf", 3))."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)


# ── 5. NODES AND SUPPORTS ────────────────────────────────────────────────────
def define_nodes_and_supports() -> None:
    """Corner nodes of the frame (source ops.node) and the fixed bases (source ops.fix)."""
    ops.node(NODE_BASE_L, 0.0 * mm, 0.0 * mm)
    ops.node(NODE_BASE_R, bay_width, 0.0 * mm)
    ops.node(NODE_TOP_L, 0.0 * mm, story_height)
    ops.node(NODE_TOP_R, bay_width, story_height)
    ops.fix(NODE_BASE_L, 1, 1, 1)
    ops.fix(NODE_BASE_R, 1, 1, 1)


def define_nodal_masses(mass: float) -> None:
    """Lumped masses at the two top nodes in X and Y, none in rotation (source ops.mass(3, ...) and ops.mass(4, ...)).

    Args:
        mass: Nodal mass in N·s²/mm (1 N·s²/mm = 1000 kg).
    """
    ops.mass(NODE_TOP_L, mass, mass, 0.0)
    ops.mass(NODE_TOP_R, mass, mass, 0.0)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
def section_properties() -> tuple:
    """Gross area and second moment of area of the column and of the beam (mm², mm⁴).

    Returns:
        (area_col, inertia_col, area_beam, inertia_beam).
    """
    area_col = col_width * col_depth
    inertia_col = col_width * col_depth**3 / 12
    area_beam = beam_width * beam_depth
    inertia_beam = beam_width * beam_depth**3 / 12
    return area_col, inertia_col, area_beam, inertia_beam


def define_sections() -> None:
    """Elastic column and beam sections with Ec = 4700 sqrt(fc) (source ops.section("Elastic", ...))."""
    area_col, inertia_col, area_beam, inertia_beam = section_properties()
    ops.section("Elastic", SEC_COL, ec, area_col, inertia_col)
    ops.section("Elastic", SEC_BEAM, ec, area_beam, inertia_beam)


# ── 7. ELEMENTS ──────────────────────────────────────────────────────────────
def define_elements() -> None:
    """Linear transformation, Lobatto integration and the two columns and the beam as forceBeamColumn elements (source)."""
    ops.geomTransf("Linear", TRANSF_LIN)
    ops.beamIntegration("Lobatto", INTG_COL, SEC_COL, num_int_points)
    ops.beamIntegration("Lobatto", INTG_BEAM, SEC_BEAM, num_int_points)
    ops.element("forceBeamColumn", ELE_COL_L, NODE_BASE_L, NODE_TOP_L, TRANSF_LIN, INTG_COL)
    ops.element("forceBeamColumn", ELE_COL_R, NODE_BASE_R, NODE_TOP_R, TRANSF_LIN, INTG_COL)
    ops.element("forceBeamColumn", ELE_BEAM, NODE_TOP_L, NODE_TOP_R, TRANSF_LIN, INTG_BEAM)


# ── 8. OUTPUT DATABASE (ODB) ─────────────────────────────────────────────────
def create_odb(odb_tag: int) -> "opst.post.CreateODB":
    """Nodal and frame responses of one response spectrum analysis, one step per mode. The model data are saved here.

    Args:
        odb_tag: Tag of this analysis (one ODB per analysis, because each analysis rebuilds the model).

    Returns:
        The CreateODB instance.
    """
    odb = opst.post.CreateODB(
        odb_tag=odb_tag,
        model_update=False,
        save_nodal_resp=True,
        save_frame_resp=True,
    )
    odb.save_model_data()
    return odb


# ── 9. LOADING (RESPONSE SPECTRUM INPUT) ─────────────────────────────────────
def define_spectrum(sa_values: list) -> None:
    """Path time series of the spectrum: periods as times, spectral accelerations as values (source ops.timeSeries).

    Args:
        sa_values: Spectral accelerations at the periods tn_s, in the units of the model (mm/s², or m/s² as written).
    """
    ops.timeSeries("Path", TS_SPECTRUM, "-time", *tn_s, "-values", *sa_values)


# ── 10. ANALYSIS ─────────────────────────────────────────────────────────────
def build_frame(mass: float, sa_values: list, output_dir: Path | None = None) -> None:
    """Build the frame, its nodal masses and its spectrum input. The visualisation stages V1 to V3 are written when
    output_dir is given.

    Args:
        mass: Nodal mass at nodes 3 and 4, in N·s²/mm.
        sa_values: Spectral accelerations of the spectrum input.
        output_dir: Folder for the V1 to V3 HTML files, or None to skip them.
    """
    init_model()
    define_nodes_and_supports()
    if output_dir is not None:
        vis_nodes(output_dir)                 # V1: nodes and supports
    define_sections()
    define_elements()
    if output_dir is not None:
        vis_model(output_dir)                 # V2: geometry
    define_nodal_masses(mass)
    define_spectrum(sa_values)
    if output_dir is not None:
        vis_loads(output_dir)                 # V3: the RSA input (no static load vectors in this analysis)


def run_modal_analysis(modal_report: Path | None) -> np.ndarray:
    """Eigenvalues lambda = omega² of the first modes (source ops.eigen) and the modal properties that the response spectrum
    command needs (source ops.modalProperties, written to modal_report when given).

    Args:
        modal_report: File for the modal report, or None to skip the file.

    Returns:
        Array of the first num_modes eigenvalues, in rad²/s².
    """
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    eigs = np.array(ops.eigen("-genBandArpack", num_modes))
    if modal_report is None:
        ops.modalProperties("-unorm")
    else:
        ops.modalProperties("-print", "-file", str(modal_report), "-unorm")
    return eigs


def run_rsa_modes(odb: "opst.post.CreateODB", sa_values: list, route: str) -> dict:
    """Response spectrum analysis of each mode in turn (source TEST 02 for the list route), with one ODB step per mode and
    the element responses read after each mode. The source's all-modes calls are not converted: they store no element
    response to read (see validate and the README notes).

    Args:
        odb: CreateODB of this analysis; fetch_response_step() is called after each mode.
        sa_values: Spectral accelerations at the periods tn_s, in the units of the model.
        route: ROUTE_LIST (spectrum as -Tn/-Sa lists) or ROUTE_PATH (spectrum as the Path time series).

    Returns:
        Dict of arrays over the modes: the column 1 base moment (N mm) and axial force (N), the global base force of
        column 1 (Fx, Fy, Mz), the base shear of both columns in X (N) and the beam moment at integration point 2 (N mm).
    """
    records = {"col_moment": [], "col_axial": [], "col_base_global": [], "base_shear_x": [], "beam_moment": []}
    for mode in range(1, num_modes + 1):
        if route == ROUTE_LIST:
            ops.responseSpectrumAnalysis(RSA_DIR_X, "-Tn", *tn_s, "-Sa", *sa_values, "-mode", mode)
        else:
            ops.responseSpectrumAnalysis(TS_SPECTRUM, RSA_DIR_X, "-mode", mode)
        odb.fetch_response_step()
        col_sec = ops.eleResponse(ELE_COL_L, "section", str(PT_COL_BASE), "force")
        beam_sec = ops.eleResponse(ELE_BEAM, "section", str(PT_BEAM_2), "force")
        col_l = ops.eleResponse(ELE_COL_L, "globalForce")
        col_r = ops.eleResponse(ELE_COL_R, "globalForce")
        records["col_moment"].append(col_sec[1])
        records["col_axial"].append(col_sec[0])
        records["col_base_global"].append(col_l[0:3])
        records["base_shear_x"].append(col_l[0] + col_r[0])
        records["beam_moment"].append(beam_sec[1])
    return {key: np.array(value) for key, value in records.items()}


def run_case(mass: float, sa_values: list, route: str, odb_tag: int, output_dir: Path | None = None) -> dict:
    """Build the frame, create its ODB, run the modal analysis and the response spectrum analysis mode by mode.

    Args:
        mass: Nodal mass at nodes 3 and 4, in N·s²/mm.
        sa_values: Spectral accelerations of the spectrum input.
        route: ROUTE_LIST or ROUTE_PATH.
        odb_tag: Tag of this analysis' ODB.
        output_dir: Folder for the figures and the modal report, or None for a check run.

    Returns:
        Dict with the eigenvalues ("eigs"), the CreateODB instance ("odb") and the per-mode records ("records").
    """
    build_frame(mass, sa_values, output_dir)
    odb = create_odb(odb_tag)
    modal_report = None if output_dir is None else output_dir / "SALAR_ModalReport.txt"
    eigs = run_modal_analysis(modal_report)
    if output_dir is not None:
        vis_pre_analysis(output_dir)          # V4: all definitions complete, before the response spectrum analysis
    records = run_rsa_modes(odb, sa_values, route)
    return {"eigs": eigs, "odb": odb, "records": records}


def run_analysis(output_dir: Path) -> dict:
    """Run the main analysis (SI reading, list route), the Path-route check and the as-written reproduction check.

    Args:
        output_dir: Folder for the ODB, figures and reports.

    Returns:
        Dict with the three runs under the keys "main", "path" and "as_written".
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))              # direct all ODB files to output/, before any CreateODB
    main = run_case(mass_node_si, sa_mm_s2, ROUTE_LIST, ODB_TAG_LIST, output_dir)
    ops.printModel("-JSON", "-file", str(output_dir / "RESPONSE_SPECTRUM_ANALYSIS.json"))   # the main model
    path = run_case(mass_node_si, sa_mm_s2, ROUTE_PATH, ODB_TAG_PATH)
    as_written = run_case(mass_node_as_written, sa_source_m_s2, ROUTE_LIST, ODB_TAG_AS_WRITTEN)
    return {"main": main, "path": path, "as_written": as_written}


# ── 11. POST-PROCESSING ──────────────────────────────────────────────────────
def cqc_rho(damp_i: float, damp_j: float, ratio: float) -> float:
    """CQC correlation coefficient of two modes, with the source's expression and the ratio passed in.

    Args:
        damp_i: Damping ratio of mode i.
        damp_j: Damping ratio of mode j.
        ratio: Ratio b of the two modes (see cqc_source and cqc_frequency_ratio).

    Returns:
        The correlation coefficient rho_ij.
    """
    num = 8.0 * np.sqrt(damp_i * damp_j) * (damp_i + ratio * damp_j) * ratio ** 1.5
    den = ((1.0 - ratio**2) ** 2 + 4.0 * damp_i * damp_j * ratio * (1.0 + ratio**2)
           + 4.0 * (damp_i**2 + damp_j**2) * ratio**2)
    return num / den


def cqc_source(mu: np.ndarray, lambdas: np.ndarray, dmp: list, scalf: list) -> float:
    """The source's CQC function. Its ratio is b_ij = lambda_i / lambda_j, a ratio of eigenvalues (omega²), not of
    frequencies (README note on the CQC coefficient).

    Args:
        mu: Modal responses.
        lambdas: Eigenvalues of the modes.
        dmp: Damping ratio of each mode.
        scalf: Scale factor of each mode.

    Returns:
        The combined response, sqrt(sum of rho_ij mu_i mu_j).
    """
    total = 0.0
    for i in range(len(lambdas)):
        for j in range(len(lambdas)):
            total += scalf[i] * mu[i] * scalf[j] * mu[j] * cqc_rho(dmp[i], dmp[j], lambdas[i] / lambdas[j])
    return float(np.sqrt(total))


def cqc_frequency_ratio(mu: np.ndarray, lambdas: np.ndarray, dmp: list) -> float:
    """CQC with the frequency ratio omega_j / omega_i = sqrt(lambda_j / lambda_i). Used as a check against cqc_source.

    Args:
        mu: Modal responses.
        lambdas: Eigenvalues of the modes.
        dmp: Damping ratio of each mode.

    Returns:
        The combined response.
    """
    total = 0.0
    for i in range(len(lambdas)):
        for j in range(len(lambdas)):
            total += mu[i] * mu[j] * cqc_rho(dmp[i], dmp[j], np.sqrt(lambdas[j] / lambdas[i]))
    return float(np.sqrt(total))


def plot_spectrum(output_dir: Path) -> None:
    """The source's response spectrum plot (source plt.plot and plt.show), as an interactive HTML file. Its values are the
    source's, in m/s².

    Args:
        output_dir: Folder where the HTML file is written.
    """
    vis_curves(
        output_dir,
        panels=[{"x": tn_s, "y": sa_source_m_s2, "xlabel": "Period T [s]", "ylabel": "Sa [m/s2]",
                 "title": "Given response spectrum"}],
        filename="vis_07_response_spectrum.html",
        title="Response spectrum (source values, m/s2)",
    )


def post_process(results: dict, output_dir: Path) -> None:
    """Flush the three ODBs to disk, then write the deformed-shape figure and the spectrum figure.

    Args:
        results: Output of run_analysis().
        output_dir: Folder where the ODB and HTML files are written.
    """
    for key in ("main", "path", "as_written"):
        results[key]["odb"].save_response()   # once per ODB, after its analysis
    vis_defo(output_dir, filename="vis_05_deformed_rsa.html", odb_tag=ODB_TAG_LIST, resp_dof="UX")
    plot_spectrum(output_dir)


# ── 12. VALIDATION (independent numpy calculations) ─────────────────────────
# The source's own run as written (OpenSeesPy 3.8.0): its printed eigenvalues, its printed TEST 02 column moment for mode 1,
# and the beam moment of mode 1 in its TEST 00 recorder file.
source_lambda_1 = 0.026907182725235932
source_lambda_2 = 2.4902529411301493
source_col_m1 = -156152547.504767
source_beam_m1 = 58580476.25042558


def element_global_stiffness(node_i: tuple, node_j: tuple, ea: float, ei: float) -> tuple:
    """Global 6 x 6 stiffness of an elastic 2D beam-column (Euler-Bernoulli, exact for the elastic forceBeamColumn here).

    Args:
        node_i: (x, y) of the first node.
        node_j: (x, y) of the second node.
        ea: Axial stiffness E A (N).
        ei: Flexural stiffness E I (N mm²).

    Returns:
        (global stiffness, local stiffness, transformation matrix).
    """
    dx = node_j[0] - node_i[0]
    dy = node_j[1] - node_i[1]
    length = float(np.hypot(dx, dy))
    c, s = dx / length, dy / length
    a = ea / length
    b = 12.0 * ei / length**3
    d = 6.0 * ei / length**2
    e = 4.0 * ei / length
    f = 2.0 * ei / length
    k_local = np.array([
        [a, 0.0, 0.0, -a, 0.0, 0.0],
        [0.0, b, d, 0.0, -b, d],
        [0.0, d, e, 0.0, -d, f],
        [-a, 0.0, 0.0, a, 0.0, 0.0],
        [0.0, -b, -d, 0.0, b, -d],
        [0.0, d, f, 0.0, -d, e],
    ])
    t = np.array([
        [c, s, 0.0, 0.0, 0.0, 0.0],
        [-s, c, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, c, s, 0.0],
        [0.0, 0.0, 0.0, -s, c, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
    ])
    return t.T @ k_local @ t, k_local, t


def assemble_frame_stiffness() -> tuple:
    """Global stiffness of the frame (DOFs ux, uy, rotation of nodes 1 to 4) and the global stiffness of each member.

    Returns:
        (12 x 12 global stiffness, dict of member global stiffnesses keyed by element tag).
    """
    coords = {NODE_BASE_L: (0.0, 0.0), NODE_BASE_R: (bay_width, 0.0),
              NODE_TOP_L: (0.0, story_height), NODE_TOP_R: (bay_width, story_height)}
    area_col, inertia_col, area_beam, inertia_beam = section_properties()
    members = {ELE_COL_L: (NODE_BASE_L, NODE_TOP_L, area_col, inertia_col),
               ELE_COL_R: (NODE_BASE_R, NODE_TOP_R, area_col, inertia_col),
               ELE_BEAM: (NODE_TOP_L, NODE_TOP_R, area_beam, inertia_beam)}
    k = np.zeros((12, 12))
    member_k = {}
    for ele, (node_i, node_j, area, inertia) in members.items():
        k_g, _, _ = element_global_stiffness(coords[node_i], coords[node_j], ec * area, ec * inertia)
        dofs = [3 * (node_i - 1) + d for d in range(3)] + [3 * (node_j - 1) + d for d in range(3)]
        k[np.ix_(dofs, dofs)] += k_g
        member_k[ele] = k_g
    return k, member_k


def numpy_modal_response(mass: float, sa_values: list) -> dict:
    """Independent modal response of the frame in X: condensed eigenproblem, participation, the modal static forces
    M phi Gamma Sa(T) solved on the full frame, and the base forces of the columns.

    Args:
        mass: Nodal mass at nodes 3 and 4, in N·s²/mm.
        sa_values: Spectral accelerations at the periods tn_s, in the units of the model.

    Returns:
        Dict with the eigenvalues ("lam"), periods ("t"), spectral accelerations at the periods ("sa"), participation
        factors ("gamma"), and per mode the column 1 base moment ("base_moment"), axial force ("base_axial") and the base
        shear of both columns in X ("base_shear").
    """
    k, member_k = assemble_frame_stiffness()
    kf = k[6:, 6:]                                  # free DOFs: nodes 3 and 4 (nodes 1 and 2 are fixed)
    trans, rot = [0, 1, 3, 4], [2, 5]               # ux3, uy3, ux4, uy4 | theta3, theta4 (no rotational mass)
    k_red = kf[np.ix_(trans, trans)] - kf[np.ix_(trans, rot)] @ np.linalg.solve(
        kf[np.ix_(rot, rot)], kf[np.ix_(rot, trans)])
    inv_sqrt_m = 1.0 / np.sqrt(mass)
    w2, v = np.linalg.eigh(k_red * inv_sqrt_m**2)  # equal masses: M^-1/2 K M^-1/2 = K / mass
    phi = v * inv_sqrt_m                            # mass-normalised eigenvectors: phi^T M phi = 1
    lam = w2[:num_modes]
    r = np.array([1.0, 0.0, 1.0, 0.0])              # influence vector of the X excitation
    gamma = phi[:, :num_modes].T @ (mass * r)
    t_n = 2.0 * np.pi / np.sqrt(lam)
    sa_n = np.interp(t_n, tn_s, sa_values)
    base_moment, base_axial, base_shear = [], [], []
    for n in range(num_modes):
        f = np.zeros(6)
        f[trans] = gamma[n] * sa_n[n] * mass * phi[:, n]
        u = np.linalg.solve(kf, f)
        f_col_l = member_k[ELE_COL_L] @ np.concatenate([np.zeros(3), u[0:3]])
        f_col_r = member_k[ELE_COL_R] @ np.concatenate([np.zeros(3), u[3:6]])
        base_moment.append(f_col_l[2])
        base_axial.append(f_col_l[1])
        base_shear.append(f_col_l[0] + f_col_r[0])
    return {"lam": lam, "t": t_n, "sa": sa_n, "gamma": gamma, "base_moment": np.array(base_moment),
            "base_axial": np.array(base_axial), "base_shear": np.array(base_shear)}


def all_modes_probe() -> dict:
    """Read the column 1 base moment after the source's all-modes calls (no -mode), with the Path and with the list.
    Those calls store no element response, so the source reads its per-mode values from a recorder that is not converted.

    Returns:
        Dict with the moment after the Path call ("path") and after the list call ("list"), N mm.
    """
    out = {}
    build_frame(mass_node_si, sa_mm_s2)
    run_modal_analysis(None)
    ops.responseSpectrumAnalysis(TS_SPECTRUM, RSA_DIR_X)
    out["path"] = ops.eleResponse(ELE_COL_L, "section", str(PT_COL_BASE), "force")[1]
    build_frame(mass_node_si, sa_mm_s2)
    run_modal_analysis(None)
    ops.responseSpectrumAnalysis(RSA_DIR_X, "-Tn", *tn_s, "-Sa", *sa_mm_s2)
    out["list"] = ops.eleResponse(ELE_COL_L, "section", str(PT_COL_BASE), "force")[1]
    return out


def check(report: list, name: str, value: float, reference: float, tol: float) -> bool:
    """Compare two values by relative difference and record the line in the report.

    Args:
        report: Report lines (appended to).
        name: Label of the check.
        value: Value from the model.
        reference: Independent or reference value.
        tol: Relative tolerance.

    Returns:
        True when the check passes.
    """
    rel = abs(value - reference) / max(abs(reference), 1.0e-300)
    ok = rel <= tol
    report.append(f"{'PASS' if ok else 'FAIL'}  {name}: {value:.10e} vs {reference:.10e} "
                  f"(relative {rel:.1e}, tolerance {tol:.0e})")
    return ok


def validate(results: dict, output_dir: Path) -> None:
    """Independent checks: numpy eigenvalues and modal response, base-shear equilibrium, the Path route, the CQC forms, the
    source's printed values reproduced as written, and the all-modes calls. Writes output/validation.txt and prints it.

    Args:
        results: Output of run_analysis().
        output_dir: Folder where validation.txt is written.
    """
    main, path, written = results["main"], results["path"], results["as_written"]
    m_si = main["records"]["col_moment"]
    ref = numpy_modal_response(mass_node_si, sa_mm_s2)
    ref_written = numpy_modal_response(mass_node_as_written, sa_source_m_s2)
    report, oks = [], []

    report.append("RESULTS (converted model, N-mm-s)")
    for n in range(num_modes):
        report.append(
            f"  mode {n + 1}: T = {ref['t'][n]:.6f} s, lambda = {main['eigs'][n]:.8g}, participation Gamma = {ref['gamma'][n]:.6f}, "
            f"Sa(T) = {ref['sa'][n]:.4f} mm/s2, column 1 base moment = {m_si[n]:.6e} N.mm, "
            f"axial = {main['records']['col_axial'][n]:.6e} N, base shear (both columns) = {main['records']['base_shear_x'][n]:.6e} N")
    cqc_src = cqc_source(m_si, main["eigs"], [damping_ratio] * num_modes, [1.0] * num_modes)
    cqc_frq = cqc_frequency_ratio(m_si, main["eigs"], [damping_ratio] * num_modes)
    report.append(f"  CQC of the column 1 base moment: source form {cqc_src:.10e} N.mm, frequency-ratio form {cqc_frq:.10e} N.mm")

    report.append("CHECKS")
    oks.append(check(report, "eigenvalue 1 vs numpy (SI)", main["eigs"][0], ref["lam"][0], 1.0e-8))
    oks.append(check(report, "eigenvalue 2 vs numpy (SI)", main["eigs"][1], ref["lam"][1], 1.0e-8))
    oks.append(check(report, "mode 1 column 1 base moment vs numpy, magnitude (SI)",
                     abs(m_si[0]), abs(ref["base_moment"][0]), 1.0e-7))
    oks.append(check(report, "mode 1 base shear (both columns) vs numpy, magnitude (SI)",
                     abs(main["records"]["base_shear_x"][0]), abs(ref["base_shear"][0]), 1.0e-7))
    oks.append(check(report, "mode 1 base shear = Gamma^2 Sa(T1) (equilibrium, SI)",
                     abs(main["records"]["base_shear_x"][0]), ref["gamma"][0] ** 2 * ref["sa"][0], 1.0e-7))
    gamma2_ok = abs(ref["gamma"][1]) < 1.0e-9 and abs(m_si[1]) < 1.0e-3
    oks.append(gamma2_ok)
    report.append(f"{'PASS' if gamma2_ok else 'FAIL'}  mode 2 has no X participation (Gamma = {ref['gamma'][1]:.2e}, "
                  f"moment = {m_si[1]:.2e} N.mm)")
    oks.append(check(report, "CQC source form vs |mode 1 moment| (mode 2 negligible)", cqc_src, abs(m_si[0]), 1.0e-7))
    oks.append(check(report, "CQC frequency-ratio form vs source form", cqc_frq, cqc_src, 1.0e-9))
    oks.append(check(report, "Path route = list route, mode 1 column moment",
                     path["records"]["col_moment"][0], m_si[0], 1.0e-9))
    oks.append(check(report, "Path route = list route, mode 1 beam moment",
                     path["records"]["beam_moment"][0], main["records"]["beam_moment"][0], 1.0e-9))
    oks.append(check(report, "as written: eigenvalue 1 vs source", written["eigs"][0], source_lambda_1, 1.0e-10))
    oks.append(check(report, "as written: eigenvalue 2 vs source", written["eigs"][1], source_lambda_2, 1.0e-10))
    oks.append(check(report, "as written: column 1 base moment, mode 1 vs source TEST 02",
                     written["records"]["col_moment"][0], source_col_m1, 1.0e-9))
    oks.append(check(report, "as written: beam moment, mode 1 vs source TEST 00 recorder",
                     written["records"]["beam_moment"][0], source_beam_m1, 1.0e-9))
    oks.append(check(report, "as written: numpy base moment vs OpenSees, magnitude",
                     abs(written["records"]["col_moment"][0]), abs(ref_written["base_moment"][0]), 1.0e-7))

    probe = all_modes_probe()
    report.append(f"INFO  all-modes calls (no -mode), column 1 moment read after the call: Path {probe['path']:.3e} N.mm, "
                  f"list {probe['list']:.3e} N.mm (no element response is stored by these calls)")
    report.append("RESULT: " + ("ALL CHECKS PASS" if all(oks) else "SOME CHECKS FAILED"))
    (output_dir / "validation.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    for line in report:
        print(line)


# ── 13. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(output_dir)                          # opstool's working files go to output/
    results = run_analysis(output_dir)
    post_process(results, output_dir)
    validate(results, output_dir)
