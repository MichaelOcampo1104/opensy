#!/usr/bin/env python3
# ── 0. FILE HEADER ──────────────────────────────────────────────────────────────
"""
Post-process : ODB deformed-shape HTML + experimental vs. FEM comparison plots
Model       : XMU_Chapter9
Author      : Claude
Date        : 2026-06-17
Purpose     : Read ODB data for deformed-shape visualizations and generate
              time-history comparison plots of experimental vs. FEM node-4
              displacement from saved optimization results.
Units       : N, mm, MPa, s
"""

# ── 1. IMPORTS ───────────────────────────────────────────────────────────────────
import numpy as np
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[3] / "standards"))
from vis_utils import _headless

import opstool as opst
import matplotlib.pyplot as plt

# ── 2. PATHS ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR   = Path(__file__).parent
OUTPUT_DIR   = SCRIPT_DIR / "output"
EXP_PATH     = SCRIPT_DIR / "node4_exp.txt"
RESULTS_PATH = OUTPUT_DIR / "opt_results.json"
FEM_PATH     = OUTPUT_DIR / "node4_optimised.out"

FIGS_DIR = OUTPUT_DIR / "figures"
ODB_TAG  = 1


# ── ODB VISUALIZATION ────────────────────────────────────────────────────────────
def generate_odb_visualizations() -> None:
    """Generate deformed-shape HTML from saved ODB data.

    Requires that model.py has already run and populated output/ with ODB files.
    Safe to call standalone — skips if ODB data is missing.
    """
    if _headless():
        print("OPENSEES_HEADLESS=1 — skipping ODB visualization.")
        return

    opst.post.set_odb_path(str(OUTPUT_DIR))

    try:
        fig_peak = opst.vis.plotly.plot_nodal_responses(
            odb_tag=ODB_TAG, step="absMax", defo_scale=True,
            resp_type="disp", resp_dof="UX",
        )
        fig_peak.write_html(str(OUTPUT_DIR / "vis_05_deformed_peak.html"))
        print("  -> vis_05_deformed_peak.html")
    except Exception as e:
        print(f"  Peak deformed view skipped: {e}")

    try:
        fig_slider = opst.vis.plotly.plot_nodal_responses(
            odb_tag=ODB_TAG, slides=True, defo_scale=True,
            resp_type="disp", resp_dof="UX",
        )
        fig_slider.write_html(str(OUTPUT_DIR / "vis_06_deformed_slider.html"))
        print("  -> vis_06_deformed_slider.html")
    except Exception as e:
        print(f"  Slider view skipped: {e}")


# ── COMPARISON PLOTS ─────────────────────────────────────────────────────────────
def plot_comparison(
    t_exp: np.ndarray,
    u_exp: np.ndarray,
    t_fem: np.ndarray,
    u_fem: np.ndarray,
    save_path: Path,
) -> None:
    """Time-history comparison: experimental vs. FEM displacement."""
    FIGS_DIR.mkdir(parents=True, exist_ok=True)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    # Full time history
    ax1.plot(t_exp, u_exp, "k-", linewidth=1.0, alpha=0.7, label="Experimental")
    ax1.plot(t_fem, u_fem, "r--", linewidth=1.2, label="FEM (optimised)")
    ax1.set_ylabel("Displacement UX [mm]")
    ax1.set_title("XMU Chapter 9 — Node 4 Displacement: Experimental vs. FEM")
    ax1.legend(loc="upper right")
    ax1.grid(True, alpha=0.3)

    # Zoom: first 5 seconds
    mask = t_exp <= 5.0
    ax2.plot(t_exp[mask], u_exp[mask], "k-", linewidth=1.0, alpha=0.7, label="Experimental")
    ax2.plot(t_fem[mask], u_fem[mask], "r--", linewidth=1.2, label="FEM (optimised)")
    ax2.set_xlabel("Time [s]")
    ax2.set_ylabel("Displacement UX [mm]")
    ax2.set_title("First 5 s (zoom)")
    ax2.legend(loc="upper right")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(str(save_path), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Comparison plot saved to {save_path}")


def plot_error(
    t_exp: np.ndarray,
    u_exp: np.ndarray,
    t_fem: np.ndarray,
    u_fem: np.ndarray,
    save_path: Path,
) -> None:
    """Error (residual) time history."""
    n = min(len(u_exp), len(u_fem))
    error = u_exp[:n] - u_fem[:n]
    t = t_exp[:n] if len(t_exp) >= n else t_fem[:n]

    fig, ax = plt.subplots(figsize=(12, 3))
    ax.plot(t, error, "b-", linewidth=0.6, alpha=0.8)
    ax.axhline(y=0, color="k", linewidth=0.5, linestyle="--")
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Error (exp − FEM) [mm]")
    ax.set_title("XMU Chapter 9 — Displacement Residual")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(str(save_path), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Error plot saved to {save_path}")


def print_summary(result: dict, u_exp: np.ndarray, u_fem: np.ndarray) -> None:
    """Print a text summary of the optimisation result."""
    n = min(len(u_exp), len(u_fem))
    rmse = np.sqrt(np.mean((u_exp[:n] - u_fem[:n]) ** 2))
    max_err = np.max(np.abs(u_exp[:n] - u_fem[:n]))

    print(f"\n{'=' * 60}")
    print("XMU Chapter 9 — Optimisation Summary")
    print(f"{'=' * 60}")
    print(f"  E1      = {result['E1_MPa']:.2f} MPa")
    print(f"  fy1     = {result['fy1_MPa']:.6f} MPa")
    print(f"  b1      = {result['b1']:.6f}")
    print(f"  E2      = {result['E2_MPa']:.2f} MPa")
    print(f"  fy2     = {result['fy2_MPa']:.6f} MPa")
    print(f"  b2      = {result['b2']:.6f}")
    print(f"  F       = {result['F_final']:.6e}")
    print(f"  RMSE    = {rmse:.6e} mm")
    print(f"  Max err = {max_err:.6e} mm")
    print(f"  n_iter  = {result['nit']}")
    print(f"  Status  : {result['message']}")


# ── MAIN ─────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Load data
    if not RESULTS_PATH.exists():
        print(f"ERROR: {RESULTS_PATH} not found. Run model.py first.")
        raise SystemExit(1)

    with open(RESULTS_PATH) as f:
        opt_result = json.load(f)

    exp_data = np.loadtxt(EXP_PATH)
    t_exp = exp_data[:, 0]
    u_exp = exp_data[:, 1]

    fem_data = np.loadtxt(FEM_PATH)
    t_fem = fem_data[:, 0]
    u_fem = fem_data[:, 1]

    print_summary(opt_result, u_exp, u_fem)

    # Matplotlib comparison plots
    plot_comparison(
        t_exp, u_exp, t_fem, u_fem,
        FIGS_DIR / "vis_comparison.png",
    )

    plot_error(
        t_exp, u_exp, t_fem, u_fem,
        FIGS_DIR / "vis_error.png",
    )

    # ODB-based deformed-shape HTML
    print("\nGenerating ODB visualizations...")
    generate_odb_visualizations()

    print("\nDone.")
