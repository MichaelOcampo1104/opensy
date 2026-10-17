"""Build report figures for the L-bar walkway (opstool plotly HTML).

Figures (values labelled, converted units):
  01_loads         - model + UDL arrows, kN/m annotated per member
  02_sls_deformed  - SLS deformed shape, mm (UY, max/min shown)
  03_uls_moment    - ULS bending moment MZ, kN.m
  04_uls_shear     - ULS shear VY, kN
  05_uls_axial     - ULS axial N, kN

Output: <mm>/raw/calculation-reports/Temp_works/Walk Ways/
        2m L bars Walk way/figure/
Run: .venv python models/LbarWalkway2m/make_figures.py
"""

import sys
from pathlib import Path

import plotly.graph_objects as go
import opstool as opst

sys.path.insert(0, str(Path(__file__).parent))
from model import (run_analysis, post_process, member_w_values,
                   JOINTS_M, MEMBERS, F_DL, F_LL)

FIG_DIR = Path(r"C:\Users\Michael Ocampo\Documents\mm"
               r"\raw\calculation-reports\Temp_works\Walk Ways"
               r"\2m L bars Walk way\figure")


def _title(fig, text: str):
    fig.update_layout(title=dict(text=text, x=0.5, font=dict(size=16)))
    return fig


def build_figures(w_sls: dict, w_uls: dict) -> dict:
    """Build the five opstool report figures (requires odb tags
    'sls' and 'uls' to be loaded). Returns {key: fig}."""
    figs = {}
    # --- 01 loads (characteristic + factored, kN/m) ---
    fig = opst.vis.plotly.plot_model(
        show_node_numbering=True, show_ele_numbering=True,
        show_bc=True, show_nodal_loads=False, show_ele_loads=True,
        load_scale=1.0)
    mx, my, mz, mt = [], [], [], []
    for mid, (j1, j2) in MEMBERS.items():
        p1, p2 = JOINTS_M[j1], JOINTS_M[j2]
        mx.append((p1[0] + p2[0]) / 2.0 * 1000.0)
        my.append((p1[1] + p2[1]) / 2.0 * 1000.0 + 120.0)
        mz.append(0.0)
        mt.append(f"M{mid}: {w_sls[mid]:.3f} kN/m (SLS) / "
                  f"{w_uls[mid]:.3f} kN/m (ULS)")
    fig.add_trace(go.Scatter3d(x=mx, y=my, z=mz, mode="text", text=mt,
                               textfont=dict(size=13, color="red"),
                               showlegend=False))
    figs["01_loads_kn_per_m"] = _title(
        fig, "L-bar walkway 2 m - applied UDL (kN/m), -Y on members 1-2 "
             "+ selfweight all members")

    # --- 02 SLS deformed (mm) ---
    fig = opst.vis.plotly.plot_nodal_responses(
        odb_tag="sls", resp_type="disp", resp_dof="UY", defo_scale=True,
        show_defo=True, show_undeformed=True, unit_symbol="mm",
        unit_factor=1.0, show_max_min=True)
    figs["02_sls_deformed_mm"] = _title(
        fig, "L-bar walkway 2 m - SLS deformed shape, UY (mm)")

    # --- 03/04/05 ULS diagrams ---
    for stem, dof, unit, factor, name in [
            ("03_uls_moment", "MZ", "kN.m", 1.0e-6, "bending moment MZ"),
            ("04_uls_shear", "VY", "kN", 1.0e-3, "shear VY"),
            ("05_uls_axial", "N", "kN", 1.0e-3, "axial N")]:
        fig = opst.vis.plotly.plot_frame_responses(
            odb_tag="uls", resp_type="sectionForces", resp_dof=dof,
            step="absMax", show_values=True, unit_symbol=unit,
            unit_factor=factor, show_model=True)
        figs[stem] = _title(fig, f"L-bar walkway 2 m - ULS {name} ({unit})")
    return figs


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = Path(__file__).parent / "output"

    # --- SLS + ULS runs (odb tags "sls" / "uls") ---
    odb_sls, tot_sls = run_analysis(out, 1.0, 1.0, "sls", "SLS 1.0DL+1.0LL")
    post_process(odb_sls, out, tot_sls, "SLS 1.0DL+1.0LL", "sls", "sls")
    odb_uls, tot_uls = run_analysis(out, F_DL, F_LL, "uls",
                                    "ULS 1.35DL+1.5LL")
    post_process(odb_uls, out, tot_uls)

    w_sls = member_w_values(1.0, 1.0)    # N/mm == kN/m
    w_uls = member_w_values(F_DL, F_LL)  # N/mm == kN/m
    figs = build_figures(w_sls, w_uls)
    for stem, fig in figs.items():
        fig.write_html(str(FIG_DIR / f"{stem}.html"))
        print(f"wrote {stem}.html")
    print(f"figures in: {FIG_DIR}")


if __name__ == "__main__":
    main()
