# =========================================================================
# This script is used to model the force-deformation behavior of a single 
# bolted-bolted angle subject to a tension force on the outstanding leg. 
# The model uses a zeroLengthSection Fiber section and experimentally 
# calibrated material properties reported by Beland et al. (2019). 
#  _
# | |   Note: This model assumes the vertical leg of the angle is connected
# | |         to a perfectly rigid member (e.g., a stiff column), a single
# |X|         fiber is located at the heel of the angle, and the load is
# | |         applied in the positive x-direction only.
# | |_______________
# |______X_____X____| ---> Applied Tension

## Source procedures 
set root "/Users/Cameron/Desktop/PhD/Modeling";     # root directory
set prc "$root/SharedFiles/OpenSees/Procedures/";   # procedure directory
foreach f [glob -dir "$prc" *.tcl] {source $f};     # source procedures

## Set up output directory
set out "../Output/Scaled/";                        # output directory path
MakeOutDir $out;                                    # make output directory

## Build the model and run analyses
set cycles [list]
for {set TC 1} {$TC<=19} {incr TC} {;               # loop thru test cases
   wipe;                                            # wipe any prev. model
   model basic -ndm 2 -ndf 3;                       # 2D, 3 DOF (1,2,6)
   source "A-DriftTargets.tcl";                     # define drift targets
   source "A-Materials-S.tcl";                      # load angle materials 
   set AngleMat [expr $TC*4+15];                    # define angle material
   section Fiber 1 {;                               # start fiber section
      fiber 0.0 0.0 1.0 $AngleMat;                  # single angle fiber
      layer straight 2 2 1e-9 -1.0 0 1.0 0};        # for num. stability
   section Aggregator 2 1 Vy -section 1;            # stiff shear material
   recorder Node -file "$out/TC$TC.txt" -time \
      -node 2 -dof 1 2 3 disp;                      # create the recorder
   ZLSAnalysis 2 "FD" $driftTargets "half";         # analyze the section
};                                                  # end for
# =========================================================================
