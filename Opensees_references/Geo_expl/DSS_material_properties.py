# PDMY03 input parameters materials
# By: Arash Khosravifar   January 2009
# Last edit:              August 2018

# The matTag variable should be defined before this script is run,
# for example: matTag = 2
# It is assumed to be defined in a parent script that imports or executes this one.
 
if matTag == 1:
    # defined variables for Sand (N1)60=35 "nonliq" (Mat 1)
    massDen = 2.06       # (ton/m3)
    refG = 111.9e3       # (kPa)
    refB = 298.3e3       # (kPa)
    frictionAng = 42.2  # (degree)
    peakShearStrain = 0.1
    refPress = 100.0     # (kPa)
    pressDependCoe = 0.5
    phaseTransAng = 37.2 # (degree)

    contraction_a = 0.001  # Contraction rate.s
    contraction_b = 0.0    # fabric damage
    contraction_c = 0.8    # k_sigma effect
    contraction_d = 2.2    # ~CRR*[3/(1+2k0)]/2
    contraction_e = 0.0
    dilation_a = 0.6
    dilation_b = 3.0
    dilation_c = -0.5    # k_sigma effect

    liqParam1 = 1.0
    liqParam2 = 0.0

    noYieldSurf = 20
    # void = 0.55
    # cs1 = 0.9
    # cs2 = 0.02
    # cs3 = 0.0
    pa = 100             # (kPa)
    S0 = 1.73            # (kPa)

elif matTag == 2:
    # defined variables for Sand (N1)60=25 (Mat 2)
    massDen = 2.03       # (ton/m3)
    refG = 94.6e3        # (kPa)
    refB = 252.6e3       # (kPa)
    frictionAng = 35.8
    peakShearStrain = 0.1
    refPress = 100       # (kPa)
    pressDependCoe = 0.5
    phaseTransAng = 30.8

    contraction_a = 0.005
    contraction_b = 1.0
    contraction_c = 0.6
    contraction_d = 4.6  # ~CRR*[3/(1+2k0)]/2
    contraction_e = -1.0
    dilation_a = 0.45
    dilation_b = 3.0
    dilation_c = -0.4

    liqParam1 = 1.0
    liqParam2 = 0.0

    noYieldSurf = 20
    # void = 0.60
    # cs1 = 0.9
    # cs2 = 0.02
    # cs3 = 0.0
    pa = 100             # (kPa)
    S0 = 1.73            # (kPa)

elif matTag == 3:
    # defined variables for Sand (N1)60=15 (Mat 3)
    massDen = 1.99       # (ton/m3)
    refG = 73.7e3        # (kPa)
    refB = 196.8e3       # (kPa)
    frictionAng = 30.3
    peakShearStrain = 0.1
    refPress = 100       # (kPa)
    pressDependCoe = 0.5
    phaseTransAng = 25.3

    contraction_a = 0.012
    contraction_b = 3.0
    contraction_c = 0.4
    contraction_d = 9.0  # ~CRR*[3/(1+2k0)]/2
    contraction_e = 0.0
    dilation_a = 0.3
    dilation_b = 3.0
    dilation_c = -0.3

    liqParam1 = 1.0
    liqParam2 = 0.0

    noYieldSurf = 20
    # void = 0.67
    # cs1 = 0.9
    # cs2 = 0.02
    # cs3 = 0.0
    pa = 100             # (kPa)
    S0 = 1.73            # (kPa)

elif matTag == 4:
    # defined variables for Sand (N1)60=5 (Mat 4)
    massDen = 1.94       # (ton/m3)
    refG = 46.9e3        # (kPa)
    refB = 125.1e3       # (kPa)
    frictionAng = 25.4
    peakShearStrain = 0.1
    refPress = 100       # (kPa)
    pressDependCoe = 0.5
    phaseTransAng = 20.0

    contraction_a = 0.03
    contraction_b = 5.0
    contraction_c = 0.2
    contraction_d = 16.0 # ~CRR*[3/(1+2k0)]/2
    contraction_e = 2.0
    dilation_a = 0.15
    dilation_b = 3.0
    dilation_c = -0.2

    liqParam1 = 1.0
    liqParam2 = 0.0

    noYieldSurf = 20
    # void = 0.76
    # cs1 = 0.9#
    # cs2 = 0.02
    # cs3 = 0.0
    pa = 100             # (kPa)
    S0 = 1.73            # (kPa)
    

elif matTag == 55:
    # defined variables for Sand (N1)60=5 (Mat 4)
    massDen = 1.94              # (ton/m3)
    refG = 100e3                # (kPa) reference shear modulus, fit to deviatoric stress vs axial strain in monotonic condition
    refB = 170e3                # (kPa) reference bulk modulus, fit to deviatoric stress vs axial strain in monotonic condition
    frictionAng = 35.5          # Friction Angle , fit based on the stress path
    peakShearStrain = 0.085       # gamma_max Peak Shear strain
    refPress = 100              # (kPa) reference effective confinement pressure (P'r) , fit to deviatoric stress vs axial strain in monotonic condition
    pressDependCoe = 0.5        # n Pressure dependence coefficient, Asssume this value as 0.5
    phaseTransAng = 31.0        # Phase transformation angle, , fit based on the stress path

    contraction_a = 0.125        # Fit in cyclic and monotonic condition can be defined controlling the increase in pore pressure during contractive phase
    contraction_b = 0.5         # No influence in monotonic condition, fit in cyclic analysis
    contraction_c = 1.0         # Fit in cyclic and monotonic condition can be defined controlling the increase in pore pressure during contractive phase
    contraction_d = 0.0        # ~CRR*[3/(1+2k0)]/2
    contraction_e = 0.0         
    dilation_a = 0.25           # Fit in cyclic and Monotonic obtain by analysing the dilative tendency and negative pore pressure build-up
    dilation_b = 3.9
    dilation_c = -0.2

    liqParam1 = 1.0             # Liquefaction Paramaters
    liqParam2 = 0.0

    noYieldSurf = 20
    # void = 0.76
    # cs1 = 0.9#
    # cs2 = 0.02
    # cs3 = 0.0
    pa = 100                    # (kPa) Fix across all the soil type
    S0 = 1.73                   # (kPa) Fix across all the soil type