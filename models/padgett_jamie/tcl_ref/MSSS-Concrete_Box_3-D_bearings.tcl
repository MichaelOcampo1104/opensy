# this code generates the elastomeric bearing elements
# for details on the elastomeric bearing model refer: Nielson (2005) -  Analytical fragility curves for highway bridges in moderate seismic zones
# for fixed bearings -- the simply supported spans have fixed bearings on one end and expansion bearing on the other end

puts $fileID "#\n#=========================================================================="
puts $fileID "#        GENERATE MATERIAL AND ELEMENTS FOR FIXED ELASTOMERIC BEARINGS"
puts $fileID "#==========================================================================\n#"

# set G_fac 1.
# set dowel_dec 0.

puts $fileID "uniaxialMaterial Elastic 8378 2900.0" ;# material for vertical stiffness of the bearing pad
set Gp	[expr $st_ep*$G_fac] ; # Elastomeric pad shear stiffness (ksi), modified by G-fac to account for hargening due to oxidation

#   Bearing Pad Areas and stiffness
set Ap(0) $bear_pad_area
set kpp(0) [expr $Gp*$Ap(0)/$bear_pad_d]

set Ap(1) $bear_pad_area
set kpp(1) [expr $Gp*$Ap(1)/$bear_pad_d]

set Ap(2) $bear_pad_area
set kpp(2) [expr $Gp*$Ap(2)/$bear_pad_d]

set Ap(3) $bear_pad_area
set kpp(3) [expr $Gp*$Ap(3)/$bear_pad_d]

set kp(0) $kpp([expr $brg(0)-1])
set kp(1) $kpp([expr $brg(1)-1])



set b_add_rxn [expr 0.] ; # additional vertical load on bearings (if any, could be due to pressence of trucks etc.)
set Fyp(0) [expr $cof_ep*($R(0)+$b_add_rxn)*(0.05+0.4/($R(0)/$Ap([expr $brg(0)-1])/0.145))] ; # Where 0.145 is conversion from ksi to MPa which is req'd for equation
set Fyp(1) [expr $cof_ep*($R(1)+$b_add_rxn)*(0.05+0.4/($R(1)/$Ap([expr $brg(1)-1])/0.145))] ; # Where 0.145 is conversion from ksi to MPa which is req'd for equation
 

set D_Ar_fac [expr (1-$dowel_dec)*(1-$dowel_dec)] ; # factor to be multiplied with area of dowel bar to consider decrease in area due to aging 
set dwl_str [expr $dwl_str*$D_Ar_fac]

# elastomeric bearing pads
puts $fileID "# Define uniaxialMaterial\n#  These materials define the response of the elastomeric pads"
puts $fileID "#                          Tag     Fy    Eo   b"
puts $fileID "uniaxialMaterial Steel01   203    $Fyp(0)  $kp(0)    0.0;# End spans"
puts $fileID "uniaxialMaterial Steel01   204    $Fyp(1)  $kp(1)    0.0;# Middle spans"
puts $fileID "#\n# Define uniaxialMaterial"
# Gap elements used to model gap due to difference in the diameter of the holes in the bearing pad and the diameter of the steel dowel
puts $fileID "uniaxialMaterial ElasticPPGap 200  9e5   9e10   0.125"
puts $fileID "uniaxialMaterial ElasticPPGap 202  9e5  -9e10  -0.125"

# steel dowels
puts $fileID "#\n#  This material quantifies the response of the 2 - 1 in diameter dowels\n#"
puts $fileID "uniaxialMaterial Hysteretic 201  [expr $dwl_str*2*0.965]   .048     [expr $dwl_str*2]     0.21       0    0.2101  [expr -$dwl_str*2*0.965]   -.048    [expr -$dwl_str*2]  -0.21     -0   -.2101    1.0   0.0    0.0   0.0    0.0  "
puts $fileID "# Combine them"
puts $fileID "uniaxialMaterial Parallel  5   200     202"
puts $fileID "uniaxialMaterial Series    6   201       5"
puts $fileID "#\n# Combine them"
puts $fileID "uniaxialMaterial Parallel  7   6   203; # For end spans"
puts $fileID "uniaxialMaterial Parallel  8   6   204; # For middle spans"
puts $fileID "#\n#================Generate elements===========================================\n#"

set n 500
set m [expr 500 +$gd]
set p 12000
for {set i 0} {$i < $spans} {incr i 1} {
	puts $fileID "#\n#      Fixed Bearing - Span No. [expr $i+1]\n#                     tag  i-node j-node   material             X    Z "
	for {set j 0} {$j < $gd} {incr j 1} {
		set n [expr $n + 1]
		set m [expr $m + 1]
		set p [expr $p +1]
		if {$i == 0 | $i == [expr $spans-1]} {
			puts $fileID "element zeroLength $n $m $p -mat 7 8378 7 -dir 1 2 3"
#         puts $fileID "element zeroLength $n $m $p -mat 7 7 -dir 1 3"
#         puts $fileID "equalDOF  $m $p 2"
		} else {
			puts $fileID "element zeroLength $n $m $p -mat 8 8378 8 -dir 1 2 3"
#         puts $fileID "element zeroLength $n $m $p -mat 8 8 -dir 1 3"
#       puts $fileID "equalDOF  $m $p 2"
		}
	}
	if {$i == 0} {
		set p [expr $p + $gd]
	} else {
		set m [expr $m + $gd]
		set p [expr $p + $gd]
	}
}

puts $fileID "#\n#=========================================================================="
puts $fileID "#        GENERATE MATERIAL AND ELEMENTS FOR EXPANSION ELASTOMERIC BEARINGS"
puts $fileID "#=========================================================================="
puts $fileID "# Use same pad materials 203 and 204 for end spans and middle spans respectively."
puts $fileID "#\n# Define uniaxialMaterial"
# the main difference b/w fixed and expansion bearings is in the gap specified in the two lines below
# for more details please refer: Nielson (2005) -  Analytical fragility curves for highway bridges in moderate seismic zones
puts $fileID "uniaxialMaterial ElasticPPGap 300  9e5   9e10   [expr $dwl_gap]"
puts $fileID "uniaxialMaterial ElasticPPGap 302  9e5  -9e10  [expr -1.25+$dwl_gap]"
puts $fileID "#\n#  Use same dowel material 201 as before"
puts $fileID "#\n# Combine them"
puts $fileID "uniaxialMaterial Parallel  35   300     302"
puts $fileID "uniaxialMaterial Series    36   201      35"
puts $fileID "#\n# Combine them"
puts $fileID "uniaxialMaterial Parallel  37   36   203; # For end spans"
puts $fileID "uniaxialMaterial Parallel  38   36   204; # For middle spans" 

set n 700
set m [expr 500 +2*$gd]
set p [expr 12000 + $gd]
for {set i 0} {$i < $spans} {incr i 1} {
	puts $fileID "#\n#      Expansion Bearing - Span No. [expr $i+1]\n#                     tag  i-node j-node   material             X    Z "
	for {set j 0} {$j < $gd} {incr j 1} {
		set n [expr $n + 1]
		set m [expr $m + 1]
		set p [expr $p +1]
		if {$i == 0 | $i == [expr $spans-1]} {
			puts $fileID "element zeroLength $n $m $p -mat 37 8378 7 -dir 1 2 3"

		} else {
			puts $fileID "element zeroLength $n $m $p -mat 38 8378 8 -dir 1 2 3"

		}
	}
		set m [expr $m + $gd]
		set p [expr $p + $gd]
}

