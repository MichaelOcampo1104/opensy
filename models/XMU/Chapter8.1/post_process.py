"""Standalone post-processing — reads existing ODB data, generates visualizations.

Usage:
    conda activate opensy
    python post_process.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[3] / "standards"))
from vis_utils import _headless
import opstool as opst

ODB_TAG = 1
output_dir = Path(__file__).parent / "output"

if not output_dir.exists():
    print(f"Output directory not found: {output_dir}")
    print("Run model.py first to generate ODB data.")
    sys.exit(1)

opst.post.set_odb_path(str(output_dir))

if _headless():
    print("OPENSEES_HEADLESS=1 — skipping visualization.")
    sys.exit(0)

print("Peak deformation view ...")
try:
    opst.vis.plotly.plot_nodal_responses(
        odb_tag=ODB_TAG, step="absMax", defo_scale=True,
        resp_type="disp", resp_dof="UX",
    ).write_html(str(output_dir / "vis_05_deformed_peak.html"))
    print("  -> vis_05_deformed_peak.html")
except Exception as e:
    print(f"  Skipped: {e}")

print("Step-by-step slider view ...")
try:
    opst.vis.plotly.plot_nodal_responses(
        odb_tag=ODB_TAG, slides=True, defo_scale=True,
        resp_type="disp", resp_dof="UX",
    ).write_html(str(output_dir / "vis_06_deformed_slider.html"))
    print("  -> vis_06_deformed_slider.html")
except Exception as e:
    print(f"  Skipped: {e}")

print("Done.")
