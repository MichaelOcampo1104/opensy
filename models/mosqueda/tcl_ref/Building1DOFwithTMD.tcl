# File: Building1DOFwithTMD.tcl (use with Specimen_IsolatedMass.tcl)
# units are [kip,in.]
#
# $Revision: $
# $Date: $
# $URL: $
#
# Written: Andreas Schellenberg (andreas.schellenberg@gmail.com)
# Created: 10/13
# Revision: A
#
# Purpose: this file contains the tcl input to perform
# a local hybrid simulation of a ...


# ------------------------------
# Start of model generation
# ------------------------------
set outDIR "output/Run035a"
file mkdir $outDIR
logFile $outDIR/Building1DOFwithTMD.log

# create ModelBuilder (with two-dimensions and 2 DOF/node)
model BasicBuilder -ndm 3 -ndf 6

# define some general constants
set g [expr 32.174*12]
set pi [expr acos(-1.0)]
set cm2in [expr 1.0/2.54]

set fxBldg 4.0;                       # building (w/o TMD) fundamental frequency in X
set fyBldg [expr 1.25*$fxBldg];       # building (w/o TMD) fundamental frequency in Y
set fzBldg 11.0;                      # building (w/o TMD) fundamental frequency in Z
set mRatio 0.88585;                   # effective mass ratio
set hRatio 0.64721;                   # effective height ratio
set wTMD 56.0;                        # weight of TMD
set wRatioTMD [expr 56.0/450.0];      # ratio of TMD weight to building weight
set withTMD 1;                        # run with or without TMD
set withGravity 1;                    # run with or without gravity
set expElmFact 0.0;                   # experimental element contribution factor (0..1)
set isoType "FPSB";                   # LPRB or FPSB
set inputType "LPGscaled";            # Sine, TaperedSine, LPGoriginal, LPGscaled, SHWoriginal, SHWscaled
set ampScaleH 1.5;                    # amplitude scale
set ampScaleV [expr 1.0*$ampScaleH];  # amplitude scale
set numCtrlDOF 1;                     # number of DOF to be controlled
set expCtrlType "SimFEAdapter";           # SimFEAdapter, xPCtarget, SCRAMNet, SCRAMNetGT

puts "\nOutput Dir: $outDIR"
puts "Input Type: $inputType"
puts "Input Amplitude Scale: $ampScaleH"
puts "Number of Controlled DOF: $numCtrlDOF"
puts "Experimental Element Factor: $expElmFact"
puts "Isolator Type: $isoType \n"

# Define geometry for model
# -------------------------
set lengthScale 3.0;                  # length scale of model
set mTMD [expr $wTMD/$g];             # mass of TMD
set hTMD 6.0;                         # height of TMD
set wBldg [expr $wTMD/$wRatioTMD];    # weight of building
set mBldg [expr $mRatio*$wBldg/$g];   # mass of building
set hBldg [expr $hRatio*(5.0*144.0)/$lengthScale]
# node $tag $xCrd $yCrd $zCrd $mass
node  1  0.0  0.0    0.0
node  2  0.0  0.0  $hBldg  -mass $mBldg $mBldg $mBldg 0.0 0.0 0.0

# set the boundary conditions
#   $tag $DX $DY $DZ $RX $RY $RZ
fix  1    1   1   1   1   1   1
if {$numCtrlDOF == 1} {
    fix  2    0   1   0   1   1   1
} elseif {$numCtrlDOF == 2} {
    fix  2    0   0   0   1   1   1
} elseif {$numCtrlDOF == 3} {
    fix  2    0   0   0   1   1   1
}

# Define numerical elements
# -------------------------
# # define coordinate transformation
# geomTransf Linear 1 1 0 0

# set E_Bldg 3600.0
# set nu_Bldg 0.2
# set G_Bldg [expr $E_Bldg/(1.0+$nu_Bldg)/2.0]

# set dyBldg 60.0
# set dzBldg 60.0
# set A_Bldg [expr $dyBldg*$dzBldg]
# set Avy_Bldg [expr 5/6*$A_Bldg]
# set Avz_Bldg [expr 5/6*$A_Bldg]
# set Iy_Bldg [expr $dyBldg*pow($dzBldg,3)/12.0]
# set Iz_Bldg [expr $dzBldg*pow($dyBldg,3)/12.0]
# set Jx_Bldg [expr $Iy_Bldg + $Iz_Bldg]
# set ky_Bldg [expr 3.0*$E_Bldg*$Iz_Bldg/pow($hBldg,3.0)]
# set fy_Bldg [expr sqrt($ky_Bldg/$mBldg)/(2.0*$pi)]

# puts "A_Bldg = $A_Bldg, Iy_Bldg = $Iy_Bldg, Iz_Bldg = $Iz_Bldg, ky_Bldg = $ky_Bldg, fy_Bldg = $fy_Bldg"
# element ElasticTimoshenkoBeam 1 1 2 $E_Bldg $G_Bldg $A_Bldg $Jx_Bldg $Iy_Bldg $Iz_Bldg $Avy_Bldg $Avz_Bldg 1

set kxBldg [expr $mBldg*pow(2.0*$pi*$fxBldg,2)]
set kyBldg [expr $mBldg*pow(2.0*$pi*$fyBldg,2)]
set kzBldg [expr $mBldg*pow(2.0*$pi*$fzBldg,2)]
uniaxialMaterial Elastic 1 $kxBldg
uniaxialMaterial Elastic 2 $kyBldg
uniaxialMaterial Elastic 3 $kzBldg
puts "mBldg = $mBldg, hBldg = $hBldg"
puts "fxBldg = $fxBldg, kxBldg = $kxBldg"
puts "fyBldg = $fyBldg, kyBldg = $kyBldg"
puts "fzBldg = $fzBldg, kzBldg = $kzBldg\n"

# twoNodeLink $eleTag $iNode $jNode -mat $matTags -dir $dirs <-orient <$x1 $x2 $x3> $y1 $y2 $y3> <-pDelta $Mratios> <-shearDist $sDratios> <-doRayleigh> <-mass $m>
if {$numCtrlDOF == 1} {
    element twoNodeLink 1 1 2 -mat 1 3 -dir 2 1 -orient 1 0 0 -doRayleigh
} elseif {$numCtrlDOF == 2} {
    element twoNodeLink 1 1 2 -mat 1 2 3 -dir 2 3 1 -orient 1 0 0 -doRayleigh
} elseif {$numCtrlDOF == 3} {
    element twoNodeLink 1 1 2 -mat 1 2 3 -dir 2 3 1 -orient 1 0 0 -doRayleigh
}

# Define damping
# --------------
# calculate the Rayleigh damping factors for nodes & elements
set zeta 0.05
set omega [expr sqrt([eigen -fullGenLapack 1])]
set T [expr 2*$pi/$omega]
set alphaM     0.0;                      # D = alphaM*M
set betaK      0.0;                      # D = betaK*Kcurrent
set betaKinit  [expr 2.0*$zeta/$omega];  # D = beatKinit*Kinit
set betaKcomm  0.0;                      # D = betaKcomm*KlastCommit
puts "zeta = $zeta, omega1 = $omega, f1 = [expr 1.0/$T]"
puts "alphaM = $alphaM, betaK = $betaK, betaKinit = $betaKinit, betaKcomm = $betaKcomm"

# Define analytical element in parallel with experimental
# -------------------------------------------------------
if {$withTMD == 1 && $expElmFact < 1.0} {
    
	# create node for TMD
	node  3  0.0  0.0  [expr $hBldg+$hTMD]  -mass $mTMD $mTMD $mTMD 0.0 0.0 0.0

	# set the boundary conditions
	if {$numCtrlDOF == 1} {
		fix  3    0   1   0   1   1   1
	} elseif {$numCtrlDOF == 2} {
		fix  3    0   0   0   1   1   1
	} elseif {$numCtrlDOF == 3} {
		fix  3    0   0   0   1   1   1
	}
	
	# create isolator element
	if {$isoType == "LPRB"} {
		# Isolator parameters
		set khInit [expr (1.0-$expElmFact)*4.0*8.96];
		set fy [expr (1.0-$expElmFact)*4.0*2.22];
		set alpha1 0.1
		set alpha2 0.0
		set n 1.0
		puts "khInit = $khInit, fy = $fy, alpha1 = $alpha1"

		set wIso [expr (1.0-$expElmFact)*$wTMD];  # initial weight (axial load) per isolator [kip]
		set mv [expr $wIso/$g] 
		set kv [expr (1.0-$expElmFact)*4.0*1089.0]
		set zetaVertical 0.1
		set cv [expr 2.0*$zetaVertical*sqrt($kv*$mv)]
		uniaxialMaterial Elastic 10 [expr $kv/100.0] $cv $kv
		uniaxialMaterial Elastic 11 6.0
		uniaxialMaterial Elastic 12 419.0
		uniaxialMaterial Elastic 13 419.0

		# # element elastomericBearingPlasticity eleTag NodeI NodeJ kInit fy alpha1 alpha2 mu -P matTag -T matTag -My matTag -Mz matTag <-orient <x1 x2 x3> y1 y2 y3> <-shearDist sDratio> <-doRayleigh> <-mass m>
		#element elastomericBearingPlasticity 2 2 3 $khInit $fy $alpha1 $alpha2 $n -P 10 -T 11 -My 12 -Mz 13 -orient 1 0 0

		# element elastomericBearingBoucWen eleTag NodeI NodeJ kInit fy alpha1 alpha2 mu eta beta gamma -P matTag -T matTag -My matTag -Mz matTag <-orient <x1 x2 x3> y1 y2 y3> <-shearDist sDratio> <-doRayleigh> <-mass m> <-iter maxIter tol>
		element elastomericBearingBoucWen 2 2 3 $khInit $fy $alpha1 $alpha2 $n 1.0 0.5 0.5 -P 10 -T 11 -My 12 -Mz 13 -orient 1 0 0

	} elseif {$isoType == "FPSB"} {
		# Isolator parameters
		set mu1 0.055;      # friction coefficient 0.01
		set mu2 0.13;      # friction coefficient 0.08
		set mu3 0.13;      # friction coefficient 0.13
		set L1  [expr 3.0-1.65/2.0];      # effective radius of pendulum 1 [in.]
		set L2  [expr 18.64-2.94/2.0];    # effective radius of pendulum 2 [in.]
		set L3  [expr 18.64-2.94/2.0];    # effective radius of pendulum 3 [in.]
		set d1  [expr (2.60-1.75)/2.0];     # pendulum 1 displacement limit [in.]
		set d2  [expr (9.0-3.0)/2.0];       # pendulum 2 displacement limit [in.]
		set d3  [expr (9.0-3.0)/2.0];       # pendulum 3 displacement limit [in.]
		
		set wIso [expr (1.0-$expElmFact)*$wTMD];  # initial weight (axial load) per isolator [kip]
		set uy  0.0047;                             # displacement where sliding starts [in.]
		set kvc [expr (1.0-$expElmFact)*5.0E3];   # vertical compression stiffness [kip/in.]
		set kvt [expr (1.0-$expElmFact)*0.001];   # vertical tension stiffness [kip/in.]
		set minFv 1.0E-6;                         # minimum compression force in the bearing [kip]
		set tol 1.0E-6;                           # relative tolerance for checking convergence
		
		set mv [expr $wIso/$g]
		set zetaVertical 0.1
		set cv [expr 2.0*$zetaVertical*sqrt($kvc*$mv)]
		uniaxialMaterial Elastic 10 $kvc
		uniaxialMaterial Elastic 11 0.0

		# frictionModel Coulomb tag mu
		frictionModel Coulomb 1 $mu1
		frictionModel Coulomb 2 $mu2
		frictionModel Coulomb 3 $mu3

		# frictionModel VDependent tag muSlow muFast transRate
		#frictionModel VDependent 1 [expr 0.6*$mu1] $mu1 0.77
		#frictionModel VDependent 2 [expr 0.6*$mu2] $mu2 0.77
		#frictionModel VDependent 3 [expr 0.6*$mu3] $mu3 0.77
		
		# element singleFPBearing eleTag NodeI NodeJ frnMdlTag Reff kInit -P matTag -T matTag -My matTag -Mz matTag <-orient <x1 x2 x3> y1 y2 y3> <-shearDist sDratio> <-doRayleigh> <-mass m> <-iter maxIter tol>
		#element singleFPBearing 2 2 3 3 [expr $L2+$L3] [expr $wPlant*$mu3/$uy] -P 10 -T 11 -My 11 -Mz 11 -orient 1 0 0
		
		# element TripleFrictionPendulum $eleTag $iNode $jNode $frnMdlTag1 $frnMdlTag2 $frnMdlTag3 $matTagP $matTagT $matTagMy $matTagMz $L1 $L2 $L3 $d1 $d2 $d3 $W $uy $kvt $minFv $tol
		element TripleFrictionPendulum 2 2 3  1 2 3  10 11 11 11  $L1 $L2 $L3 $d1 $d2 $d3 $wIso $uy $kvt $minFv $tol
	}
}

# set the Rayleigh damping 
rayleigh $alphaM $betaK $betaKinit $betaKcomm

# Get initial stiffness
# ---------------------
initialize
wipeAnalysis

# ------------------------------
# End of model generation
# ------------------------------


if {$withGravity == 1} {
    # ------------------------------
    # Start of load generation
    # ------------------------------

    # Define gravity loads
    # --------------------
    timeSeries Linear 1 -factor 1.0
    # Create a Plain load pattern with a Linear TimeSeries
    pattern Plain 1 1 {
        # Create nodal loads
        #    nd    FX  FY         FZ  MX  MY  MZ 
        load    2   0.0 0.0 [expr -$wBldg-$expElmFact*$wTMD] 0.0 0.0 0.0
		if {$withTMD == 1 && $expElmFact < 1.0} {
			load    3   0.0 0.0 [expr -(1.0-$expElmFact)*$wTMD] 0.0 0.0 0.0
		}
    }
    # ------------------------------
    # End of load generation
    # ------------------------------


    # ------------------------------
    # Start of analysis generation
    # ------------------------------
    # create the system of equations
    system BandGeneral
    # create the DOF numberer
    numberer Plain
    # create the constraint handler
    constraints Transformation
    # create the convergence test
    test NormDispIncr 1.0e-12 25
    # create the integration scheme
    integrator LoadControl 0.1
    # create the solution algorithm
    algorithm Newton
    # create the analysis object 
    analysis Static
    # ------------------------------
    # End of analysis generation
    # ------------------------------


    # ------------------------------
    # Start of recorder generation
    # ------------------------------
    # create the recorder objects
    recorder Node -file $outDIR/Gravity_Node_Dsp.out -time -node 1 2 -dof 1 2 3 disp
    recorder Node -file $outDIR/Gravity_Node_Vel.out -time -node 1 2 -dof 1 2 3 vel
    recorder Node -file $outDIR/Gravity_Node_Acc.out -time -node 1 2 -dof 1 2 3 accel
    recorder Node -file $outDIR/Gravity_Node_Rct.out -time -node 1 2 -dof 1 2 3 reaction

    recorder Element -file $outDIR/Gravity_Elmt_Frc.out -time -ele 1 2 forces
    # --------------------------------
    # End of recorder generation
    # --------------------------------


    # ------------------------------
    # Perform the gravity analysis
    # ------------------------------
    # perform the gravity load analysis, requires 10 steps to reach the load level
    record
    analyze 10 
    puts "\nGravity load analysis completed";

    # Set the gravity loads to be constant & reset the time in the domain
    loadConst -time 0.0
    remove recorders
    wipeAnalysis
    # --------------------------------
    # End of gravity analysis
    # --------------------------------
}


# --------------------------------
# Perform an eigenvalue analysis
# --------------------------------
set pi [expr acos(-1.0)]
set lambda [eigen -fullGenLapack [expr 2*$numCtrlDOF]]
puts "\nEigenvalues at start of transient:"
puts "|   lambda   |  omega   |  period | frequency |"
foreach lambda $lambda {
    set omega [expr pow($lambda,0.5)]
    set period [expr 2.0*$pi/$omega]
    set frequ [expr 1.0/$period]
    puts [format "| %5.3e | %8.4f | %7.4f | %9.4f |" $lambda $omega $period $frequ]
}
puts "\n"
wipeAnalysis


if {$withTMD == 1} {
    # ------------------------------
    # Start of model generation
    # ------------------------------

    # create ModelBuilder (with two-dimensions and 2 DOF/node)
    model BasicBuilder -ndm 3 -ndf 6

    # Load OpenFresco package
    # -----------------------
    # (make sure all dlls are in the same folder as openSees.exe)
    loadPackage OpenFresco

    # Define control points
    # ---------------------
    # expControlPoint $cpTag <-node $nodeTag> $dof $rspType <-fact $f> <-lim $l $u> <-isRel> ...
    if {$numCtrlDOF == 1} {
        expControlPoint 1  1 disp
        expControlPoint 2  1 disp 1 force
    } elseif {$numCtrlDOF == 2} {
        expControlPoint 1  1 disp 2 disp
        expControlPoint 2  1 disp 2 disp 1 force 2 force
    } elseif {$numCtrlDOF == 3} {
        expControlPoint 1  1 disp 2 disp 3 disp
        expControlPoint 2  1 disp 2 disp 3 disp 1 force 2 force 3 force
    }

    # Define experimental control
    # ---------------------------
    if {$expCtrlType == "SimFEAdapter"} {
        expControl SimFEAdapter 1 "127.0.0.1" 44000 -trialCP 1 -outCP 2 
    } elseif {$expCtrlType == "xPCtarget"} {
        expControl xPCtarget 1 "192.168.2.20" 22222 "C:/Projects/RTActualTestModels/cmAPI-xPCTarget-SCRAMNetGT-469D/HybridControllerD2D2" -trialCP 1 -outCP 2
    } elseif {$expCtrlType == "SCRAMNet"} {
        expControl SCRAMNet 1 4096 1 -nodeID 4
    } elseif {$expCtrlType == "SCRAMNetGT"} {
        expControl SCRAMNetGT 1 2048 6 -nodeID 3
    }

    # Define experimental setup
    # -------------------------
    # expSetup NoTransformation $tag <–control $ctrlTag> –dof $dofs -sizeTrialOut $t $o <–trialDispFact $f> ...
    if {$numCtrlDOF == 1} {
        expSetup NoTransformation 1 -control 1 -dof 1 -sizeTrialOut 1 1  -outForceFact $expElmFact
    } elseif {$numCtrlDOF == 2} {
        expSetup NoTransformation 1 -control 1 -dof 1 2 -sizeTrialOut 2 2  -outForceFact $expElmFact $expElmFact
    } elseif {$numCtrlDOF == 3} {
        expSetup NoTransformation 1 -control 1 -dof 1 2 3 -sizeTrialOut 3 3  -outForceFact $expElmFact $expElmFact $expElmFact
    }
	
    # Define experimental site
    # ------------------------
    # expSite LocalSite $tag $setupTag
    expSite LocalSite 1 1
	
    # Define experimental elements
    # ----------------------------
    # roof of building
    # set kInitX 0.0
    # set kInitY 0.0
    # set kInitZ 0.0
    set kInitX [expr $expElmFact*250.0]
    set kInitY [expr $expElmFact*250.0]
    set kInitZ [expr $expElmFact*5000.0]
	
    # expElement generic $eleTag -node $Ndi -dof $dofNdi -dof $dofNdj ... -server $ipPort <$ipAddr>  <-ssl> <-dataSize $size>
    if {$expCtrlType == "SimFEAdapter"} {
        if {$numCtrlDOF == 1} {
            expElement generic 100 -node 2 -dof 1 -site 1 -initStif $kInitX -noRayleigh -checkTime
        } elseif {$numCtrlDOF == 2} {
            expElement generic 100 -node 2 -dof 1 2 -site 1 -initStif $kInitX 0.0 0.0 $kInitY -noRayleigh -checkTime
        } elseif {$numCtrlDOF == 3} {
            expElement generic 100 -node 2 -dof 1 2 3 -site 1 -initStif $kInitX 0.0 0.0 0.0 $kInitY 0.0 0.0 0.0 $kInitZ -noRayleigh -checkTime
        }
    } else {
        if {$numCtrlDOF == 1} {
            expElement generic 100 -node 2 -dof 1 -site 1 -initStif $kInitX -noRayleigh
        } elseif {$numCtrlDOF == 2} {
            expElement generic 100 -node 2 -dof 1 2 -site 1 -initStif $kInitX 0.0 0.0 $kInitY -noRayleigh
        } elseif {$numCtrlDOF == 3} {
            expElement generic 100 -node 2 -dof 1 2 3 -site 1 -initStif $kInitX 0.0 0.0 0.0 $kInitY 0.0 0.0 0.0 $kInitZ -noRayleigh
        }
    }
	
    # ------------------------------
    # End of model generation
    # ------------------------------
}


# ------------------------------
# Start of load generation
# ------------------------------

# Define dynamic loads
# --------------------
# set time series to be passed to multiple-support excitation
if {$inputType == "Sine"} {
    set npts 8192 
    set frequ 0.5
    set omega [expr 2*$pi*$frequ]
    set period [expr 1.0/$frequ]
    timeSeries Sine 11 0.0 30.0 $period -factor $ampScaleH
    timeSeries Sine 12 0.0 30.0 $period -shift [expr $pi/2.0] -factor [expr $ampScaleH*$omega]
    timeSeries Sine 13 0.0 30.0 $period -factor [expr -1.0*$ampScaleH*pow($omega,2.0)]
    
} elseif {$inputType == "TaperedSine"} {
    set npts 8192 
    timeSeries Path 11 -filePath motions/TaperedSine.DT2 -dt [expr 10.0/2048.0] -factor $ampScaleH
    timeSeries Path 12 -filePath motions/TaperedSine.VT2 -dt [expr 10.0/2048.0] -factor $ampScaleH
    timeSeries Path 13 -filePath motions/TaperedSine.AT2 -dt [expr 10.0/2048.0] -factor $ampScaleH

} elseif {$inputType == "LPGoriginal"} {
    set npts 8192 
    set lengthScale 3.0
    set timeScale [expr sqrt($lengthScale)]

    timeSeries Path 11 -filePath motions/RSN768_LOMAP_G04000.DT2 -dt [expr 0.005/$timeScale] -factor [expr $cm2in*$ampScaleH]
    timeSeries Path 12 -filePath motions/RSN768_LOMAP_G04000.VT2 -dt [expr 0.005/$timeScale] -factor [expr $cm2in*$ampScale*$timeScaleH]
    timeSeries Path 13 -filePath motions/RSN768_LOMAP_G04000.AT2 -dt [expr 0.005/$timeScale] -factor [expr $g*$ampScaleH*pow($timeScale,2)]

    timeSeries Path 14 -filePath motions/RSN768_LOMAP_G04090.DT2 -dt [expr 0.005/$timeScale] -factor [expr $cm2in*$ampScaleH]
    timeSeries Path 15 -filePath motions/RSN768_LOMAP_G04090.VT2 -dt [expr 0.005/$timeScale] -factor [expr $cm2in*$ampScaleH*$timeScale]
    timeSeries Path 16 -filePath motions/RSN768_LOMAP_G04090.AT2 -dt [expr 0.005/$timeScale] -factor [expr $g*$ampScaleH*pow($timeScale,2)]

    timeSeries Path 17 -filePath motions/RSN768_LOMAP_G04-UP.DT2 -dt [expr 0.005/$timeScale] -factor [expr $cm2in*$ampScaleV]
    timeSeries Path 18 -filePath motions/RSN768_LOMAP_G04-UP.VT2 -dt [expr 0.005/$timeScale] -factor [expr $cm2in*$ampScaleV*$timeScale]
    timeSeries Path 19 -filePath motions/RSN768_LOMAP_G04-UP.AT2 -dt [expr 0.005/$timeScale] -factor [expr $g*$ampScaleV*pow($timeScale,2)]

} elseif {$inputType == "LPGscaled"} {
    set npts 8192 
    set lengthScale 3.0
    set timeScale [expr sqrt($lengthScale)]

    timeSeries Path 11 -filePath motions/RSN768_LOMAP_G04000.dsp -dt [expr 0.005/$timeScale] -factor $ampScaleH
    timeSeries Path 12 -filePath motions/RSN768_LOMAP_G04000.vel -dt [expr 0.005/$timeScale] -factor $ampScaleH
    timeSeries Path 13 -filePath motions/RSN768_LOMAP_G04000.acc -dt [expr 0.005/$timeScale] -factor [expr $g*$ampScaleH]

    timeSeries Path 14 -filePath motions/RSN768_LOMAP_G04090.dsp -dt [expr 0.005/$timeScale] -factor $ampScaleH
    timeSeries Path 15 -filePath motions/RSN768_LOMAP_G04090.vel -dt [expr 0.005/$timeScale] -factor $ampScaleH
    timeSeries Path 16 -filePath motions/RSN768_LOMAP_G04090.acc -dt [expr 0.005/$timeScale] -factor [expr $g*$ampScaleH]

    timeSeries Path 17 -filePath motions/RSN768_LOMAP_G04_UP.dsp -dt [expr 0.005/$timeScale] -factor $ampScaleV
    timeSeries Path 18 -filePath motions/RSN768_LOMAP_G04_UP.vel -dt [expr 0.005/$timeScale] -factor $ampScaleV
    timeSeries Path 19 -filePath motions/RSN768_LOMAP_G04_UP.acc -dt [expr 0.005/$timeScale] -factor [expr $g*$ampScaleV]

} elseif {$inputType == "SHWoriginal"} {
    set npts 10240 
    set lengthScale 3.0
    set timeScale [expr sqrt($lengthScale)]

    timeSeries Path 11 -filePath motions/RSN728_SUPER.B_B-WSM090.DT2 -dt [expr 0.005/$timeScale] -factor [expr $cm2in*$ampScaleH]
    timeSeries Path 12 -filePath motions/RSN728_SUPER.B_B-WSM090.VT2 -dt [expr 0.005/$timeScale] -factor [expr $cm2in*$ampScaleH*$timeScale]
    timeSeries Path 13 -filePath motions/RSN728_SUPER.B_B-WSM090.AT2 -dt [expr 0.005/$timeScale] -factor [expr $g*$ampScaleH*pow($timeScale,2)]

    timeSeries Path 14 -filePath motions/RSN728_SUPER.B_B-WSM180.DT2 -dt [expr 0.005/$timeScale] -factor [expr $cm2in*$ampScaleH]
    timeSeries Path 15 -filePath motions/RSN728_SUPER.B_B-WSM180.VT2 -dt [expr 0.005/$timeScale] -factor [expr $cm2in*$ampScaleH*$timeScale]
    timeSeries Path 16 -filePath motions/RSN728_SUPER.B_B-WSM180.AT2 -dt [expr 0.005/$timeScale] -factor [expr $g*$ampScaleH*pow($timeScale,2)]

    timeSeries Path 17 -filePath motions/RSN728_SUPER.B_B-WSM-UP.DT2 -dt [expr 0.005/$timeScale] -factor [expr $cm2in*$ampScaleV]
    timeSeries Path 18 -filePath motions/RSN728_SUPER.B_B-WSM-UP.VT2 -dt [expr 0.005/$timeScale] -factor [expr $cm2in*$ampScaleV*$timeScale]
    timeSeries Path 19 -filePath motions/RSN728_SUPER.B_B-WSM-UP.AT2 -dt [expr 0.005/$timeScale] -factor [expr $g*$ampScaleV*pow($timeScale,2)]

} elseif {$inputType == "SHWscaled"} {
    set npts 10240 
    set lengthScale 3.0
    set timeScale [expr sqrt($lengthScale)]

    timeSeries Path 11 -filePath motions/RSN728_SUPER.B_B_WSM090.dsp -dt [expr 0.005/$timeScale] -factor $ampScaleH
    timeSeries Path 12 -filePath motions/RSN728_SUPER.B_B_WSM090.vel -dt [expr 0.005/$timeScale] -factor $ampScaleH
    timeSeries Path 13 -filePath motions/RSN728_SUPER.B_B_WSM090.acc -dt [expr 0.005/$timeScale] -factor [expr $g*$ampScaleH]

    timeSeries Path 14 -filePath motions/RSN728_SUPER.B_B_WSM180.dsp -dt [expr 0.005/$timeScale] -factor $ampScaleH
    timeSeries Path 15 -filePath motions/RSN728_SUPER.B_B_WSM180.vel -dt [expr 0.005/$timeScale] -factor $ampScaleH
    timeSeries Path 16 -filePath motions/RSN728_SUPER.B_B_WSM180.acc -dt [expr 0.005/$timeScale] -factor [expr $g*$ampScaleH]

    timeSeries Path 17 -filePath motions/RSN728_SUPER.B_B_WSM_UP.dsp -dt [expr 0.005/$timeScale] -factor $ampScaleV
    timeSeries Path 18 -filePath motions/RSN728_SUPER.B_B_WSM_UP.vel -dt [expr 0.005/$timeScale] -factor $ampScaleV
    timeSeries Path 19 -filePath motions/RSN728_SUPER.B_B_WSM_UP.acc -dt [expr 0.005/$timeScale] -factor [expr $g*$ampScaleV]

}

# create MultipleSupport excitation load pattern
pattern  MultipleSupport  2  {
    # groundMotion $gmTag type -disp $tsTag 
    groundMotion  1  Plain  -disp 11  -vel 12  -accel 13
    if {$numCtrlDOF >= 2} {
        groundMotion  2  Plain  -disp 14  -vel 15  -accel 16
    }
    if {$numCtrlDOF >= 3} {
        groundMotion  3  Plain  -disp 17  -vel 18  -accel 19
    }
    
    # imposedMotion $nodeTag $dofTag $gmTag 
    imposedMotion  1  1  1 
    if {$numCtrlDOF >= 2} {
        imposedMotion  1  2  2
    }
    if {$numCtrlDOF >= 3} {
        imposedMotion  1  3  3
    }        
}
# ------------------------------
# End of load generation
# ------------------------------


# ------------------------------
# Start of analysis generation
# ------------------------------
# create the system of equations
system BandGeneral
# create the DOF numberer
numberer Plain
# create the constraint handler
constraints Transformation
# create the convergence test
#test NormDispIncr 1.0e-12 25
# create the integration scheme
#integrator NewmarkExplicit 0.5
#integrator HHTGeneralizedExplicit 0.0 0.5
integrator AlphaOSGeneralized 0.0
# create the solution algorithm
algorithm Linear
# create the analysis object 
analysis Transient
# ------------------------------
# End of analysis generation
# ------------------------------


# ------------------------------
# Start of recorder generation
# ------------------------------
# create the recorder objects
recorder Node -file $outDIR/Node_Dsp.out -time -node 1 2 3 -dof 1 2 3 disp
recorder Node -file $outDIR/Node_Vel.out -time -node 1 2 3 -dof 1 2 3 vel
recorder Node -file $outDIR/Node_Acc.out -time -node 1 2 3 -dof 1 2 3 accel
recorder Node -file $outDIR/Node_Rct.out -time -node 1 2 3 -dof 1 2 3 reaction

recorder Element -file $outDIR/Elmt_Frc.out     -time -ele 100 1 2 forces
recorder Element -file $outDIR/Elmt_ctrlDsp.out -time -ele 100 ctrlDisp
recorder Element -file $outDIR/Elmt_daqDsp.out  -time -ele 100 daqDisp
recorder Element -file $outDIR/Elmt_daqFrc.out  -time -ele 100 daqForce

if {$withTMD == 1} {
    if {$expCtrlType == "SCRAMNet" || $expCtrlType == "SCRAMNetGT"} {
        expRecorder Control -file $outDIR/Control_ctrlDsp.out -time -control 1 ctrlDisp
    } else {
        expRecorder Control -file $outDIR/Control_ctrlDsp.out -time -control 1 ctrlSig
    }
}
# --------------------------------
# End of recorder generation
# --------------------------------


# ------------------------------
# Finally perform the analysis
# ------------------------------
# record initial state of model 
record
# open output file for writing
set outFileID [open $outDIR/elapsedTime.txt w]
# perform the transient analysis
set tTot [time {
    for {set i 1} {$i < $npts} {incr i} {
        set t [time {analyze  1  [expr 10.0/2048.0]}]
        puts $outFileID $t
        #puts "step $i"
    }
}]
puts "\nElapsed Time = $tTot \n"
# close the output file
close $outFileID

wipeAnalysis
wipe
exit
# --------------------------------
# End of analysis
# --------------------------------
