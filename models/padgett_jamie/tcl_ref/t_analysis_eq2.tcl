# this code sets up the dynamic analysis for earthquake performance assessment of the bridge

puts $fileID "#  Set up the acceleration record for Rix Ground motions."
puts $fileID "set g 384.6"; # in inch/s2
rectify_gm  $EQ $load_dir $name ;# changing the incidence angle of ground motions

puts $fileID {set ground_motion_x "Series -dt 0.005 -filePath [concat $name/gm_x.acn]  -factor [expr 1.00*$g]"} ; # setting up time series for ground motion acceleration in x direction (longitudinal)
puts $fileID {set ground_motion_z "Series -dt 0.005 -filePath [concat $name/gm_z.acn]  -factor [expr 1.00*$g]"} ; # setting up time series for ground motion acceleration in x direction (transverse)

puts $fileID "#\n#                          tag   dir   accel series arg"
puts $fileID {pattern UniformExcitation   2     1   -accel        $ground_motion_x;  #   Longitudinal ground motion pattern
puts $fileID {pattern UniformExcitation   3     3   -accel        $ground_motion_z;  #   Transverse ground motion pattern


puts $fileID "#\n#===SET UP TRANSIENT ANALYSIS========================================================="
# setting up analysis options
puts $fileID "#\n#                  Tol     Iter   Flag"
puts $fileID "test NormDispIncr 1.0e-5    100     3"
puts $fileID "#\n#Create the solution algorithm"
puts $fileID "algorithm NewtonLineSearch";
puts $fileID "#\n#Create damping"

# creating damping
puts $fileID {set ww [eigen 2]}
puts $fileID {set wi [expr sqrt([lindex $ww 0])]}
puts $fileID {set wj [expr sqrt([lindex $ww 1])]}

puts $fileID "set xi $dr; # damping coefficient in the first 2 modes"
puts $fileID {set alpha [expr $xi*(2*$wi*$wj)/($wi+$wj)]}
puts $fileID {set beta  [expr $xi*(2)/($wi+$wj)]}


puts $fileID {puts "w_1 = $wi rad/sec"}
puts $fileID {puts "w_2 = $wj rad/sec"}

puts $fileID "#         alpa_m   beta   beta_init"
puts $fileID "rayleigh  \$alpha    0.0     \$beta     0.0"
puts $fileID "#\n#Create the system of equation storage and solver"

puts $fileID "system SparseGEN"
puts $fileID "#\n# Create the constraint handler"
puts $fileID "constraints Plain"
puts $fileID "#\n# Create integration scheme"
puts $fileID "integrator TRBDF2"
 
 
puts $fileID "#\n# Create the DOF numberer\n"
puts $fileID "numberer RCM"
puts $fileID "#\n#  Create the transient analysis"
puts $fileID "analysis Transient"

 

puts $fileID "#\n#===END OF ANALYSIS GENERATION========================================================="
puts $fileID "#\n# set some variables"
puts $fileID "set dt 0.001" ; # time step for the dynamic analysis
set f_len [open [concat $name/gm_length.out] "r"] ;# loading information on the length of ground motion files
set q [read $f_len]
close $f_len
puts $fileID "set record_length $q"

puts $fileID {set tFinal [expr  $record_length * 0.005]};# the points in the ground motion file have a dt of 0.005s    

puts $fileID {set tCurrent [getTime]}
puts $fileID "set ok 0"
puts $fileID "#\n# Perform the transient analysis"
puts $fileID "while {\$ok == 0 && \$tCurrent < \$tFinal} {"
puts $fileID " "    
puts $fileID {    set ok [analyze 1 $dt]}
puts $fileID {    puts [getTime]}
# setting up alternate analysis options if the analysis fails
puts $fileID "\n    # if the analysis fails try initial tangent iteration"
puts $fileID "    if {\$ok != 0} {"
puts $fileID {	puts "regular time step failed .. lets try a smaller step and a less stringent test"}
puts $fileID "	test NormDispIncr 1.0e-1  165 1"
puts $fileID {	set ok [analyze 1 [expr $dt*.02]]}
puts $fileID "	if {\$ok == 0} {puts \"that worked .. back to regular time step and test criteria\"}"
puts $fileID "	test NormDispIncr 1.0e-4  100 3 "
puts $fileID "    }\n"

puts $fileID "   if {\$ok != 0 } {      ;					# analysis was not successful."
puts $fileID {puts "here"}
puts $fileID "# --------------------------------------------------------------------------------------------------"
puts $fileID "# change some analysis parameters to achieve convergence"
puts $fileID "# performance is slower inside this loop"
puts $fileID "#    Time-controlled analysis"
puts $fileID "set ok 0"
puts $fileID "set DtAnalysis .0001"
puts $fileID "	set Tol .1"
puts $fileID "set algorithmTypeDynamic NewtonLineSearch"
puts $fileID {set controlTime [getTime]}
puts $fileID "while {\$controlTime < \$tFinal && \$ok == 0} {"
puts $fileID {		set controlTime [getTime]}
puts $fileID {		set ok [analyze 1 $DtAnalysis]}
puts $fileID "		if {\$ok != 0} {"
puts $fileID {puts "Trying Newton with Initial Tangent .."}
puts $fileID "			test NormDispIncr   \$Tol 100  0"
puts $fileID "			algorithm Newton -initial"
puts $fileID {			set ok [analyze 1 $DtAnalysis]}
puts $fileID "			test NormDispIncr 1e-1 165  0"
puts $fileID "			algorithm \$algorithmTypeDynamic"
puts $fileID "		}"
puts $fileID "		if {\$ok != 0} {"
puts $fileID {			puts "Trying Broyden .."}
puts $fileID "			algorithm Broyden 8"
puts $fileID {			set ok [analyze 1 $DtAnalysis]}
puts $fileID "			algorithm \$algorithmTypeDynamic"
puts $fileID "		}"
puts $fileID "		if {\$ok != 0} { "
puts $fileID {			puts "Trying NewtonWithLineSearch .."}
puts $fileID "			algorithm NewtonLineSearch .8"
puts $fileID {			set ok [analyze 1 $DtAnalysis]}
puts $fileID {			algorithm $algorithmTypeDynamic}
puts $fileID "		}"
puts $fileID "	}"
puts $fileID "	}"

    
puts $fileID {    set tCurrent [getTime]}
puts $fileID "}\n"

puts $fileID "# Print a message to indicate if analysis succesfull or not"
puts $fileID "if {\$ok == 0} {"
puts $fileID {   puts "################################################"}
puts $fileID {   puts "Transient analysis completed SUCCESSFULLY";}
puts $fileID {   puts "################################################"}
puts $fileID "} else {"
puts $fileID {   puts "################################################"}
puts $fileID {   puts "Transient analysis FAILED";    }
puts $fileID {   puts "################################################"}

# creating a .fail file for cases that do not converge. The .fail file has the 
# analysis flag and the time at which the solution stopped converging
puts $fileID {   set fail_file [open [concat $name.fail] w]}
puts $fileID {   puts $fail_file "The time at which we failed is $tCurrent seconds."}
puts $fileID {   close $fail_file}
puts $fileID "}\n"

puts $fileID {set endt [clock clicks -milliseconds]}
puts $fileID {set totaltime [expr ($endt-$begin)]}
puts $fileID {set totaltimem [expr ($endt-$begin)/60000.0]}
puts $fileID " "
puts $fileID {puts "Time in hours: [expr $totaltimem/60.]"}
puts $fileID {puts "$totaltimem is the total time in minutes"}