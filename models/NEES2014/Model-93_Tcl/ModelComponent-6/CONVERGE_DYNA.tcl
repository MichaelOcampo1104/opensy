proc CONVERGE_DYNA {ALG C_dt} {
	
	#############################################################

	#
	# INPUTS:
	#	C_TOL:		Better Convergence Tolerance for test
	#	ALG:			Defult Algorithem
	#	D_TOL:		Defult Tolerance for test
	# 	N_Itr:		Defult Iteration number for convergence
	#	C_dt			current dt	
	#############################################################
	
	set ok [analyze 1 $C_dt];

	set C_TOL 1e-3;
	
	if {$ok != 0} {
		puts "Trying KrylovNewton ........................"
		test EnergyIncr $C_TOL  2500 0
		algorithm KrylovNewton
		set ok [analyze 1 $C_dt]
		algorithm $ALG
		test NormDispIncr 1.0e-4 300 0
	}


	if {$ok != 0} {
		puts "Trying Newton .............................."
		test EnergyIncr $C_TOL  2000 0
		algorithm Newton
		set ok [analyze 1 $C_dt]
		algorithm $ALG
		test NormDispIncr 1.0e-4 300 0
	}


	if {$ok != 0} {
		puts "Trying Newton with Initial Tangent.........."
		test NormDispIncr $C_TOL 2000 0
		algorithm Newton -initial
		set ok [analyze 1 $C_dt]
		algorithm $ALG
		test NormDispIncr 1.0e-4 300 0
	}

	if {$ok != 0} {
		puts "Trying NewtonWithLineSearch ..............."
		algorithm NewtonLineSearch 0.6 
		set ok [analyze 1 $C_dt]
			algorithm $ALG
		test NormDispIncr 1.0e-4 300 0
	}

#	if {$ok != 0} {
#		algorithm NewtonLineSearch 0.6;
#		test NormDispIncr 1.0e-3 3000
#		set ok [analyze 1 $C_dt];
#		algorithm $ALG
#		test NormDispIncr 1.0e-4 300
#	}
#	
#	if {$ok != 0} {
#		algorithm Newton;
#		test NormDispIncr 1.0e-3 3000
#		set ok [analyze 1 $C_dt];
#		algorithm $ALG
#		test NormDispIncr 1.0e-4 300 0
#	}
#	
#	if {$ok != 0} {
#		algorithm  ModifiedNewton -initial
#		test NormDispIncr 1.0e-3 3000
#		set ok [analyze 1 $C_dt];
#		algorithm $ALG
#		test NormDispIncr 1.0e-4 300
#	}
	
}; #end of procedure##############################################