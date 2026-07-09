# Declare a 2d model
model BasicBuilder -ndm 3

# Define constants
set	pi	[expr {2.0*asin(1.0)}];
set	g	386.089;
set	P	-522.0;
set	mm_in	25.4;
set	mpa_ksi	6.895;

# Define material tags
set	mattag_steel	1;
set	mattag_coverconcrete	2;
set	mattag_coreconcrete	3;
set	mattag_barslip1	4;
set	mattag_barslip2	5;
set	mattag_barslip3	6
set	mattag_shear	7;

# Define section tags
set	sectag_flexure	1;
set	sectag_shear	2;
set	sectag_barslip	3;
set	sectag_fiber	4;
set	sectag_zerolength	5;

# Define shear model type
set	ShearTag	"NonLinear";

# Load material properties and integration info
source DesignPropertyC1.tcl
source GetGaussLobattoIP.tcl

puts "Loaded design properties."

# Set up element number and integration points
set	numEle	1;
set	numIntgrPts 6;
set	LIP	""
set	LIPR	""
set	XIP	""
set	IntegrationTag	"GaussLobattol"
if {$IntegrationTag == "NewtonCotes"} {
	for {set IPTag 1} {$IPTag <= $numIntgrPts} {incr IPTag} {
		set LIP [lappend LIP [expr $L/numEle/$numIntgrPts]];	# NewtonCotes: uniformly distributed integration points
	}
} else {
	set tempIP [GetGaussLobattolLIP $numIntgrPts];
	set tempXIP [lindex $tempIP 0]; 
	set tempLIP [lindex $tempIP 1];
	for {set IPTag 1} {$IPTag <= $numIntgrPts} {incr IPTag} {
		set LIPR [lappend LIPR [expr 0.5*[lindex $tempLIP $IPTag-1]]];
		set LIP [lappend LIP [expr 0.5*[lindex $tempLIP $IPTag-1]*$L/$numEle]];
		set XIP [lappend XIP [expr 0.5*[lindex $tempXIP $IPTag-1]+0.5]];
	}
}

# Create concrete mateirals
# cover concrete
set	eco	[expr 2.0*$fc/$Ec];
# core concrete
set	ds	[expr $D-2.0*$c-$dbt];
set	Ac	[expr 0.25*$pi*$ds*$ds];
set	rouCC	[expr $nsl*$Asl/$Ac];
set	Acc	[expr $Ac*(1-$rouCC)];
set	Ae	[expr 0.25*$pi*($ds-0.5*($s-$dbt))*($ds-0.5*($s-$dbt))];
set	ke	[expr $Ae/$Acc];
set	rouS	[expr 4.0*$Ast/$ds/$s];
set	fl	[expr 0.5*$rouS*$fyt];
set	flp	[expr $fl*$ke];
set	fcc	[expr $fc*(-1.254+2.254*sqrt(1+7.94*$flp/abs($fc))-2.0*$flp/abs($fc))];
set	ecc	[expr $eco*(1.0+5.0*($fcc/$fc-1.0))];
set	fpcu	[expr 0.2*$fcc];
set	Gfc	[expr 1.7*2.0*(-$fc)*$mpa_ksi];
for {set IPTag 1} {$IPTag <= $numIntgrPts} {incr IPTag} {
	set	ConcrCoverID	[expr $IPTag*10+1];
	set	ConcrCoreID		[expr $IPTag*10+2];
	set	SteelID		[expr $IPTag*10+3];
	set	tempLIP		[lindex $LIP $IPTag-1];
	set	ecu	[expr -($Gfc/0.6/(-$fcc*$mpa_ksi)/($tempLIP*$mm_in)-0.8*(-$fcc)/$Ec+(-$ecc))];
	puts "ecu = $ecu"
	uniaxialMaterial Concrete02 $ConcrCoverID $fc $eco 0.0 -0.008 0.1 $ft [expr 0.05*$Ec];
	uniaxialMaterial Concrete02 $ConcrCoreID $fcc $ecc $fpcu $ecu 0.1 $ft [expr 0.05*$Ec];
	# Create steel material
	uniaxialMaterial ReinforcingSteel $SteelID $fyl $ful $Esl $Esh $esh $esu;
	#uniaxialMaterial Steel02 $mattag_steel $fyl $Esl $b 18 0.925 0.15;
}
# Create bar-slip material
set	alpha	0.4;
set	Sy	[expr 0.1*pow($dbl/4000.0*$fyl*1000.0/sqrt(-$fc*1000.0)*(2.0*$alpha+1.0),1.0/$alpha)+0.013];
set	Su	[expr 50.0*$Sy];
set	b	0.3;
set	R	0.9;
uniaxialMaterial Bond_SP01 $mattag_barslip1 $fyl $Sy $ful $Su $b $R;
uniaxialMaterial Concrete02 $mattag_barslip2 $fcc $ecc [expr 4.0*$fpcu] [expr 10.0*$ecc] 0.1 $ft [expr 0.05*$Ec];
uniaxialMaterial Concrete02 $mattag_barslip3 $fc $eco 0.0 -0.008 0.1 $ft [expr 0.05*$Ec];

set	numCirc	20;
set	numRad1	4;
set	numRad2	40;
set	intRad	[expr 0.5*$D-$c-$dbt];
set	extRad	[expr 0.5*$D];
# Create cross sections per IP point
# shear
set	Gc	[expr $Ec/2.0/(1.0+0.2)];
set	vn	[expr 3.0*sqrt(-$fc*1000.0)/1000.0+$rouS*$fyt];
if {$vn > [expr 8.0*sqrt(-$fc*1000.0)/1000.0]} {
	set vn [expr 8.0*sqrt(-$fc*1000.0)/1000.0];
}
set	s1p	[expr 0.002*sqrt(-$fc*1000.0)*$Ac];
set	e1p	[expr $s1p/$Gc/$Ac];
set	s2p	[expr 0.6*$vn*$Ac];
set	e2p	[expr $e1p+($s2p-$s1p)/0.4/$Gc/$Ac];
set	s3p	[expr $vn*$Ac];
set	e3p	[expr $e2p+0.4*$vn/0.1/$Gc];
set	s1n	[expr -$s1p];
set	e1n	[expr -$e1p];
set	s2n	[expr -$s2p];
set	e2n	[expr -$e2p];
set	s3n	[expr -$s3p];
set	e3n	[expr -$e3p];
set	pinchX	1.0;
set	pinchY	1.0;
set	damage1	0.0;
set	damage2	0.0;
set	beta	0.0;
if {$ShearTag == "Linear"} {
	uniaxialMaterial Elastic $mattag_shear [expr 0.1*$s1p/$e1p];
} else {
	uniaxialMaterial Hysteretic $mattag_shear $s1p $e1p $s2p $e2p $s3p $e3p $s1n $e1n $s2n $e2n $s3n $e3n $pinchX $pinchY $damage1 $damage2 $beta;
}
# flexure
for {set IPTag 1} {$IPTag <= $numIntgrPts} {incr IPTag} {
	section Fiber [expr $IPTag*100+1] -GJ 10000000.0 {
	# cover concrete
	patch circ [expr $IPTag*10+1] $numCirc $numRad1 0.0 0.0 $intRad $extRad 0.0 360.0;
	# core concrete
	patch circ [expr $IPTag*10+2] $numCirc $numRad2 0.0 0.0 0.0 $intRad 0.0 360.0;
	# reinforcement
	set	bartag	0;
	while {$bartag<$nsl} {
		set	yLoc	[expr $intRad*sin($bartag*2.0*$pi/$nsl)];
		set	zLoc	[expr $intRad*cos($bartag*2.0*$pi/$nsl)];
		fiber $yLoc $zLoc $Asl [expr $IPTag*10+3];
		incr bartag;
	}
	}
	section Aggregator [expr $IPTag*10+1] $mattag_shear Vy $mattag_shear Vz -section [expr $IPTag*100+1];
}

# bar-slip
section Fiber $sectag_barslip -GJ 10000000.0 {
# cover concrete
patch circ $mattag_barslip3 $numCirc $numRad1 0.0 0.0 $intRad $extRad 0.0 360.0;
# core concrete
patch circ $mattag_barslip2 $numCirc $numRad2 0.0 0.0 0.0 $intRad 0.0 360.0;
# reinforcement
set	bartag	0;
while {$bartag<$nsl} {
	set	yLoc	[expr $intRad*cos($bartag*2.0*$pi/$nsl)];
	set	zLoc	[expr $intRad*sin($bartag*2.0*$pi/$nsl)];
	fiber $yLoc $zLoc $Asl $mattag_barslip1;
	incr bartag;	
}
}
section Aggregator $sectag_zerolength $mattag_shear Vy $mattag_shear Vz -section $sectag_barslip;

# Create nodes
node 1 0 0 0;
node 2 0 0 0 -mass 0.0 0.0 0.0 0.0 0.0 0.0;
node 3 0 0 $L -mass [expr -$P/$g] 0.0 1e-2 0.0 [expr -0.125*$P*$L*$L/$g] 0.0;
fix 1 1 1 1 1 1 1;
fix 2 0 0 0 0 0 1;

# Create fiber-based element
set	transfTag 1;
geomTransf PDelta $transfTag 0 -1 0;
set secTags ""
for {set IPTag 1} {$IPTag <= $numIntgrPts} {incr IPTag} {
	set	secTags	[lappend secTags [expr $IPTag*10+1]]
}
set	integration	"UserDefined $numIntgrPts $secTags $XIP $LIPR";
element forceBeamColumn 1 2 3 $transfTag $integration;
# Create bar-slip element
element zeroLengthSection 101 1 2 $sectag_zerolength -orient 0 0 1 -1 0 0;

puts "Completed modeling."

# Apply gravity load
pattern Plain 1 Linear {
load 3 0.0 0.0 $P 0 0 0;
}

set numsteps_grav 10;
set tol 1e-6
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
	puts "Completed gravity-load analysis."
}
loadConst -time 0.0
wipeAnalysis

# Define the damping parameters
set dampRat 0.03
set dampRatF 1.0
set modes {1 2 3}

set eigenvalues [eigen -fullGenLapack [lindex $modes 2]]
set periodForRayleighDamping_1 [expr {2.0*$pi/sqrt([lindex $eigenvalues [lindex $modes 0]-1])}]
set periodForRayleighDamping_2 [expr {2.0*$pi/sqrt([lindex $eigenvalues [lindex $modes 1]-1])}]
set periodForRayleighDamping_3 [expr {2.0*$pi/sqrt([lindex $eigenvalues [lindex $modes 2]-1])}]

# Define damping for all beams and all columns (i.e. elastic elements), but not on the joints b/c they have the nonlinearity in them.  This is the approach proposed by Medina.  Compute the damping paramters based on Chopra text page 457.
set omegaI [expr (2.0 * $pi) / $periodForRayleighDamping_1]
set omegaJ [expr (2.0 * $pi) / ($periodForRayleighDamping_3)]
set alpha1Coeff [expr (2.0 * $omegaI * $omegaJ) / ($omegaI + $omegaJ)]
set alpha2Coeff [expr (2.0) / ($omegaI + $omegaJ)]
set alpha1  [expr $alpha1Coeff * $dampRat * $dampRatF]
set alpha2  [expr $alpha2Coeff * $dampRat * $dampRatF]
puts "T1 = $periodForRayleighDamping_1"
puts "T2 = $periodForRayleighDamping_2"
puts "T3 = $periodForRayleighDamping_3"

set ctrl_nodes {
    2
    3
}

source SquenceTestNew.tcl