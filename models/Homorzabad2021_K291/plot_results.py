"""
Post-processing & visualization for Homorzabad2021_K291.

Modes:
  python plot_results.py matplotlib     — 2D time-history PNGs
  python plot_results.py deformed       — 3D deformed shape PNG
  python plot_results.py geometry       — 3D undeformed geometry PNG
  python plot_results.py animate        — 3D deformed shape animation
  python plot_results.py all            — everything above

Animate options:
  --scale NUM   displacement scale factor (default: 10)
  --speed NUM   frame subsample rate (default: 1 = all frames)
  --gif NAME    save animation as GIF
  --mp4 NAME    save animation as MP4
  --interval MS delay between frames in ms (default: 30)

Examples:
  python plot_results.py animate --scale 50 --speed 5
  python plot_results.py animate --scale 20 --gif deformed --speed 10

Requires: pip install matplotlib numpy
"""

import sys
import argparse
import numpy as np
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "output"
ODB_DIR    = Path(__file__).parent / "CRSBF_ODB"

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ── helpers ──────────────────────────────────────────────────────────────────
def _file(path: Path) -> str:
    return str(path.resolve())

def _load_txt(path: Path) -> np.ndarray | None:
    if not path.exists():
        return None
    return np.loadtxt(path)


# ── structure data from VFO ODB ──────────────────────────────────────────────
class Structure:
    """Holds node coordinates, element connectivity, and node-tag → index map."""
    def __init__(self, odb_dir: Path):
        nodes = _load_txt(odb_dir / "Nodes.out")
        elems = _load_txt(odb_dir / "Elements_2Node.out")
        if nodes is None or elems is None:
            raise FileNotFoundError(
                f"Missing Nodes.out or Elements_2Node.out in {odb_dir}")
        # nodes: [tag, x, y, z]
        self.node_tags = nodes[:, 0].astype(int)       # (N,)
        self.coords    = nodes[:, 1:4]                  # (N, 3) — matches node_tags order
        # elems: [tag, n1, n2, ...]  for 2-node elements
        self.elems_n1n2 = elems[:, 1:3].astype(int)     # (E, 2)
        # Map node tag → row index in coords
        self._tag_to_idx = {tag: i for i, tag in enumerate(self.node_tags)}

    def row(self, node_tag: int) -> int:
        return self._tag_to_idx.get(node_tag, -1)


# ── 3D plot ──────────────────────────────────────────────────────────────────
def plot_3d_frames(struct: Structure,
                   defl: np.ndarray | None = None,
                   title: str = "Structure",
                   filename: str | None = None) -> None:
    """Matplotlib 3D wireframe.  If defl is given, overlay deformed in red."""
    from mpl_toolkits.mplot3d import Axes3D
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    def draw(c, style, label):
        for n1, n2 in struct.elems_n1n2:
            i1, i2 = struct.row(n1), struct.row(n2)
            if i1 < 0 or i2 < 0:
                continue
            ax.plot([c[i1, 0], c[i2, 0]],
                    [c[i1, 1], c[i2, 1]],
                    [c[i1, 2], c[i2, 2]],
                    style, linewidth=0.5, label=label if n1 == struct.elems_n1n2[0, 0] else "")
            label = None

    c0 = struct.coords
    draw(c0, "b-", "Undeformed")
    if defl is not None:
        draw(c0 + defl, "r--", "Deformed")

    ax.set_xlabel("X (mm)"); ax.set_ylabel("Y (mm)"); ax.set_zlabel("Z (mm)")
    ax.set_title(title); ax.legend()
    fig.tight_layout()
    if filename:
        fig.savefig(filename, dpi=150)
        print(f"  → {filename}")
    plt.close(fig)


# ── 2D time-history plots ────────────────────────────────────────────────────
def plot_matplotlib() -> None:
    """From output/ *.out files."""
    def load(name: str) -> tuple:
        p = OUTPUT_DIR / name
        if not p.exists():
            raise FileNotFoundError(f"Missing: {p}")
        raw = np.loadtxt(p)
        return raw[:, 0], raw[:, 1:]

    print("── 2D time-history plots ──")

    t, d = load("disp604.out")
    fig, axs = plt.subplots(3, 1, figsize=(10, 6), sharex=True)
    for i, (ax, dof) in enumerate(zip(axs, ["X", "Y", "Z"])):
        ax.plot(t, d[:, i]); ax.set_ylabel(f"Roof {dof}-disp"); ax.grid(True)
    axs[-1].set_xlabel("Time (s)")
    fig.suptitle("Roof Displacement (Node 604)")
    fig.tight_layout()
    fig.savefig(_file(OUTPUT_DIR / "plot_roof_disp.png"), dpi=150)

    if (OUTPUT_DIR / "disp2011.out").exists():
        _, d11 = load("disp2011.out")
        _, d51 = load("disp2051.out")
        fig, axs = plt.subplots(2, 1, figsize=(10, 4), sharex=True)
        axs[0].plot(t, d11[:, 1]); axs[0].set_ylabel("Fuse 2011 Y-disp"); axs[0].grid(True)
        axs[1].plot(t, d51[:, 1]); axs[1].set_ylabel("Fuse 2051 Y-disp"); axs[1].grid(True)
        axs[-1].set_xlabel("Time (s)")
        fig.suptitle("Fuse Shear Deformation")
        fig.tight_layout()
        fig.savefig(_file(OUTPUT_DIR / "plot_fuse_disp.png"), dpi=150)

    if (OUTPUT_DIR / "Strand1.out").exists():
        _, s1 = load("Strand1.out")
        _, s2 = load("Strand2.out")
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(t, s1[:, 0], label="Strand 6011")
        ax.plot(t, s2[:, 0], label="Strand 6051")
        ax.set_xlabel("Time (s)"); ax.set_ylabel("Axial Force (N)"); ax.legend(); ax.grid(True)
        fig.suptitle("PT Strand Forces")
        fig.tight_layout()
        fig.savefig(_file(OUTPUT_DIR / "plot_strand_forces.png"), dpi=150)

    if (OUTPUT_DIR / "BaseReactions.out").exists():
        _, r = load("BaseReactions.out")
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(t, np.sum(r[:, 0::6], axis=1))
        ax.set_xlabel("Time (s)"); ax.set_ylabel("Base Shear X (N)"); ax.grid(True)
        fig.suptitle("Total Base Shear")
        fig.tight_layout()
        fig.savefig(_file(OUTPUT_DIR / "plot_base_shear.png"), dpi=150)

    plt.close("all")
    print("Done.")


# ── undeformed geometry ──────────────────────────────────────────────────────
def plot_geometry() -> None:
    if not ODB_DIR.exists():
        print("No structure data found — run model.py first.")
        return
    print("── 3D geometry ──")
    struct = Structure(ODB_DIR)
    plot_3d_frames(struct, title="CRSBF Model Geometry",
                   filename=_file(OUTPUT_DIR / "geo_undeformed.png"))
    print("Done.")


# ── deformed shape ───────────────────────────────────────────────────────────
def plot_deformed() -> None:
    if not ODB_DIR.exists():
        print("No structure data found — run model.py first.")
        return

    disp_path = OUTPUT_DIR / "NodeDisp_All.out"
    if not disp_path.exists():
        print("No NodeDisp_All.out — re-run model.py to capture displacements.")
        return

    print("── 3D deformed shape ──")
    struct = Structure(ODB_DIR)

    raw = _load_txt(disp_path)
    if raw is None:
        return

    # raw has shape (nsteps, 1 + 3*N) — first col is time, then 3 DOF per node
    t = raw[:, 0]
    n_nodes = struct.coords.shape[0]
    u = raw[-1, 1:].reshape(n_nodes, 3)          # last time step

    plot_3d_frames(struct, defl=u,
                   title=f"Deformed Shape at t={t[-1]:.2f}s",
                   filename=_file(OUTPUT_DIR / "geo_deformed.png"))
    print("Done.")


# ── animated deformed shape ───────────────────────────────────────────────────
def animate_deformed() -> None:
    """Animate the deformed shape over time using matplotlib."""
    if not ODB_DIR.exists():
        print("No structure data found — run model.py first.")
        return

    disp_path = OUTPUT_DIR / "NodeDisp_All.out"
    if not disp_path.exists():
        print("No NodeDisp_All.out — re-run model.py to capture displacements.")
        return

    from matplotlib.animation import FuncAnimation
    from mpl_toolkits.mplot3d.art3d import Line3DCollection

    # --- parse CLI extras ---
    extra = sys.argv[2:]  # e.g. --scale 50 --speed 5 --gif anim
    parser = argparse.ArgumentParser()
    parser.add_argument("--scale", type=float, default=10.0)
    parser.add_argument("--speed", type=int, default=1)
    parser.add_argument("--gif", type=str, default=None)
    parser.add_argument("--mp4", type=str, default=None)
    parser.add_argument("--interval", type=int, default=30)
    known, _ = parser.parse_known_args(extra)

    print("── animated deformed shape ──")

    struct = Structure(ODB_DIR)
    raw = _load_txt(disp_path)
    if raw is None:
        return

    t = raw[:, 0]
    n_nodes = struct.coords.shape[0]
    n_steps = len(t)
    u = raw[:, 1:].reshape(n_steps, n_nodes, 3) * known.scale

    # Subsample frames
    step = max(1, known.speed)
    frame_indices = range(0, n_steps, step)

    c0 = struct.coords

    # Build segment index pairs
    seg_indices = [(i1, i2) for n1, n2 in struct.elems_n1n2
                   if (i1 := struct.row(n1)) >= 0 and (i2 := struct.row(n2)) >= 0]

    # Pre-compute deformed bounds across all time steps
    all_deformed = c0 + u  # (n_steps, n_nodes, 3)
    x_lim = (float(np.min(all_deformed[:, :, 0])), float(np.max(all_deformed[:, :, 0])))
    y_lim = (float(np.min(all_deformed[:, :, 1])), float(np.max(all_deformed[:, :, 1])))
    z_lim = (float(np.min(all_deformed[:, :, 2])), float(np.max(all_deformed[:, :, 2])))

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    # Static undeformed (drawn once)
    undef_segs = [[c0[i1].tolist(), c0[i2].tolist()] for i1, i2 in seg_indices]
    ax.add_collection(Line3DCollection(undef_segs, colors="blue", linewidths=0.3, alpha=0.3))

    # Deformed (updated each frame)
    def_segs = undef_segs  # initial
    def_coll = Line3DCollection(def_segs, colors="red", linewidths=0.5)
    ax.add_collection(def_coll)

    ax.set_xlim(*x_lim)
    ax.set_ylim(*y_lim)
    ax.set_zlim(*z_lim)
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.set_zlabel("Z (mm)")
    time_text = ax.text2D(0.02, 0.95, "", transform=ax.transAxes, fontsize=12)

    def update(frame):
        c_def = c0 + u[frame]
        def_coll.set_segments([[c_def[i1].tolist(), c_def[i2].tolist()]
                               for i1, i2 in seg_indices])
        time_text.set_text(f"t = {t[frame]:.2f} s")
        return def_coll, time_text

    ani = FuncAnimation(fig, update, frames=frame_indices,
                        interval=known.interval, blit=False)

    if known.gif:
        path = (OUTPUT_DIR / known.gif).with_suffix(".gif")
        ani.save(str(path), writer="pillow", dpi=100)
        print(f"  → {path}")
    if known.mp4:
        path = (OUTPUT_DIR / known.mp4).with_suffix(".mp4")
        ani.save(str(path), writer="ffmpeg", dpi=100)
        print(f"  → {path}")

    print("Close the plot window to exit.")
    plt.show()
    print("Done.")


# ── all ──────────────────────────────────────────────────────────────────────
def plot_all() -> None:
    plot_matplotlib()
    plot_geometry()
    plot_deformed()


# ── main ─────────────────────────────────────────────────────────────────────
def main() -> None:
    modes = {
        "matplotlib": plot_matplotlib,
        "deformed":   plot_deformed,
        "geometry":   plot_geometry,
        "animate":    animate_deformed,
        "all":        plot_all,
    }
    mode = sys.argv[1] if len(sys.argv) > 1 else "matplotlib"
    if mode in modes:
        modes[mode]()
    else:
        print(f"Unknown: {mode} — available: {', '.join(modes)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
