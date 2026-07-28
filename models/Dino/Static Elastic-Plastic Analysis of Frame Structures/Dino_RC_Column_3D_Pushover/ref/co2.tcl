wipe
puts "System"
model basic -ndm 3 -ndf 6
puts "restraint"
node 1 0.000E+000 0.000E+000 0.000E+000
node 2 0.000E+000 0.000E+000 3.000E+003
node 3 0.000E+000 0.000E+000 3.750E+002
node 4 0.000E+000 0.000E+000 7.500E+002
node 5 0.000E+000 0.000E+000 1.125E+003
node 6 0.000E+000 0.000E+000 1.500E+003
node 7 0.000E+000 0.000E+000 1.875E+003
node 8 0.000E+000 0.000E+000 2.250E+003
node 9 0.000E+000 0.000E+000 2.625E+003
puts "rigidDiaphragm"
puts "mass"

puts "node"
fix 1 1 1 1 1 1 1;
fix 2 0 1 0 1 0 1;
fix 3 0 1 0 1 0 1;
fix 4 0 1 0 1 0 1;
fix 5 0 1 0 1 0 1;
fix 6 0 1 0 1 0 1;
fix 7 0 1 0 1 0 1;
fix 8 0 1 0 1 0 1;
fix 9 0 1 0 1 0 1;
puts "Equal DOF"
puts "material"

uniaxialMaterial Steel01 1 335 200000 0.00001 
uniaxialMaterial Concrete01 2 -26.8 -0.002 -15 -0.006

##NC500X500 
section Fiber 1 {
fiber -2.188E+002 -2.188E+002 3.906E+003 2
fiber -1.563E+002 -2.188E+002 3.906E+003 2
fiber -9.375E+001 -2.188E+002 3.906E+003 2
fiber -3.125E+001 -2.188E+002 3.906E+003 2
fiber 3.125E+001 -2.188E+002 3.906E+003 2
fiber 9.375E+001 -2.188E+002 3.906E+003 2
fiber 1.563E+002 -2.188E+002 3.906E+003 2
fiber 2.188E+002 -2.188E+002 3.906E+003 2
fiber -2.188E+002 -1.563E+002 3.906E+003 2
fiber -1.563E+002 -1.563E+002 3.906E+003 2
fiber -9.375E+001 -1.563E+002 3.906E+003 2
fiber -3.125E+001 -1.563E+002 3.906E+003 2
fiber 3.125E+001 -1.563E+002 3.906E+003 2
fiber 9.375E+001 -1.563E+002 3.906E+003 2
fiber 1.563E+002 -1.563E+002 3.906E+003 2
fiber 2.188E+002 -1.563E+002 3.906E+003 2
fiber -2.188E+002 -9.375E+001 3.906E+003 2
fiber -1.563E+002 -9.375E+001 3.906E+003 2
fiber -9.375E+001 -9.375E+001 3.906E+003 2
fiber -3.125E+001 -9.375E+001 3.906E+003 2
fiber 3.125E+001 -9.375E+001 3.906E+003 2
fiber 9.375E+001 -9.375E+001 3.906E+003 2
fiber 1.563E+002 -9.375E+001 3.906E+003 2
fiber 2.188E+002 -9.375E+001 3.906E+003 2
fiber -2.188E+002 -3.125E+001 3.906E+003 2
fiber -1.563E+002 -3.125E+001 3.906E+003 2
fiber -9.375E+001 -3.125E+001 3.906E+003 2
fiber -3.125E+001 -3.125E+001 3.906E+003 2
fiber 3.125E+001 -3.125E+001 3.906E+003 2
fiber 9.375E+001 -3.125E+001 3.906E+003 2
fiber 1.563E+002 -3.125E+001 3.906E+003 2
fiber 2.188E+002 -3.125E+001 3.906E+003 2
fiber -2.188E+002 3.125E+001 3.906E+003 2
fiber -1.563E+002 3.125E+001 3.906E+003 2
fiber -9.375E+001 3.125E+001 3.906E+003 2
fiber -3.125E+001 3.125E+001 3.906E+003 2
fiber 3.125E+001 3.125E+001 3.906E+003 2
fiber 9.375E+001 3.125E+001 3.906E+003 2
fiber 1.563E+002 3.125E+001 3.906E+003 2
fiber 2.188E+002 3.125E+001 3.906E+003 2
fiber -2.188E+002 9.375E+001 3.906E+003 2
fiber -1.563E+002 9.375E+001 3.906E+003 2
fiber -9.375E+001 9.375E+001 3.906E+003 2
fiber -3.125E+001 9.375E+001 3.906E+003 2
fiber 3.125E+001 9.375E+001 3.906E+003 2
fiber 9.375E+001 9.375E+001 3.906E+003 2
fiber 1.563E+002 9.375E+001 3.906E+003 2
fiber 2.188E+002 9.375E+001 3.906E+003 2
fiber -2.188E+002 1.563E+002 3.906E+003 2
fiber -1.563E+002 1.563E+002 3.906E+003 2
fiber -9.375E+001 1.563E+002 3.906E+003 2
fiber -3.125E+001 1.563E+002 3.906E+003 2
fiber 3.125E+001 1.563E+002 3.906E+003 2
fiber 9.375E+001 1.563E+002 3.906E+003 2
fiber 1.563E+002 1.563E+002 3.906E+003 2
fiber 2.188E+002 1.563E+002 3.906E+003 2
fiber -2.188E+002 2.188E+002 3.906E+003 2
fiber -1.563E+002 2.188E+002 3.906E+003 2
fiber -9.375E+001 2.188E+002 3.906E+003 2
fiber -3.125E+001 2.188E+002 3.906E+003 2
fiber 3.125E+001 2.188E+002 3.906E+003 2
fiber 9.375E+001 2.188E+002 3.906E+003 2
fiber 1.563E+002 2.188E+002 3.906E+003 2
fiber 2.188E+002 2.188E+002 3.906E+003 2
fiber -2.150E+002 -2.150E+002 4.906E+002 1
fiber -1.075E+002 -2.150E+002 4.906E+002 1
fiber 0.000E+000 -2.150E+002 4.906E+002 1
fiber 1.075E+002 -2.150E+002 4.906E+002 1
fiber 2.150E+002 -2.150E+002 4.906E+002 1
fiber -2.150E+002 2.150E+002 4.906E+002 1
fiber -1.075E+002 2.150E+002 4.906E+002 1
fiber 0.000E+000 2.150E+002 4.906E+002 1
fiber 1.075E+002 2.150E+002 4.906E+002 1
fiber 2.150E+002 2.150E+002 4.906E+002 1
fiber -2.150E+002 -1.075E+002 4.906E+002 1
fiber -2.150E+002 0.000E+000 4.906E+002 1
fiber -2.150E+002 1.075E+002 4.906E+002 1
fiber 2.150E+002 -1.075E+002 4.906E+002 1
fiber 2.150E+002 0.000E+000 4.906E+002 1
fiber 2.150E+002 1.075E+002 4.906E+002 1
}

puts "transformation"
geomTransf Linear 1 1.000 0.000 0.000 
geomTransf Linear 2 1.000 0.000 0.000 
geomTransf Linear 3 1.000 0.000 0.000 
geomTransf Linear 4 1.000 0.000 0.000 
geomTransf Linear 5 1.000 0.000 0.000 
geomTransf Linear 6 1.000 0.000 0.000 
geomTransf Linear 7 1.000 0.000 0.000 
geomTransf Linear 8 1.000 0.000 0.000 
puts "element"
element nonlinearBeamColumn 1 1 3 3 1 1
element nonlinearBeamColumn 2 3 4 3 1 2
element nonlinearBeamColumn 3 4 5 3 1 3
element nonlinearBeamColumn 4 5 6 3 1 4
element nonlinearBeamColumn 5 6 7 3 1 5
element nonlinearBeamColumn 6 7 8 3 1 6
element nonlinearBeamColumn 7 8 9 3 1 7
element nonlinearBeamColumn 8 9 2 3 1 8
puts "shell element"
puts "SOLID element"
puts "recorder"

puts "gravity"
## Load Case = DEAD
pattern Plain 1 Linear {
load 2 0.000E+000 0.000E+000 -1.500E+006 0.000E+000 0.000E+000 0.000E+000
}
puts "analysis"
constraints Plain
numberer Plain
system BandGeneral
test EnergyIncr 1.0e-6 200
algorithm Newton
integrator LoadControl 1.000E-002
analysis Static
analyze 10
puts "pushover"

recorder Node -file node0.out -time -nodeRange 1 9 -dof 1 2 3 disp
loadConst 0.0

## Load Case = PUSH
pattern Plain 3 Linear {
load 2 1.000E+003 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
}
puts "analysis"
constraints Plain
numberer Plain
system BandGeneral
test EnergyIncr 1.0e-6 200
algorithm Newton
integrator DisplacementControl 2 1 1.000E+000
analysis Static
analyze 100
