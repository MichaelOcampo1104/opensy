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
    odb_tag: int = 1,
    resp_dof: str | None = None,
    resp_type: str = "disp",
    scale: float = 10.0,
) -> None:
    """V5/V6 — Deformed shape coloured by displacement ($resp_dof or magnitude).

    Args:
        output_dir: Directory where the HTML file is written.
        filename: Output HTML filename.
        odb_tag: ODB tag to read responses from.
        resp_dof: DOF component for colour scale (e.g. ``"UX"``, ``"UY"``).
                  If None, colours by total displacement magnitude.
        resp_type: Response type — ``"disp"``, ``"vel"``, ``"accel"``, etc.
        scale: Deformation scale factor.
    """
    if _headless():
        return

    fig = opst.vis.plotly.plot_nodal_responses(
        odb_tag=odb_tag,
        resp_type=resp_type,
        resp_dof=resp_dof,
        defo_scale=scale,
        show_defo=True,
        show_undeformed=False,
    )
    fig.write_html(str(output_dir / filename))


def vis_anim(
    output_dir: Path,
    filename: str = "vis_07_animation.html",
    odb_tag: int = 1,
    framerate: int | None = None,
    defo_scale: float = 10.0,
    resp_type: str = "disp",
    resp_dof: tuple = ("UX", "UY", "UZ"),
    show_undeformed: bool = True,
    lazy_load: bool = False,
) -> None:
    """V7 — Animated deformed shape over all analysis steps.

    Uses opstool's built-in plot_nodal_responses_animation which returns a
    plotly Figure with frame-by-frame animation.  Output is a self-contained
    HTML file.

    Args:
        output_dir: Directory where the HTML file is written.
        filename: Output HTML filename.
        odb_tag: ODB tag to read responses from.
        framerate: Frames-per-second for the animation.
                   If None, defaults to ``n_steps / 10`` (10-second animation).
        defo_scale: Deformation scale factor.
        resp_type: Response type — ``"disp"``, ``"vel"``, ``"accel"``, etc.
        resp_dof: DOF components to colour by (e.g. ``("UX", "UY", "UZ")``).
        show_undeformed: Overlay undeformed wireframe for reference.
        lazy_load: If True, defer loading ODB data until playback starts
                   (better for large models with many steps).
    """
    if _headless():
        return

    fig = opst.vis.plotly.plot_nodal_responses_animation(
        odb_tag=odb_tag,
        framerate=framerate,
        defo_scale=defo_scale,
        resp_type=resp_type,
        resp_dof=resp_dof,
        show_undeformed=show_undeformed,
        lazy_load=lazy_load,
    )
    fig.write_html(str(output_dir / filename))
