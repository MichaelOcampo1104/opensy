# =========================================================================
# This procedure is used to concisely define groups of similar elements. 
#
# Input Arguments:
#     eType = type of OpenSees element (can be modified as indicated below)
#     eT    = element ID tag(s)
#     iN    = element iNode(s)
#     jN    = element jNode(s)
#     args  = additional OpenSees element arguments (element-specific)

proc DefineElements {eType eT iN jN args} {;        # begin procedure
   set mF 0;                                        # modifier flag
   if {$eType == "zeroLength-IMK"} {;               # rotSpring2DModIKModel
      set eType "zeroLength"; set mF 1;             # IMK spring model
   } elseif {$eType == "zeroLength-SBL"} {;         # ZLS bridge element
      set eType "zeroLength"; set mF 2;             # conn. bridge left
   } elseif {$eType == "zeroLength-SBR"} {;         # ZLS bridge element
      set eType "zeroLength"; set mF 3;             # conn. bridge right
   };                                               # end if
   for {set N 0} {$N<[llength $eT]} {incr N} {;     # loop through elements
      set eleTag [lindex $eT $N];                   # element ID tag
      set iNd [lindex $iN $N];                      # element iNode
      set jNd [lindex $jN $N];                      # element jNode
      set vars [list];                              # empty argument list
      for {set n 0} {$n<[llength $args]} {incr n} {;# loop through args
         set argn [lindex $args $n];                # current argument
         if {[llength $argn]>1} {;                  # if curr. arg. is list
            lappend vars [lindex $argn $N];         # index and append vars
         } else {;                                  # else
            lappend vars $argn;                     # append arg. to vars
         };                                         # end if
      };                                            # end for
      element $eType $eleTag $iNd $jNd {*}$vars;    # create the element
      if {$mF==1} {equalDOF $iNd $jNd 1 2};         # IMK equalDOF
      if {$mF==2} {equalDOF $iNd [expr $jNd-1] 2 3};# SBL equalDOF
      if {$mF==3} {equalDOF [expr $iNd+1] $jNd 2 3};# SBR equalDOF
   };                                               # end for
};                                                  # end procedure
# =========================================================================