# this code defines the rigid links that are included in the bent and at the ends of columns
puts $fileID "#\n#=========================================================================="
puts $fileID "#                       RIGID LINKS"
puts $fileID "#==========================================================================\n#"
puts $fileID "#                  TAG   Xv  Yv  Zv"
puts $fileID "geomTransf Linear   6    1   0   0"

# these rigid links are incorporated to ensure that the deck is situated at the correct height in the finite element model
set n 9000
set mnode [expr 500+2*$gd]
set snode [expr $mnode +$gd]
puts $fileID "#\n# Links at the bent caps."
for {set i 0} {$i < [expr $spans-1]} {incr i 1} {
	puts $fileID "#    Bent No. [expr $i+1]"
	puts $fileID "#                          Tag     iN    jN     A      E      G     J      Iz     Iy    Transf"
	for {set j 0} {$j < $gd} {incr j 1} {
		set n [expr $n + 1]		
		set mnode [expr $mnode+1]
		set snode [expr $mnode +$gd]
		puts $fileID [format "%-7s %-17s %5d %5d %5d %6s %6s %6s %6s %6s %6s %5d" element elasticBeamColumn $n $mnode $snode \$Atd \$Etd \$Gtd \$Jtd \$Itd \$Itd 6]
	}
	set mnode [expr $mnode+$gd]
} 

# rigid links are provided at the base and at top of columns to mimic the rigid connection with the bent and the pile cap
set q 0
puts $fileID "#\n# Links at the column tops."
for {set i 0} {$i < [expr $spans-1]} {incr i 1} {
	puts $fileID "#    Bent No. [expr $i+1]"
	for {set j 0} {$j < $bn} {incr j 1} {
		set q [expr $q+1]
		set n [expr $n + 1]
		set mnode [expr 1000+$q*50]
		set snode [expr $mnode + 1]
		puts $fileID [format "%-7s %-17s %5d %5d %5d %6s %6s %6s %6s %6s %6s %5d" element elasticBeamColumn $n $mnode $snode \$Atd \$Etd \$Gtd \$Jtd \$Itd \$Itd 6]
	}
}
set q 0
set mnode 7999
set snode 1008
puts $fileID "#\n# Links at the column bases."
for {set i 0} {$i < [expr $spans-1]} {incr i 1} {
	puts $fileID "#    Bent No. [expr $i+1]"
	for {set j 0} {$j < $bn} {incr j 1} {
  puts $fileID {puts "*************************** ok till here ****************************"} 
		set n [expr $n + 1]
		set snode [expr $snode + 50]
		set mnode [expr $mnode + 2]
		puts $fileID [format "%-7s %-17s %5d %5d %5d %6s %6s %6s %6s %6s %6s %5d" element elasticBeamColumn $n $mnode $snode \$Atd \$Etd \$Gtd \$Jtd \$Itd \$Itd 6]
	}
}
