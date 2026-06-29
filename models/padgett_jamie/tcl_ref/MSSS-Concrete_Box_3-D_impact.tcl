# this code defines the impact element that are introduced between the bridge decks to model pounding
# details of the impact elements can be found in: 
# Muthukumar, S. and DesRoches, R., 2006. A Hertz contact model with non-linear
# damping for pounding simulation. Earthquake engineering & structural dynamics, 35(7), pp.811-828.

puts $fileID "#\n#=========================================================================="
puts $fileID "#        GENERATE MATERIAL AND ELEMENTS FOR IMPACT OF DECKS"
puts $fileID "#==========================================================================\n#"
puts $fileID "#"
puts $fileID "set gap1 -$gap1"
puts $fileID "set gap2 -$gap2"
puts $fileID "set gap3 -$gap3"
puts $fileID "set gap4 -$gap4"
puts $fileID "#\n#     				tag       K         Fy      gap"
puts $fileID {uniaxialMaterial ElasticPPGap 402      6368    -637     [expr $gap1]}
puts $fileID {uniaxialMaterial ElasticPPGap 403      2190    -9e9     [expr $gap1-0.1418]}

puts $fileID {uniaxialMaterial ElasticPPGap 404      6368    -637     [expr $gap2]}
puts $fileID {uniaxialMaterial ElasticPPGap 405      2190    -9e9     [expr $gap2-0.1418]}

puts $fileID {uniaxialMaterial ElasticPPGap 406      6368    -637     [expr $gap3]}
puts $fileID {uniaxialMaterial ElasticPPGap 407      2190    -9e9     [expr $gap3-0.1418]}

puts $fileID {uniaxialMaterial ElasticPPGap 408      6368    -637     [expr $gap4]}
puts $fileID {uniaxialMaterial ElasticPPGap 409      2190    -9e9     [expr $gap4-0.1418]}

puts $fileID "#\n# Combine them"

puts $fileID "uniaxialMaterial Parallel  131   402   403; # Left Abutment gap"
puts $fileID "uniaxialMaterial Parallel  132   404   405; # Right Abutment gap"
puts $fileID "uniaxialMaterial Parallel  133   406   407; # Left Hinge gap"
puts $fileID "uniaxialMaterial Parallel  134   408   409; # Right Hinge gap"

# impact element between the deck and the abutments
set n 14000
set m [expr 500+$gd]
set p 12000

for {set i 0} {$i < 2} {incr i 1} {
	puts $fileID "#\n#      Abutment No. [expr $i+1] - Impact"
	puts $fileID "#                      tag  i-node j-node material               X"
	for {set j 0} {$j < $gd} {incr j 1} {
		set n [expr $n +1 ]	
		set m [expr $m + 1]
		set p [expr $p + 1]
		if {$i == 0} {
			puts $fileID [format "%-8s %-11s %5d %5d %5d  %6s  %5d %6s %5d" element zeroLength $n $m $p  -mat 131 -dir 1]
		} else {
			puts $fileID [format "%-8s %-11s %5d %5d %5d  %6s  %5d %6s %5d" element zeroLength $n $m $p  -mat 132 -dir 1]
		}
	}
	set p [expr 500 +$gd*2*$spans]
	set m [expr 12000 + (2*$spans -1)*$gd]
}

# impact elements between the decks

set m [expr 12000 + $gd]

for {set i 0} {$i < [expr $spans-1]} {incr i 1} {
	puts $fileID "#\n#      Bent No. [expr $i+1] - Impact"
	puts $fileID "#                      tag  i-node j-node material               X"
	for {set j 0} {$j < $gd} {incr j 1} {
		set n [expr $n +1 ]	
		set m [expr $m + 1]
		set p [expr $m + $gd]
		if {$i == 0} {
			puts $fileID [format "%-8s %-11s %5d %5d %5d  %6s  %5d %6s %5d" element zeroLength $n $m $p  -mat 133 -dir 1]
		} else {
			puts $fileID [format "%-8s %-11s %5d %5d %5d  %6s  %5d %6s %5d" element zeroLength $n $m $p  -mat 134 -dir 1]
		}
	}
	set m [expr $m +$gd]
}



