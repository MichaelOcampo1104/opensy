# =========================================================================
# This procedure returns a list of the specified `indices' from `lst'
proc Lindices {lst indices} {set var [list];        # begin procedure
   foreach idx $indices {;                          # for each index
   lappend var [lindex $lst $idx]};return $var;     # append the index
};                                                  # end procedure
# =========================================================================