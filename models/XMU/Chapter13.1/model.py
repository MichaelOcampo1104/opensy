# ── 0. FILE HEADER ──────────────────────────────────────────────────────────
"""
Model    : Train-bridge interaction (XMU Chapter 13.1)
UniqueID : XMU_Chapter13_1
Author   : XMU Finite Element Analysis course
Date     : 2026-06-22
Purpose  : 2D train-bridge interaction with WheelRail contact elements,
           rail irregularities, suspension system, and transient dynamics.
Ref      : XMU Finite Element Analysis course, Chapter 13.1.
Units    : m, kg, N, Pa, sec (SI — WheelRail element expects SI)
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────
import time
import openseespy.opensees as ops
import opstool as opst
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[3] / "standards"))
from vis_utils import _headless, vis_nodes, vis_model, vis_loads, vis_pre_analysis, vis_defo

# ── 2. TAG REGISTRY ──────────────────────────────────────────────────────────
MAT_RAIL_SPRING  = 101  # elastic bridge-rail connection
MAT_RAIL_DAMPER  = 201  # viscous bridge-rail damper
MAT_SUSP_PRIMARY = 801  # primary suspension spring (Kv1)
MAT_SUSP_SECONDARY = 802  # secondary suspension spring (Kv2)
MAT_DAMP_PRIMARY = 701  # primary suspension damper (Cv1)
MAT_DAMP_SECONDARY = 702  # secondary suspension damper (Cv2)

TRANSF_WHEELRAIL = 1
TRANSF_BEAM      = 2

TS_GRAVITY = 1
PAT_GRAVITY = 10

# ── 3. PARAMETERS ────────────────────────────────────────────────────────────
# Train parameters
pInitLocation = 10.0          # m (initial train X offset)
pDeltT = 0.001                # s (time step)
pVel   = 27.78                # m/s (train speed ~100 km/h)
pRWheel = 0.4575              # m (wheel radius)
pI     = 2.0 * 2.037e-5       # m^4 (wheel moment of inertia ×2)
pE     = 2.06e11              # Pa (steel modulus)
pA     = 77.45e-4             # m^2 (rail area)

# Bridge parameters
LenE  = 1.5                   # m (element length)
H     = 0.05                  # m (rail-to-bridge height)
Ec    = 2.943e9               # Pa (bridge concrete modulus)
AB    = 7.94                  # m^2 (bridge area)
IzB   = 2.88                  # m^4 (bridge moment of inertia)

# Rail parameters
AR      = 77.45e-4            # m^2
E_rail  = 2.06e11             # Pa
Iz_rail = 2.0 * 2.037e-5      # m^4

# Bridge-rail connection
Krb = 2.0 * 6.58e7            # N/m (spring stiffness)
Crb = 2.0 * 3.21e4            # N·s/m (damping)
Arb = H                       # m (connection length)

# Train suspension
Kv1 = 1.87e6                  # N/m (primary spring)
Cv1 = 5.0e5                   # N·s/m (primary damping)
Kv2 = 1.72e6                  # N/m (secondary spring)
Cv2 = 1.96e5                  # N·s/m (secondary damping)

Av1 = 0.2200                  # m^2 (primary spring area)
Av2 = 0.3000                  # m^2 (secondary spring area)

g = 9.801                     # m/s^2

# Train masses
Mt     = 5.2e4                # kg (car body)
JMt    = 2.31e6               # kg·m^2 (car body inertia)
Mb     = 3.2e3                # kg (bogie)
JMb    = 3.12e3               # kg·m^2 (bogie inertia)
MWheel = 1.4e3                # kg (wheel)

# Train beam properties
Ab  = 0.54                    # m^2 (bogie beam area)
Izb = 4.05e7                  # m^4 (bogie beam inertia)
At  = 8.4                     # m^2 (car body beam area)
Izt = 3.0e7                   # m^4 (car body beam inertia)

# Analysis
N_STATIC = 10
N_TRANSIENT = 3000

# Module-level state
_RAIL_NODES: list = []


# ── 4. MODEL INITIALISATION ──────────────────────────────────────────────────
def init_model() -> None:
    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 3)


# ── 5. MATERIALS ─────────────────────────────────────────────────────────────
def define_materials() -> None:
    # Bridge-rail connection
    ops.uniaxialMaterial("Elastic", MAT_RAIL_SPRING, Krb)
    ops.uniaxialMaterial("Viscous", MAT_RAIL_DAMPER, Crb, 1)
    # Train suspension
    ops.uniaxialMaterial("Elastic", MAT_SUSP_PRIMARY, Kv1)
    ops.uniaxialMaterial("Elastic", MAT_SUSP_SECONDARY, Kv2)
    ops.uniaxialMaterial("Viscous", MAT_DAMP_PRIMARY, Cv1, 1)
    ops.uniaxialMaterial("Viscous", MAT_DAMP_SECONDARY, Cv2, 1)


# ── 6. SECTIONS ──────────────────────────────────────────────────────────────
# Bridge section (Elastic)
def define_sections() -> None:
    ops.section("Elastic", 2, Ec, AB, IzB)


# ── 7. NODES ─────────────────────────────────────────────────────────────────
def build_nodes() -> None:
    global _RAIL_NODES
    _RAIL_NODES = []

    # Rail nodes 1-81 at y=H (0.05 m)
    for i in range(1, 82):
        ops.node(i, (i - 1) * LenE, H)
        _RAIL_NODES.append(i)

    # Bridge nodes 101-181 at y=0
    for i in range(101, 182):
        ops.node(i, (i - 101) * LenE, 0.0)


def build_train_nodes(pInitLocation: float) -> None:
    """Create train nodes (wheels, bogies, car body)."""
    ytranslation = 0.05 + pRWheel
    xtranslation = 10.25 + pInitLocation

    # Wheel nodes
    ops.node(2001, -10.25 + xtranslation, 0.0 + ytranslation)
    ops.node(2002, -7.75 + xtranslation, 0.0 + ytranslation)
    ops.node(2003, 7.75 + xtranslation, 0.0 + ytranslation)
    ops.node(2004, 10.25 + xtranslation, 0.0 + ytranslation)

    # Lower bogie nodes
    ops.node(2005, -10.25 + xtranslation, 0.22 + ytranslation)
    ops.node(2006, -9.00 + xtranslation, 0.22 + ytranslation)
    ops.node(2007, -7.75 + xtranslation, 0.22 + ytranslation)
    ops.node(2008, 7.75 + xtranslation, 0.22 + ytranslation)
    ops.node(2009, 9.00 + xtranslation, 0.22 + ytranslation)
    ops.node(2010, 10.25 + xtranslation, 0.22 + ytranslation)

    # Car body nodes
    ops.node(2011, -9.00 + xtranslation, 0.52 + ytranslation)
    ops.node(2012, 0.00 + xtranslation, 0.52 + ytranslation)
    ops.node(2013, 9.00 + xtranslation, 0.52 + ytranslation)


# ── 8. BOUNDARY CONDITIONS ───────────────────────────────────────────────────
def define_boundary_conditions() -> None:
    # Bridge base: nodes 101-130 and 152-181 fixed (fully)
    for n in range(101, 131):
        ops.fix(n, 1, 1, 1)
    for n in range(152, 182):
        ops.fix(n, 1, 1, 1)

    # Support ends: roller/pin
    ops.fix(131, 1, 1, 0)   # pin + free RZ
    ops.fix(151, 0, 1, 0)   # roller UX + fixed UY, free RZ

    # Rail ends: expansion/rotation constraint
    ops.fix(1, 1, 0, 1)     # fix UX, free UY, fix RZ
    ops.fix(81, 1, 0, 1)    # fix UX, free UY, fix RZ

    # Wheel constraints: free UY, fixed UX and RZ
    for n in [2001, 2002, 2003, 2004]:
        ops.fix(n, 1, 0, 1)

    # Bogie/car body elements: free UX, free UY, free RZ
    for n in range(2005, 2014):
        ops.fix(n, 1, 0, 0)

    # equalDOF for rotational coupling
    ops.equalDOF(2012, 2011, 3)
    ops.equalDOF(2012, 2013, 3)
    ops.equalDOF(2006, 2005, 3)
    ops.equalDOF(2006, 2007, 3)
    ops.equalDOF(2009, 2008, 3)
    ops.equalDOF(2009, 2010, 3)


# ── 9. ELEMENTS ──────────────────────────────────────────────────────────────
def build_bridge_elements() -> None:
    """Bridge elastic sections, rail + bridge beam elements, connection springs."""
    define_sections()

    # Bridge beams: dispBeamColumn with 5 IPs
    for i in range(131, 151):
        ops.element("dispBeamColumn", i, i, i + 1, 5, 2, TRANSF_BEAM,
                    "-mass", 1.2e4, "-cMass")

    # Rail beams: elasticBeamColumn
    for i in range(1, 81):
        ops.element("elasticBeamColumn", i, i, i + 1, AR, E_rail, Iz_rail,
                    TRANSF_BEAM, "-mass", 2.0 * 51.5, "-cMass")

    # Bridge-rail connection: truss springs and dampers
    for i in range(1, 82):
        ops.element("truss", 6000 + i, i, 100 + i, Arb, MAT_RAIL_SPRING)
        ops.element("truss", 7000 + i, i, 100 + i, Arb, MAT_RAIL_DAMPER)


def build_train_elements() -> None:
    """Train bogie/car body beams, suspension springs and dampers."""
    E = 2.06e11

    # Bogie beams
    ops.element("elasticBeamColumn", 2001, 2005, 2006, Ab, E, Izb, TRANSF_BEAM)
    ops.element("elasticBeamColumn", 2002, 2006, 2007, Ab, E, Izb, TRANSF_BEAM)
    ops.element("elasticBeamColumn", 2003, 2008, 2009, Ab, E, Izb, TRANSF_BEAM)
    ops.element("elasticBeamColumn", 2004, 2009, 2010, Ab, E, Izb, TRANSF_BEAM)

    # Car body beams
    ops.element("elasticBeamColumn", 2005, 2011, 2012, At, E, Izt, TRANSF_BEAM)
    ops.element("elasticBeamColumn", 2006, 2012, 2013, At, E, Izt, TRANSF_BEAM)

    # Primary suspension springs (wheelset → bogie)
    for tag, n1, n2 in [(2007, 2001, 2005), (2008, 2002, 2007),
                         (2009, 2003, 2008), (2010, 2004, 2010)]:
        ops.element("truss", tag, n1, n2, Av1, MAT_SUSP_PRIMARY)

    # Secondary suspension springs (bogie → car body)
    ops.element("truss", 2011, 2006, 2011, Av2, MAT_SUSP_SECONDARY)
    ops.element("truss", 2012, 2009, 2013, Av2, MAT_SUSP_SECONDARY)

    # Primary suspension dampers
    for tag, n1, n2 in [(2013, 2001, 2005), (2014, 2002, 2007),
                         (2015, 2003, 2008), (2016, 2004, 2010)]:
        ops.element("truss", tag, n1, n2, Av1, MAT_DAMP_PRIMARY)

    # Secondary suspension dampers
    ops.element("truss", 2017, 2006, 2011, Av2, MAT_DAMP_SECONDARY)
    ops.element("truss", 2018, 2009, 2013, Av2, MAT_DAMP_SECONDARY)


def build_wheelrail_elements(irreg_path: str) -> None:
    """Create WheelRail contact elements for each wheelset.

    NOTE: WheelRail is a custom element. If OpenSeesPy was not compiled with
    this element, the model will fail with 'element type WheelRail not found'.
    """
    locs = [pInitLocation + offset for offset in [0.0, 2.5, 17.5, 20.0]]
    wheel_nodes = [2001, 2002, 2003, 2004]

    for tag, loc, wn in zip(range(3001, 3005), locs, wheel_nodes):
        ops.element("WheelRail", tag, pDeltT, pVel, loc, wn, pRWheel,
                    pI, pE, pA, TRANSF_WHEELRAIL, 10,
                    *_RAIL_NODES, irreg_path)


# ── 10. OUTPUT DATABASE (ODB) ───────────────────────────────────────────────
def create_odb(output_dir: Path, odb_tag: int = 1) -> "opst.post.CreateODB":
    odb = opst.post.CreateODB(
        odb_tag=odb_tag,
        save_nodal_resp=True,
        save_truss_resp=False,
        node_tags=list(range(1, 82)) + list(range(101, 182)) + list(range(2001, 2014)),
    )
    odb.save_model_data()
    return odb


# ── 11. LOADING ──────────────────────────────────────────────────────────────
def define_gravity(train_node_loads: dict) -> None:
    """Define gravity load pattern for train nodes."""
    ops.timeSeries("Linear", TS_GRAVITY)
    ops.pattern("Plain", PAT_GRAVITY, TS_GRAVITY)
    for node, force in train_node_loads.items():
        ops.load(node, 0.0, force, 0.0)


# ── 12. ANALYSIS ─────────────────────────────────────────────────────────────
def run_analysis(output_dir: Path) -> "opst.post.CreateODB":
    output_dir.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(output_dir))

    init_model()
    define_materials()
    build_nodes()
    build_train_nodes(pInitLocation)
    define_boundary_conditions()
    vis_nodes(output_dir)
    build_bridge_elements()
    build_train_elements()
    irreg_path = str(Path(__file__).parent / "rail_Irreg.txt")
    build_wheelrail_elements(irreg_path)
    vis_model(output_dir)

    odb = create_odb(output_dir=output_dir, odb_tag=1)

    # Gravity loads on train
    train_node_loads = {
        2001: -MWheel * g, 2002: -MWheel * g,
        2003: -MWheel * g, 2004: -MWheel * g,
        2006: -Mb * g, 2009: -Mb * g,
        2012: -Mt * g,
    }
    define_gravity(train_node_loads)
    vis_loads(output_dir)
    vis_pre_analysis(output_dir)

    # Train masses
    for n in [2001, 2002, 2003, 2004]:
        ops.mass(n, MWheel, MWheel, 0.0)
    ops.mass(2006, Mb, Mb, JMb)
    ops.mass(2009, Mb, Mb, JMb)
    ops.mass(2012, Mt, Mt, JMt)

    # ── Phase 1: Static gravity ──
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.test("NormDispIncr", 1.0e-8, 100, 2)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", 0.1)
    ops.analysis("Static")

    for step in range(1, N_STATIC + 1):
        ok = ops.analyze(1)
        if ok != 0:
            print(f"WARNING: static analysis failed at step {step}")
            break
    print("Static gravity finished!")

    # Freeze gravity at t=0, reset analysis
    ops.loadConst("-time", 0.0)
    ops.wipeAnalysis()

    # ── Phase 2: Transient dynamics ──
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.test("NormDispIncr", 1.0e-8, 100, 2)
    ops.algorithm("Newton")
    ops.integrator("Newmark", 0.5, 0.25)
    ops.analysis("Transient")

    start_t = time.time()
    for step in range(1, N_TRANSIENT + 1):
        ok = ops.analyze(1, pDeltT)
        if ok != 0:
            print(f"WARNING: transient analysis failed at step {step}")
            break
        if step % 100 == 0:
            print(f"  transient step {step}/{N_TRANSIENT}")
        odb.fetch_response_step()
    elapsed = time.time() - start_t
    print(f"Over! ({elapsed:.2f}s, {step} steps)")

    odb.save_response()
    return odb


# ── 13. POST-PROCESSING ─────────────────────────────────────────────────────
def post_process(odb: "opst.post.CreateODB", output_dir: Path) -> None:
    if not _headless():
        vis_defo(output_dir, filename="vis_05_defo_lateral.html")


# ── 14. MAIN ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output_dir = Path(__file__).parent / "output"
    odb = run_analysis(output_dir)
    post_process(odb, output_dir)
