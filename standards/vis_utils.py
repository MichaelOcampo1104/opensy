"""
Thin wrappers around opstool for standardised in-model visualisation.
All functions write self-contained HTML files to output_dir so results
are portable and do not require a display server.

Set OPENSEES_HEADLESS=1 to suppress all output (e.g. in CI pipelines).

Usage example (mirrors the opstool pattern):
    fig = opst.vis.plotly.plot_model(show_ele_loads=True)
    fig.write_html("output/vis_03_loads.html")
"""

import os
from pathlib import Path
import opstool as opst


def _headless() -> bool:
    """Return True when running in a headless / CI environment."""
    return os.getenv("OPENSEES_HEADLESS", "0") == "1"


def vis_nodes(output_dir: Path, filename: str = "vis_01_nodes.html") -> None:
    """V1 — Render node positions and boundary conditions.

    Args:
        output_dir: Folder where the HTML file is written.
        filename: Output filename (default: vis_01_nodes.html).
    """
    if _headless():
        return
    fig = opst.vis.plotly.plot_model(
        show_node_numbering=True,
        show_ele_numbering=False,
    )
    fig.write_html(str(output_dir / filename))


def vis_model(
    output_dir: Path,
    filename: str = "vis_02_model.html",
    show_node_numbering: bool = True,
    show_ele_numbering: bool = True,
) -> None:
    """V2 — Render full undeformed model geometry (nodes + members).

    Args:
        output_dir: Folder where the HTML file is written.
        filename: Output filename (default: vis_02_model.html).
        show_node_numbering: Annotate node tags on the figure.
        show_ele_numbering: Annotate element tags on the figure.
    """
    if _headless():
        return
    fig = opst.vis.plotly.plot_model(
        show_node_numbering=show_node_numbering,
        show_ele_numbering=show_ele_numbering,
    )
    fig.write_html(str(output_dir / filename))


def vis_loads(output_dir: Path, filename: str = "vis_03_loads.html") -> None:
    """V3 — Render applied load vectors superimposed on the geometry.

    Args:
        output_dir: Folder where the HTML file is written.
        filename: Output filename (default: vis_03_loads.html).
    """
    if _headless():
        return
    fig = opst.vis.plotly.plot_model(
        show_ele_loads=True,
    )
    fig.write_html(str(output_dir / filename))


def vis_pre_analysis(
    output_dir: Path,
    filename: str = "vis_04_pre_analysis.html",
) -> None:
    """V4 — Full model + loads, final sanity check before solver runs.

    Args:
        output_dir: Folder where the HTML file is written.
        filename: Output filename (default: vis_04_pre_analysis.html).
    """
    if _headless():
        return
    fig = opst.vis.plotly.plot_model(
        show_ele_loads=True,
        show_node_numbering=True,
        show_ele_numbering=True,
    )
    fig.write_html(str(output_dir / filename))


def vis_defo(
    output_dir: Path,
    filename: str = "vis_05_deformed.html",
    odb_tag: int = 1,
    resp_dof: str = "UX",
    scale: float = 10.0,
) -> None:
    """V5/V6 — Deformed shape coloured by nodal response at end of analysis.

    Uses plot_nodal_responses (ODB-based) rather than plot_defo (live model state),
    so it can be called after the analysis loop has closed.

    Args:
        output_dir: Folder where the HTML file is written.
        filename: Output filename (default: vis_05_deformed.html).
        odb_tag: ODB tag to read responses from (default 1).
        resp_dof: Response DOF to colour by, e.g. "UX", "UY", "UZ" (default "UX").
                  Must be uppercase — opstool requires "UX"/"UY"/"UZ"/"RX"/"RY"/"RZ".
        scale: Displacement amplification factor for visualisation (default 10.0).
    """
    if _headless():
        return
    fig = opst.vis.plotly.plot_nodal_responses(
        odb_tag=odb_tag,
        resp_type="disp",
        resp_dof=resp_dof,
        scale=scale,
    )
    fig.write_html(str(output_dir / filename))
