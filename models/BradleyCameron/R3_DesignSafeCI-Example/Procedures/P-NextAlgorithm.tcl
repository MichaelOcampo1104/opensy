# =========================================================================
# This procedure is used to advance the analysis of a model for a variety 
# of solution algorithms, which are allowed to contain custom options. The
# input argument "AlgOpts" is used to define the current algorithm and it's
# options, which can be algorithm switches or step size factors.

proc NextAlgorithm {AlgOpts} {;                     # begin procedure
   ## Set variables from upper level
   upvar 1 ok ok1;                                  # prev. analysis result
   upvar 1 alg alg1;                                # previous algorithm
   upvar 1 testType testType1;                      # convergence test type
   upvar 1 tol tol1;                                # convergence tolerance
   upvar 1 itr itr1;                                # no. of iterations
   upvar 1 numIncr nIncr1;                          # no. of analysis steps
   upvar 1 dx dx1;                                  # disp. or time step
   upvar 1 pFlag pFlag1;                            # analysis print flag

   ## Separate the algorithm and its options
   set algNext [lindex $AlgOpts 0];                 # next algorithm
   set opt [lindex $AlgOpts 1];                     # algorithm options

   ## Adjust displacement or time step
   set sAdj 1;                                      # step adjust value
   if {[string index $opt 0] eq "-"} {;             # if opt is a switch
      set aSwitch $opt;                             # set algorithm switch
   } else {;                                        # if opt not a switch
      set aSwitch "";                               # set switch empty
      if {$opt == "small"} {          set sAdj 20;  # adjust step by 1/20
      } elseif {$opt == "tiny"} {     set sAdj 50;  # adjust step by 1/50
      } elseif {$opt == "miniscule"} {set sAdj 100; # adjust step by 1/100
      } elseif {$opt == "itsybitsy"} {set sAdj 200; # adjust step by 1/200
      };                                            # end if
   };                                               # end if
   
   ## Analyze with next algorithm if needed
   if {$ok1 != 0} {;                                # if prev. alg. failed
      set alg $algNext;                             # define the algorithm
      test $testType1 $tol1 $itr1 $pFlag1;          # convergence test
      if {$alg == "NewtonLineSearch"} {;            # if NewtonLineSearch
         algorithm $alg -type Bisection \
            -tol 0.5 -maxIter 200;                  # solution algorithm
      } else {;                                     # if not NLS
         algorithm $alg $aSwitch;                   # solution algorithm
      };                                            # end if
      set ok1 [analyze $nIncr1 [expr $dx1/$sAdj]];  # advance the analysis
      if {$ok1 == 0} {;                             # if analyze ok
         set check 1;                               # algorithm succeeded
      } else {;                                     # if analyze not ok
         set check -1;                              # algorithm has failed
      };                                            # end if
   } else {;                                        # if prev. alg. worked
      set check 0;                                  # dummy value
      set alg $alg1;                                # algorithm that worked
   };                                               # end if
   return [list $ok1 $alg $opt $check];             # return some variables
};                                                  # end procedure
# =========================================================================