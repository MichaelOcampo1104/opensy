# =========================================================================
# This script is used to manage output files at the end of an analysis.

## Log the end of the analysis
set tEnd [clock seconds];                           # get the end time
set run [expr $tEnd-$tStart];                       # analysis runtime
set checkgrav [string first "gravity" "$out"];      # check if gravity file
if {$checkgrav == -1} {;                            # if not gravity file
   WriteToLog $out "Algorithms Failed: $fail";      # log algorithm failure
   WriteToLog $out "Algorithms Succeeded: $succ";   # log algorithm success
};                                                  # end if
WriteToLog $out "Runtime = $run seconds.";          # log runtime
WriteToLog $out "Analysis complete.";               # log complete

## Rename output directory if on Tufts' HPC
set local [string first "Desktop" [pwd] 0];         # check if local
if {$local == -1} {;                                # if remote
   if {$aType != "gravity"} {;                      # if not gravity analy.
      if {$checkgrav == -1} {;                      # if not gravity file
         if {[file exists "$out-DONE/"] == 1} {;    # if directory exists
            file delete -force -- "$out-DONE/";     # delete directory
         };                                         # end if
         file rename "$out/" "$out-DONE/";          # mark ouput dir. done
      };                                            # end if
   } else {;                                        # if gravity analysis
      file rename "$out/" "$out-DONE/";             # mark ouput dir. done
   };                                               # end if
};                                                  # end if
# =========================================================================