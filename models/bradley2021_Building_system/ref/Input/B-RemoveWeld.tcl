# =========================================================================
# This script removes elements representing brace-to-gusset welds from the
# model if the force in the element exceeds the specified weld capacity
# (i.e., DCR > 1.0). To improve numerical stability, the materials of the
# weld elements are modified within a loop to become progressively softer 
# until the element is effectively removed from the model. This process is 
# intended to simulate brittle fracture of a weld group without creating
# numerical instability that might prevent solution convergence.

if {[info exists WR] == 0} {set WR [list]};         # removed weld indices
if {[lsearch $WR $idx] == -1} {;                    # weld not yet removed
   
   ## Define some parameters of the welds
   lappend WR $idx;                                 # removed weld indices
   set wf 1;                                        # weld fracture flag
   set wEBC [expr [lindex $WeldEles $idx]-1];       # connected EBC element
   scan [eleResponse $wEBC localForce] "%s" wForce; # weld/axial force
   set WeldEle [lindex $WeldEles $idx];             # fractured ele. tag
   set iNode [lindex $iNodes $idx];                 # fractured ele. iNode
   set jNode [lindex $jNodes $idx];                 # fractured ele. jNode
   set nWM [llength $WeldMat];                      # no. weld materials
   set rMat1 [lindex $WeldMat 0];                   # first replacement mat
   
   ## Replace the weld elements' DOF 6 material 
   remove element $WeldEle;                         # remove weld element
   element zeroLength $WeldEle $iNode $jNode \
   -mat $rMat1 $rMat1 $rMat1 -dir 1 2 6;            # replace weld element
   system $SOE;                                     # system of eq. solver

   ## Repeatedly reduce weld element stiffness
   for {set pwr 1} {$pwr <= $nWM} {incr pwr} {;     # loop flexible mats.
      set newValue [expr 2.9*pow(10,4-$pwr)];       # modulus of elasticity
      for {set i 1} {$i <= 3} {incr i} {;           # for DOF 1, 2, 6
         parameter 1 element $WeldEle material $i E;# define modulus param.
         updateParameter 1 $newValue;               # modify modulus param.
         remove parameter 1;                        # remove modulus param.
      };                                            # end for
      source "$bldPath-AdvanceAnalysis.tcl";        # advance analysis
   };                                               # end for
   if {$bf == 1} {break};                           # break analysis loop

   ## If analysis advanced successfully
   LogNotes $kind $wForce;                          # log and proceed
   system $SOE;                                     # system of equations
   set wf 0;                                        # weld fracture flag
}
# =========================================================================