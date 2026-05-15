"""
Standardised opstool visualisation wrappers for OpenSeesPy models.

All functions write self-contained HTML files to output_dir so results
are portable and do not require a display server.

Set OPENSEES_HEADLESS=1 to suppress all output (e.g. in CI pipelines).

Compatible with opstool v0.8.7 (plotly backend saves to ModelVis.html in CWD).
"""

import os
import shutil
from pathlib import Path
import opstool as opst


def _headless() -> bool:
    """Return True when running in a headless / CI environment."""
    return os.getenv("OPENSEES_HEADLESS", "0") == "1"


_TMP_HTML = "ModelVis.html"


def _plot_and_save(output_dir: Path, filename: str, **kwargs) -> None:
    """Call plot_model(backend='plotly', …) and save the output.

    opstool v0.8.7 writes directly to ModelVis.html in CWD and returns None.
    We copy that file to the desired output path.
    """
    if _headless():
        return
    # Remove any previous temp file so we can detect a new one
    Path(_TMP_HTML).unlink(missing_ok=True)
    opst.vis.plot_model(backend="plotly", **kwargs)
    output_dir.mkdir(parents=True, exist_ok=True)
    src = Path(_TMP_HTML)
    if src.exists():
        shutil.copy2(str(src), str(output_dir / filename))
        src.unlink()
    else:
        print(f"Warning: {_TMP_HTML} not created by plot_model")


def vis_nodes(output_dir: Path, filename: str = "vis_01_nodes.html") -> None:
    """V1 — Render node positions and boundary conditions."""
    _plot_and_save(output_dir, filename,
                   show_node_label=True, show_ele_label=False)


def vis_model(
    output_dir: Path,
    filename: str = "vis_02_model.html",
    show_node_label: bool = True,
    show_ele_label: bool = True,
) -> None:
    """V2 — Render full undeformed model geometry (nodes + members)."""
    _plot_and_save(output_dir, filename,
                   show_node_label=show_node_label,
                   show_ele_label=show_ele_label)


def vis_loads(output_dir: Path, filename: str = "vis_03_loads.html") -> None:
    """V3 — Render applied load vectors superimposed on the geometry."""
    _plot_and_save(output_dir, filename,
                   show_load=True, show_node_label=False,
                   show_ele_label=False)


def vis_pre_analysis(output_dir: Path, filename: str = "vis_04_pre_analysis.html") -> None:
    """V4 — Full model + loads, final sanity check before solver runs."""
    _plot_and_save(output_dir, filename,
                   show_load=True, show_node_label=True,
                   show_ele_label=True)
