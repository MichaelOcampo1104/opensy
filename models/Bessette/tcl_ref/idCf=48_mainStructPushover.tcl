###################################################################################################
# JP3 Parametric Study - Phase 1 - Structure Fixed-Base Analyses - Static Pushover Analysis
# 
# AnalysisID: "ModelConfig_id48_StructurePushoverAnalysis"
# 
# Struct. id: RC1
# 
# copyright: Caroline Bessette, University of Colorado Boulder, 04/17/2024 00:22
###################################################################################################
#--------------------------------------------------------------------------------------------------
#          00 - Set Up & Source Definition
#--------------------------------------------------------------------------------------------------

wipe
set startTime [clock clicks -milliseconds]

#--------------------------------------------------------------------------------------------------
#          1 - DEFINE NODES
#--------------------------------------------------------------------------------------------------

# Structure Nodes
model basic -ndm 3 -ndf 6
# tag x y z
node 3000001 -2.5 0 0
node 3000002 2.5 0 0
node 3000003 -2.5 0 4
node 3000004 -2.5 0 4
node 3000005 2.5 0 4
node 3000006 2.5 0 4
node 3000007 -2.5 0 1
node 3000008 2.5 0 1
node 3000009 -2.5 0 2
node 3000010 2.5 0 2
node 3000011 -2.5 0 3
node 3000012 2.5 0 3
node 3000013 -1.5 0 4
node 3000014 -0.5 0 4
node 3000015 0.5 0 4
node 3000016 1.5 0 4

model basic -ndm 3 -ndf 6
# tag x y z
node 5000001 -2.5 0 0
node 5000002 2.5 0 0

puts "Finished creating all structure nodes..."

#--------------------------------------------------------------------------------------------------
#          2 - MATERIALS
#--------------------------------------------------------------------------------------------------

# Structure Material
# Beam Column Elements
uniaxialMaterial Elastic 6 1000000000.0

# Spring Elements
# INPUT Properties
set Ke 6526.99;
set as_P 0.0279347;
set as_N 0.0279347;
set My_P 27.1256;
set My_N 27.1256;
set L_S 282.618;
set L_K 79926.5;
set L_A 9941.97;
set L_C 785.198;
set c_S 1;
set c_K 60186;
set c_A 0.192156;
set c_C 91.42;
set th_pP 0.0625298;
set th_pN 0.0625298;
set th_pcP 0.153246;
set th_pcN 0.153246;
set ResP 0.5;
set ResN 0.5;
set th_uP 0.242617;
set th_uN 0.242617;
set D_pos 0.292898;
set D_neg 0.292898;
set c_S     1.00;
set c_C     1.00;
set c_K     1.00;
set c_A     1.00;
set FmaxFyP 1.41539;
set FmaxFyN 1.41539;

uniaxialMaterial IMKPeakOriented 501 $Ke $th_pP $th_pcP $th_uP $My_P $FmaxFyP $ResP $th_pN $th_pcN $th_uN $My_N $FmaxFyN $ResN $L_S $L_C $L_A $L_K $c_S $c_C $c_A $c_K $D_pos $D_neg;


puts "Finished creating all materials..."

#--------------------------------------------------------------------------------------------------
#          3 - ELEMENTS
#--------------------------------------------------------------------------------------------------

# beam_column_elements elasticBeamColumn
model basic -ndm 3 -ndf 6

# Geometric transformation command
# z elements
geomTransf PDelta 4000001 1.0 0.0 -0.0
element elasticBeamColumn 4000001 3000001 3000007 0.64 2900000000.0 966666666.7 0.068266700000000000 0.034133299999999998 0.034133299999999998 4000001
geomTransf PDelta 4000002 1.0 0.0 -0.0
element elasticBeamColumn 4000002 3000007 3000009 0.64 2900000000.0 966666666.7 0.068266700000000000 0.034133299999999998 0.034133299999999998 4000002
geomTransf PDelta 4000003 1.0 0.0 -0.0
element elasticBeamColumn 4000003 3000009 3000011 0.64 2900000000.0 966666666.7 0.068266700000000000 0.034133299999999998 0.034133299999999998 4000003
geomTransf PDelta 4000004 1.0 0.0 -0.0
element elasticBeamColumn 4000004 3000011 3000003 0.64 2900000000.0 966666666.7 0.068266700000000000 0.034133299999999998 0.034133299999999998 4000004
geomTransf PDelta 4000005 1.0 0.0 -0.0
element elasticBeamColumn 4000005 3000002 3000008 0.64 2900000000.0 966666666.7 0.068266700000000000 0.034133299999999998 0.034133299999999998 4000005
geomTransf PDelta 4000006 1.0 0.0 -0.0
element elasticBeamColumn 4000006 3000008 3000010 0.64 2900000000.0 966666666.7 0.068266700000000000 0.034133299999999998 0.034133299999999998 4000006
geomTransf PDelta 4000007 1.0 0.0 -0.0
element elasticBeamColumn 4000007 3000010 3000012 0.64 2900000000.0 966666666.7 0.068266700000000000 0.034133299999999998 0.034133299999999998 4000007
geomTransf PDelta 4000008 1.0 0.0 -0.0
element elasticBeamColumn 4000008 3000012 3000005 0.64 2900000000.0 966666666.7 0.068266700000000000 0.034133299999999998 0.034133299999999998 4000008

# x elements
geomTransf Linear 4000009 0.0 0.0 1.0
element elasticBeamColumn 4000009 3000004 3000013 0.64 2900000000.0 966666666.7 0.068266700000000000 0.034133299999999998 0.034133299999999998 4000009
geomTransf Linear 4000010 0.0 0.0 1.0
element elasticBeamColumn 4000010 3000013 3000014 0.64 2900000000.0 966666666.7 0.068266700000000000 0.034133299999999998 0.034133299999999998 4000010
geomTransf Linear 4000011 0.0 0.0 1.0
element elasticBeamColumn 4000011 3000014 3000015 0.64 2900000000.0 966666666.7 0.068266700000000000 0.034133299999999998 0.034133299999999998 4000011
geomTransf Linear 4000012 0.0 0.0 1.0
element elasticBeamColumn 4000012 3000015 3000016 0.64 2900000000.0 966666666.7 0.068266700000000000 0.034133299999999998 0.034133299999999998 4000012
geomTransf Linear 4000013 0.0 0.0 1.0
element elasticBeamColumn 4000013 3000016 3000006 0.64 2900000000.0 966666666.7 0.068266700000000000 0.034133299999999998 0.034133299999999998 4000013

# zero_length_elements zeroLength
model basic -ndm 3 -ndf 6

# Structure base (Floor 1)
element zeroLength 600001 5000001 3000001 -mat 6 6 6 6 501 6 -dir 1 2 3 4 5 6
element zeroLength 600002 5000002 3000002 -mat 6 6 6 6 501 6 -dir 1 2 3 4 5 6

# per floor
element zeroLength 600003 3000003 3000004 -mat 6 6 6 6 501 6 -dir 1 2 3 4 5 6
element zeroLength 600004 3000005 3000006 -mat 6 6 6 6 501 6 -dir 1 2 3 4 5 6

puts "Finished creating all elements..."

#--------------------------------------------------------------------------------------------------
#          4 -  BOUNDARY CONDITIONS
#--------------------------------------------------------------------------------------------------

# Structure BC
model basic -ndm 3 -ndf 6
# Constraints.sp fix
fix 3000001 0 1 0 1 0 1
fix 3000002 0 1 0 1 0 1
fix 3000003 0 1 0 1 0 1
fix 3000004 0 1 0 1 0 1
fix 3000005 0 1 0 1 0 1
fix 3000006 0 1 0 1 0 1
fix 3000007 0 1 0 1 0 1
fix 3000008 0 1 0 1 0 1
fix 3000009 0 1 0 1 0 1
fix 3000010 0 1 0 1 0 1
fix 3000011 0 1 0 1 0 1
fix 3000012 0 1 0 1 0 1
fix 3000013 0 1 0 1 0 1
fix 3000014 0 1 0 1 0 1
fix 3000015 0 1 0 1 0 1
fix 3000016 0 1 0 1 0 1
# Fixed-Base condition
fix 5000001 1 1 1 1 1 1
fix 5000002 1 1 1 1 1 1

puts "Finished creating all boundary conditions..."

#--------------------------------------------------------------------------------------------------
#          5 - NODAL MASSES - STRUCTURE
#--------------------------------------------------------------------------------------------------

mass 3000003 3.446 0.0 0.0 0.0 0.0 0.0
mass 3000004 3.446 0.0 0.0 0.0 0.0 0.0
mass 3000005 3.446 0.0 0.0 0.0 0.0 0.0
mass 3000006 3.446 0.0 0.0 0.0 0.0 0.0

#--------------------------------------------------------------------------------------------------
#          7 - NODAL LOADS - STRUCTURE
#-------------------------------------------------------------------------------------------------

pattern Plain 2 Constant {
	 load 3000004 0.0 0.0 -67.6195 0.0 0.0 0.0
	 load 3000006 0.0 0.0 -67.6195 0.0 0.0 0.0
}
#--------------------------------------------------------------------------------------------------
#          8 - STAGE 1 - GRAVITY LOADS AND GRAVITY ANALYSIS
#--------------------------------------------------------------------------------------------------

puts ""
puts "BEGIN GRAVITY ANALYSIS"
# analyses command
constraints Penalty 1e+15 1e+15
numberer RCM
system BandGeneral
test NormDispIncr 1.0e-6 100 1
algorithm KrylovNewton -iterate current
integrator Newmark 0.50 0.25
set NstepGravity 10
set DGravity [expr 1.0/$NstepGravity]
integrator LoadControl $DGravity
analysis Static
analyze $NstepGravity

loadConst -time 0.0

#--------------------------------------------------------------------------------------------------
#          9. RECORDERS
#--------------------------------------------------------------------------------------------------

set dataDirPush ResultsPushover

file mkdir $dataDirPush

recorder Drift -file $dataDirPush/DriftRoof.out -time -iNode 5000001 -jNode 3000004 -dof 1 -perpDirn 3
recorder Node -file $dataDirPush/RoofDispx.out -time -node 3000004 -dof 1 disp
recorder Node -file $dataDirPush/VBase.out -time -node 5000001 5000002 -dof 1 reaction

set springele {600001 600003}
eval "recorder Element -file $dataDirPush/springforce.out -time -ele $springele force"
eval "recorder Element -file $dataDirPush/springdeform.out -time -ele $springele deformation"

#--------------------------------------------------------------------------------------------------
#          10. PUSHOVER ANALYSIS
#--------------------------------------------------------------------------------------------------

wipeAnalysis

puts "Running Pushover..."
set lat1 1.0

pattern Plain 200 Linear {
   load 3000004 $lat1 0.0 0.0 0.0 0.0 0.0
   load 3000006 $lat1 0.0 0.0 0.0 0.0 0.0
}

# displacement parameters
set IDctrlNode 3000003;					# node where disp is read for disp control
set IDctrlDOF 1;					    # degree of freedom read for disp control (1 = x displacement)
set Dmax [expr 0.1*4.0];		    # maximum displacement of pushover: 10
set Dincr [expr 0.001];				# displacement increment

# analysis commands
constraints Transformation
numberer RCM
system BandGeneral
test NormUnbalance 1e-3 10000
algorithm Newton
integrator DisplacementControl $IDctrlNode $IDctrlDOF $Dincr
analysis Static
set Nsteps [expr int($Dmax/$Dincr)]
set ok [analyze $Nsteps]
puts "Pushover complete"
# Reset for next analysis case
# ----------------------------
setTime 0.0
loadConst
remove recorders
wipeAnalysis
wipe

# --------------------------------------------------------------------------------------------------
