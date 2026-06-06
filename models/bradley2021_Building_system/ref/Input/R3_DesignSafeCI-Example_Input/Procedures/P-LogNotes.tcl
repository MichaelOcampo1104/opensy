# =========================================================================
# This procedure is used to log key analysis events in a consistent format.
#
# Input Arguments:
#   code   = abbreviation for event classification
#    --> "TL"  : Analysis terminated after successfully reaching max. time
#    --> "CF"  : Analysis terminated due to convergence failure
#    --> "DL"  : Analysis terminated after interstory drift exceeded limit 
#    --> "DLR" : Analysis terminated after frame drift exceeded limit 
#    --> "VB0" : Analysis terminated after reaching 0 base shear (pushover)
#    --> "FDT" : Analysis terminated after reaching final drift (pushover)
#    --> "CDT" : Cyclic pushover reached current drift target (pushover)
#    --> "WF"  : Weld element fractured and removed from model 
#    --> "WR"  : Weld element removed from model based on EBF limits
#    --> "GB"  : Global buckling of braces predicted by interstory drift
#   Fw = axial force in weld or brace (applies to WF, WR, and GB)

proc LogNotes {code {Fw {}}} {;                     # begin procedure
   set T [getTime];                                 # pseudo time
   
   ## Format roof and intestory drift/disp
   upvar 1 drift dR;                                # roof/frame drift, %
   upvar 1 disp DR;                                 # roof/frame disp., in.
   set dR [format "%+.3f" $dR];                     # fmt. frame drift
   set DRs "[format "%+.3f" $DR] inches";           # fmt. frame disp.
   set rdr "a frame drift of $dR% ($DRs)";          # roof drift string
   
  ## Define event-specific parameters
  if {$code=="WF" || $code=="WR" || $code=="GB"} {; # if weld/brace note
    upvar 1 bld bld1;                               # path to log file
    upvar 1 idx idx1;                               # weld/brace index
    source "$bld1-WeldInfo.tcl";                    # DCRs, elements, nodes
    source "$bld1-BraceInfo.tcl";                   # brace length ratios
    set story [lindex $WeldStories $idx1];          # story with event
    set s [lindex $WeldSides $idx1];                # side of frame
    set S [string toupper [string range $s 0 0]];   # uppercase side letter
    
    set C $code$story$S;                            # failure code
      if {$code == "WF" || $code == "WR"} {;        # weld fracture/removal
       set WE [lindex $WeldEles $idx1];             # fractured ele. tag
       if {$code == "WF"} {;                        # if fracture
          set s0 "Fracture";                        # part 0 of string
       } else {;                                    # if removal
          set s0 "Removal";                         # part 0 of string
       };                                           # end if
       set s1 "brace-gusset weld (element $WE)";    # part 1 of string
    } elseif {$code == "GB"} {;                     # if global buckling
      set wEBC [expr [lindex $WeldEles $idx1]-1];   # connected EBC element
      scan [eleResponse $wEBC localForce] "%s" Fw;  # weld/axial force
       set s0 "Global buckling"; set s1 "brace";    # part 0 of string
    };                                              # end if
    set f [format "%+.1f" [expr -1*$Fw]];           # fmt. weld/brace force
  } elseif {$code == "DL"} {;                       # if drift limit
    upvar 1 k story;                                # story
    set C $code$story;                              # failure code
  } else {;                                         # otherwise
    set C $code;                                    # failure code
  };                                                # end if
  ## Story-specific events
  set storyEvents [list "WF" "WR" "GB" "DL"];       # story-specific events
  if {[lsearch $storyEvents $code] != -1} {;        # if story-specific
    upvar 1 D dI;                                   # interstory drift, %
    upvar 1 hS hS1;                                 # story height, in.
    set dI [format "%+.3f" $dI];                    # fmt. interstory drift
    set DI [expr $dI*$hS1/100];                     # interstory disp.
    set DI [format "(%+.3f in.)" $DI];              # fmt. interstory disp.
    set idr "a drift of $dI% $DI in story $story";  # IDR string
  };                                                # end if
  ## Define analysis-specific notes
  upvar 1 aType aType1;                             # analysis type
  set s2 $rdr;                                      # part 2 of string
  if {$aType1 == "groundmotion"} {;                 # if groundmotion
    upvar 1 gm gm1; upvar 1 sf sf1;                 # get GM and SF info.
    set GM "GM$gm1 at a scale factor of $sf1";      # GM and SF string
    set s2 "$s2 after simulating $T sec. of $GM";   # part 2 of string
  };                                                # end if
  ## Define the string to include in the log file
  set SA "Stopping analysis";                       # stopping analysis
  set sDL "$SA due to drift limits after reaching"; # drift limit string
  set sDT "drift target was reached at $s2";        # pushover only
  if {$code=="WF" || $code=="WR" || $code=="GB"} {
    set E "$s0 of the story $story $s\
                 $s1 at an axial force of $f\
                 kips, $idr, and $s2";              # welds/brace buckling
  } elseif {$code=="TL"} {;                         # time limit
    set E "$SA at $s2";                             # groundmotion only
  } elseif {$code=="CF"}  {;                        # convergence failure
    set E "$SA because model was unable to\
                 converge at $s2";                  
  } elseif {$code=="DL"} {;                         # interstory drift lim.
    set E "$sDL $idr with $s2";                      
  } elseif {$code=="DLR"} {;                        # roof/frame drift lim.
    set E "$sDL $s2";                               
  } elseif {$code=="VB0"} {;                        # negative base shear
    set E "$SA because model has zero base\
                 shear capacity";                   # pushover only
  } elseif {$code=="FDT"} {;                        # final drift target
    set E "$SA because maximum $sDT";               # pushover only
  } elseif {$code=="CDT"} {;                        # current drift target
    set E "Continuing analysis after\
                 current cyclic $sDT";              # cyclic pushover only
  };                                                # end switch
  ## Write the notes to the log file
  upvar 1 out out1;                                 # path to log file
  WriteToLog $out1 "EVENT: $E.";                    # log the failure
  WriteToLog $out1 "CODE: $C ($T)";                 # log the comment
};                                                  # end procedure
# =========================================================================