"""3D SLS deflection figure — P103 light config (RHS100x50x1.9 + PFC 7/17).

Builds the light-section SLS model (COMB 301: 1.0 DL + 1.0 LL, 0.525 kN/m on
23/24/25, no ballast), solves, and writes:
  - PNG (matplotlib 3D, no display server needed)
  - HTML (opstool interactive deformed shape)
to the mm StructChecks figures folder. Units on the figure are mm.

Run with the opensy .venv (has openseespy + opstool + matplotlib).
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
from units import kN_m  # noqa: E402

SEC_RHS = (555.6, 7.391e5, 2.511e5, 5.787e5)   # RHS100x50x1.9 theory
SEC_PFC = (1300.0, 2.080e6, 3.230e5, 2.259e4)  # CH100X50X10, unchanged
OUTRIGGERS = (7, 17)
GAM = 7.68e-5
W_LL = 0.525 * kN_m
TS, PAT, N_STEPS = 1, 2, 10
DEFO_SCALE = 20.0  # exaggeration for visibility; colours/labels are TRUE mm

FIG_DIR = Path(r"C:\Users\Michael Ocampo\Documents\mm\raw\python-scripts\StructChecks\p103-movable-platform\outputs\figures")
ODB_DIR = _HERE / "output" / "defo_light_sls"


def sec(mid):
    return SEC_PFC if mid in OUTRIGGERS else SEC_RHS


def member_udl(mid):
    w_dl = sec(mid)[0] * GAM
    if mid in (21, 22, 23, 24):
        w_dl += 0.15
    if mid in (5, 7, 17, 21, 23, 24, 25):
        w_dl += 0.03
    w_ll = W_LL if mid in (23, 24, 25) else 0.0
    return 1.0 * w_dl + 1.0 * w_ll


def build_and_solve():
    ODB_DIR.mkdir(parents=True, exist_ok=True)
    opst.post.set_odb_path(str(ODB_DIR))
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)
    for tag, (x, y, z) in base.JOINTS_M.items():
        ops.node(tag, x * base.m, y * base.m, z * base.m)
    ops.geomTransf("Linear", 1, 0.0, 0.0, 1.0)
    ops.geomTransf("Linear", 2, 1.0, 0.0, 0.0)
    for s in base.SUPPORT_NODES:
        ops.fix(s, 1, 1, 1, 0, 0, 0)
    for mid, (j1, j2) in base.MEMBERS.items():
        A, Is, Iw, J = sec(mid)
        ops.element("elasticBeamColumn", mid, j1, j2, A, base.E_STEEL_MOD,
                    base.G_STEEL_MOD, J, Iw, Is, base.ELE_TRANS[mid])
    odb = opst.post.CreateODB(odb_tag=1, save_nodal_resp=True,
                              node_tags=list(base.JOINTS_M),
                              save_frame_resp=True,
                              frame_tags=list(base.MEMBERS))
    odb.save_model_data()
    ops.timeSeries("Linear", TS)
    ops.pattern("Plain", PAT, TS)
    for mid in base.MEMBERS:
        w = member_udl(mid)
        wx, wy, wz = base._member_udl_local(mid, w)
        ops.eleLoad("-ele", mid, "-type", "-beamUniform", wy, wz, wx)
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.integrator("LoadControl", 1.0 / N_STEPS)
    ops.test("EnergyIncr", 1.0e-8, 100)
    ops.algorithm("Linear")
    ops.analysis("Static")
    for _ in range(N_STEPS):
        if ops.analyze(1) != 0:
            raise RuntimeError("solve failed")
        odb.fetch_response_step()
    odb.save_response()
    return odb


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    odb = build_and_solve()
    ops.reactions()
    disp = {n: np.array([float(ops.nodeDisp(n, i + 1)) for i in range(3)])
            for n in base.JOINTS_M}  # mm
    res = {n: float(np.linalg.norm(v)) for n, v in disp.items()}
    nmax = max(res, key=res.get)
    ux = {n: float(ops.nodeDisp(n, 1)) for n in base.JOINTS_M}
    uy = {n: float(ops.nodeDisp(n, 2)) for n in base.JOINTS_M}
    uz = {n: float(ops.nodeDisp(n, 3)) for n in base.JOINTS_M}
    print("max resultant %.3f mm at joint %d" % (res[nmax], nmax))
    print("max |UY| %.3f mm | max |UX| %.3f mm | max |UZ| %.3f mm"
          % (max(abs(v) for v in uy.values()),
             max(abs(v) for v in ux.values()),
             max(abs(v) for v in uz.values())))
    print("tip 24: UY %+.3f UZ %+.3f resultant %.3f mm"
          % (uy[24], uz[24], res[24]))

    # ── matplotlib 3D PNG (true mm colours, x20 exaggerated shape) ──
    P0 = {n: np.array(base.JOINTS_M[n]) * base.m for n in base.JOINTS_M}  # mm
    P1 = {n: P0[n] + disp[n] * DEFO_SCALE for n in base.JOINTS_M}
    fig = plt.figure(figsize=(16, 10))
    ax = fig.add_subplot(111, projection="3d")
    for mid, (j1, j2) in base.MEMBERS.items():
        a, b = P0[j1], P0[j2]
        ax.plot([a[0], b[0]], [a[1], b[1]], [a[2], b[2]], color="0.75", lw=1)
    vals = np.array([res[mid_j] for mid_j in []])  # unused
    import matplotlib.cm as cm
    import matplotlib.colors as mc
    vmax = max(res.values())
    norm = mc.Normalize(vmin=0.0, vmax=vmax if vmax > 0 else 1.0)
    cmap = cm.get_cmap("jet")
    for mid, (j1, j2) in base.MEMBERS.items():
        a, b = P1[j1], P1[j2]
        c = cmap(norm((res[j1] + res[j2]) / 2.0))
        ax.plot([a[0], b[0]], [a[1], b[1]], [a[2], b[2]], color=c, lw=2.5)
    xyz0 = np.array(list(P0.values()))
    ax.scatter(xyz0[:, 0], xyz0[:, 1], xyz0[:, 2], c="k", s=12)
    for s in base.SUPPORT_NODES:
        p = P0[s]
        ax.text(p[0], p[1], p[2], " %d: %.2fmm" % (s, res[s]), fontsize=7)
    # ── maximum-deflection callout: red star + Ux/Uy/Uz box at J<nmax> ──
    pmax = P1[nmax]
    ax.scatter([pmax[0]], [pmax[1]], [pmax[2]], c="red", s=120,
               marker="*", depthshade=False)
    ax.text(pmax[0], pmax[1], pmax[2],
            "  MAX J%d: res %.3f mm\n  Ux %+.3f  Uy %+.3f  Uz %+.3f mm"
            % (nmax, res[nmax], ux[nmax], uy[nmax], uz[nmax]),
            fontsize=9, color="darkred", weight="bold",
            bbox=dict(facecolor="white", edgecolor="darkred", boxstyle="round,pad=0.3"))
    sm = cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cb = fig.colorbar(sm, ax=ax, shrink=0.6, pad=0.08)
    cb.set_label("resultant displacement [mm, TRUE scale]")
    ax.set_xlabel("X [mm]")
    ax.set_ylabel("Y [mm]")
    ax.set_zlabel("Z [mm]")
    ax.set_title("P103 light config (RHS100x50x1.9, PFC 7/17) — SLS COMB 301 "
                 "(1.0DL+1.0LL 0.525kN/m, no ballast)\n"
                 "Deformed shape x%.0f exaggerated; colours/labels TRUE mm | "
                 "MAX J%d: res %.3f mm (Ux %+.3f, Uy %+.3f, Uz %+.3f mm)" %
                 (DEFO_SCALE, nmax, res[nmax], ux[nmax], uy[nmax], uz[nmax]))
    ax.view_init(elev=18, azim=-62)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    png = FIG_DIR / "fig_defo_3d_light_rhs100x50x19_sls301.png"
    fig.tight_layout()
    fig.savefig(str(png), dpi=150)
    print("PNG written: %s" % png)

    # ── opstool interactive HTML ──
    try:
        fig2 = opst.vis.plotly.plot_nodal_responses(
            odb_tag=1, resp_type="disp", resp_dof="UY",
            defo_scale=DEFO_SCALE, show_defo=True, show_undeformed=False)
        fig2.update_layout(
            title="P103 light RHS100x50x1.9 — SLS COMB301 deflection [mm] "
                  "(x%.0f exaggerated) | MAX J%d: res %.3f mm "
                  "(Ux %+.3f, Uy %+.3f, Uz %+.3f mm)"
                  % (DEFO_SCALE, nmax, res[nmax],
                     ux[nmax], uy[nmax], uz[nmax]))
        # 3D marker at the max-deflection joint (deformed position, same
        # x20 exaggeration as the shape) + fixed 2D callout box so the
        # values are visible without rotating the view.
        pm = P1[nmax]
        fig2.add_scatter3d(
            x=[pm[0]], y=[pm[1]], z=[pm[2]], mode="markers+text",
            marker=dict(size=7, color="red", symbol="diamond"),
            text=["MAX J%d: %.3f mm<br>Ux %+.3f Uy %+.3f Uz %+.3f mm"
                  % (nmax, res[nmax], ux[nmax], uy[nmax], uz[nmax])],
            textfont=dict(size=12, color="darkred"),
            textposition="top center",
            hoverinfo="skip", showlegend=False, name="max-defo")
        fig2.add_annotation(
            x=0.02, y=0.02, xref="paper", yref="paper",
            text="<b>MAX J%d</b>: res %.3f mm<br>Ux %+.3f mm<br>Uy %+.3f mm<br>Uz %+.3f mm"
                 % (nmax, res[nmax], ux[nmax], uy[nmax], uz[nmax]),
            showarrow=False, align="left",
            bordercolor="darkred", borderwidth=1,
            bgcolor="white", font=dict(size=12, color="darkred"))
        html = FIG_DIR / "fig_defo_3d_light_rhs100x50x19_sls301.html"
        fig2.write_html(str(html))
        print("HTML written: %s" % html)
    except Exception as e:
        print("opstool HTML failed: %r" % e)


if __name__ == "__main__":
    main()
