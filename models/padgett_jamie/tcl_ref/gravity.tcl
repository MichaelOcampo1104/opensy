# this code assigns gravity loads to the nodes in the finite element model


puts $fileID "#\n#=========================================================================="
puts $fileID "#                       DEFINE GRAVITY and TRUCK LOADS"
puts $fileID "#==========================================================================\n#"



set n 1001

puts $fileID "#\npattern Plain 1 \"Linear\" {"
puts $fileID "#           Node     X   Y     Z   Mx   My   Mz"


puts $fileID "#======================================================================================"
puts $fileID "#              DECK WEIGHT"
puts $fileID "#======================================================================================"  
set n 10000

# assigning gravity loads to each of the deck nodes
for {set i 0} {$i < $spans} {incr i 1} {; # for each span

set deck_wt [expr -$dm(0)*384.6]; # mass times gravity, negative sign for downward direction of the load  
 
 
	puts $fileID "#       DECK NUMBER [expr $i+1]"
	for {set j 0} {$j < [expr $div($i)-1]} {incr j 1} {; # for all nodes on a girder
    set z [expr -$width/2.0]
  
    
    for {set k 0} {$k < $n_trans} {incr k 1} {; # for each girder
		  set n [expr $n+1]
		  

		  puts $fileID "load $n 0.0 $deck_wt 0 0 0 0" ; # load applied in 'y' direction (downward)
      
    }

	}
  
}


puts $fileID "#======================================================================================"
puts $fileID "#              BENT CAP WEIGHT"
puts $fileID "#======================================================================================"
# The total mass of the bent cap is 3.5' x 4.0 ' and has a mass of 0.0004529 k-s^2/in per inch
# and a mass of 0.03397 k-s^2/in per 75" section.
# the weight assigned to bent nodes is scaled according the the spacing between the girders (gd_spc) and the cross section area of the bridge bent (bWidth*bDepth)
puts $fileID "set  bcm   \[expr -386.4*($gd_spc/75.)*(\$bWidth*\$bDepth)*0.03397/(3.5*4.0*144)]  ; # bent cap mass for 75 inch section (k-s^2/in)"; # scaling for girder spacing (which govern the node spacing on the bent) and cross section area
puts $fileID {set  bcm2   [expr $bcm/2.] ; ; # nodes at the edge are assigned half the weight 
set n [expr 500 + 3*$gd]

for {set i 1} {$i < $spans} {incr i 1} {
	puts $fileID "#\n#          Bent No. [expr $i+1]"
	puts $fileID "#       node X-mass   Y-mass   Z-mass   MX-mass  MY-mass  MZ-mass"

	set n [expr $n+1]
	puts $fileID "load $n 0 \$bcm2  0 0 0 0"
	for {set j 1} {$j < [expr $gd-1]} {incr j 1} {
		set n [expr $n+1]
		puts $fileID "load $n 0 \$bcm  0 0 0 0"
	}
	set n [expr $n+1]
	puts $fileID "load $n 0 \$bcm2  0 0 0 0"
	set n [expr $n + $gd]
}

puts $fileID "#======================================================================================"
puts $fileID "#              COLUMN WEIGHT"
puts $fileID "#======================================================================================"
# A 36" diameter column has a mass of 0.000229 k-s^2/in per inch
# Weight for a column with different diameter is scaled arrording to the ratio of cross-section area 
puts $fileID "set  colm   [expr -386.4*($D*$D/(36.*36.))*0.000229*$ch/3.]  ; # column mass for [expr $ch/3.] inch section (k-s^2/in)"; # scaling the weight of the column according to the cross section and the length of the column element
puts $fileID {set  colm2   [expr $colm/2.] ; # column weight for [expr $ch/6.] inch section (k-s^2/in)}  -- used for elements that are half the length of the regular column elements
set n [expr 1050]
set q 0
#

for {set i 1} {$i < $spans} {incr i 1} {
	for {set j 0} {$j < $bn} {incr j 1} {
	puts $fileID "#\n#    Bent No. $i, Column No. [expr $j+1]"
	puts $fileID "#       node X-mass   Y-mass   Z-mass   MX-mass  MY-mass  MZ-mass"
	set n [expr $n+1]
	puts $fileID "load $n 0 \$colm2  0  0  0  0"
	set n [expr $n+1]
	puts $fileID "load $n 0 \$colm  0  0  0  0"
	set n [expr $n+1]
	puts $fileID "load $n 0 \$colm  0  0  0  0"
	set n [expr $n+5]
	puts $fileID "load $n 0 \$colm2  0  0  0  0"
	puts $fileID "#==================================================================="
	set q [expr $q+1]
	set n [expr 1050 + $q*50]
	}
} 

  
puts $fileID "}"





# performing gravity analysis in 5 steps with 0.2 load increment
puts $fileID "#\n#=========================================================================="
puts $fileID "#             START OF ANALYSIS GENERATION FOR GRAVITY ANALYSIS"
puts $fileID "#==========================================================================\n#"
puts $fileID "# Create the convergence test"
puts $fileID "test NormDispIncr 1.0e-6    100     1"
puts $fileID "system SparseGEN"
puts $fileID "#\nalgorithm  NewtonLineSearch\n#\nintegrator LoadControl   .2   1  .2   .2"
puts $fileID "#\nnumberer   RCM\n#\nconstraints Plain\n#\nanalysis Static"
puts $fileID "#\n#=========================================================================="
puts $fileID "#             PERFORM GRAVITY LOAD ANALYSIS"
puts $fileID "#==========================================================================\n#"
puts $fileID {set ok [analyze 5]}
puts $fileID "#\nloadConst -time 0.0\n#"
puts $fileID {puts "################################################"}
puts $fileID {puts "Gravity Analysis Complete"}
puts $fileID {puts "################################################"}

# writing the result flag corresponding for the gravity analysis
puts $fileID {set ok_file [open [concat $name/ok.out] w ]}
puts $fileID {puts $ok_file "$ok"}
puts $fileID {close $ok_file}