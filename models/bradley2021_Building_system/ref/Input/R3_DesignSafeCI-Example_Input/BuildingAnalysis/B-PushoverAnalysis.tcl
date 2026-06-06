# =========================================================================
# This script is used to perform either monotonic (single drift target) or
# cyclic (reversed drift target) static pushover analyses using a constant
# lateral load profile.

## Recorders and loads
source "$bldPath-GravityAnalysis.tcl";              # run gravity analysis
set tStart [clock seconds];                         # get the start time
set out "./Output/$aType-$pType";                   # output directory
MakeOutDir $out;                                    # create output dir.
source $recFile;                                    # define recorders
source "$bld-PushoverLoads.tcl";                    # ASCE 7-10 ELFP dist.

## Analysis parameters
source "$bldPath-DefaultParameters.tcl";            # default parameters
set intgr "DisplacementControl";                    # analysis ctrl. method
set drMax 0.10;                                     # maximum drift ratio
set dMax [expr $drMax*$height];                     # max. drif: 10%
set cDOF 1;                                         # disp. ctrl. DOF (dx)
set dx 0.02;                                        # disp. increment (in.)

## Loading protocol
proc GetSign x {expr {$x<0? -1: $x>0}};             # get loading direction
if {$pType == "monotonic"} {;                       # if monotonic loading
   set drTs [list $drMax];                          # set max drift target
} elseif {$pType == "cyclic"} {;                    # if cyclic loading
   source "$bldPath-CyclicDriftTargets.tcl";        # define drift targets
   set drTs [DriftProtocol $driftTargets "FEMA461"];# convert disp. targets
};                                                  # end if
set drMaxStr [format "%.3f" [expr 100*$drMax]];     # format the string
set drFinal [lindex $drTs end];                     # final drift target
set dspMax [expr abs($drMax)*$height];              # max roof displacement
set nTargs [llength $drTs];                         # no. of target drifts

## Run the analysis
set ii 0;                                           # target counter
while {$bf == 0 && $ii < $nTargs} {;                # while break flag is 0
   set tf 0;                                        # set target flag to 0
   set drTar [expr 100*[lindex $drTs $ii]];         # current drift target
   set dxsign [GetSign $drTar];                     # set sign disp. incr.
   integrator $intgr $cNode $cDOF $dx;              # define integrator
   analysis Static;                                 # type of analysis
   while {$tf == 0 && $bf == 0} {;                  # break/target flags 0
      source "$bldPath-AdvanceAnalysis.tcl";        # run solution scheme
   };                                               # end while
incr ii;                                            # incr. target counter
};                                                  # end while
source "$bldPath-ManageOutput.tcl";                 # wrap up the analysis
# =========================================================================