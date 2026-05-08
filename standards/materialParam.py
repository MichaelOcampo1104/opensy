import openseespy.opensees as ops

# parameters.py

# ---------------- Loose Sand ----------------
matTag_loose = 11
fmass = 1.0   # fluid mass density
smass_loose = 1.7   # rho = saturated soil mass density # TON / m^3
dof = 2       # degrees of freedom (usually 2 or 3)

# Elastic parameters
G_loose = 5.5e4
B_loose = 1.5e5

# Strength parameters
frictionAngle_loose = 29
peakshearStrain_loose = 0.1

# Pressure dependency
refPressure = 80
pressDependCoef = 0.5

# Plasticity parameters
PTang_loose = 29.0
contrac_loose = 0.21
dilat1_loose = 0.0
dilat2_loose = 0.0

# Liquefaction parameters
liquefac1_loose = 10.0
liquefac2_loose = 0.02
liquefac3_loose = 1

# Void ratio
voidratio_loose = 0.85

loose_sand_params = dict(
    matTag=matTag_loose,
    dof=dof,
    massDensity=smass_loose,
    shearModulus=G_loose,
    bulkModulus=B_loose,
    frictionAngle=frictionAngle_loose,
    peakShearStrain=peakshearStrain_loose,
    refPressure=refPressure,
    pressDependCoef=pressDependCoef,
    PTang=PTang_loose,
    contrac=contrac_loose,
    dilat1=dilat1_loose,
    dilat2=dilat2_loose,
    liquefac1=liquefac1_loose,
    liquefac2=liquefac2_loose,
    liquefac3=liquefac3_loose,
    voidRatio=voidratio_loose,
)

# ---------------- Medium Sand ----------------
matTag_medium = 12
smass_medium = 1.9 # TON / m^3

# Elastic parameters
G_medium = 7.5e4
B_medium = 2.0e5

# Strength parameters
frictionAngle_medium = 33
peakshearStrain_medium = 0.1

# Plasticity parameters
PTang_medium = 27
contrac_medium = 0.07
dilat1_medium = 0.4
dilat2_medium = 2.0

# Liquefaction parameters
liquefac1_medium = 10.0
liquefac2_medium = 0.01
liquefac3_medium = 1

# Void ratio
voidratio_medium = 0.7

medium_sand_params = dict(
    matTag=matTag_medium,
    dof=dof,
    massDensity=smass_medium,
    shearModulus=G_medium,
    bulkModulus=B_medium,
    frictionAngle=frictionAngle_medium,
    peakShearStrain=peakshearStrain_medium,
    refPressure=refPressure,
    pressDependCoef=pressDependCoef,
    PTang=PTang_medium,
    contrac=contrac_medium,
    dilat1=dilat1_medium,
    dilat2=dilat2_medium,
    liquefac1=liquefac1_medium,
    liquefac2=liquefac2_medium,
    liquefac3=liquefac3_medium,
    voidRatio=voidratio_medium,
)

# ---------------- Medium Dense Sand ----------------
matTag_medium_dense = 13
smass_medium_dense = 2.0 # TON / m^3

# Elastic parameters
G_medium_dense = 1.0e5
B_medium_dense = 3.0e5

# Strength parameters
frictionAngle_medium_dense = 37
peakshearStrain_medium_dense = 0.1

# Plasticity parameters
PTang_medium_dense = 27
contrac_medium_dense = 0.05
dilat1_medium_dense = 0.6
dilat2_medium_dense = 3.0

# Liquefaction parameters
liquefac1_medium_dense = 5.0
liquefac2_medium_dense = 0.003
liquefac3_medium_dense = 1

# Void ratio
voidratio_medium_dense = 0.5

medium_dense_sand_params = dict(
    matTag=matTag_medium_dense,
    dof=dof,
    massDensity=smass_medium_dense,
    shearModulus=G_medium_dense,
    bulkModulus=B_medium_dense,
    frictionAngle=frictionAngle_medium_dense,
    peakShearStrain=peakshearStrain_medium_dense,
    refPressure=refPressure,
    pressDependCoef=pressDependCoef,
    PTang=PTang_medium_dense,
    contrac=contrac_medium_dense,
    dilat1=dilat1_medium_dense,
    dilat2=dilat2_medium_dense,
    liquefac1=liquefac1_medium_dense,
    liquefac2=liquefac2_medium_dense,
    liquefac3=liquefac3_medium_dense,
    voidRatio=voidratio_medium_dense,
)

# ---------------- Dense Sand ----------------
matTag_dense = 14
smass_dense = 2.1 # TON / m^3

# Elastic parameters
G_dense = 1.3e5
B_dense = 3.9e5

# Strength parameters
frictionAngle_dense = 40
peakshearStrain_dense = 0.1

# Plasticity parameters
PTang_dense = 27
contrac_dense = 0.03
dilat1_dense = 0.8
dilat2_dense = 5.0

# Liquefaction parameters
liquefac1_dense = 0.0
liquefac2_dense = 0.0
liquefac3_dense = 0

# Void ratio
voidratio_dense = 0.45

dense_sand_params = dict(
    matTag=matTag_dense,
    dof=dof,
    massDensity=smass_dense,
    shearModulus=G_dense,
    bulkModulus=B_dense,
    frictionAngle=frictionAngle_dense,
    peakShearStrain=peakshearStrain_dense,
    refPressure=refPressure,
    pressDependCoef=pressDependCoef,
    PTang=PTang_dense,
    contrac=contrac_dense,
    dilat1=dilat1_dense,
    dilat2=dilat2_dense,
    liquefac1=liquefac1_dense,
    liquefac2=liquefac2_dense,
    liquefac3=liquefac3_dense,
    voidRatio=voidratio_dense,
)


# Flexible helper to build the OpenSees nDMaterial command
def create_material(ops, params, matTag=None, dof=None):
    p = params.copy()
    if matTag is not None:
        p["matTag"] = matTag
    if dof is not None:
        p["dof"] = dof

    ops.nDMaterial(
        "PressureDependMultiYield02", #STABLE MATERIAL COMPARED TO PMDY ORIGINAL
        p["matTag"], p["dof"], p["massDensity"], p["shearModulus"], p["bulkModulus"],
        p["frictionAngle"], p["peakShearStrain"], p["refPressure"], p["pressDependCoef"],
        p["PTang"], p["contrac"], p["dilat1"], p["dilat2"],
        p["liquefac1"], p["liquefac2"], p["liquefac3"], p["voidRatio"]
    )
    '''
    import parameters as param
    medium_dense = param.create_material(ops, param.medium_dense_sand_params, matTag=13, dof=2)
    '''

    return p  # return the parameters used for traceability