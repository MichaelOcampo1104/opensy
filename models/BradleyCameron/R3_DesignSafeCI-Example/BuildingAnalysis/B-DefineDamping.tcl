# =========================================================================
# This script is used to calculate the eigenvalues of the building system
# and use those values to both determine the natrual structural periods and
# assign damping to specified elements using Modal or Rayleigh methods.

## Eigenvalue analysis        
set pi [expr 2.0*asin(1.0)];                        # define pi
set nEigenJ 3;                                      # num. of modes to get
set j 3;                                            # jth eigen mode
set lambdaN [eigen -fullGenLapack $nEigenJ];        # eigenvalue analysis

## Calculate natural frequencies and periods
set wn {}; set Tn {};                               # create empty lists
WriteToLog $out "Natural Structural Periods:";      # comment in log file
for {set i 0} {$i < $j} {incr i} {;                 # loop eigenvalues
   set lambda [lindex $lambdaN $i];                 # ith eigenvalue
   lappend wn [expr pow($lambda,0.5)];              # natural frequencies
   lappend Tn [expr 2.0*$pi/[lindex $wn $i]];       # natural periods
   set Tni [format "%.3fs" [lindex $Tn $i]];        # format nat. periods
   WriteToLog $out "T[expr $i+1] = $Tni";           # record nat. periods
};                                                  # end for

## Define damping
if {$dampType == "Modal"} {;                        # modal damping
   eigen 3;                                         # calculate eigenvalues
   modalDamping $zeta;                              # define damping
} elseif {$dampType == "Rayleigh"} {;               # rayleigh damping
   set wi [lindex $wn 0];                           # 1st mode circ. freq.
   set wj [lindex $wn [expr $j-1]];                 # jth mode circ. freq.
   set a0 [expr $zeta*2.0*$wi*$wj/($wi + $wj)];     # mass damping coeff. 
   set a1 [expr $zeta*2.0/($wi + $wj)];             # stiffness damping 
   set a1_mod [expr $a1*(1.0+$n)/$n];               # mod. stiff damping 
   source "$bld-Regions.tcl";                       # define damping region
};                                                  # end if
# =========================================================================