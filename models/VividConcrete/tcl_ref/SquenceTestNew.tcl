# Create recorders
set recorderdir "./TestResult"
recorder EnvelopeDrift -file $recorderdir/drift_env.out -iNode 1 -jNode 3 -dof 1 -perpDirn 3
recorder Node -file $recorderdir/disp.out -time -node 3 -dof 1 disp;
recorder Node -file $recorderdir/reaction.out -time -node 1 -dof 1 2 3 reaction;
recorder Drift -file $recorderdir/drift.out -time -iNode 1 -jNode 3 -dof 1 -perpDirn 3;
#set	bartag	0;
#while {$bartag<$nsl} {
	#recorder Element -file $recorderdir/SS_IP1_$bartag.out -time -ele 1 section 1 fiber [expr $intRad*sin($bartag*2.0*$pi/$nsl)] [expr $intRad*cos($bartag*2.0*$pi/$nsl)] stressStrain;
	#recorder Element -file $recorderdir/SS_IP2_$bartag.out -time -ele 1 section 2 fiber [expr $intRad*sin($bartag*2.0*$pi/$nsl)] [expr $intRad*cos($bartag*2.0*$pi/$nsl)] stressStrain;
	#recorder Element -file $recorderdir/SS_IP3_$bartag.out -time -ele 1 section 3 fiber [expr $intRad*sin($bartag*2.0*$pi/$nsl)] [expr $intRad*cos($bartag*2.0*$pi/$nsl)] stressStrain;
	#recorder Element -file $recorderdir/SS_IP4_$bartag.out -time -ele 1 section 4 fiber [expr $intRad*sin($bartag*2.0*$pi/$nsl)] [expr $intRad*cos($bartag*2.0*$pi/$nsl)] stressStrain;
	#recorder Element -file $recorderdir/SS_IP5_$bartag.out -time -ele 1 section 5 fiber [expr $intRad*sin($bartag*2.0*$pi/$nsl)] [expr $intRad*cos($bartag*2.0*$pi/$nsl)] stressStrain;
	#recorder Element -file $recorderdir/SS_IP6_$bartag.out -time -ele 1 section 6 fiber [expr $intRad*sin($bartag*2.0*$pi/$nsl)] [expr $intRad*cos($bartag*2.0*$pi/$nsl)] stressStrain;
	#recorder Element -file $recorderdir/SS2.out -time -ele 1 section 1 fiber [expr -0.5*$D+$c+$dbt] 0 stressStrain;
	#incr bartag;
#}
recorder Element -file $recorderdir/force.out -time -ele 1 force;

set	dt	0.0042;
recorder Node -file $recorderdir/node_disp_1.out -node 1 -dof 1 2 3 4 5 6 disp
recorder Node -file $recorderdir/node_disp_3.out -node 3 -dof 1 2 3 4 5 6 disp
for {set ip_id 1} {$ip_id < $numIntgrPts+1} {incr ip_id} {
	recorder Element -file $recorderdir/curvature_1_ip$ip_id.out -ele 1 section $ip_id deformation
	recorder Element -file $recorderdir/force_1_ip$ip_id.out -ele 1 section $ip_id force
}

# curvatures
set	ip_id	1;
while {$ip_id<=$numIntgrPts} {
	recorder Element -file $recorderdir/Curvature_IP$ip_id.out -ele 1 section $ip_id deformation;
	incr ip_id;
}
# bond rotation
recorder Element -file $recorderdir/bond_rotation.out -time -ele 101 deformation;

# Define the ground motion time series
puts "EQ1: Loma Prieta, Agnews State Hospital, 1.0x";
set	dt	0.0042;
set	numpts	25919;
timeSeries Path 101 -dt $dt -filePath ./TableInput/EQ1GM.txt -factor [expr $g*1.0]
set eq_load_pattern 101
pattern UniformExcitation $eq_load_pattern 1 -accel 101
source ./SolverNewmark.tcl
# source ./solver_cdm.tcl

loadConst -time 0.0
puts "EQ2: Loma Prieta, Corralitos, 1.0x";
set	dt	0.0042;
set	numpts	26399;
timeSeries Path 102 -dt $dt -filePath ./TableInput/EQ2GM.txt -factor [expr $g*1.0]
set eq_load_pattern 102
pattern UniformExcitation $eq_load_pattern 1 -accel 102
source ./SolverNewmark.tcl

loadConst -time 0.0
puts "EQ3: Loma Prieta, LGPC, 1.0x";
set	dt	0.0042;
set	numpts	24959;
timeSeries Path 103 -dt $dt -filePath ./TableInput/EQ3GM.txt -factor [expr $g*1.0]
set eq_load_pattern 103
pattern UniformExcitation $eq_load_pattern 1 -accel 103
source ./SolverNewmark.tcl

loadConst -time 0.0
puts "EQ4: Loma Prieta, Corralitos, 1.0x";
set	dt	0.0042;
set	numpts	25199;
timeSeries Path 104 -dt $dt -filePath ./TableInput/EQ4GM.txt -factor [expr $g*1.0]
set eq_load_pattern 104
pattern UniformExcitation $eq_load_pattern 1 -accel 104
source ./SolverNewmark.tcl

loadConst -time 0.0
puts "EQ5: Kobe, Takatori, -0.8x";
set	dt	0.0042;
set	numpts	36239;
timeSeries Path 105 -dt $dt -filePath ./TableInput/EQ5GM.txt -factor [expr $g*1.0]
set eq_load_pattern 105
pattern UniformExcitation $eq_load_pattern 1 -accel 105
source ./SolverNewmark.tcl

loadConst -time 0.0
puts "EQ6: Loma Prieta, LGPC, 1.0x";
set	dt	0.0042;
set	numpts	28319;
timeSeries Path 106 -dt $dt -filePath ./TableInput/EQ6GM.txt -factor [expr $g*1.0]
set eq_load_pattern 106
pattern UniformExcitation $eq_load_pattern 1 -accel 106
source ./SolverNewmark.tcl

# KZ: I commented the following sections out
if {0} {
	loadConst -time 0.0
	puts "EQ7: Kobe, Takatori, 1.0x";
	set	dt	0.01;
	set	numpts	[expr 4096+20.0/$dt];
	timeSeries Path 107 -dt $dt -filePath ./GroundMotion/RSN1120_KOBE_TAK000.txt -factor [expr $g*1.0]
	set eq_load_pattern 107
	pattern UniformExcitation $eq_load_pattern 1 -accel 107
	source ./SolverNewmark.tcl

	loadConst -time 0.0
	puts "EQ8: Kobe, Takatori, -1.2x";
	set	dt	0.01;
	set	numpts	[expr 4096+20.0/$dt];
	timeSeries Path 108 -dt $dt -filePath ./GroundMotion/RSN1120_KOBE_TAK000.txt -factor [expr -$g*1.2]
	set eq_load_pattern 108
	pattern UniformExcitation $eq_load_pattern 1 -accel 108
	source ./SolverNewmark.tcl

	loadConst -time 0.0
	puts "EQ9: Kobe, Takatori, 1.2x";
	set	dt	0.01;
	set	numpts	[expr 4096+20.0/$dt];
	timeSeries Path 109 -dt $dt -filePath ./GroundMotion/RSN1120_KOBE_TAK000.txt -factor [expr $g*1.2]
	set eq_load_pattern 109
	pattern UniformExcitation $eq_load_pattern 1 -accel 109
	source ./SolverNewmark.tcl

	loadConst -time 0.0
	puts "EQ10: Kobe, Takatori, 1.2x";
	set	dt	0.01;
	set	numpts	[expr 4096+20.0/$dt];
	timeSeries Path 110 -dt $dt -filePath ./GroundMotion/RSN1120_KOBE_TAK000.txt -factor [expr $g*1.2]
	set eq_load_pattern 110
	pattern UniformExcitation $eq_load_pattern 1 -accel 110
	source ./SolverNewmark.tcl
}