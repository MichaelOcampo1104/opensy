##################################################################################################################
# ConstructBrace.py
#
# SubRoutine to construct a 2D brace element between the 2 given points in a 2D/3D system (Z coordinates set to 0).
#
##################################################################################################################
#
# Input Arguments:
#------------------
# elelID 		Brace element ID
# NodeI 		Brace start node ID
# NodeJ			Brace end node ID
# numSeg		Number of segments along the brace length
# Initial_GI	Initial geometric imperfection ratio at brace mid-length
# nInt 			Number of integration point per segment
# Trans_tag 	Geometric transformation ID
#
# Written by: Dr. Ahmed Elkady, University of Southampton, UK
#
##################################################################################################################
import openseespy.opensees as ops
import math
from lognrmrand import generate_lognrmrand


def construct_brace(eleID, NodeI, NodeJ, secID, numSeg, Initial_GI, nInt, Trans_tag,
                   Sigma_GI=0.0, integrationTag=None):
    """
    Construct a bracing element with geometric imperfection using dispBeamColumn elements.

    Parameters
    ----------
    eleID        : int   - Base element ID (first element created is eleID+1, matching Tcl)
    NodeI        : int   - Start node ID
    NodeJ        : int   - End node ID
    secID        : int   - Section ID for beam integration
    numSeg       : int   - Number of segments (must be >= 1)
    Initial_GI   : float - Initial geometric imperfection ratio (e.g. 0.001 = L/1000)
    nInt         : int   - Number of integration points per element
    Trans_tag    : int   - Geometric transformation tag
    Sigma_GI     : float - Log-normal std dev for randomising GI (0.0 = deterministic)
    integrationTag : int - Unique tag for beamIntegration object.
                          Defaults to eleID to avoid collisions across multiple brace calls.

    Notes
    -----
    - Faithfully translated from the Tcl ConstructBrace proc.
    - zLocal = yLocal is preserved from the Tcl original (imperfection applied in both Y and Z).
    - If braces are not in the Z=0 plane, upgrade to 3D coordinate extraction (see comment below).
    """

    # ------------------------------------------------------------------
    # FIX 1: Sigma_GI is now a parameter instead of relying on a global.
    # FIX 2: integrationTag defaults to eleID, not secID, to avoid
    #         collisions when the same secID is reused across brace calls.
    # ------------------------------------------------------------------
    if integrationTag is None:
        integrationTag = eleID

    # ------------------------------------------------------------------
    # FIX 3: numSeg == 1 edge-case guard.
    # Tcl silently crashes here; we handle it gracefully.
    # ------------------------------------------------------------------
    if numSeg < 1:
        raise ValueError(f"numSeg must be >= 1, got {numSeg}")

    if numSeg == 1:
        # Single segment — no intermediate nodes needed.
        ops.beamIntegration('Lobatto', integrationTag, secID, nInt)
        ops.element('dispBeamColumn', eleID + 1, NodeI, NodeJ, Trans_tag, integrationTag)
        return eleID + 1  # return last element ID used

    # 1. Randomise geometric imperfection if requested
    if Initial_GI != 0.0:
        Initial_GI = generate_lognrmrand(Initial_GI, Sigma_GI)

    # 2. Pre-register beam integration (required in OpenSeesPy; Tcl uses inline string)
    ops.beamIntegration('Lobatto', integrationTag, secID, nInt)

    PI = math.pi

    # 3. Get coordinates of the brace end points
    #
    # NOTE: The Tcl original only reads X and Y (2D coordinates) even though it
    # creates 3D nodes. This is preserved here for fidelity.
    # If your model has braces that are NOT in the Z=0 plane, replace this block with:
    #
    #   X1, Y1, Z1 = ops.nodeCoord(NodeI, 1), ops.nodeCoord(NodeI, 2), ops.nodeCoord(NodeI, 3)
    #   X2, Y2, Z2 = ops.nodeCoord(NodeJ, 1), ops.nodeCoord(NodeJ, 2), ops.nodeCoord(NodeJ, 3)
    #   L  = math.sqrt((X2-X1)**2 + (Y2-Y1)**2 + (Z2-Z1)**2)
    #   ... and extend the rotation matrix to 3D.
    #
    X1 = ops.nodeCoord(NodeI, 1)
    Y1 = ops.nodeCoord(NodeI, 2)
    X2 = ops.nodeCoord(NodeJ, 1)
    Y2 = ops.nodeCoord(NodeJ, 2)

    # Base node ID for intermediate nodes (matches Tcl: 1000 * NodeI)
    base_nodeID = 1000 * NodeI

    # 4. Deduce brace length and direction cosines
    L   = math.sqrt((X2 - X1)**2 + (Y2 - Y1)**2)
    Cos = (X2 - X1) / L
    Sin = (Y2 - Y1) / L

    # 5. Generate intermediate nodes
    # Tcl: for i = 1 to numSeg-1  →  Python: range(1, numSeg)  ✅ equivalent
    for i in range(1, numSeg):
        nodeid = base_nodeID + i

        # Local coordinates (imperfection as sine half-wave)
        xLocal = (L / numSeg) * i
        yLocal = math.sin(PI * i / numSeg) * Initial_GI * L
        zLocal = yLocal  # Preserved from Tcl: imperfection applied equally in Y and Z

        # Rotate from local to global system (2D rotation matrix)
        xRotZ = xLocal * Cos - yLocal * Sin
        yRotZ = xLocal * Sin + yLocal * Cos
        zRotZ = zLocal

        xGlobal = X1 + xRotZ
        yGlobal = Y1 + yRotZ
        zGlobal = zRotZ

        # Define node in 3D space (matching Tcl's active 3D node command)
        ops.node(nodeid, xGlobal, yGlobal, zGlobal)

    # 6. Define elements
    # FIX 4: Start from eleID+1, matching Tcl exactly (eleID itself is reserved by caller).
    current_eleID = eleID + 1

    # First element: NodeI → first intermediate node
    ops.element('dispBeamColumn', current_eleID, NodeI, base_nodeID + 1,
                Trans_tag, integrationTag)

    # Internal elements: intermediate node to intermediate node
    # Tcl: for i = 1 to numSeg-2  →  Python: range(1, numSeg-1)  ✅ equivalent
    for i in range(1, numSeg - 1):
        current_eleID += 1
        iNode = base_nodeID + i
        jNode = base_nodeID + i + 1
        ops.element('dispBeamColumn', current_eleID, iNode, jNode,
                    Trans_tag, integrationTag)

    # Last element: last intermediate node → NodeJ
    # FIX 5: Tcl uses [expr $ElementID+1] as an expression; Python mutates then uses,
    #         both produce the same result. Using += 1 is cleaner and equivalent.
    current_eleID += 1
    ops.element('dispBeamColumn', current_eleID, base_nodeID + numSeg - 1, NodeJ,
                Trans_tag, integrationTag)

    # Return the last element ID used so the caller can continue numbering
    return current_eleID
