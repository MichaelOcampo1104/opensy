# =========================================================================
# This procedure is used to analyze either the moment-rotation or uniaxial
# force-deformation behavior of zeroLengthSection elements. For example, 
# this procedure is used to evaulate axial force-deformation behavior in 
# the angle model and moment-rotation behavior in the connection model.
#
# Input Arguments:
#    secTag = tag identifying section to be analyzed
#    lType  = loading type: "Axial" or "Moment"
#    dT     = list of cycle peak displacement targets

proc ZLSAnalysis {secTag lType dT {cT "full"}} {;   # begin procedure
   ## Build the model
   node 1 0.0 0.0;                                  # place node 1 at (0,0)
   node 2 0.0 0.0;                                  # place node 2 at (0,0)
   fix 1 1 1 1;                                     # fix all node 1 DOFs
   fix 2 0 1 0;                                     # fix node 2 DOF 2: dy
   element zeroLengthSection 1 1 2 $secTag \
      -orient 1 0 0 0 1 0 -doRayleigh 0;            # define ZLS element

   ## Define analysis parameters
   constraints Plain;                               # boundary conditions
   numberer Plain;                                  # dof numberer
   system BandGeneral;                              # equations solver
   test EnergyIncr 1.0e-7 400;                      # convergence test
   algorithm Newton;                                # solution algorithm

   ## Define loading configuration
   if {$lType == "MR"} {;                           # if moment-rotation
      set dx 0.0; set dy 0.0; set rz 1.0;           # x, y and z loading
      set dof 3;                                    # loading DOF (moment)
   } elseif {$lType == "FD"} {;                     # if force-deformation
      set dx 1.0; set dy 0.0; set rz 0.0;           # x, y and z loading
      set dof 1;;                                   # loading DOF (axial)
   };                                               # end if
   pattern Plain 1 "Linear" {;                      # load pattern 1
      load 2 $dx $dy $rz;                           # define loading
   };                                               # end load pattern 1

   ## Analyze the section
   if {[llength $dT] == 1} {;                       # if monotonic/backbone
      set nS 1000;                                  # no. steps per incr.
      set dT [expr $dT/$nS];                        # convert disp. targets
   } else {;                                        # if cyclic
      set nS 100;                                   # no. steps per incr.
      set dT [DriftProtocol $dT "FEMA350" $nS $cT]; # convert disp. targets
   };                                               # end if
   set intgr "DisplacementControl";                 # advancement method
   foreach dTar $dT {;                              # for each disp. target
      integrator $intgr 2 $dof $dTar 1 $dTar $dTar; # define integrator
      analysis Static;                              # type of analysis
      set ok [analyze $nS];                         # analyze nS steps
   };                                               # end foreach
};                                                  # end procedure
# =========================================================================