wipe
puts "System"
model basic -ndm 3 -ndf 6
puts "restraint"
node 1 6.000E+003 0.000E+000 3.000E+003
node 2 6.000E+003 0.000E+000 0.000E+000
puts "rigidDiaphragm"
puts "mass"
mass 1 9.375E-001 9.375E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 2 9.375E-001 9.375E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
puts "node"
fix 1 0 1 0 1 0 1;
fix 2 1 1 1 1 1 1;
puts "Equal DOF"
puts "material"
uniaxialMaterial Steel01 1 335 200000 0.00001 
uniaxialMaterial Concrete01 2 -26.8 -0.002 -15 -0.006
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
fiber -2.150E+002 -1.290E+002 4.906E+002 1
fiber -2.150E+002 -4.300E+001 4.906E+002 1
fiber -2.150E+002 4.300E+001 4.906E+002 1
fiber -2.150E+002 1.290E+002 4.906E+002 1
fiber 2.150E+002 -1.290E+002 4.906E+002 1
fiber 2.150E+002 -4.300E+001 4.906E+002 1
fiber 2.150E+002 4.300E+001 4.906E+002 1
fiber 2.150E+002 1.290E+002 4.906E+002 1
}


puts "transformation"
geomTransf Linear 1 1.000 0.000 0.000 
puts "element"
element nonlinearBeamColumn 1 2 1 3 1 1
puts "shell element"
puts "SOLID element"
puts "recorder"

puts "loading"




puts "gravity"
## Load Case = DEAD
pattern Plain 1 Linear {
load 1 0.000E+000 0.000E+000 -4.500E+006 0.000E+000 0.000E+000 0.000E+000
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
puts "pushover"

loadConst 0.0

recorder Node -file node1.out -time -node 1 -dof 1 2 3 disp

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
integrator DisplacementControl 1 1 1.0
analysis Static
analyze 100
