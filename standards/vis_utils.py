"""
Thin wrappers around opstool for standardised in-model visualisation.
All functions write self-contained HTML files to output_dir so results
are portable and do not require a display server.

Compatible with opstool >= 1.0 (post.CreateODB / vis.plotly API).

Set OPENSEES_HEADLESS=1 to suppress all output (e.g. in CI pipelines).
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

    fig = opst.vis.plotly.plot_model(
        show_node_numbering=True, show_ele_numbering=False,
        show_bc=True, show_nodal_loads=False,
    )
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

    fig = opst.vis.plotly.plot_model(
        show_node_numbering=show_node_label,
        show_ele_numbering=show_ele_label,
        show_bc=True, show_nodal_loads=False,
    )
    fig.write_html(str(output_dir / filename))


def vis_loads(output_dir: Path, filename: str = "vis_03_loads.html") -> None:
    """V3 — Render applied load vectors superimposed on the geometry."""
    if _headless():
        return

    fig = opst.vis.plotly.plot_model(
        show_node_numbering=False, show_ele_numbering=False,
        show_bc=True, show_nodal_loads=True,
    )
    fig.write_html(str(output_dir / filename))


def vis_pre_analysis(
    output_dir: Path,
    filename: str = "vis_04_pre_analysis.html",
) -> None:
    """V4 — Full model + loads, final sanity check before solver runs."""
    if _headless():
        return

    fig = opst.vis.plotly.plot_model(
        show_node_numbering=True, show_ele_numbering=True,
        show_bc=True, show_nodal_loads=True,
    )
    fig.write_html(str(output_dir / filename))


def vis_defo(
    output_dir: Path,
    filename: str = "vis_05_deformed.html",
    resp_dof: str = "disp",
    scale: float = 10.0,
) -> None:
    """V5/V6 — Deformed shape coloured by total displacement magnitude."""
    if _headless():
        return

    fig = opst.vis.plotly.plot_nodal_responses(
        odb_tag=1,
        resp_type="disp",
        defo_scale=scale,
        show_defo=True,
        show_undeformed=False,
    )
    fig.write_html(str(output_dir / filename))
