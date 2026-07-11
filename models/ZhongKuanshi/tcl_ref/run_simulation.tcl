wipe
model BasicBuilder -ndm 2 -ndf 3
# load
source ./model_id.tcl
source ./ModelingParameters/$model_id.tcl
source load_algorithm.tcl
# nodes
node 1 [expr 0.0*$L]  0.0
node 2 [expr 0.5*$L]  0.0
node 3 [expr 0.5*$L]  0.0
node 4 [expr 1.0*$L]  0.0
# boundary conditions
fix 1 1 1 1
fix 4 1 0 1
equalDOF 2 3 1 3
# material properties
set Ec [expr (57000.0*sqrt($fc*1000.0))/1000.0]
puts "Ec = $Ec (ksi)"
uniaxialMaterial Elastic 1 $Ec
set G [expr $Ec/(2.0*(1.0+0.2))]
set Ag [expr $b*$h]
set Ig [expr $b*$h*$h*$h/12.0]
# set hinge parameters
set y1 [expr $V1*$rpp]
set x1 [expr $theta1*$L]
set y2 [expr $V2*$rpp]
set x2 [expr $theta2*$L]
set y3 [expr $V3*$rpp]
set x3 [expr $theta3*$L]
set y4 [expr $V4*$rpp]
set x4 [expr $theta4*$L]
set y5 [expr $V5*$rpp]
set x5 [expr $theta5*$L]
set y1_n [expr -$y1*$rnp]
set x1_n [expr -$x1]
set y2_n [expr -$y2*$rnp]
set x2_n [expr -$x2]
set y3_n [expr -$y3*$rnp]
set x3_n [expr -$x3]
set y4_n [expr -$y4*$rnp]
set x4_n [expr -$x4]
set y5_n [expr -$y5*$rnp]
set x5_n [expr -$x5]
set pinch_x [expr $px]
set pinch_y [expr $py]
set damage1 0.00
set damage2 0.00
set betaunloading [expr $beta]
puts "Backbone: ($x1, $y1), ($x2, $y2), ($x3, $y3), ($x4, $y4), ($x5, $y5)"
# create material
uniaxialMaterial HystereticSM 2 -posEnv $y1 $x1 $y2 $x2 $y3 $x3 $y4 $x4 $y5 $x5 -negEnv $y1_n $x1_n $y2_n $x2_n $y3_n $x3_n $y4_n $x4_n $y5_n $x5_n -pinch $pinch_x $pinch_y -damage $damage1 $damage2 -beta $betaunloading
# create element
geomTransf PDelta 1 
element elasticBeamColumn 1 1 2 $Ag $Ec $Ig 1
element elasticBeamColumn 2 3 4 $Ag $Ec $Ig 1
element zeroLength 3 2 3 -mat 2  -dir 2 -orient 1 0 0 0 1 0
# define load and analysis
timeSeries Linear 1
system BandSPD
numberer RCM
constraints Plain
integrator LoadControl 1.0
algorithm Newton
analysis Static
# recorder
set dir_out ./SimuOutput
file mkdir $dir_out/$model_id
recorder Node -file $dir_out/$model_id/disp.out -time -node 4 -dof 2 disp
recorder Node -file $dir_out/$model_id/shear.out -time -node 1 -dof 2 reaction
recorder Element -file $dir_out/$model_id/eleGlobal.out -time -ele 3 forces
recorder Element -file $dir_out/$model_id/eleLocal.out  -time -ele 3 basicForces
# define loding history
set LoadType "CyclicStep"
set numIncr 800
set Dincr 0.0001
set Tol 1e-4
set numIter 800
# analyze
set F_ref 1.0;
pattern Plain 1 Linear {
	load 4 0.0 $F_ref  0.0;
}
set dir_loading ./LoadingHistory
source $dir_loading/$model_id.tcl