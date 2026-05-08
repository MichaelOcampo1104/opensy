"""
Consistent SI Unit System for OpenSeesPy
=========================================
Base units: kN, m, sec

Import this module in every script to avoid redefining units.

Usage:
    from units import *
    E_concrete = 30 * GPa      # → 30_000_000 kN/m²
    depth      = 500 * mm      # → 0.5 m
    fy_steel   = 500 * MPa     # → 500_000 kN/m²
"""

# ── Base units ────────────────────────────────────────────────────────────────
m   = 1.0
kN  = 1.0
sec = 1.0

# ── Length ────────────────────────────────────────────────────────────────────
mm   = m / 1_000
cm   = m / 100
inch = 25.4 * mm
ft   = 12.0 * inch
km   = 1_000 * m

# ── Force ─────────────────────────────────────────────────────────────────────
N    = kN / 1_000
MN   = kN * 1_000
kips = kN * 4.448_221_615
lbf  = kips / 1_000

# ── Stress (kN/m² = kPa) ─────────────────────────────────────────────────────
Pa  = N / m**2
kPa = 1.0               # kN/m² ≡ kPa
MPa = 1_000 * kPa
GPa = 1_000 * MPa
ksi = 6.894_757_3 * MPa
psi = ksi / 1_000

# ── Mass ──────────────────────────────────────────────────────────────────────
kg    = N * sec**2 / m        # from F = ma
tonne = kN * sec**2 / m

# ── Acceleration ──────────────────────────────────────────────────────────────
g_accel = 9.81 * m / sec**2   # gravitational acceleration

# ── Area & Inertia helpers ────────────────────────────────────────────────────
mm2 = mm**2
cm2 = cm**2
mm4 = mm**4
cm4 = cm**4

# ── Common material properties (for quick reference) ─────────────────────────
# Steel
E_STEEL      = 200 * GPa
FY_S275      = 275 * MPa
FY_S355      = 355 * MPa
FY_S500      = 500 * MPa      # rebar
DENSITY_STEEL = 78.5 * kN / m**3

# Concrete (characteristic values — adjust for your design code)
FC_C25 = 25 * MPa
FC_C30 = 30 * MPa
FC_C40 = 40 * MPa
EC_C30 = 31_476 * MPa         # Ec for C30
DENSITY_CONCRETE = 24.0 * kN / m**3
