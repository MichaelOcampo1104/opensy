"""
Thin wrappers around opstool for standardised in-model visualisation.
All functions write self-contained HTML files to output_dir so results
are portable and do not require a display server.

Set OPENSEES_HEADLESS=1 to suppress all output (e.g. in CI pipelines).
"""

import os
from pathlib import Path
import opstool as opst

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
    
    # Corrected arguments: show_node_numbering instead of show_node_label
    fig = opst.vis.plotly.plot_model(show_node_numbering=True, show_ele_numbering=False)
    fig.write_html(str(output_dir / filename))

def vis_model(
    output_dir: Path,
    filename: str = "vis_02_model.html",
    show_node_numbering: bool = True,
    show_ele_numbering: bool = True,
) -> None:
    """V2 — Render full undeformed model geometry (nodes + members)."""
    if _headless():
        return
    
    fig = opst.vis.plotly.plot_model(
        show_node_numbering=show_node_numbering,
        show_ele_numbering=show_ele_numbering,
    )
    fig.write_html(str(output_dir / filename))

def vis_loads(output_dir: Path, filename: str = "vis_03_loads.html") -> None:
    """V3 — Render applied load vectors superimposed on the geometry."""
    if _headless():
        return
    
    fig = opst.vis.plotly.plot_model(show_nodal_loads=True, show_ele_loads=True)
    fig.write_html(str(output_dir / filename))

def vis_pre_analysis(
    output_dir: Path,
    filename: str = "vis_04_pre_analysis.html",
) -> None:
    """V4 — Full model + loads, final sanity check before solver runs."""
    if _headless():
        return
    
    fig = opst.vis.plotly.plot_model(
        show_node_numbering=True,
        show_ele_numbering=True,
        show_nodal_loads=True,
        show_ele_loads=True,
    )
    fig.write_html(str(output_dir / filename))

def vis_defo(
    output_dir: Path,
    filename: str = "vis_05_deformed.html",
    odb_tag: int = 1,
    resp_dof: str = "UX",
    scale: float = 10.0,
) -> None:
    """V5/V6 — Deformed shape coloured by total displacement magnitude."""
    if _headless():
        return
    
    # Handle minor API variations in the 1.0.x series for the scale parameter
    try:
        fig = opst.vis.plotly.plot_nodal_responses(
            odb_tag=odb_tag, 
            resp_type="disp", 
            resp_dof=resp_dof,
            defo_scale=scale  # Standard parameter in v1.0.26
        )
    except TypeError:
        fig = opst.vis.plotly.plot_nodal_responses(
            odb_tag=odb_tag, 
            resp_type="disp", 
            resp_dof=resp_dof,
            scale=scale      # Fallback for earlier 1.x versions
        )
        
    fig.write_html(str(output_dir / filename))
