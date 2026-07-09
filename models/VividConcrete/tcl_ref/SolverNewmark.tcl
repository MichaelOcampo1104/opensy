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
set testIter 100
test $testType $testTol $testIter 0

# set time steps (Note: the normal dt is initiated as a half of recording time interval)
# the minimum tolerable dt is limited by 1.0e-6 below which the algorithm would be switched
# the maximum tolerable dt is as same as the initial normal dt
set dtAna [expr $dt/2.0]
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
#				test $testType $testTol $testIter 0
#				algorithm KrylovNewton
#				set ok [analyze 1 $dtAna]
#				test $testType $testTol $testIter 0
#				algorithm Newton
#			}
		}
		if {$ok != 0} {
			# increase tolerance and resume max time step
			set testTol [expr $testTol*10.0]
			set dtAna $dtMax
			test $testType $testTol [expr 2*$testIter] 0
			set ok [analyze 1 $dtAna]
		}
	}
	if {$ok == 0 && [expr $dtAna*2.0] <= $dtMax} {
		# double the dtAna if current step converged but no more than dtMax
		set dtAna [expr $dtAna*2.0]
		# resume the initial testTol
		set testTol 1.0e-6
		test $testType $testTol $testIter 0
            puts [format "Increasing time step size (dtNew = %1.6e)" $dtAna]
	}  
	set tCurrent [getTime]
}

set eigenvalues [eigen -fullGenLapack [lindex $modes 2]]
set periodForRayleighDamping_1 [expr {2.0*$pi/sqrt([lindex $eigenvalues [lindex $modes 0]-1])}]
set periodForRayleighDamping_2 [expr {2.0*$pi/sqrt([lindex $eigenvalues [lindex $modes 1]-1])}]
set periodForRayleighDamping_3 [expr {2.0*$pi/sqrt([lindex $eigenvalues [lindex $modes 2]-1])}]

puts "T1 = $periodForRayleighDamping_1"
puts "T2 = $periodForRayleighDamping_2"
puts "T3 = $periodForRayleighDamping_3"
