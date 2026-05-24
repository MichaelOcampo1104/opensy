"""
Consistent N-mm Unit System for OpenSeesPy
==========================================
Base units: N, mm, sec

Import this module in every script to avoid redefining units.

Usage:
    from units_nmm import *
    E_concrete = 30000 * MPa     # → 30000 N/mm²
    depth      = 500 * mm        # → 500 mm
    fy_steel   = 500 * MPa       # → 500 N/mm²
"""

# ── Base units ────────────────────────────────────────────────────────────────
N   = 1.0
mm  = 1.0
sec = 1.0

# ── Length ────────────────────────────────────────────────────────────────────
m    = 1000 * mm
cm   = 10 * mm
km   = 1_000_000 * mm
inch = 25.4 * mm
ft   = 12.0 * inch

# ── Force ─────────────────────────────────────────────────────────────────────
kN   = 1000 * N
MN   = 1_000_000 * N
kgf  = 9.80665 * N
lbf  = 4.44822 * N
kip  = 1000 * lbf

# ── Stress (N/mm² = MPa) ─────────────────────────────────────────────────────
Pa   = N / mm**2
MPa  = 1.0
kPa  = 0.001 * MPa
GPa  = 1000.0
ksi  = 6.894757 * MPa
psi  = ksi / 1000.0

# ── Mass ──────────────────────────────────────────────────────────────────────
kg   = N * sec**2 / mm
tonne = 1000 * kg

# ── Acceleration ──────────────────────────────────────────────────────────────
g_accel = 9806.65 * mm / sec**2

# ── Area & Inertia helpers ────────────────────────────────────────────────────
mm2 = mm**2
cm2 = cm**2
mm4 = mm**4
cm4 = cm**4
m2  = m**2
m4  = m**4

# ── Moment of Inertia conversions ────────────────────────────────────────────
m4_to_mm4 = 1e12
mm4_to_m4 = 1e-12

# ── Common material properties (for quick reference) ─────────────────────────
# Steel
E_STEEL      = 200000 * MPa
FY_S275      = 275 * MPa
FY_S355      = 355 * MPa
FY_S500      = 500 * MPa
DENSITY_STEEL = 7850 * kg / m**3

# Concrete (characteristic values — adjust for your design code)
FC_C25 = 25 * MPa
FC_C30 = 30 * MPa
FC_C40 = 40 * MPa
EC_C30 = 31476 * MPa
DENSITY_CONCRETE = 2400 * kg / m**3

# Masonry
E_MASONRY = 5000 * MPa
