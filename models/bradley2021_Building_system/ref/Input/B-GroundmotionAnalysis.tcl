# =========================================================================   
# This script loops through scale factors of GM intensity (IDA) until
# the building reaches predefined drift limits that represent collapse.
                           
## Get process info. (for OpenSeesMP only)
set pid [getPID];                                   # process ID
set numP  [getNP];                                  # no. of processes
set count 0;                                        # process counter

## Run the analysis
set g 386.09;                                       # acc. gravity (in/s^2)
set dxsign 1.0;                                     # set increment sign
for {set gm $gmmin} {$gm<=$gmmax} {incr gm} {;      # loop ground motions
   if {[expr $count % $numP] == $pid}  {;           # if correct PID
      set gmfile "GM[format "%02d" $gm].acc";       # ground motion file
      set gmpth "$gmdir/$city/Text/$gmfile";        # ground motion path
      set sf $sfmin;                                # reset scale factor
      set gmf 0;                                    # ground motion flag
      while {$sf <= $sfmax && $gmf == 0} {;         # loop scale factors
         
         ## Recorders and loads
         wipeAnalysis;                              # clear prev. analysis
         set tStart [clock seconds];                # get the start time
         source "$bldPath-GravityAnalysis.tcl";     # run gravity analysis
         set out "../Output/$aType/gm$gm/sf$sf";    # output directory
         MakeOutDir $out;                           # create output dir.
         source $recFile;                           # define recorders
         set acc "Series -dt 0.005 -filePath \
            {$gmpth} -factor [expr $sf*$g]";        # define accelerations
         pattern UniformExcitation 2 1 -accel $acc; # GM loading (global x)

         ## Analysis parameters and definition
         source "$bldPath-DefaultParameters.tcl";   # default parameters
         set intgr "Newmark";                       # analysis ctrl. method
         set drMax 0.1;                             # maximum drift ratio
         set dMax [expr $drMax*$height];            # max. drif: 10%
         set dx 0.005;                              # time increment (s)
         set tMax 60.0;                             # max. simulated time
         set gamma 0.5;                             # newmark integr. gamma
         set beta 0.25;                             # newmark integr. beta
         set wf 0;                                  # weld fracture counter
         integrator $intgr $gamma $beta;            # define integrator
         analysis Transient;                        # type of analysis
         
         ## Run the analysis
         while {$bf == 0} {;                        # while break flag is 0
            source "$bldPath-AdvanceAnalysis.tcl";  # run solution scheme
         };                                         # end while
         if {[getTime] < $tMax} {set gmf 1};        # ground motion failed
         source "$bldPath-ManageOutput.tcl";        # wrap up the analysis
         set sf [format "%.1f" [expr $sf+$sfinc]];  # incr. scale factor
         unset algs;                                # unset algorithms
      };                                            # end while
      wipe;                                         # wipe any prev. model
   };                                               # end if
   incr count 1;                                    # incr. process counter
};                                                  # end for
# =========================================================================