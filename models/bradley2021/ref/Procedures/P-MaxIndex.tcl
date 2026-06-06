# =========================================================================
# This procedure returns the index of the maximum value in list "lst".

proc MaxIndex {lst} {;                              # begin procedure
   set index 0;                                     # start at first index
   set maxindex $index;                             # set maxindex to index
   set maxval [lindex $lst 0];                      # set maxval to value
   foreach val $lst {;                              # foreach value in list
      if {$val > $maxval} {;                        # if val > previous max
         set maxindex $index;                       # set maxindex to index
         set maxval $val;                           # set maxval to value
      };                                            # end if
      incr index;                                   # increment index
   };                                               # end for each
   return $maxindex;                                # return index of max
};                                                  # end procedure
# =========================================================================