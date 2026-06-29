# this code creates elements for the abutments
# for details on material models refer: Nielson (2005) -  Analytical fragility curves for highway bridges in moderate seismic zones
puts $fileID "#\n#=========================================================================="
puts $fileID "#        GENERATE MATERIAL AND ELEMENTS FOR ABUTMENTS"
puts $fileID "#==========================================================================\n#"


# backfill model
# Assume an 8' tall backwall,  All the  calculations are for a section with width gd_spc (girder spacing)
set k_soil       [expr $st_abp*12]; # kips/in/ft
set k1p [expr $k_soil*$gd_spc/12.]; # Initial passive soil pressure (kips/in) for a section with width = gd_spc
set D3p [expr (0.06+(($k_soil-20.)/(50.-20.))*0.04)*96.]
set D1p [expr 0.1*$D3p]
set D2p [expr 0.35*$D3p]
set f1p [expr $k1p*$D1p]
set f3p [expr 7.7*(8)*($gd_spc/12.)]; # for 7.7 ksf soil pressure and 8' wall - units are (kips)
set f2p [expr (0.45)*$f1p+(0.55)*$f3p]
set k2p [expr (0.55*($f3p-$f1p))/0.25/$D3p]
set k3p [expr (0.45*($f3p-$f1p))/0.65/$D3p]

set f2  [expr 0.55*($f3p-$f1p)]
set f3  [expr 0.45*($f3p-$f1p)]

puts $fileID "#\n#     Passive Soil Contribution per 75 in width (1 - girder) of deck"
puts $fileID "set   s1   $f1p"
puts $fileID "set   e1   $D1p"
puts $fileID "set   s2   $f2p"
puts $fileID "set   e2   $D2p"
puts $fileID "set   s3   $f2p"
puts $fileID "set   e3   $D3p"

puts $fileID "#\n#                             tag   s1p   e1p   s2p   e2p   s3p   e3p   s1n   e1n   s2n   e2n   s3n   e3n     px    py    d1    d2  beta"
puts $fileID {uniaxialMaterial Hysteretic    500  $s1   $e1   $s2   $e2   $s3   $e3  -$s1  -$e1  -$s2  -$e2  -$s3  -$e3    1.0   0.0   0.0   0.0  0.0}
puts $fileID "uniaxialMaterial ElasticPPGap  501  $k3p   [expr $f2p-$f3p]   -$D2p"
puts $fileID "uniaxialMaterial Parallel      502  500 501"
puts $fileID "uniaxialMaterial ENT           503  1e8"
puts $fileID "uniaxialMaterial Series        504  502 503"
# 
#  Assume, based off of existing plans, that the spacing between abutment piles is 62.5 inches
#  each pile has an effective stiffness of 40 kips/in and an ultimate load of 40 kips.
#
set k_pile $st_aba; # kips/in per pile
set keff [expr $k_pile*($gd_spc/62.5)]; # 75" width of deck ==> 1.2 piles
set k1a  [expr $keff*2.33]
set k2a  [expr $keff*0.428]
set D2a  1; # (inches) this is an assumed value
set D1a  [expr $D2a*0.3]
set f1a  [expr $k1a*$D1a]
set f2a  [expr (0.7*$D2a)*$k2a]
puts $fileID "#\n#   Pile Portion (for longitudinal and transverse) for 75 in. width\n#"       
puts $fileID "set   s1   $f1a"
puts $fileID "set   e1   $D1a"
puts $fileID "set   s2   [expr $f2a+$f1a]"
puts $fileID "set   e2   $D2a"
puts $fileID "set   s3   [expr $f2a+$f1a]"
puts $fileID "set   e3   [expr 2*$D2a] "
# model for pile
puts $fileID "#                           tag   s1p   e1p   s2p   e2p   s3p   e3p   s1n   e1n   s2n   e2n   s3n   e3n     px    py    d1    d2  beta"
puts $fileID {uniaxialMaterial Hysteretic  10   $s1   $e1   $s2   $e2   $s3   $e3  -$s1  -$e1  -$s2  -$e2  -$s3  -$e3   0.75   0.5   0.0   0.0   0.1}

puts $fileID "#\n#  Combine them in parallel\n#"
puts $fileID "uniaxialMaterial Parallel  9   504 10; #  Abutment Longitudinal  "

set n 7000
set m 500

for {set i 0} {$i < 2} {incr i 1} {
	puts $fileID "#\n#      Abutment No. [expr $i+1] - Soil_Pile Springs"
	puts $fileID "#                      tag  i-node j-node material               X"
	for {set j 0} {$j < $gd} {incr j 1} {
		set n [expr $n + 1]	
		set m [expr $m + 1]
		set p [expr $m + $gd]
		puts $fileID "element zeroLength $n $m $p  -mat 9 10 -dir 1 3"
	}
	set m [expr 500 + 2*$spans*$gd]
}
