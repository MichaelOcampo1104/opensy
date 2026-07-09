#########################################################################
# Build the wall element								#
# Author: Kuanshi Zhong									#
# Email: kuanhsi@stanford.edu								#
# Date: 02/2017										#	
#########################################################################
#
#########################################################################
# Parent:	1. BuildWallModelMainMP.tcl
# Calling:	None
# Input:	None
#########################################################################
#
proc RCWallElement {node1Tag node2Tag eleStartTag numEle numIntgrPts eleType secTag} {

	# Define two node tags for fixed-end and free-end
	set nodeStartTag [expr $node1Tag+10000]; # fixed

	# Define fiber element
	set transfTag	$secTag
	geomTransf PDelta $transfTag
	for {set i 1} {$i <= $numEle} {incr i 1} {
  		if {$eleType == "force"} {
			if {$i == 1} {
				element forceBeamColumn [expr $eleStartTag+$i-1] $node1Tag $node2Tag $numIntgrPts $secTag $transfTag -integration NewtonCotes;
			} else {
				if {$i < $numEle} {
					element forceBeamColumn [expr $eleStartTag+$i-1] [expr $nodeStartTag+$i-1] [expr $nodeStartTag+$i] $numIntgrPts $secTag $transfTag -iter 1000 1E-6 -integration NewtonCotes;
				} else {
					element forceBeamColumn [expr $eleStartTag+$i-1] [expr $nodeStartTag+$i-1] $node2Tag $numIntgrPts $secTag $transfTag -iter 1000 1E-6 -integration NewtonCotes;
				}
			}
		} else {
			if {$i == 1} {
				element dispBeamColumn [expr $eleStartTag+$i-1] $node1Tag [expr $nodeStartTag+$i-1] $numIntgrPts $secTag $transfTag;
			} else {
				if {$i < $numElem} {
					element dispBeamColumn [expr $eleStartTag+$i-1] [expr $nodeStartTag+$i-1] [expr $nodeStartTag+$i] $numIntgrPts $secTag $transfTag;
				} else {
					element dispBeamColumn [expr $eleStartTag+$i-1] [expr $nodeStartTag+$i-1] $node2Tag $numIntgrPts $secTag $transfTag;
				}
			}
		}
	}
}