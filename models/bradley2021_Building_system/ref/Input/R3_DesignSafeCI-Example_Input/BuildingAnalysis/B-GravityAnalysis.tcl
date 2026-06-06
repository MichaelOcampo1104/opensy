# =========================================================================
# This script applies the gravity loads to the model and saves the 
# resulting model state for use as initial conditions in the pushover
# or groundmotion analyses.

## Recorders and loads
wipeAnalysis;                                       # clear prev. analysis
set tStart [clock seconds];                         # get the start time
set out "./Output/gravity";                         # output directory
source "$bldPath-CreateModel.tcl";                  # create the model
if {$aType == "gravity"} {;                         # if gravity analysis
   MakeOutDir $out;                                 # create output dir.
   source $recFile;                                 # define recorders
};                                                  # end if
source "$bld-GravityLoads.tcl";                     # loads (1.0D+0.2L)

## Analysis parameters and definition
source "$bldPath-DefaultParameters.tcl";            # basic analysis setup
set intgr "LoadControl";                            # analysis ctrl. method
set Nsteps 20;                                      # apply loads, N steps
set px [expr 1.0/$Nsteps];                          # load increment (%)
integrator $intgr $px;                              # define integrator
analysis Static;                                    # type of analysis

## Run the analysis
WriteToLog $out "Running analysis...";              # comment in log file
set ok [analyze $Nsteps];                           # run gravity analysis
set bf 0; set wf 0;                                 # initialize flags
if {$ok != 0} {;                                    # if analysis failed
   LogNotes "CF"; set bf 1;                         # convergence failure
} else {;                                           # else...
   WriteToLog $out "Gravity loading successful.";   # comment in log file
   loadConst -time 0.0;                             # keep load, reset time
   remove recorders;                                # delete gravity recs.
};                                                  # end if
source "$bldPath-ManageOutput.tcl";                 # wrap up the analysis
# =========================================================================