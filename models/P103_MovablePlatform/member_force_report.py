# ── 0. FILE HEADER ─────────────────────────────────────────────────────────────
"""
Model    : P103 movable platform — member force diagrams + tabulation
UniqueID : P103_MovablePlatform
Author   : Claude Code session
Date     : 2026-09-13
Purpose  : Internal force diagrams (axial, shear, torsion, bending) along every
           member, and a tabulated member-force schedule. ALL VALUES ARE FROM
           THE OPENSEES MODEL — STAAD values are not used anywhere in this
           report (STAAD appears only in the reaction cross-check line).
Ref      : runs on top of model_comb202.py, which imports the shared geometry
           from model.py. Case is selectable: `python member_force_report.py 202`
Units    : N, mm, N.mm  (see standards/units.py)

METHOD — internal force diagrams are computed ANALYTICALLY, not by re-meshing.
Each member is an elasticBeamColumn under a single uniform member load, so the
internal actions are closed-form along the member:

    axial  N(x)  = -(fA_x + wx.x)                       [tension positive]
    shear  Vy/Vz = -(fA_y + wy.x) / -(fA_z + wz.x)
    moment M(x)  = -( mA + (-x,0,0) x fA + (-x/2,0,0) x (w.x) )

where fA/mA are the LOCAL end force/moment applied TO the member at end A, and
(wx,wy,wz) is the local uniform load per unit length. These expressions are
exact for this element type (no discretisation error), and the script ASSERTS
the two boundary identities at x=0 and x=L against the element's own end
forces before reporting.

SIGN CONVENTION: N positive in tension; sagging bending moment positive;
V positive in the local +y / +z directions. Verified against the closed-form
simply-supported result M_mid = wL^2/8 (self-test in --selftest).

STAAD SHEAR-DEFORMATION NOTE (see README): this model is Euler-Bernoulli while
STAAD includes shear deformation. These diagrams are the OpenSees solution and
are internally consistent; they are NOT expected to match STAAD's member end
forces to within 3% (open item DQ-065 in the mm wiki).
"""

# ── 1. IMPORTS ─────────────────────────────────────────────────────────────────
import csv
import sys
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE))

import model as base               # noqa: E402
import model_comb202 as M          # noqa: E402
import openseespy.opensees as ops  # noqa: E402

# ── 3. PARAMETERS ──────────────────────────────────────────────────────────────
N_SAMPLES = 51                    # points along each member for the diagrams
COMPONENTS = ("N", "Vy", "Vz", "T", "My", "Mz")
COMP_LABEL = {
    "N": "Axial N  [N]  (+ tension)",
    "Vy": "Shear Vy  [N]  (local y)",
    "Vz": "Shear Vz  [N]  (local z)",
    "T": "Torsion T  [N&middot;mm]",
    "My": "Moment My  [N&middot;mm]",
    "Mz": "Moment Mz  [N&middot;mm]",
}


# ── 13. LOCAL FRAME & INTERNAL FORCES ──────────────────────────────────────────
def local_frame(mid: int):
    """Return (R, L) for member mid: R maps LOCAL -> GLOBAL (columns = local
    axes expressed in global coords), L is the member length [mm].

    Built with the same convention model.py uses for its geomTransf vecxz, so
    the local frame here is exactly the element's own local frame.
    """
    j1, j2 = base.MEMBERS[mid]
    p1 = np.array(base.JOINTS_M[j1], dtype=float) * 1000.0
    p2 = np.array(base.JOINTS_M[j2], dtype=float) * 1000.0
    x = p2 - p1
    L = float(np.linalg.norm(x))
    x = x / L
    vec = (np.array([0.0, 0.0, 1.0]) if base.ELE_TRANS[mid] == base.TRANS_XZ
           else np.array([1.0, 0.0, 0.0]))
    z = vec - float(np.dot(vec, x)) * x
    z = z / np.linalg.norm(z)
    y = np.cross(z, x)
    return np.column_stack([x, y, z]), L


def member_internal_forces(mid: int, case: str):
    """Sample the internal force diagram along member mid.

    Returns:
        dict with 'x' [mm] and one array per component in COMPONENTS, plus
        'fA','mA','fB','mB' (local end forces) and 'L'.
    """
    spec = M.LOAD_CASES[case]
    w = M.factored_udl(mid, spec["f_dl"], spec["f_ll"], spec["ll_mode"])
    wx, wy, wz = base._member_udl_local(mid, w)
    wvec = np.array([wx, wy, wz])

    R, L = local_frame(mid)
    v = np.array(ops.eleForce(mid))          # global end forces, 12 values
    fA, mA = R.T @ v[0:3], R.T @ v[3:6]
    fB, mB = R.T @ v[6:9], R.T @ v[9:12]

    x = np.linspace(0.0, L, N_SAMPLES)
    # internal actions = -1 x (resultant of everything to the LEFT of the cut)
    N = -(fA[0] + wx * x)
    Vy = -(fA[1] + wy * x)
    Vz = -(fA[2] + wz * x)

    T = np.empty_like(x)
    My = np.empty_like(x)
    Mz = np.empty_like(x)
    for i, xi in enumerate(x):
        m_left = (mA
                  + np.cross([-xi, 0.0, 0.0], fA)
                  + np.cross([-xi / 2.0, 0.0, 0.0], wvec * xi))
        T[i], My[i], Mz[i] = -m_left

    # boundary identities: at x=0 -> -fA/-mA ; at x=L -> fB/mB
    assert np.allclose([N[0], Vy[0], Vz[0]], -fA, atol=1e-6, rtol=1e-9)
    assert np.allclose([T[0], My[0], Mz[0]], -mA, atol=1e-6, rtol=1e-9)
    assert np.allclose([N[-1], Vy[-1], Vz[-1]], fB, atol=1e-6, rtol=1e-9)
    assert np.allclose([T[-1], My[-1], Mz[-1]], mB, atol=1e-6, rtol=1e-9)

    return {"x": x, "N": N, "Vy": Vy, "Vz": Vz, "T": T, "My": My, "Mz": Mz,
            "fA": fA, "mA": mA, "fB": fB, "mB": mB, "L": L, "w": w}


def self_test() -> None:
    """Closed-form check: a simply-supported span with UDL gives M_mid = wL^2/8."""
    ops.wipe()
    ops.model("BasicBuilder", "-ndm", 3, "-ndf", 6)
    ops.node(1, 0.0, 0.0, 0.0)
    ops.node(2, 1000.0, 0.0, 0.0)
    ops.geomTransf("Linear", 1, 0.0, 0.0, 1.0)
    ops.fix(1, 1, 1, 1, 1, 0, 0)          # simply supported about local z
    ops.fix(2, 0, 1, 1, 1, 0, 0)
    A, E, G, J, Iy, Iz = 4224.0, 200000.0, 76923.08, 8.177e6, 5.553e6, 5.553e6
    ops.element("elasticBeamColumn", 1, 1, 2, A, E, G, J, Iy, Iz, 1)
    w = 0.5                                # N/mm downward
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    ops.eleLoad("-ele", 1, "-type", "-beamUniform", -w, 0.0)
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.integrator("LoadControl", 1.0)
    ops.test("EnergyIncr", 1.0e-10, 100)
    ops.algorithm("Linear")
    ops.analysis("Static")
    assert ops.analyze(1) == 0
    v = np.array(ops.eleForce(1))
    L = 1000.0
    R = np.column_stack([[1, 0, 0], [0, 1, 0], [0, 0, 1]]).astype(float)
    fA, mA = R.T @ v[0:3], R.T @ v[3:6]
    xm = L / 2.0
    m_left = mA + np.cross([-xm, 0, 0], fA) + np.cross([-xm / 2, 0, 0],
                                                       np.array([0, -w, 0]) * xm)
    M_mid = -m_left[2]
    expect = w * L ** 2 / 8.0
    print(f"  self-test simply-supported span: M_mid = {M_mid:.6f} N.mm "
          f"vs wL^2/8 = {expect:.6f} N.mm  -> "
          f"{'OK' if abs(M_mid - expect) < 1e-6 else 'FAIL'}")
    assert abs(M_mid - expect) < 1e-6
    ops.wipe()


# ── 14. REPORT ─────────────────────────────────────────────────────────────────
def build_html(case: str, results: dict, diagrams: dict, out_path: Path,
               xcheck: str) -> None:
    mids = sorted(diagrams)

    # ── figure: one member at a time, 6 stacked diagrams, dropdown to switch ──
    fig = make_subplots(
        rows=6, cols=1, shared_xaxes=True, vertical_spacing=0.035,
        subplot_titles=[COMP_LABEL[c] for c in COMPONENTS])
    for i, mid in enumerate(mids):
        d = diagrams[mid]
        first = (i == 0)
        for r, comp in enumerate(COMPONENTS, start=1):
            fig.add_trace(
                go.Scatter(x=d["x"], y=d[comp], mode="lines",
                           name=f"M{mid} {comp}",
                           line=dict(width=2),
                           visible=first,
                           showlegend=False,
                           hovertemplate="x=%{x:.1f} mm<br>%{y:.3g}<extra></extra>"),
                row=r, col=1)
    buttons = []
    n_comp = len(COMPONENTS)
    for i, mid in enumerate(mids):
        vis = [False] * (len(mids) * n_comp)
        for r in range(n_comp):
            vis[i * n_comp + r] = True
        buttons.append(dict(
            label=f"Member {mid}",
            method="update",
            args=[{"visible": vis},
                  {"title": f"Internal force diagrams — member {mid} "
                            f"(joint {base.MEMBERS[mid][0]} &rarr; "
                            f"{base.MEMBERS[mid][1]}, L = "
                            f"{diagrams[mid]['L']:.1f} mm)"}]))
    for r in range(n_comp):
        fig.update_yaxes(title_text="", row=r, col=1)
    fig.update_xaxes(title_text="distance from joint A along member [mm]", row=6, col=1)
    fig.update_layout(
        height=1150, template="plotly_white",
        margin=dict(l=70, r=30, t=110, b=60),
        title=f"Internal force diagrams — member {mids[0]} "
              f"(joint {base.MEMBERS[mids[0]][0]} &rarr; "
              f"{base.MEMBERS[mids[0]][1]}, L = {diagrams[mids[0]]['L']:.1f} mm)",
        updatemenus=[dict(type="dropdown", buttons=buttons,
                          x=0.0, y=1.10, xanchor="left", yanchor="top",
                          showactive=True,
                          bgcolor="#ffffff", bordercolor="#888")])
    plot_html = fig.to_html(full_html=False, include_plotlyjs="cdn",
                            div_id="force-diagrams")

    # ── table 1: section actions at each end (consistent with the diagrams) ──
    rows1 = []
    for mid in mids:
        d = diagrams[mid]
        a, b = end_actions(d)
        cells = "".join(f"<td>{a[c]:,.1f}</td>" for c in COMPONENTS)
        cells += "".join(f"<td>{b[c]:,.1f}</td>" for c in COMPONENTS)
        rows1.append(
            f"<tr><td class='mono'>{mid}</td>"
            f"<td class='mono'>{base.MEMBERS[mid][0]}&rarr;{base.MEMBERS[mid][1]}</td>"
            f"<td>{d['L']:.1f}</td>{cells}</tr>")

    # ── table 2: extremes along each member ──
    rows2 = []
    for mid in mids:
        d = diagrams[mid]
        cells = []
        for comp in COMPONENTS:
            y = d[comp]
            i = int(np.argmax(np.abs(y)))
            cells.append(f"<td>{y[i]:,.1f}</td>"
                         f"<td class='mono'>{d['x'][i]:,.0f}</td>")
        rows2.append(f"<tr><td class='mono'>{mid}</td>"
                     f"<td>{d['L']:.1f}</td>" + "".join(cells) + "</tr>")

    head1 = ("<tr><th rowspan='2'>Mem</th><th rowspan='2'>Joints</th>"
             "<th rowspan='2'>L<br>[mm]</th>"
             "<th colspan='6'>Section actions at end A</th>"
             "<th colspan='6'>Section actions at end B</th></tr>"
             "<tr><th>N [N]</th><th>Vy [N]</th><th>Vz [N]</th>"
             "<th>T [N&middot;mm]</th><th>My [N&middot;mm]</th><th>Mz [N&middot;mm]</th>"
             "<th>N [N]</th><th>Vy [N]</th><th>Vz [N]</th>"
             "<th>T [N&middot;mm]</th><th>My [N&middot;mm]</th><th>Mz [N&middot;mm]</th></tr>")
    head2 = ("<tr><th rowspan='2'>Mem</th><th rowspan='2'>L<br>[mm]</th>"
             + "".join(f"<th colspan='2'>{c}</th>" for c in COMPONENTS) + "</tr><tr>"
             + "".join("<th>extreme</th><th>x [mm]</th>" for _ in COMPONENTS)
             + "</tr>")

    r = results
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>P103 Movable Platform — Member Force Report ({case})</title>
<style>
 body {{ font-family: -apple-system, Segoe UI, Roboto, sans-serif; margin: 24px 40px;
        color: #1a1a1a; max-width: 1500px; }}
 h1 {{ font-size: 22px; margin-bottom: 4px; }}
 h2 {{ font-size: 17px; margin-top: 32px; border-bottom: 2px solid #1F3864;
       padding-bottom: 4px; color: #1F3864; }}
 .sub {{ color: #555; font-size: 13px; margin-bottom: 18px; }}
 table {{ border-collapse: collapse; font-size: 12px; width: 100%; }}
 th, td {{ border: 1px solid #c8ccd4; padding: 4px 6px; text-align: right;
           white-space: nowrap; }}
 th {{ background: #1F3864; color: #fff; font-weight: 600; text-align: center; }}
 tbody tr:nth-child(even) {{ background: #f4f6fa; }}
 td.mono {{ font-family: Consolas, monospace; text-align: center; }}
 .note {{ background: #fff8e1; border-left: 4px solid #f0ad4e; padding: 10px 14px;
          font-size: 13px; margin: 16px 0; }}
 .ok {{ color: #1a7f37; font-weight: 600; }}
 .kv {{ font-size: 13px; }}
 .scroll {{ overflow-x: auto; }}
</style></head><body>

<h1>P103 Movable Platform — Member Force Report</h1>
<div class="sub">
  <b>Case:</b> {r['title']} &nbsp;|&nbsp;
  <b>Source:</b> OpenSeesPy model <code>model_comb202.py</code> (units N, mm, N&middot;mm)
  &nbsp;|&nbsp; <b>Generated:</b> 2026-09-13
</div>

<div class="note">
  <b>All values in this report are from the OpenSees model.</b> STAAD is used only for the
  reaction cross-check line below. Per the README, this model is Euler&ndash;Bernoulli while
  STAAD includes shear deformation, so these member forces are <i>not</i> expected to match
  STAAD's end forces (mm-wiki open item <b>DQ-065</b>).
</div>

<h2>1. Model &amp; counter-check summary</h2>
<table class="kv" style="width:auto">
<tr><th>Quantity</th><th>Value</th></tr>
<tr><td>Applied total vertical load</td><td>{r['applied_total_N']:,.1f} N</td></tr>
<tr><td>OpenSees line A (jts 1+6+7)</td><td>{r['opensees_line_A_N']:,.1f} N</td></tr>
<tr><td>OpenSees line B (jts 11+16+17)</td><td>{r['opensees_line_B_N']:,.1f} N</td></tr>
<tr><td>&Sigma;F<sub>y</sub> residual</td><td>{r['fy_residual_N']:+.3f} N</td></tr>
<tr><td>Uplift</td><td>{'none &mdash; all supports in compression' if not r['uplift'] else str(r['uplift'])}</td></tr>
<tr><td>vs STAAD (reactions only)</td><td>{xcheck}</td></tr>
</table>

<h2>2. Member force diagrams</h2>
<div class="sub">Use the dropdown to switch member. Six stacked diagrams: axial,
both shear components, torsion, and both bending components. Computed in closed form
from the element end forces plus the applied uniform load.</div>
{plot_html}

<h2>3. Member forces — section actions at each end</h2>
<div class="sub">Internal section actions at the two ends of each member, in the
member's local axes &mdash; the endpoints of the diagrams above. N positive = tension.
(These are section actions, not the raw element end forces: the element end force at
A relates as <code>action_A = &minus;f<sub>A</sub></code>; at B they coincide.
Both are the same OpenSees solution.)</div>
<div class="scroll"><table>{head1}<tbody>{''.join(rows1)}</tbody></table></div>

<h2>4. Extreme internal actions along each member</h2>
<div class="sub">Largest magnitude of each component over the member length, with its
position measured from joint A. For design, read the governing value and where it occurs.</div>
<div class="scroll"><table>{head2}<tbody>{''.join(rows2)}</tbody></table></div>

<h2>Notes</h2>
<ul class="kv">
<li>Internal forces are computed analytically (exact for a uniform-load elastic member);
     the script asserts the x=0 and x=L identities against the element's own end forces.</li>
<li>Sign convention: N positive in tension; sagging moment positive; V positive along the
     local +y / +z axes. Validated against the closed-form M<sub>mid</sub> = wL&sup2;/8.</li>
<li>Member local frames use the same vecxz convention as the model's geomTransf, so local
     axes here are the element's own axes.</li>
</ul>
</body></html>"""
    out_path.write_text(html, encoding="utf-8")


def end_actions(d: dict) -> tuple:
    """Section actions at end A (x=0) and end B (x=L) — what the diagrams show.

    NOTE these are SECTION ACTIONS, not raw element end forces. The element end
    force at A is the force applied TO the member from outside, and relates to
    the section action by  action_A = -fA  (likewise moments), while at B the
    two coincide: action_B = +fB. Quoting section actions at both ends keeps the
    tabulation consistent with the plotted diagrams and with the usual
    hogging/sagging reading of a bending moment diagram.
    """
    return ({c: float(d[c][0]) for c in COMPONENTS},
            {c: float(d[c][-1]) for c in COMPONENTS})


def write_csv(diagrams: dict, out_path: Path) -> None:
    """Wide CSV: section actions at each end + extremes along the member."""
    comps = COMPONENTS
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        wtr = csv.writer(fh)
        wtr.writerow(["member", "joint_A", "joint_B", "L_mm"]
                     + [f"A_{c}" for c in comps] + [f"B_{c}" for c in comps]
                     + [f"maxabs_{c}" for c in comps] + [f"x_{c}_mm" for c in comps]
                     + ["w_local_N_per_mm"])
        for mid in sorted(diagrams):
            d = diagrams[mid]
            a, b = end_actions(d)
            ex, xa = [], []
            for c in comps:
                i = int(np.argmax(np.abs(d[c])))
                ex.append(round(float(d[c][i]), 4))
                xa.append(round(float(d["x"][i]), 3))
            wtr.writerow([mid, base.MEMBERS[mid][0], base.MEMBERS[mid][1],
                          round(d["L"], 3)]
                         + [round(a[c], 4) for c in comps]
                         + [round(b[c], 4) for c in comps]
                         + ex + xa + [round(d["w"], 6)])


# ── 15. MAIN ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if "--selftest" in sys.argv:
        print("Running closed-form self-test ...")
        self_test()
        sys.exit(0)

    case = next((a for a in sys.argv[1:] if not a.startswith("-")), "202")
    out_dir = _HERE / "output" / f"comb{case}"
    odb, applied_total, applied_moment_b = M.run_analysis(case, out_dir)
    results = M.post_process(odb, out_dir, case, applied_total, applied_moment_b)

    print("\nSampling internal force diagrams ...")
    diagrams = {mid: member_internal_forces(mid, case)
                for mid in sorted(base.MEMBERS)}
    print(f"  {len(diagrams)} members x {N_SAMPLES} points; "
          f"boundary identities asserted at both ends of every member")

    xcheck = (f"line A {results['opensees_line_A_N']:.1f} vs "
              f"{results['staad_line_A_N']:.1f} N ({results['diff_line_A_pct']:.3f}%), "
              f"line B {results['opensees_line_B_N']:.1f} vs "
              f"{results['staad_line_B_N']:.1f} N ({results['diff_line_B_pct']:.3f}%)")

    html_path = out_dir / f"member_forces_comb{case}.html"
    csv_path = out_dir / f"member_forces_comb{case}.csv"
    build_html(case, results, diagrams, html_path, xcheck)
    write_csv(diagrams, csv_path)
    print(f"\nHTML report : {html_path}")
    print(f"CSV  table  : {csv_path}")
