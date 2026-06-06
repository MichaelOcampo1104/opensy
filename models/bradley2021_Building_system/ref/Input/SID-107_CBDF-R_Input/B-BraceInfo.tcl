# =========================================================================
# This script obtains the displacments of the brace end nodes and uses those
# values to calculate brace lengths at each step. In addition this script
# defines variables containing the brace longitudinal displacement ratios.
 
set BR_LDR {}
set BRn_1 [list 813 824 835 846 857 868]
set BRn_2 [list 821 832 843 854 865 876]
for {set BRi 0} {$BRi <= 5} {incr BRi} {;
set node1 [lindex $BRn_1 $BRi]
set node2 [lindex $BRn_2 $BRi]
 
## Get brace end node original positions
set x1o [nodeCoord $node1 1]
set x2o [nodeCoord $node2 1]
set y1o [nodeCoord $node1 2]
set y2o [nodeCoord $node2 2]
 
## Get brace end node displacements
scan [nodeResponse $node1 1 1] "%s" dx1
scan [nodeResponse $node2 1 1] "%s" dx2
scan [nodeResponse $node1 2 1] "%s" dy1
scan [nodeResponse $node2 2 1] "%s" dy2
 
## Calculate brace end node current positions
set x1 [expr $x1o + $dx1]
set x2 [expr $x2o + $dx2]
set y1 [expr $y1o + $dy1]
set y2 [expr $y2o + $dy2]
 
## Calculate brace length and length ratio
if {[info exists Lo_BR] == 0 || [llength $Lo_BR] < 6} {
if {$BRi == 0} {
set Lo_BR {}
}
lappend Lo_BR [expr {hypot([expr $x2-$x1], [expr $y2-$y1])}]
}
set L_BR [expr {hypot([expr $x2-$x1], [expr $y2-$y1])}]
lappend BR_LDR [expr $L_BR/[lindex $Lo_BR $BRi]]
}
# =========================================================================
