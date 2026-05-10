"""
Standardised opstool visualisation wrappers for OpenSeesPy models.

All functions write self-contained HTML files to output_dir so results
are portable and do not require a display server.

Set OPENSEES_HEADLESS=1 to suppress all output (e.g. in CI pipelines).

Usage:
    fig = opst.vis.plot_model(show_load=True)
    fig.write_html("output/vis_03_loads.html")
"""

import os
from pathlib import Path
import opstool as opst


def _headless() -> bool:
    """Return True when running in a headless / CI environment."""
    return os.getenv("OPENSEES_HEADLESS", "0") == "1"


def vis_nodes(output_dir: Path, filename: str = "vis_01_nodes.html") -> None:
    """V1 — Render node positions and boundary conditions."""
    if _headless():
        return
    fig = opst.vis.plot_model(show_node_label=True, show_ele_label=False)
    fig.write_html(str(output_dir / filename))


def vis_model(
    output_dir: Path,
    filename: str = "vis_02_model.html",
    show_node_label: bool = True,
    show_ele_label: bool = True,
) -> None:
    """V2 — Render full undeformed model geometry (nodes + members)."""
    if _headless():
        return
    fig = opst.vis.plot_model(
        show_node_label=show_node_label, show_ele_label=show_ele_label
    )
    fig.write_html(str(output_dir / filename))


def vis_loads(output_dir: Path, filename: str = "vis_03_loads.html") -> None:
    """V3 — Render applied load vectors superimposed on the geometry."""
    if _headless():
        return
    fig = opst.vis.plot_model(
        show_load=True, show_node_label=False, show_ele_label=False
    )
    fig.write_html(str(output_dir / filename))


def vis_pre_analysis(output_dir: Path, filename: str = "vis_04_pre_analysis.html") -> None:
    """V4 — Full model + loads, final sanity check before solver runs."""
    if _headless():
        return
    fig = opst.vis.plot_model(
        show_load=True, show_node_label=True, show_ele_label=True
    )
    fig.write_html(str(output_dir / filename))
