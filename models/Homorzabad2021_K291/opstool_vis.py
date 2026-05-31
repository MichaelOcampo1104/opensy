"""
opstool_vis.py — Model, node, and loading visualization using opstool.

Rebuilds the model in OpenSees (geometry only — no analysis) and renders
it with opstool showing nodes, boundary conditions, and loads.

Usage:
  python opstool_vis.py                   — pyvista interactive 3D window
  python opstool_vis.py --backend plotly  — plotly, saves HTML to output/
  python opstool_vis.py --labels          — show node labels
  python opstool_vis.py --no-loads        — hide load arrows
  python opstool_vis.py --no-bc           — hide boundary conditions
  python opstool_vis.py --backend plotly --html mymodel
"""

import sys
import os
import argparse
from pathlib import Path

MODEL_DIR = Path(__file__).parent.resolve()
OUTPUT_DIR = MODEL_DIR / "output"
OPSTOOL_DIR = MODEL_DIR / "opstool_output"

os.chdir(MODEL_DIR)
sys.path.insert(0, str(MODEL_DIR.parents[2] / "standards"))

# numpy compat patches (same as model.py)
import numpy as np

np.NAN = np.nan
np.NaN = np.nan

import openseespy.opensees as ops
import opstool as opst

from model import (
    init_model,
    define_materials,
    define_nodes,
    define_boundary_conditions,
    define_elements,
    define_gravity_loads,
)


def build_model():
    if ops.getNodeTags():
        print("Model already loaded.")
        return
    print("Building model geometry in OpenSees ...")
    init_model()
    define_materials()
    define_nodes()
    define_boundary_conditions()
    define_elements()
    define_gravity_loads()
    n_nodes = len(ops.getNodeTags())
    n_eles = len(ops.getEleTags())
    print(f"  {n_nodes} nodes, {n_eles} elements")
    OPSTOOL_DIR.mkdir(exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description="opstool model visualization")
    parser.add_argument("--backend", choices=["pyvista", "plotly"], default="pyvista")
    parser.add_argument("--labels", action="store_true", help="Show node labels")
    parser.add_argument("--no-loads", action="store_true", help="Hide load arrows")
    parser.add_argument("--no-bc", action="store_true", help="Hide boundary conditions")
    parser.add_argument("--html", type=str, default=None, help="Save plotly HTML filename")
    args = parser.parse_args()

    build_model()

    # opstool's plot_model() reads from the current ops domain and
    # writes results to opstool_output/ relative to CWD
    opst.plot_model(
        backend=args.backend,
        show_node_label=args.labels,
        show_load=not args.no_loads,
        show_fix_node=not args.no_bc,
        show_outline=True,
        line_width=2,
        point_size=3,
    )

    # Move plotly HTML to output/ and clean up temp files
    if args.backend == "plotly":
        src = MODEL_DIR / "ModelVis.html"
        if src.exists():
            dst_name = args.html or "model_vis_plotly"
            dst = (OUTPUT_DIR / dst_name).with_suffix(".html")
            dst.parent.mkdir(parents=True, exist_ok=True)
            src.replace(dst)
            print(f"Saved: {dst}")

    # Clean up intermediate files
    if OPSTOOL_DIR.exists():
        import shutil
        shutil.rmtree(OPSTOOL_DIR)

    print("Done.")


if __name__ == "__main__":
    main()
