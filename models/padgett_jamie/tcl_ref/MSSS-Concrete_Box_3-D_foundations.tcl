# This code generates the foundation elements - modeled as springs

puts $fileID "#\n#=========================================================================="
puts $fileID "#        GENERATE MATERIAL AND ELEMENTS FOR FOUNDATIONS"
puts $fileID "#==========================================================================\n#"

# 
#  Assuming that each column is suppoorted by a pile group containing 8 piles.
#  Each pile has an effective stiffness of 40 kips/in and an ultimate load of 40 kips.
#  For parameters and details refer to Nielson 2005: Analytical fragility curves for highway bridges in moderate seismic zones

set n_pile	8
set k_pile $trns_fnd; # kips/in per pile
set k1_fnd  [expr $k_pile*2.33*$n_pile]
set k2_fnd  [expr $k_pile*0.428*$n_pile]
set f1_fnd  [expr $k1_fnd*$D1a]
set f2_fnd  [expr (0.7*$D2a)*$k2_fnd]
puts $fileID "#\n#   Foundation Springs - Translational and Rotationaln#"       
puts $fileID "#				          tag       K       Fy       gap"
puts $fileID [format "%-17s %-13s %5d %8.1f %8.1f %8.3f" uniaxialMaterial ElasticPPGap 701 $k1_fnd -$f1_fnd  0.0]
puts $fileID [format "%-17s %-13s %5d %8.1f %8.1f %8.3f" uniaxialMaterial ElasticPPGap 702 $k2_fnd -$f2_fnd  -$D1a]
puts $fileID [format "%-17s %-13s %5d %8.1f %8.1f %8.3f" uniaxialMaterial ElasticPPGap 703 $k1_fnd $f1_fnd  0.0]
puts $fileID [format "%-17s %-13s %5d %8.1f %8.1f %8.3f" uniaxialMaterial ElasticPPGap 704 $k2_fnd $f2_fnd  $D1a]

puts $fileID "#\n#  Combine them in parallel\n#"
puts $fileID "uniaxialMaterial Parallel 15   701 702 703 704; #  Foundation - Translational spring (k/in) "

set lever_arm [expr 30.0]
set kfndr   [expr $rot_fnd*6*$lever_arm*$lever_arm]; # Rotational stiffness per pile cap (kin-in/rad)
puts $fileID "# Rotational stiffness"
puts $fileID "uniaxialMaterial Elastic  16    $kfndr     ; # kip-in/rad"

set n 8000
set m 7999

for {set i 0} {$i < [expr $spans-1]} {incr i 1} {
	puts $fileID "#\n#      Bent No. [expr $i+1] - Foundation Springs"
	puts $fileID "#                      tag  i-node j-node material                       X   Z  Mx  Mz"
	for {set j 0} {$j < $bn} {incr j 1} {
		set n [expr $n + 1]	
		set m [expr $m + 2]
		set p [expr $m + 1]
        # The vertical and the torsional degrees of freedom are restrained so the springs are only provided in remaining directions
		puts $fileID [format "%-8s %-11s %5d %5d %5d  %6s  %3d %3d %3d %3d %6s %3d %3d %3d %3d" element zeroLength $n $m $p  -mat 15 15 16 16 -dir 1 3 4 6]
	}
}
