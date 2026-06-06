# =========================================================================
# This procedure defines a fiber section for the geometry of AISC standard 
# W or square HSS sections. 
# 
# Input Arguments: 
#    sID  = section ID number
#    mID  = material ID number 
#    args = varies for W and HSS, see below
# Note: NF stands for "number of fibers"

proc Section {Shape sID mID args} {;                # begin procedure

   if {$Shape=="W"} {;                              # if wide flange

      ## Input arguments
      set d [lindex $args 0];                       # nominal depth
      set bf [lindex $args 1];                      # flange width
      set tf [lindex $args 2];                      # flange thickness
      set tw [lindex $args 3];                      # web thickness
      set n1 [lindex $args 4];                      # NF web depth
      set n2 [lindex $args 5];                      # NF web thickness
      set n3 [lindex $args 6];                      # NF flange width
      set n4 [lindex $args 7];                      # NF flange thickness
      set ax [lindex $args 8];                      # strong: 1 or weak: 0

      ## Define some dimensions
      set dw [expr  $d - 2 * $tf];                  # depth of web
      set y1 [expr -$d/2];                          # neg. outer flange
      set y2 [expr -$dw/2];                         # neg. inner flange
      set y3 [expr  $dw/2];                         # pos. inner flange
      set y4 [expr  $d/2];                          # pos. outer flange
      set z1 [expr -$bf/2];                         # neg. flange width
      set z2 [expr -$tw/2];                         # neg. web width
      set z3 [expr  $tw/2];                         # pos. web width
      set z4 [expr  $bf/2];                         # pos. flange width

      ## Define the fiber sections
      if {$ax == 1} {;                              # if strong axis
         section Fiber $sID {;                      # begin section
            patch quadr $mID $n3 $n4 $y1 $z4 $y1 \
               $z1 $y2 $z1 $y2 $z4;                 # top flange
            patch quadr $mID $n2 $n1 $y2 $z3 $y2 \
               $z2 $y3 $z2 $y3 $z3;                 # web
            patch quadr $mID $n3 $n4 $y3 $z4 $y3 \
               $z1 $y4 $z1 $y4 $z4;                 # bottom flange
         };                                         # end section
      } elseif {$ax == 0} {;                        # if weak axis
         section Fiber $sID {;                      # begin section
            patch quadr $mID $n3 $n4 $z1 $y1 $z4 \
               $y1 $z4 $y2 $z1 $y2;                 # left flange
            patch quadr $mID $n2 $n1 $z2 $y2 $z3 \
               $y2 $z3 $y3 $z2 $y3;                 # web
            patch quadr $mID $n3 $n4 $z1 $y3 $z4 \
               $y3 $z4 $y4 $z1 $y4;                 # right flange
         };                                         # end section
      };                                            # end if
   } elseif {$Shape=="HSS"} {;                      # if HSS (square)

      ## Input arguments
      set d [lindex $args 0];                       # nominal depth
      set t [lindex $args 1];                       # wall thickness
      set nfdw [lindex $args 2];                    # NF web depth
      set nftw [lindex $args 3];                    # NF web thickness
      set nfbf [lindex $args 4];                    # NF flange width
      set nftf [lindex $args 5];                    # NF flange thickness
      ## Define some dimensions
      set dw [expr $d - 2 * $t];                    # depth of web
      set y1 [expr -$d/2];                          # outer left web
      set y2 [expr -$dw/2];                         # inner left web
      set y3 [expr  $dw/2];                         # inner right web
      set y4 [expr  $d/2];                          # outer right web
      set z1 [expr -$d/2];                          # outer bottom flange
      set z2 [expr -$dw/2];                         # inner bottom flange
      set z3 [expr  $dw/2];                         # inner top flange
      set z4 [expr  $d/2];                          # outer top flange
    
      ## Define the fiber sections
      section fiberSec $sID {;                      # begin section
         patch quadr $mID $nftf $nfdw $y2 $z4 $y2 \
            $z3 $y3 $z3 $y3 $z4;                    # top flange
         patch quadr $mID $nftf $nfdw $y2 $z2 $y2 \
            $z1 $y3 $z1 $y3 $z2;                    # bottom flange
         patch quadr $mID $nfbf $nftw $y1 $z4 $y1 \
            $z1 $y2 $z1 $y2 $z4;                    # left web
         patch quadr $mID $nfbf $nftw $y3 $z4 $y3 \
            $z1 $y4 $z1 $y4 $z4;                    # right web
      };                                            # end section
   };                                               # end if
};                                                  # end procedure
# =========================================================================