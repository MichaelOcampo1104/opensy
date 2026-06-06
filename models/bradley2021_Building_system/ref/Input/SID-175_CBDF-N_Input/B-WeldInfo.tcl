# =========================================================================
# This script obtains the local forces of the rigid elements at the lower
# end of the braces, and uses those values to calculate weld DCRs. In
# addition, this script defines several variables that contain information
# about the weld elements including element tags, start and end node tags,
# and tags of the materials that are used to replace the material of
# fractured weld elements.
 
## Get the weld force parallel to the brace (local-x direction)
scan [eleResponse 845 localForce] "%s" BR1
scan [eleResponse 857 localForce] "%s" BR2
scan [eleResponse 869 localForce] "%s" BR3
scan [eleResponse 881 localForce] "%s" BR4
scan [eleResponse 893 localForce] "%s" BR5
scan [eleResponse 905 localForce] "%s" BR6
 
## Calculate weld demand-to-capacity ratios
set WeldDCRs [list \
   [expr abs($BR1)/(2.895602e+02*1.40)] \
   [expr abs($BR2)/(2.301633e+02*1.40)] \
   [expr abs($BR3)/(1.336432e+02*1.40)] \
   [expr abs($BR4)/(2.895602e+02*1.40)] \
   [expr abs($BR5)/(2.301633e+02*1.40)] \
   [expr abs($BR6)/(1.336432e+02*1.40)] \
]
 
## Define variables containing weld element information
set WeldEles    [list 846 858 870 882 894 906]
set iNodes      [list 812 823 834 845 856 867]
set jNodes      [list 813 824 835 846 857 868]
set WeldMat     [list 8 7 6 5 4 3 2 1]
set WeldStories [list 1 2 3 1 2 3]
set WeldSides   [list "left" "left" "left" "right" "right" "right"]
# =========================================================================
