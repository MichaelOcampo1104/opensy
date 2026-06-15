# --------------------------------------------------------------------------------------------------
# Example: 4-Story Steel Moment Frame with Concentrated Plasticity
# Centerline Model with Concentrated Plastic Hinges at Beam-Column Joint
# Created by:  Laura Eads and Kuanshi Zhong, Stanford University, 2021
# Units: kips, inches, seconds

# Updated 9 May 2012:  fixed errors defining rayleigh damping (see line 440)
# Updated 3 Sept 2013: changed solution algorithm and convergence criteria to help with convergence (by Filipe Ribeiro and Andre Barbosa) 
# Updated 21 Feb 2021: changed to a 4-story frame
	
############################################################################
#   Time History/Dynamic Analysis               			   			   #
############################################################################	
	
	# damping
	set dampRat 0.05
	set dampRatF 1.0
	set modes {1 3}
	set pi [expr {2.0*asin(1.0)}]
	set g 386.089
	set eigenvalues [eigen -fullGenLapack [lindex $modes 1]]
	set periodForRayleighDamping_1 [expr {2.0*$pi/sqrt([lindex $eigenvalues [lindex $modes 0]-1])}]
	set periodForRayleighDamping_2 [expr {2.0*$pi/sqrt([lindex $eigenvalues [lindex $modes 1]-1])}]
	puts "T1 = $periodForRayleighDamping_1"
	set omegaI [expr (2.0 * $pi) / $periodForRayleighDamping_1]
    set omegaJ [expr (2.0 * $pi) / ($periodForRayleighDamping_2)]
    set alpha1Coeff [expr (2.0 * $omegaI * $omegaJ) / ($omegaI + $omegaJ)]
    set alpha2Coeff [expr (2.0) / ($omegaI + $omegaJ)]
    set alpha1  [expr $alpha1Coeff * $dampRat * $dampRatF]
    set alpha2  [expr $alpha2Coeff * $dampRat * $dampRatF]
    rayleigh $alpha1 0 $alpha2 0;    # Initial stiffness

	# define dynamic analysis parameters
		wipeAnalysis;					# destroy all components of the Analysis object, i.e. any objects created with system, numberer, constraints, integrator, algorithm, and analysis commands
		constraints Plain;				# how it handles boundary conditions
		numberer RCM;					# renumber dof's to minimize band-width (optimization)
		system UmfPack;					# how to store and solve the system of equations in the analysis
		test NormDispIncr 1.0e-3 50;	# type of convergence criteria with tolerance, max iterations
		algorithm NewtonLineSearch;		# use NewtonLineSearch solution algorithm: updates tangent stiffness at every iteration and introduces line search to the Newton-Raphson algorithm to solve the nonlinear residual equation. Line search increases the effectiveness of the Newton method
		integrator Newmark 0.5 0.25;	# uses Newmark's average acceleration method to compute the time history
		analysis Transient;				# type of analysis: transient or static
		
	# perform the dynamic analysis and display whether analysis was successful	
		set dtAna [expr $dt/2]
		set dtMin 1.0e-9
		set dtMinex 1.0e-12
		set dtMax $dtAna

		set ok 0;
		set tFinal [expr $numStep * $dt]
		set tCurrent [getTime]

		puts "Start time history analysis";

		record;

		set algo_tag 0;
		set timer	1;
		while {$ok == 0 && $tCurrent < $tFinal} {
			
			set ok [analyze 1 $dtAna]
			
			if {$ok != 0} {
				if {[expr $dtAna/2.0] >= $dtMin} {
					set dtAna [expr $dtAna/2.0]
					puts [format "\nReducing time step size (dtNew = %1.6e)" $dtAna]
					set ok 0;
				} else {
				if {[expr $dtAna/2.0] >= $dtMinex} {
					set dtAna [expr $dtAna/2.0]
					algorithm KrylovNewton
					puts "Try KrylovNewton"
					set algo_tag 1;
					set ok 0
				}
			}
			} else {
				if {[expr $dtAna*2.0] <= $dtMax} {
				if {$algo_tag == 1} {
					puts "Back to Newton"
					algorithm Newton
					set algo_tag 0
				}
					set dtAna [expr $dtAna*2.0]
					puts [format "\nIncreasing time step size (dtNew = %1.6e)" $dtAna]
				}
			}
			
			set tCurrent [getTime]
		}

		if {$ok != 0} {
			puts [format "\nModel failed (time = %1.3e)" $tCurrent]
		} else {
			puts [format "\nResponse-history analysis completed"]
		}