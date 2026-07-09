#############################################################################################################
# Kuanshi Zhong							                                                      #
# John A. Blume Earthquake Engineering Center                                                               #
# Stanford University                                                                                       #
# Last edited: 08/09/2019														#	
#############################################################################################################

# Initialize the analysis parameters and run the analysis. Check whether the structure has collapsed after
# every second and halt the analysis if it has.
constraints Transformation
numberer RCM
system SparseGEN
algorithm Newton
integrator Newmark 0.5 0.25
analysis Transient

# set the test parameters
# start with NormDispIncr but can be switched to energy-based tests
# start with 1e-6 but can be relaxed latter to enforce convergence if possible
# the test interation number is initiated with 50 but will be increased to help convergence later
set testType NormDispIncr
set testTol 1.0e-6
set testTolMax 1.0e-3
set testIter 500
test $testType $testTol $testIter 0

# set time steps (Note: the normal dt is initiated as a half of recording time interval)
# the minimum tolerable dt is limited by 1.0e-6 below which the algorithm would be switched
# the maximum tolerable dt is as same as the initial normal dt
set dtAna [expr min(0.02,$dt)]
set dtMin 1.0e-6
set dtMax $dtAna

# initiate analysis states
set ok 0
set tFinal [expr $numpts*$dt]
set tCurrent [getTime]
record

# start time-history analysis
while {$ok == 0 && $tCurrent < $tFinal} {
	set ok [analyze 1 $dtAna]
	while {$ok != 0 && $testTol <= $testTolMax} {
		# start with the initial or a new testTol
		while {$ok != 0 && [expr $dtAna/2.0] >= $dtMin} {
			# decrease time step
			set dtAna [expr $dtAna/2.0]
            		puts [format "Reducing time step size (dtNew = %1.6e)" $dtAna]
            		set ok [analyze 1 $dtAna]
			if {$ok != 0} {
				# try NewtonLineSearch to help convergence
				puts "Try NewtonLineSearch"
				test $testType $testTol $testIter 0
				algorithm NewtonLineSearch 0.6
				set ok [analyze 1 $dtAna]
				test $testType $testTol $testIter 0
				algorithm Newton
			}
			if {$ok != 0} {
				# try ModifiedNewton to help convergence
				puts "Try ModifiedNewton"
				test $testType $testTol $testIter 0
				algorithm ModifiedNewton -initial
				set ok [analyze 1 $dtAna]
				test $testType $testTol $testIter 0
				algorithm Newton
			}
			if {$ok != 0} {
				# try Broyden to help convergence
				puts "Try Broyden"
				test $testType $testTol $testIter 0
				algorithm Broyden 10
				set ok [analyze 1 $dtAna]
				test $testType $testTol $testIter 0
				algorithm Newton
			}
#			if {$ok != 0} {
#				# try KrylovNewton to help convergence
#				test $testType $testTol $testIter
#				algorithm KrylovNewton
#			 	set ok [analyze 1 $dtAna]
#			 	test $testType $testTol $testIter
#			 	algorithm Newton
#			}
#			if {$ok != 0} {
#				# try BFGS to help convergence
#				test $testType $testTol $testIter
#				algorithm BFGS
#			 	set ok [analyze 1 $dtAna]
#			 	test $testType $testTol $testIter
#			 	algorithm Newton
#			}
		}
		if {$ok != 0} {
			# increase tolerance and resume max time step
			set testTol [expr $testTol*10.0]
			set dtAna $dtMax
			test $testType $testTol [expr $testIter] 0
			set ok [analyze 1 $dtAna]
		}
	}
	
        if {$ok != 0} {
		set testTol 1.0e-6; # reset tolerance
		set dtAna [expr min(0.005,$dt)]; # reset dt
		set testType EnergyIncr; # do energy-based
		test $testType $testTol $testIter 0
		set ok [analyze 1 $dtAna]
	}
	while {$ok != 0 && $testTol <= $testTolMax} {
		# start with the initial or a new testTol
		while {$ok != 0 && [expr $dtAna/2.0] >= $dtMin} {
			# decrease time step
			set dtAna [expr $dtAna/2.0]
			set ok [analyze 1 $dtAna]
			if {$ok != 0} {
				# try NewtonLineSearch to help convergence
				puts "Try NewtonLineSearch"
				test $testType $testTol $testIter 0
				algorithm NewtonLineSearch 0.6
				set ok [analyze 1 $dtAna]
				test $testType $testTol $testIter 0
				algorithm Newton
			}
			if {$ok != 0} {
				# try ModifiedNewton to help convergence
				puts "Try ModifiedNewton"
				test $testType $testTol $testIter 0
				algorithm ModifiedNewton -initial
				set ok [analyze 1 $dtAna]
				test $testType $testTol $testIter 0
				algorithm Newton
			}
			if {$ok != 0} {
				# try Broyden to help convergence
				puts "Try Broyden"
				test $testType $testTol $testIter 0
				algorithm Broyden 10
				set ok [analyze 1 $dtAna]
				test $testType $testTol $testIter 0
				algorithm Newton
			}
		}
		if {$ok != 0} {
			# increase tolerance and resume max time step
			set testTol [expr $testTol*10.0]
			set dtAna $dtMax
			test $testType $testTol [expr $testIter] 0
			set ok [analyze 1 $dtAna]
		}
	}
	if {$ok == 0} {
		# double the dtAna if current step converged but no more than dtMax
		if {[expr $dtAna*2.0] <= $dtMax} {
			set dtAna [expr $dtAna*2.0]
			puts [format "Increasing time step size (dtNew = %1.6e)" $dtAna]
		}
		# resume the initial testTol
		set testTol 1.0e-6
		set testType NormDispIncr
		test $testType $testTol $testIter 0
	}  
	set tCurrent [getTime]
}

# Convergence check
if {$ok != 0 && $tCurrent < $tFinal} {
    set collapse_flag 1
} else {
    set collapse_flag 0
}