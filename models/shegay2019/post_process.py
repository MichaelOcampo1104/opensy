"""Standalone post-processing — reads existing ODB data, generates animation."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "standards"))
from units import *
import opstool as opst

ODB_TAG = 1
ODB_EVERY_N = 10
N_STEPS_GM = 8000

output_dir = Path(__file__).parent / "output"
opst.post.set_odb_path(str(output_dir))

n_frames = N_STEPS_GM // ODB_EVERY_N

print("Generating deformed shape...")
opst.vis.plotly.plot_nodal_responses(
    odb_tag=ODB_TAG, resp_type="disp", resp_dof="UX",
).write_html(str(output_dir / "vis_05_deformed.html"))

print("Generating animation...")
opst.vis.plotly.plot_nodal_responses_animation(
    odb_tag=ODB_TAG,
    framerate=n_frames // 20,
    defo_scale=True,
    resp_type="disp",
    resp_dof="UX",
).write_html(str(output_dir / "vis_06_animation.html"))

print(f"Done. Files saved to {output_dir}")
