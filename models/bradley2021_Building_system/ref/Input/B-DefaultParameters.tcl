# =========================================================================
# This script is used to define a set of default analysis parameters to be
# used as initial settings in gravity, pushover, and groundmotion analyses.

set testType "EnergyIncr";                          # convergence test type
set tol0 1.0e-8;                                    # convergence tolerance
set iter0 200;                                      # number of iterations
constraints Plain;                                  # bound. cond. handling
if {$SOE == "Mumps"} {;                             # OpenSeesMP solver
   numberer ParallelRCM;                            # parallel renumberer
} else {;                                           # OpenSees solvers
   numberer RCM;                                    # RCM renumberer
};                                                  # end if
system $SOE;                                        # system of eq. solver
test $testType $tol0 $iter0;                        # convergence test
algorithm Newton;                                   # solution algorithm
# =========================================================================