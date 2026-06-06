ops.timeSeries('Path', 2, '-dt', 0.02, '-filePath', ProjAddss+'/Structural Model/kobe.txt','-factor',0.69*9.81)
ops.pattern('UniformExcitation', 2, 2, '-accel', 2)

# Dynamic Analysis.........................................................................
ops.wipeAnalysis()
ops.constraints('Plain')
ops.numberer('RCM')
ops.system('BandGeneral')
ops.test('EnergyIncr', 1.0e-6, 100)
ops.algorithm('Linear')
ops.integrator('Newmark', 0.5, 0.25)
ops.analysis('Transient')
for iAnal in np.arange(2500):
    ErrorState = ops.analyze(1,0.01)
    if ErrorState != 0:
        print('Error: The dynamic analysis failed!!')
    # if (iAnal % 100==0):
       # DomTime = str(ops.getTime())
       # print(f'The time is {DomTime} sec.')
# print("Dynamic Analysis Done!")
print(f"Iteration {np.str(n+1)}/{np.str(ni)}, Analysis {np.str(Analysis_number+1)}/15")