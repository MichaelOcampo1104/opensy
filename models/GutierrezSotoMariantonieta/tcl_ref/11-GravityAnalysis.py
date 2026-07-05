# Gravity loading analysis------------------------------------------------
ops.constraints('Plain')
ops.numberer('RCM')
ops.system('BandGen')
ops.test('EnergyIncr', 1.0e-6, 100)
ops.algorithm('Linear')
ops.integrator('LoadControl', 1.0)
ops.analysis('Static')
ops.analyze(1)
ops.loadConst('-time', 0.0)
# Gravity loading analysis-----------------------------------------------
# print("The gravaty analysis is done")

