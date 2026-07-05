# set damping based on two eigen modes
xDamp = 0.05;					# damping ratio
MpropSwitch = 1.0
KcurrSwitch = 0.0
KcommSwitch = 1.0
KinitSwitch = 0.0
nEigenI = 1		# mode 1
nEigenJ = 3		# mode 3
lambdaN = ops.eigen('-fullGenLapack', nEigenJ);			# eigenvalue analysis for nEigenJ modes
lambdaI = lambdaN[nEigenI-1]; 		# eigenvalue mode i
lambdaJ = lambdaN[nEigenJ-1]; 	# eigenvalue mode j
omegaI = lambdaI**(0.5);
omegaJ = lambdaJ**(0.5);
alphaM = MpropSwitch*xDamp*(2*omegaI*omegaJ)/(omegaI+omegaJ);	# M-prop. damping; D = alphaM*M
betaKcurr = KcurrSwitch*2.0*xDamp/(omegaI+omegaJ);         	# current-K;      +beatKcurr*KCurrent
betaKcomm = KcommSwitch*2.0*xDamp/(omegaI+omegaJ);   		    # last-committed K;   +betaKcomm*KlastCommitt
betaKinit = KinitSwitch*2.0*xDamp/(omegaI+omegaJ);        		# initial-K;     +beatKinit*Kini
# print('proportional damping.....................\n',
# 'alpha=',alphaM, '\n',
# 'beta=',betaKcomm)
ops.rayleigh(alphaM,betaKcurr,betaKinit,betaKcomm); # RAYLEIGH damping