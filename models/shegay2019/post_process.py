"""Standalone post-processing — reads existing ODB data, generates visualizations."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *
import opstool as opst

ODB_TAG = 1
output_dir = Path(__file__).parent / "output"
opst.post.set_odb_path(str(output_dir))

print("Step-by-step slider view...")
opst.vis.plotly.plot_nodal_responses(
    odb_tag=ODB_TAG,
    slides=True,
    defo_scale=True,
    resp_type="disp",
    resp_dof="UX",
).write_html(str(output_dir / "vis_05_slider.html"))

print("Peak deformation view...")
opst.vis.plotly.plot_nodal_responses(
    odb_tag=ODB_TAG,
    step="absMax",
    defo_scale=True,
    resp_type="disp",
    resp_dof="UX",
).write_html(str(output_dir / "vis_06_peak.html"))

print(f"Done. Files saved to {output_dir}")
