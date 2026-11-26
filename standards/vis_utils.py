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
    include_plotlyjs: object = True,
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
        include_plotlyjs: True embeds the plotly library in the page; "directory" writes one plotly.min.js beside it.
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
    fig.write_html(str(output_dir / filename), include_plotlyjs=include_plotlyjs)


def vis_slider(
    output_dir: Path,
    filename: str = "vis_06_slider.html",
    odb_tag: int = 1,
    resp_dof: str | None = None,
    resp_type: str = "disp",
    scale: float = 10.0,
) -> None:
    """V6 — Step-slider deformed shape (one frame per collected ODB step).

    Renders a Plotly figure with a slider so the user can scrub through the
    collected analysis steps (peak and envelope are great, but a slider shows
    the *evolution* of the deformation). Uses ``plot_nodal_responses(slides=True)``.

    Args:
        output_dir: Directory where the HTML file is written.
        filename: Output HTML filename.
        odb_tag: ODB tag to read responses from.
        resp_dof: DOF component for colour scale (e.g. ``"UX"``).
                  If None, colours by total displacement magnitude.
        resp_type: Response type — ``"disp"``, ``"vel"``, ``"accel"``, etc.
        scale: Deformation scale factor.
    """
    if _headless():
        return

    fig = opst.vis.plotly.plot_nodal_responses(
        odb_tag=odb_tag,
        slides=True,
        defo_scale=scale,
        resp_type=resp_type,
        resp_dof=resp_dof,
    )
    fig.write_html(str(output_dir / filename))


def vis_curves(
    output_dir: Path,
    panels: list,
    filename: str = "vis_08_curves.html",
    title: str = "Pushover curves",
) -> None:
    """V8 — Force-displacement curves as interactive plotly panels, one panel per curve.

    Each panel is a dict with the keys ``x``, ``y``, ``xlabel``, ``ylabel`` and ``title``;
    ``x`` and ``y`` are arrays of equal length. The output is a self-contained HTML file.
    Curves are not in opstool, so this wrapper uses plotly directly.

    Args:
        output_dir: Directory where the HTML file is written.
        panels: List of panel dicts, one per curve (left to right).
        filename: Output HTML filename.
        title: Figure title shown above the panels.
    """
    if _headless():
        return

    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    fig = make_subplots(
        rows=1, cols=len(panels),
        subplot_titles=[p["title"] for p in panels],
        horizontal_spacing=0.08,
    )
    for col, p in enumerate(panels, start=1):
        fig.add_trace(
            go.Scatter(
                x=p["x"], y=p["y"], mode="lines", name=p["title"],
                line=dict(color="#185FA5", width=3),
                hovertemplate=f"{p['xlabel']}: %{{x:.4g}}<br>{p['ylabel']}: %{{y:.4g}}<extra></extra>",
            ),
            row=1, col=col,
        )
        fig.update_xaxes(title_text=p["xlabel"], row=1, col=col)
        fig.update_yaxes(title_text=p["ylabel"], row=1, col=col)
    fig.update_layout(
        template="plotly_white", showlegend=False, height=480, width=1400,
        title_text=title, margin=dict(l=70, r=30, t=90, b=70),
    )
    fig.write_html(str(output_dir / filename))


def vis_pushover_animation(
    output_dir: Path,
    history: dict,
    height: float,
    filename: str = "vis_09_pushover_animation.html",
    stride: int = 5,
    frame_ms: int = 60,
) -> None:
    """V9 — Animated pushover test: the column moves on the left while its capacity curve is drawn on the right.

    ``history`` holds per-step arrays keyed ``lateral``, ``axial_disp``, ``shear``, ``axial``,
    ``moment`` and ``rotation``. The column is drawn as the chord between its base and top nodes,
    so bending inside a multi-point element is not shown. The output is a self-contained HTML file
    with Play, Pause and a step slider.

    Args:
        output_dir: Directory where the HTML file is written.
        history: Per-step pushover arrays (see above), all of equal length.
        height: Column height, in the same length unit as the history.
        filename: Output HTML filename.
        stride: Use every ``stride``-th analysis step as an animation frame.
        frame_ms: Time per frame in milliseconds.
    """
    if _headless():
        return

    import numpy as np
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    lat = np.asarray(history["lateral"], dtype=float)
    axd = np.asarray(history["axial_disp"], dtype=float)
    shear = np.abs(np.asarray(history["shear"], dtype=float))
    axial = np.abs(np.asarray(history["axial"], dtype=float))
    moment = np.abs(np.asarray(history["moment"], dtype=float))
    n = len(lat)
    steps = list(range(0, n, stride))
    if steps[-1] != n - 1:
        steps.append(n - 1)

    fig = make_subplots(
        rows=1, cols=2, column_widths=[0.38, 0.62],
        subplot_titles=("Column (chord between its nodes)", "Shear vs lateral displacement at top"),
    )
    # Trace order: 0 undeformed, 1 deformed column, 2 full curve (faint), 3 curve so far, 4 current point.
    fig.add_trace(go.Scatter(x=[0.0, 0.0], y=[0.0, height], mode="lines",
                             line=dict(color="#999999", dash="dash", width=2), name="undeformed"), row=1, col=1)
    fig.add_trace(go.Scatter(x=[0.0, lat[0]], y=[0.0, height + axd[0]], mode="lines+markers",
                             line=dict(color="#185FA5", width=8), marker=dict(size=8, color="#185FA5"),
                             name="deformed"), row=1, col=1)
    fig.add_trace(go.Scatter(x=lat, y=shear, mode="lines", line=dict(color="#CCCCCC", width=2),
                             name="full curve"), row=1, col=2)
    fig.add_trace(go.Scatter(x=[lat[0]], y=[shear[0]], mode="lines",
                             line=dict(color="#185FA5", width=3), name="so far"), row=1, col=2)
    fig.add_trace(go.Scatter(x=[lat[0]], y=[shear[0]], mode="markers",
                             marker=dict(size=12, color="#993556"), name="now"), row=1, col=2)

    frames = []
    for k in steps:
        frames.append(go.Frame(
            name=str(k),
            traces=[1, 3, 4],
            data=[
                go.Scatter(x=[0.0, lat[k]], y=[0.0, height + axd[k]]),
                go.Scatter(x=lat[: k + 1], y=shear[: k + 1]),
                go.Scatter(x=[lat[k]], y=[shear[k]]),
            ],
            layout=dict(title_text=(
                f"Pushover test, step {k + 1} of {n}: top lateral {lat[k]:.1f} mm, "
                f"shear {shear[k] / 1e3:.1f} kN, axial {axial[k] / 1e3:.1f} kN, "
                f"base moment {moment[k] / 1e6:.1f} kN.m"
            )),
        ))
    fig.frames = frames

    fig.update_xaxes(title_text="Lateral displacement (mm)", range=[-200.0, float(lat.max()) * 1.15 + 200.0], row=1, col=1)
    fig.update_yaxes(title_text="Height (mm)", range=[-200.0, height * 1.05], row=1, col=1)
    fig.update_xaxes(title_text="Lateral displacement at top (mm)", row=1, col=2)
    fig.update_yaxes(title_text="Shear force (N)", row=1, col=2)
    fig.update_layout(
        template="plotly_white", showlegend=False, height=640, width=1400,
        title_text="Pushover test (press Play)", margin=dict(l=70, r=30, t=110, b=110),
        updatemenus=[dict(
            type="buttons", showactive=False, x=1.0, y=1.14, xanchor="right", yanchor="top",
            buttons=[
                dict(label="Play", method="animate",
                     args=[None, dict(frame=dict(duration=frame_ms, redraw=True), fromcurrent=True,
                                      transition=dict(duration=0))]),
                dict(label="Pause", method="animate",
                     args=[[None], dict(mode="immediate", frame=dict(duration=0, redraw=False),
                                        transition=dict(duration=0))]),
            ],
        )],
        sliders=[dict(
            active=0, currentvalue=dict(prefix="top lateral (mm): "), pad=dict(t=40),
            steps=[dict(label=f"{lat[k]:.0f}", method="animate",
                        args=[[str(k)], dict(mode="immediate", frame=dict(duration=0, redraw=True),
                                             transition=dict(duration=0))]) for k in steps],
        )],
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
