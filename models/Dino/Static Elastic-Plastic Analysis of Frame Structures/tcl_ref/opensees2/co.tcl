wipe
puts "System"
model basic -ndm 3 -ndf 6
puts "restraint"
node 1 6.000E+003 0.000E+000 3.000E+003
node 2 6.000E+003 0.000E+000 0.000E+000
node 3 6.000E+003 0.000E+000 7.500E+002
node 4 6.000E+003 0.000E+000 1.500E+003
node 5 6.000E+003 0.000E+000 2.250E+003
puts "rigidDiaphragm"

puts "node"
fix 1 0 1 0 1 0 1;
fix 2 1 1 1 1 1 1;
fix 3 0 1 0 1 0 1;
fix 4 0 1 0 1 0 1;
fix 5 0 1 0 1 0 1;
puts "Equal DOF"
puts "material"
uniaxialMaterial Steel01 1 335 200000 0.00001 
uniaxialMaterial Concrete01 2 -26.8 -0.002 -15 -0.006
uniaxialMaterial Elastic 3 1.999E+005
##NC500X500 
section Fiber 1 {
fiber -2.000E+002 -2.000E+002 1.000E+004 2
fiber -1.000E+002 -2.000E+002 1.000E+004 2
fiber 0.000E+000 -2.000E+002 1.000E+004 2
fiber 1.000E+002 -2.000E+002 1.000E+004 2
fiber 2.000E+002 -2.000E+002 1.000E+004 2
fiber -2.000E+002 -1.000E+002 1.000E+004 2
fiber -1.000E+002 -1.000E+002 1.000E+004 2
fiber 0.000E+000 -1.000E+002 1.000E+004 2
fiber 1.000E+002 -1.000E+002 1.000E+004 2
fiber 2.000E+002 -1.000E+002 1.000E+004 2
fiber -2.000E+002 0.000E+000 1.000E+004 2
fiber -1.000E+002 0.000E+000 1.000E+004 2
fiber 0.000E+000 0.000E+000 1.000E+004 2
fiber 1.000E+002 0.000E+000 1.000E+004 2
fiber 2.000E+002 0.000E+000 1.000E+004 2
fiber -2.000E+002 1.000E+002 1.000E+004 2
fiber -1.000E+002 1.000E+002 1.000E+004 2
fiber 0.000E+000 1.000E+002 1.000E+004 2
fiber 1.000E+002 1.000E+002 1.000E+004 2
fiber 2.000E+002 1.000E+002 1.000E+004 2
fiber -2.000E+002 2.000E+002 1.000E+004 2
fiber -1.000E+002 2.000E+002 1.000E+004 2
fiber 0.000E+000 2.000E+002 1.000E+004 2
fiber 1.000E+002 2.000E+002 1.000E+004 2
fiber 2.000E+002 2.000E+002 1.000E+004 2
fiber -2.150E+002 -2.150E+002 2.000E+002 1
fiber -1.075E+002 -2.150E+002 2.000E+002 1
fiber 0.000E+000 -2.150E+002 2.000E+002 1
fiber 1.075E+002 -2.150E+002 2.000E+002 1
fiber 2.150E+002 -2.150E+002 2.000E+002 1
fiber -2.150E+002 2.150E+002 2.000E+002 1
fiber -1.075E+002 2.150E+002 2.000E+002 1
fiber 0.000E+000 2.150E+002 2.000E+002 1
fiber 1.075E+002 2.150E+002 2.000E+002 1
fiber 2.150E+002 2.150E+002 2.000E+002 1
fiber -2.150E+002 -1.433E+002 2.000E+002 1
fiber -2.150E+002 -7.167E+001 2.000E+002 1
fiber -2.150E+002 0.000E+000 2.000E+002 1
fiber -2.150E+002 7.167E+001 2.000E+002 1
fiber -2.150E+002 1.433E+002 2.000E+002 1
fiber 2.150E+002 -1.433E+002 2.000E+002 1
fiber 2.150E+002 -7.167E+001 2.000E+002 1
fiber 2.150E+002 0.000E+000 2.000E+002 1
fiber 2.150E+002 7.167E+001 2.000E+002 1
fiber 2.150E+002 1.433E+002 2.000E+002 1
}



geomTransf Linear 1 1.000 0.000 0.000 
geomTransf Linear 2 1.000 0.000 0.000 
geomTransf Linear 3 1.000 0.000 0.000 
geomTransf Linear 4 1.000 0.000 0.000 
puts "element"
element nonlinearBeamColumn 1 2 3 3 1 1
element nonlinearBeamColumn 2 3 4 3 1 2
element nonlinearBeamColumn 3 4 5 3 1 3
element nonlinearBeamColumn 4 5 1 3 1 4
puts "shell element"
puts "SOLID element"
puts "recorder"

puts "gravity"
## Load Case = DEAD
pattern Plain 1 Linear {
load 1 0.000E+000 0.000E+000 -1.500E+006 0.000E+000 0.000E+000 0.000E+000
}
puts "analysis"
constraints Plain
numberer Plain
system BandGeneral
test EnergyIncr 1.0e-6 200
algorithm Newton
integrator LoadControl 1.000E-002
analysis Static
analyze 100

loadConst 0.0
recorder Node -file node0.out -time -nodeRange 1 5 -dof 1 2 3 disp
recorder Node -file node1.out -time -node 1  -dof 1 2 3 disp


puts "pushover"
## Load Case = PUSH
pattern Plain 3 Linear {
load 1 1.000E+003 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
}
puts "analysis"
constraints Plain
numberer Plain
system BandGeneral
test EnergyIncr 1.0e-6 200
algorithm Newton
integrator DisplacementControl 1 1 1
analysis Static
analyze 100
