# =========================================================================
# This script is used to advance the analysis one displacement or time step
# at a time, running multiple solution algorithms if necessary to achieve
# convergence, and checks for weld fractures, global buckling, drift limits
# and EBF limits after each successful step. If unsuccessful, the analysis 
# has failed to converge.

if {[info exists algs]==0} {;                       # if first analyze step
  source "$bldPath-DefineDamping.tcl";              # define damping

  ## Define set of algorithms to try
  set algs "{Newton -initialThenCurrent}
            {Newton small}
            {NewtonLineSearch}
            {KrylovNewton}
            {Newton tiny}
            {Newton miniscule}
            {KrylovNewton small}
            {ModifiedNewton}"

  ## Solution Criteria
  set tols [split $Ltols "_"];                      # list of tolerances
  set szFs [split $Lszfs "_"];                      # step size factors
  set analysis "$aType"
  WriteToLog $out "Analysis Parameters:";           # log solution scheme
  WriteToLog $out "System Name = $sN";              # system name
  if {$aType == "groundmotion"} {
  WriteToLog $out "Analysis    = GM$gm SF$sf";      # type of analysis
  } elseif {$aType == "pushover"} {
  WriteToLog $out "Analysis    = $aType";           # type of analysis
  }
  WriteToLog $out "Damping     = $dampType";        # type of damping
  WriteToLog $out "SOE Solver  = $SOE";             # system of equations
  WriteToLog $out "Tolerances  = $tols";            # convergence tolerance
  WriteToLog $out "Iterations  = $itr";             # allowable iterations
  WriteToLog $out "StepFactor  = $szFs";            # step size factors
  WriteToLog $out "Analysis Results:";              # log analysis results

  ## Initialize algorithm success/failure counters
  set dxi $dx;                                      # init. disp/time step
  set nAlgs [llength $algs];                        # number of algorithms
  set fail [lrepeat $nAlgs 0];                      # failed algorithms
  set succ [lrepeat $nAlgs 0];                      # succeeded algorithms
};                                                  # end if

## Print some info to the console
set RT [expr [clock seconds]-$tStart];              # current runtime, sec
puts stdout "Pseudo time = [getTime] Runtime = $RT";# print to console

## Initial algorithm settings
test $testType $tol0 $iter0;                        # convergence test
set dx [expr $dxi*$dxsign];                         # set/reset dx and sign
if {$aType == "pushover"} {;                        # if pushover
   integrator $intgr $cNode $cDOF $dx;              # define integrator
};                                                  # end if
algorithm Newton;                                   # reset to newton alg.


## Run the analysis with initial settings
set pFlag 0;                                        # suppress print output
set ok [analyze 1 $dx];                             # run one analysis step
set alg "Initial analysis algorithm";               # algorithm note
set opt "";                                         # algorithm options

## If initial algorithm fails, loop thru others
set numIncr 1;                                      # no. of analysis steps
if {$ok != 0} {;                                    # if analysis failed
  set iter0 $itr;                                   # reduce no. iterations
  while {$ok != 0 && $bf == 0} {;                   # while analyze fails
    foreach tol $tols {;                            # loop thru tolerances
      if {$ok == 0} {break};                        # break if analyze ok
      foreach szF $szFs {;                          # loop thru step sizes
        if {$ok == 0} {break};                      # break if analyze ok
        set dx [expr $dxi/$szF];                    # adjust step size
        if {$aType=="pushover"} {;                  # if pushover
           integrator $intgr $cNode $cDOF $dx;      # redefine integrator
        };                                          # end if
        set str [list];                             # indicate failed algs
        for {set j 0} {$j<$nAlgs} {incr j} {;       # loop algorithms
          if {$ok == 0} {break};                    # break if analyze ok
          lappend str "."; puts stdout $str;        # show . when alg fails
          set okN [NextAlgorithm [lindex $algs $j]];# try current algorithm
          set alg [lindex $okN 1];                  # current algorithm
          set opt [lindex $okN 2];                  # current alg. options
          set check [lindex $okN 3];                # current solution
          set ok [lindex $okN 0];                   # set current solution
          if {$check == -1} {;                      # if algorithm failed
            set count [expr [lindex $fail $j]+1];   # alg. failures count
            set fail [lreplace $fail $j $j $count]; # record alg. failures
            set bc1 [expr $szF==[lindex $szFs end]];# break check 1
            set bc2 [expr $tol==[lindex $tols end]];# break check 2
            set bc3 [expr $j==[expr $nAlgs-1]];     # break check 3
            if {$bc1 && $bc2 && $bc3} {set bf 1};   # convergence failure
          } elseif {$check == 1} {;                 # if algorithm succeed.
            set count [expr [lindex $succ $j]+1];   # alg. success count
            set succ [lreplace $succ $j $j $count]; # record alg. successes
          };                                        # end if
        };                                          # end for
      };                                            # end foreach
    };                                              # end foreach
  };                                                # end while
};                                                  # end if

## Calculate interstory and total frame drifts
source "$bld-IDRs.tcl";                             # get interstory drifts
set dT    [lindex $dTs end];                        # roof displacement
set dB    [lindex $dBs 0];                          # base displacement
set disp  [expr ($dT-$dB)];                         # roof displacment (in)
set drift [expr 100*$disp/$height];                 # roof drift (percent)

## Check condition of analysis and frame components
if {$ok != 0 && $bf == 1} {;                        # if convergence failed
  LogNotes "CF"; break ;                            # log and break
} elseif {$wf != 1} {;                              # if model converged
  

  ## Calculate current structural period
  set lambdaN_curr [eigen 1];                       # eigenvalue analysis
  if {$lambdaN_curr >= 0} {;                        # if frequency is real
    set wn_curr [expr sqrt($lambdaN_curr)];         # natural frequencies
    set Tn_curr [expr (2.0*$pi)/$wn_curr];          # natural periods
    set Tn1 [format "%.3f" $Tn_curr];               # format current period
    WriteToLog $out "[getTime] $Tn1" "Periods" 0;   # record current period
  };                                                # end if

  ## Check roof drift
  if {[expr abs($disp)] > $dMax} {;                 # total drift exceeded
    LogNotes "DLR"; set bf 1; break };              # log and break

  ## Check system-specific limits
  if {$aType == "pushover"} {;                      # if pushover analysis
    source "$bld-BaseShear.tcl";                    # calculate base shear
    if {$pType == "monotonic" && $bf == 0} {;       # if monotonic
      if {$Vb>0} {LogNotes "VB0"; set bf 1; break };# log and break
    };                                              # end if
    set c1 [expr ($drTar > 0 && $drift > $drTar)];  # pos. target reached
    set c2 [expr ($drTar < 0 && $drift < $drTar)];  # neg. target reached
    if {[expr $c1+$c2 == 1]} {;                     # check targets reached
      if {$i == $nTargs-1} {;                       # if the final target
        LogNotes "FDT"; set bf 1; break ;           # log and break
      } else {;                                     # if not final target
        LogNotes "CDT"; set tf 1;                   # log and proceed
      };                                            # end if
    };                                              # end if
  } elseif {$aType == "groundmotion"} {;            # if groundmotion
    if {[getTime] >= $tMax} {;                      # if time exceeds tMax
      LogNotes "TL"; set bf 1; break };             # log and break
  };                                                # end if

  ## Get weld and brace info if it exists
  set hasBraces [file exists "$bld-BraceInfo.tcl"]; # check for brace info
  if {$hasBraces == 1 && $bf != 1} {;               # if brace info. exists
    source "$bld-WeldInfo.tcl";                     # DCRs, elements, nodes
    source "$bld-BraceInfo.tcl"};                   # brace length ratios

  ## Check story-specific limits
  for {set k 1} {$k <= $stories} {incr k} {;        # loop through stories
    set dT [lindex $dTs $k-1];                      # drift at top of story
    set dB [lindex $dBs $k-1];                      # drift of bot of story
    set hS [lindex $hSs $k-1];                      # height of the story
    set D [expr 100*($dT-$dB)/$hS];                 # interstory drift, %
    set Dabs [expr abs($D)];                        # abs. interstory drift
    ## Check if maximum IDR limit exceeded
    if {$Dabs > [expr $drMax*100]} {;               # if drift > 10%
      LogNotes "DL"; set bf 1; break ;              # log and break
    };                                              # end if
    ## Check for global buckling of braces
    if {[info exists GB]==0} {set GB [list]};       # global buck. indices
    if {$hasBraces == 1 && $bf != 1} {;             # model has braces
      set STi [lsearch -all $WeldStories $k];       # brace story indices
      set Ni [llength $STi];                        # no. braces in story
      if {$Dabs > 0.3} {;                           # if story drift > 0.3%
        for {set BRi 0} {$BRi<$Ni} {incr BRi} {;    # loop through braces
          set idx [lindex $STi $BRi];               # current brace index
          set LDR [lindex $BR_LDR $idx];            # current length ratio
          if {$LDR <= 0.9985} {;                    # brace shortened 0.15%
            if {[lsearch $GB $idx] == -1} {;        # if not yet buckled
              lappend GB $idx; LogNotes "GB"; break;# record and log
            };                                      # end if
          };                                        # end if
        };                                          # end for
      };                                            # end if
    };                                              # end if
    ## Check if any weld or EBF limits exceeded
    if {$hasBraces == 1 && $bf != 1} {;             # model has braces
      set idx [MaxIndex $WeldDCRs];                 # index of maximum DCR
      if {[lindex $WeldDCRs $idx] > 1} {;           # if max(DCRs) > 1.0
        set kind "WF";                              # weld fracture
        source "$bldPath-RemoveWeld.tcl"; break ;   # remove weld element
      } else {;                                     # else check EBF limits
        if {[llength $STi] != 0} {;                 # story has braces
          set STDCR [Lindices $WeldDCRs $STi];      # brace DCRS in story
          set midx [MaxIndex $STDCR];               # story max. DCR index
          set idx [lindex $STi $midx];              # max. DCR brace index
          set mDCR [lindex $WeldDCRs $idx];         # DCR of max. DCR brace
          set c1 [expr $Dabs>1.5 && $mDCR>0.7];     # LL EBF check 1
          set c2 [expr $Dabs>2.0 && $mDCR>0.5];     # LL EBF check 2
          set c3 [expr $Dabs>2.5 && $mDCR>0.3];     # LL EBF check 3
          set c4 [expr $Dabs>3.0 && $mDCR>0.0];     # LL EBF check 4
          if {$c1 || $c2 || $c3 || $c4} {;          # if any LL EBF checks
            set kind "WR";                          # weld removal type
            source "$bldPath-RemoveWeld.tcl";       # remove weld 
            break ;                                 # break
          };                                        # end if
        };                                          # end if
      };                                            # end if
    };                                              # end if
  };                                                # end for
};                                                  # end if
# =========================================================================



