"""
Plotting Utilities for OpenSeesPy
===================================
Consistent, publication-quality plots for FEM results.

Usage:
    from plot_utils import plot_deformed_shape, plot_pushover_curve
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")  # non-interactive backend — safe for scripts
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


# ── Style constants ───────────────────────────────────────────────────────────

COLORS = {
    "primary":    "#185FA5",   # blue — deflection, primary curves
    "secondary":  "#993556",   # burgundy — moments
    "tertiary":   "#3B6D11",   # green — shear
    "accent":     "#854F0B",   # amber — reactions / pressure
    "grid":       "#cccccc",
    "text":       "#333333",
    "text_light": "#777777",
    "bg":         "#f8f8f6",
}
FILL_ALPHA = 0.12


def _style_ax(ax, xlabel: str, ylabel: str, title: str):
    """Apply consistent styling to an axes object."""
    ax.set_facecolor(COLORS["bg"])
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(COLORS["grid"])
    ax.tick_params(colors="#555555", labelsize=9)
    ax.set_xlabel(xlabel, fontsize=9, color="#555555")
    ax.set_ylabel(ylabel, fontsize=9, color="#555555")
    ax.set_title(title, fontsize=10, fontweight="bold", color=COLORS["text"], pad=6)
    ax.axhline(0, color=COLORS["grid"], linewidth=0.8, zorder=0)


# ═══════════════════════════════════════════════════════════════════════════════
# BEAM RESULT PLOTS (deflection, moment, shear, reactions)
# ═══════════════════════════════════════════════════════════════════════════════


def plot_beam_results(
    x: np.ndarray,
    deflection_mm: np.ndarray,
    moment_kNm: np.ndarray,
    shear_kN: np.ndarray,
    reaction_kPa: np.ndarray | None = None,
    title: str = "Beam Analysis Results",
    info_text: str = "",
    save_path: str | None = None,
):
    """
    Four-panel plot: deflection, moment, shear, and (optionally) contact pressure.

    Args:
        x:              Position along beam (m).
        deflection_mm:  Vertical displacement (mm, positive downward).
        moment_kNm:     Bending moment (kN·m).
        shear_kN:       Shear force (kN).
        reaction_kPa:   Contact pressure or reaction (kPa), optional.
        title:          Overall figure title.
        info_text:      Parameter summary for bottom annotation.
        save_path:      If given, save figure to this path.
    """
    n_panels = 4 if reaction_kPa is not None else 3
    fig = plt.figure(figsize=(14, 4 * (n_panels // 2 + n_panels % 2)))
    fig.patch.set_facecolor(COLORS["bg"])
    gs = gridspec.GridSpec(
        (n_panels + 1) // 2, 2, figure=fig, hspace=0.42, wspace=0.32
    )

    # ── Deflection ────────────────────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(x, deflection_mm, color=COLORS["primary"], linewidth=2)
    ax1.fill_between(x, deflection_mm, 0, alpha=FILL_ALPHA, color=COLORS["primary"])
    ax1.invert_yaxis()
    _style_ax(ax1, "Position (m)", "Deflection (mm)", "Deflection Profile")
    ax1.set_xlim(x[0], x[-1])
    _annotate_peak(ax1, x, deflection_mm, COLORS["primary"], unit="mm", find_min=True)

    # ── Bending Moment ────────────────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(x, moment_kNm, color=COLORS["secondary"], linewidth=2)
    ax2.fill_between(x, moment_kNm, 0, alpha=FILL_ALPHA, color=COLORS["secondary"])
    _style_ax(ax2, "Position (m)", "Moment (kN·m)", "Bending Moment Diagram")
    ax2.set_xlim(x[0], x[-1])
    _annotate_peak(ax2, x, moment_kNm, COLORS["secondary"], unit="kN·m")

    # ── Shear Force ───────────────────────────────────────────────────────────
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.step(x, shear_kN, color=COLORS["tertiary"], linewidth=2, where="post")
    ax3.fill_between(
        x, shear_kN, 0, alpha=FILL_ALPHA, color=COLORS["tertiary"], step="post"
    )
    _style_ax(ax3, "Position (m)", "Shear (kN)", "Shear Force Diagram")
    ax3.set_xlim(x[0], x[-1])

    # ── Contact Pressure / Reaction ───────────────────────────────────────────
    if reaction_kPa is not None:
        ax4 = fig.add_subplot(gs[1, 1])
        ax4.plot(x, reaction_kPa, color=COLORS["accent"], linewidth=2)
        ax4.fill_between(x, reaction_kPa, 0, alpha=FILL_ALPHA, color=COLORS["accent"])
        _style_ax(ax4, "Position (m)", "Pressure (kPa)", "Contact Pressure")
        ax4.set_xlim(x[0], x[-1])
        _annotate_peak(ax4, x, reaction_kPa, COLORS["accent"], unit="kPa")

    # ── Title & info ──────────────────────────────────────────────────────────
    fig.text(
        0.5, 0.97, title,
        ha="center", va="top", fontsize=13, fontweight="bold", color=COLORS["text"],
    )
    if info_text:
        fig.text(
            0.5, 0.005, info_text,
            ha="center", va="bottom", fontsize=8,
            color=COLORS["text_light"], style="italic",
        )

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=COLORS["bg"])
        print(f"  📊 Plot saved → {save_path}")
    plt.close(fig)
    return fig


def _annotate_peak(ax, x, y, color, unit="", find_min=False):
    """Add a subtle annotation at the peak (or trough) of a curve."""
    if find_min:
        idx = np.argmin(y)
        val = y[idx]
    else:
        idx = np.argmax(np.abs(y))
        val = y[idx]

    ax.annotate(
        f"{val:.2f} {unit}",
        xy=(x[idx], val),
        xytext=(0, -14 if find_min else 10),
        textcoords="offset points",
        ha="center", fontsize=8, color=color,
        arrowprops=dict(arrowstyle="-", color=color, lw=0.8),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PUSHOVER CURVE
# ═══════════════════════════════════════════════════════════════════════════════


def plot_pushover_curve(
    disp: np.ndarray,
    base_shear: np.ndarray,
    disp_label: str = "Top Displacement (m)",
    shear_label: str = "Base Shear (kN)",
    title: str = "Pushover Curve",
    save_path: str | None = None,
):
    """Simple pushover capacity curve plot."""
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor(COLORS["bg"])
    ax.plot(disp, -base_shear, color=COLORS["primary"], linewidth=2)
    ax.fill_between(disp, -base_shear, 0, alpha=FILL_ALPHA, color=COLORS["primary"])
    _style_ax(ax, disp_label, shear_label, title)
    ax.grid(True, linestyle="dotted", alpha=0.5)

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=COLORS["bg"])
        print(f"  📊 Plot saved → {save_path}")
    plt.close(fig)
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# TIME HISTORY
# ═══════════════════════════════════════════════════════════════════════════════


def plot_time_history(
    time: np.ndarray,
    response: np.ndarray,
    ylabel: str = "Displacement (m)",
    title: str = "Time History Response",
    save_path: str | None = None,
):
    """Single-panel time history plot."""
    fig, ax = plt.subplots(figsize=(12, 4))
    fig.patch.set_facecolor(COLORS["bg"])
    ax.plot(time, response, color=COLORS["primary"], linewidth=0.8)
    _style_ax(ax, "Time (s)", ylabel, title)
    ax.set_xlim(time[0], time[-1])
    ax.grid(True, linestyle="dotted", alpha=0.3)

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=COLORS["bg"])
        print(f"  📊 Plot saved → {save_path}")
    plt.close(fig)
    return fig
