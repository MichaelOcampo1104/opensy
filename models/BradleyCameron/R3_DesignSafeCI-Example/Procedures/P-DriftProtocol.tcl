# =========================================================================
# This procedure creates a list of analysis displacement targets to reflect
# the specified protocol "p" based on a list of drift targets "t", assuming
# "nStep" analysis incremenets between each target. The optional argument
# "cT" allows for the cycle type to be defined as "half" or "full", where
# half cycle displacements alternate between zero and the peak targets.

proc DriftProtocol {t p {nStep 1} {cT "full"}} {;   # begin procedure
   set nCycs [expr [llength $t]/2];                 # no. of targets
   if {$p == "FEMA350"} {;                          # FEMA 350/AISC 341
      set cycs [list 6 6 6 4]; set addCycs 2;       # cycles per target
   } elseif {$p == "FEMA461"} {;                    # FEMA 461
      set cycs [list 1 1 1 1]; set addCycs 1;       # cycles per target
   };                                               # end if
   while {[llength $cycs] < $nCycs} {;              # if cycles < targets
      lappend cycs $addCycs;                        # append to cycles
   };                                               # end while
   for {set i 1} {$i <= $nCycs} {incr i} {;         # loop thru cycle group
      if {$cT == "full"} {      set j [expr $i*2-2];# target counter
      } elseif {$cT == "half"} {set j [expr $i-1]}; # target counter
      set nc [lindex $cycs $i-1];                   # no. cycles for tar.
      set d1 [expr [lindex $t $j]/$nStep];          # positive target
      set d2 [expr -1*$d1];                         # zero target
      set d3 [expr [lindex $t $j+1]/$nStep];        # negative target
      set d4 [expr -1*$d3];                         # zero target
      for {set cyc 1} {$cyc<=$nc} {incr cyc} {;     # loop no. cycles
         if {$nStep != 1 && $cT != "half"} {;       # if half cycles
            lappend dTars $d1 $d2 $d3 $d4;          # append to targets
         } else {;                                  # if full cycles
            lappend dTars $d1 $d2;                  # append to targets
         };                                         # end if
      };                                            # end for
   };                                               # end for
   return $dTars;                                   # return index of max
};                                                  # end procedure
# =========================================================================