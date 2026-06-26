#!/usr/bin/env python
"""Quick diagnostic — check displacements after each analysis phase."""
import openseespy.opensees as ops
import math
import numpy as np

ops.wipe()
ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)

# --- mesh params ---
N_ELEM_X, N_NODE_X = 1, 2
S_ELEM_X = 0.5
NUM_LAYERS = 3
LAYER_THICK = {3: 2.0, 2: 8.0, 1: 20.0}
N_ELEM_Y = {3: 4, 2: 16, 1: 40}
S_ELEM_Y = {k: LAYER_THICK[k] / N_ELEM_Y[k] for k in range(1, 4)}
GRADE = 1.0
SLOPE = math.atan(GRADE / 100.0)
GACC = -9.81

# Soil properties
def get_soil(k):
    s = {
        1: {"rho": 2.45, "Gr": 1.3e5, "Br": 2.6e5, "phi": 39.0, "eInit": 0.47, "uBulk": 6.88e6,
            "d1": 0.010, "d2": 0.0, "d3": 0.35, "l1": 0.0},
        2: {"rho": 2.24, "Gr": 9.0e4, "Br": 2.2e5, "phi": 32.0, "eInit": 0.77, "uBulk": 5.06e6,
            "d1": 0.067, "d2": 0.23, "d3": 0.06, "l1": 0.27},
        3: {"rho": 1.8, "Gr": 9.0e4, "Br": 2.2e5, "phi": 32.0, "eInit": 0.77, "uBulk": 5.0e-6,
            "d1": 0.067, "d2": 0.23, "d3": 0.06, "l1": 0.27},
    }[k]
    return s

# Materials
for k in range(1, 4):
    s = get_soil(k)
    ops.nDMaterial("PressureDependMultiYield02", k, 2,
        s["rho"], s["Gr"], s["Br"], s["phi"], 0.1,
        101.0, 0.5, 26.0,
        s["d1"], s["d2"], s["d3"],
        s["l1"], 20.0, 5.0, 3.0, 1.0,
        0.0, s["eInit"], 0.9, 0.02, 0.7, 101.0)

# Nodes
soil_thick = sum(LAYER_THICK.values())
npp = {}
n_total = 0
for k in range(1, NUM_LAYERS + 1):
    npp[k] = N_NODE_X * (N_ELEM_Y[k] + (1 if k == NUM_LAYERS else 0))
    n_total += npp[k]

y = 0.0
c = 0
dry = []
for k in range(1, 4):
    for j in range(1, npp[k] + 1, N_NODE_X):
        for i in range(1, N_NODE_X + 1):
            tag = j + c + i - 1
            ops.node(tag, (i - 1) * S_ELEM_X, y)
            if y >= soil_thick - 2.0:
                dry.append(tag)
        y += S_ELEM_Y[k]
    c += npp[k]

print(f"Total nodes: {n_total}, dry nodes: {len(dry)}")

# BCs
for i in range(1, N_NODE_X + 1):
    ops.fix(i, 0, 1, 0)
    if i > 1:
        ops.equalDOF(1, i, 1)

for j in range(N_NODE_X + 1, n_total, N_NODE_X):
    for i in range(j, j + N_NODE_X - 1):
        ops.equalDOF(j, i + 1, 1, 2)

for tag in dry:
    ops.fix(tag, 0, 0, 1)

# Elements
BX = GACC * math.sin(SLOPE)
BY = GACC * math.cos(SLOPE)
print(f"Body forces: BX={BX:.6f}, BY={BY:.6f} m/s^2")

n_elem = sum(N_ELEM_Y[k] * N_ELEM_X for k in range(1, 4))
print(f"Elements: {n_elem}")

c_e = 0
for k in range(1, 4):
    for j in range(1, N_ELEM_Y[k] + 1):
        for i_el in range(1, N_ELEM_X + 1):
            tag = N_ELEM_X * (j + c_e - 1) + i_el
            nI = N_NODE_X * (j + c_e - 1) + i_el
            ops.element("SSPquadUP", tag, nI, nI + 1, nI + N_NODE_X + 1, nI + N_NODE_X,
                        k, 1.0, get_soil(k)["uBulk"], 1.0, 1.0,
                        get_soil(k)["eInit"], 1.5e-6, BX, BY)
    c_e += N_ELEM_Y[k]

print("Model built.")

# Dashpot
ROCK_VS, ROCK_DEN = 700.0, 2.5
dash_C = ROCK_VS * ROCK_DEN * S_ELEM_X * 1.0
ops.model("BasicBuilder", "-ndm", 2, "-ndf", 2)
ops.node(1001, 0.0, 0.0); ops.fix(1001, 1, 1)
ops.node(1002, 0.0, 0.0); ops.fix(1002, 0, 1)
ops.uniaxialMaterial("Viscous", 4, dash_C, 1)
ops.equalDOF(1, 1002, 1)
ops.element("zeroLength", 10000, 1001, 1002, "-mat", 4, "-dir", 1)
print(f"Dashpot created (C={dash_C:.1f})")

# --- GRAVITY ---
ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)
ops.remove("sp", 1, 1)
ops.remove("sp", 1, 2)
ops.fix(1, 1, 1, 0)

for k in range(1, 4):
    ops.updateMaterialStage("-material", k, "-stage", 0)

ops.constraints("Penalty", 1.0e14, 1.0e14)
ops.test("NormDispIncr", 1.0e-4, 35, 1)
ops.algorithm("Newton")
ops.numberer("Plain")
ops.system("ProfileSPD")
ops.integrator("Newmark", 5.0/6.0, 4.0/9.0)
ops.analysis("Transient")

print("\n=== Elastic gravity ===")
ok = ops.analyze(100, 500.0)
print(f"  ok={ok}")

for tag in [1, n_total, n_total // 2]:
    d = ops.nodeDisp(tag)
    print(f"  Node {tag}: UX={d[0]:.6e}, UY={d[1]:.6e}")

print("\n=== Plastic gravity ===")
for k in range(1, 4):
    ops.updateMaterialStage("-material", k, "-stage", 1)
ok = ops.analyze(100, 1.0)
print(f"  ok={ok}")

for tag in [1, n_total, n_total // 2]:
    d = ops.nodeDisp(tag)
    print(f"  Node {tag}: UX={d[0]:.6e}, UY={d[1]:.6e}")

# Remove extra base fixity
result = ops.remove("sp", 1, 1)
print(f"\nremove sp 1 1 returned: {result}")

# Check if removal worked — apply small test force
ops.wipeAnalysis()
ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)
ops.timeSeries("Linear", 1)
ops.pattern("Plain", 1, 1)
ops.load(1, 100.0, 0.0, 0.0)

ops.constraints("Transformation")
ops.test("NormDispIncr", 1.0e-8, 10)
ops.algorithm("Newton")
ops.numberer("RCM")
ops.system("ProfileSPD")
ops.integrator("LoadControl", 1.0)
ops.analysis("Static")
ok = ops.analyze(1)
print(f"\n=== Test: 100 kN at base ===")
print(f"  ok={ok}")
d1 = ops.nodeDisp(1)
print(f"  Node 1 UX: {d1[0]:.6e}")
print(f"  IF UX=0.0 -> base is STILL FIXED (remove sp failed)")

# Also check dynamic response
print("\n=== Dynamic check: 0.15 m/s velocity via dashpot ===")
ops.wipeAnalysis()
ops.model("BasicBuilder", "-ndm", 2, "-ndf", 3)

# Create a simple pulse
npts = 100
dt = 0.005
vel = [0.15 * math.sin(2 * math.pi * 1.5 * i * dt) * math.exp(-(i * dt - 2.0)**2/1.0)
       for i in range(npts)]
ops.timeSeries("Path", 11, "-dt", dt, "-values", *vel, "-factor", dash_C)
ops.pattern("Plain", 10, 11)
ops.load(1, 1.0, 0.0, 0.0)

ops.constraints("Transformation")
ops.test("NormDispIncr", 1.0e-5, 4)
ops.algorithm("Newton")
ops.numberer("RCM")
ops.system("ProfileSPD")
ops.integrator("Newmark", 0.5, 0.25)
ops.analysis("Transient")

max_ux = 0.0
for i in range(npts):
    ok = ops.analyze(1, dt)
    if ok != 0:
        print(f"  step {i}: FAILED (ok={ok})")
        break
    d = ops.nodeDisp(n_total)
    max_ux = max(max_ux, abs(d[0]))
    if i % 20 == 0:
        print(f"  step {i}: top UX={d[0]:.6e}")
print(f"\n  Max top UX: {max_ux:.6e} m")
print(f"  IF max UX ~1e-15: no dynamic response entering the column")
