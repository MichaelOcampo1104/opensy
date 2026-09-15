"""Print + 3D-plot member local axes for the light P103 model.

Builds model_noballast_rhs100x50x19 (RHS100x50x1.9 + PFC 7/17), prints every
member's local x/y/z direction cosines (OpenSees CrdTransf convention, same
maths as model._member_udl_local), and writes an interactive 3D HTML with
opstool local-axis triads to the mm StructChecks figures folder.

Run with the opensy .venv.
"""
import sys
from pathlib import Path

import numpy as np
import openseespy.opensees as ops
import opstool as opst

_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parents[1] / "standards"))

import model as base  # noqa: E402 (shared geometry)
import model_noballast_rhs100x50x19 as L  # noqa: E402 (light sections)

FIG_DIR = Path(r"C:\Users\Michael Ocampo\Documents\mm\raw\python-scripts\StructChecks\p103-movable-platform\outputs\figures")
LOCAL_AXES_SCALE = 1.0  # opstool arm = mean member length / 5 x this (≈200 mm here)


def local_axes(mid):
    """(x, y, z) unit vectors of member mid's local axes in global coords."""
    j1, j2 = base.MEMBERS[mid]
    p1 = np.array(base.JOINTS_M[j1], dtype=float)
    p2 = np.array(base.JOINTS_M[j2], dtype=float)
    x = p2 - p1
    x = x / np.linalg.norm(x)
    vec = np.array([0.0, 0.0, 1.0]) if base.ELE_TRANS[mid] == base.TRANS_XZ \
        else np.array([1.0, 0.0, 0.0])
    z = vec - float(np.dot(vec, x)) * x
    z = z / np.linalg.norm(z)
    y = np.cross(z, x)
    return x, y, z


def main():
    L.build()
    print("member | joints | transf | local-x (along member) | "
          "local-y | local-z")
    for mid in sorted(base.MEMBERS):
        j1, j2 = base.MEMBERS[mid]
        x, y, z = local_axes(mid)
        t = "XZ" if base.ELE_TRANS[mid] == base.TRANS_XZ else "YZ"

        def f(v):
            return "(%+.3f,%+.3f,%+.3f)" % (v[0], v[1], v[2])
        sec = "PFC" if mid in L.OUTRIGGERS else "RHS1.9"
        print("m%2d %-4s %d->%-2d %s | x%s | y%s | z%s"
              % (mid, sec, j1, j2, t, f(x), f(y), f(z)))

    fig = opst.vis.plotly.plot_model(
        show_node_numbering=True, show_ele_numbering=True,
        show_bc=True, show_nodal_loads=False,
        show_local_axes=True, local_axes_scale=LOCAL_AXES_SCALE)
    fig.update_layout(
        title="P103 light RHS100x50x1.9 — OpenSees member local axes "
              "(x red along member, y green, z blue; arms %.0f mm; "
              "member tags = STAAD numbers)" % LOCAL_AXES_SCALE)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    html = FIG_DIR / "fig_model_local_axes_light_rhs100x50x19.html"
    fig.write_html(str(html))
    print("HTML written: %s" % html)


if __name__ == "__main__":
    main()
