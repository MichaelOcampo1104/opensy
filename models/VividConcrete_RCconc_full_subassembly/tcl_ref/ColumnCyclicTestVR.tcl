# Declare a 2d model
model BasicBuilder -ndm 3

# Define constants
set pi [expr {2.0*asin(1.0)}]
set g 386.089

# Refer modeling subfiles or procedures
source DesignVariableVR.tcl
source CreateConcreteMaterial.tcl
source CreateRCColumnSection.tcl
source GetGaussLobattoIP.tcl
source LoadingAlgorithmVR.tcl
source LoadingParameterVR.tcl

# Define nodes
node 1	0 0 0
node 2	0 0 $Lcol
node 10001	0 0 0
node 10002	0 0 $Lcol

# Define boundary condition
fix 10001	1 1 1 1 1 1
fix 1		1 0 0 0 1 1
fix 2		1 0 0 0 1 1
fix 10002	1 0 0 1 1 1

# Define shear section type
set ShearTag "NonLinear"

# Set up integration points
set LIP ""
set LIPR ""
set XIP ""
set IntegrationTag "GaussLobattol"
if {$IntegrationTag == "NewtonCotes"} {
	for {set IPTag 1} {$IPTag <= $numIntgrPts} {incr IPTag} {
		set LIP [lappend LIP [expr $Lcol/$numIntgrPts]];	# NewtonCotes: uniformly distributed integration points
	}
} else {
	set tempIP [GetGaussLobattolLIP $numIntgrPts];
	set tempXIP [lindex $tempIP 0]; 
	set tempLIP [lindex $tempIP 1];
	for {set IPTag 1} {$IPTag <= $numIntgrPts} {incr IPTag} {
		set LIPR [lappend LIPR [expr 0.5*[lindex $tempLIP $IPTag-1]]];
		set LIP [lappend LIP [expr 0.5*[lindex $tempLIP $IPTag-1]*$Lcol]];
		set XIP [lappend XIP [expr 0.5*[lindex $tempXIP $IPTag-1]+0.5]];
	}
}

# Define material properties
set nfCoreY 1
set nfCoreZ 100
set nfCoverY 1
set nfCoverZ 2
for {set IPTag 1} {$IPTag <= $numIntgrPts} {incr IPTag} {
	set ConcrCoverID	[expr $IPTag*10+1]
	set ConcrCoreID	[expr $IPTag*10+2]
	set SteelID		[expr $IPTag*10+3]
	DefineRegularizedUnconfinedConcreteMaterial "Concrete02" 1 $ConcrCoverID $fc [lindex $LIP $IPTag-1]
	DefineRegularizedConfinedConcreteMaterial "Concrete02" 1 $ConcrCoreID $fc $nl $s [expr $b-2.0*$c-2.0*$db] $rou $fyt [lindex $LIP $IPTag-1]
	set Lgage [lindex $LIP $IPTag-1]
	puts "Lgage/LIP = [expr $Lgage/[lindex $LIP $IPTag-1]]"
	set Epyr_reg [expr [lindex $LIP $IPTag-1]/$Lgage*0.01]
	set esu_temp [expr ($eult-$fyl/$Es-$esh)*$Lgage/[lindex $LIP $IPTag-1]+$fyl/$Es+$esh]
	
	if {$DFTag == 1} {
		uniaxialMaterial ReinforcingSteel [expr $SteelID+10000] $fyl $ful \
			$Es [expr [lindex $LIP $IPTag-1]/$Lgage*$Esh] $esh $esu_temp \
			-MPCurveParams [expr 1/$MPR1] $MPR2 $MPR3;
		uniaxialMaterial DuctileFracture $SteelID [expr $SteelID+10000] \
			-c_mono $c_mono -c_cycl $c_cycl -c_symm $c_symm \
			-E_s $Es -esu $esu_temp -k1 $k1 -k2 $k2 -db $db -b1 $b1 -b2 $b2;
	} else {
		uniaxialMaterial ReinforcingSteel $SteelID $fyl $ful \
			$Es [expr [lindex $LIP $IPTag-1]/$Lgage*$Esh] $esh $esu_temp \
			-MPCurveParams [expr 1/$MPR1] $MPR2 $MPR3;
	}
	CreateColumnSection [expr 10+$IPTag] $h $b $c $ConcrCoreID $ConcrCoverID $SteelID $db $Asli $nlb $nlt $Asli $nlm $ShearTag $fc $fyt $rou $nfCoreY $nfCoreZ $nfCoverY $nfCoverZ
}

# Set up bar-slip section
set ke	[expr ($nl-2.)/$nl*(1-$s/[expr $b-2.0*$c-2.0*$db])]
set fl	[expr $ke*$rou*$fyt]
set Kfc 	[expr -1.254+2.254*sqrt(1.0+7.94*$fl/(-$fc))-2*$fl/(-$fc)]
set BarslipSteelID	10001
set BarslipConcrCoverID	10002
set BarslipConcrCoreID	10003
set BarslipAlpha		0.4
set Barslipb		$bs
set BarslipR		$BR
set Su_Sy			[expr 1.0+2.0*(1.0+$eult/($fyl/$Es))*(($ful/$fyl)-1)]
puts "Sy = $Sy"
puts "Su/Sy = $Su_Sy"
uniaxialMaterial Bond_SP01 $BarslipSteelID $fyl $Sy $ful $Su $Barslipb $BarslipR
DefineRegularizedUnconfinedConcreteMaterial "Concrete02" 1 $BarslipConcrCoverID $fc -1
DefineRegularizedConfinedConcreteMaterial "Concrete02" 1 $BarslipConcrCoreID $fc $nl $s $b $rou $fyt -1
CreateColumnSection 10001 $h $b $c $BarslipConcrCoreID $BarslipConcrCoverID $BarslipSteelID $db $Asli $nlb $nlt $Asli $nlm $ShearTag $fc $fyt $rou $nfCoreY $nfCoreZ $nfCoverY $nfCoverZ

# Create fiber elements
set transfTag 1
#geomTransf PDelta $transfTag
geomTransf PDelta $transfTag 1 0 0
#geomTransf Linear $transfTag
set secTags ""
for {set IPTag 1} {$IPTag <= $numIntgrPts} {incr IPTag} {
	set secTags [lappend secTags [expr 10+$IPTag]]
}
puts $secTags
set integration "UserDefined $numIntgrPts $secTags $XIP $LIPR"
element forceBeamColumn 1 1 2 $transfTag $integration
element zeroLengthSection 10001 10001 1 10001 -orient 0 0 1 0 -1 0
element zeroLengthSection 10002 2 10002 10001 -orient 0 0 1 0 -1 0

# Define axial loads
pattern Plain 1 Linear {
	load 10002 0.0 0.0 $P 0.0 0.0 0.0
}

# Update state
puts "Complete modeling."

# Conduct the gravity analysis
set numsteps_grav 10
set tol 1e-8
set maxiter 500
constraints Plain
numberer RCM
system BandGeneral
test RelativeEnergyIncr $tol $maxiter
algorithm Newton
integrator LoadControl [expr {1.0/$numsteps_grav}]
analysis Static
if {[analyze $numsteps_grav]} {
	puts "Application of gravity load failed"
} else {
	puts "Applied gravity loads."
}
loadConst -time 0.0
wipeAnalysis

# Set up recorder
recorder Node -file ./CyclicOutputVR/disp.out -time -node 2 -dof 2 disp
recorder Node -file ./CyclicOutputVR/force.out -time -node 10001 -dof 2 reaction
recorder Element -file ./CyclicOutputVR/SteelBot.out -time -ele 1 section 1 fiber [expr -$h/2.0+$c+0.5*$db] [expr $b/2.0-$c-0.5*$db] stressStrain
recorder Element -file ./CyclicOutputVR/SteelTop.out -time -ele 1 section 1 fiber [expr $h/2.0-$c-0.5*$db] [expr $b/2.0-$c-0.5*$db] stressStrain
recorder Element -file ./CyclicOutputVR/SteelBot2.out -time -ele 1 section 2 fiber [expr -$h/2.0+$c+0.5*$db] [expr $b/2.0-$c-0.5*$db] stressStrain
recorder Element -file ./CyclicOutputVR/SteelTop2.out -time -ele 1 section 2 fiber [expr $h/2.0-$c-0.5*$db] [expr $b/2.0-$c-0.5*$db] stressStrain

recorder Element -file ./CyclicOutputVR/FISteelBot.out -time -ele 1 section 1 fiber [expr -$h/2.0+$c+0.5*$db] [expr $b/2.0-$c-0.5*$db] damage
recorder Element -file ./CyclicOutputVR/FISteelTop.out -time -ele 1 section 1 fiber [expr $h/2.0-$c-0.5*$db] [expr $b/2.0-$c-0.5*$db] damage
recorder Element -file ./CyclicOutputVR/FISteelBot2.out -time -ele 1 section 2 fiber [expr -$h/2.0+$c+0.5*$db] [expr $b/2.0-$c-0.5*$db] damage
recorder Element -file ./CyclicOutputVR/FISteelTop2.out -time -ele 1 section 2 fiber [expr $h/2.0-$c-0.5*$db] [expr $b/2.0-$c-0.5*$db] damage

recorder Element -file ./CyclicOutputVR/ConcrCoverBot.out -time -ele 1 section 1 fiber [expr -$h/2.0] 0.0 stressStrain
recorder Element -file ./CyclicOutputVR/ConcrCoverTop.out -time -ele 1 section 1 fiber [expr $h/2.0] 0.0 stressStrain
recorder Element -file ./CyclicOutputVR/ConcrCoreBot.out -time -ele 1 section 1 fiber [expr -$h/2.0+$c+$db] 0.0 stressStrain
recorder Element -file ./CyclicOutputVR/ConcrCoreTop.out -time -ele 1 section 1 fiber [expr $h/2.0-$c-$db] 0.0 stressStrain
recorder Element -file ./CyclicOutputVR/BarSlipForce.out -time -ele 10001 force
recorder Element -file ./CyclicOutputVR/BarSlipDisp.out -time -ele 10001 deformation

# more recorders
recorder Node -file ./CyclicOutputVR/node_disp_1.out -time -node 1 -dof 1 2 3 4 5 6 disp
recorder Node -file ./CyclicOutputVR/node_disp_2.out -time -node 2 -dof 1 2 3 4 5 6 disp
for {set ip_id 1} {$ip_id < $numIntgrPts+1} {incr ip_id} {
	recorder Element -file ./CyclicOutputVR/curvature_1_ip$ip_id.out -ele 1 section $ip_id deformation
	recorder Element -file ./CyclicOutputVR/force_1_ip$ip_id.out -ele 1 section $ip_id force
}

# Conduct loading analysis
set LoadType "CyclicStep"
set Tol 1e-6
set numIter 800
RunStaticLoading 10002 2 $LoadType $LoadHistory $Dincr $numIter $Tol