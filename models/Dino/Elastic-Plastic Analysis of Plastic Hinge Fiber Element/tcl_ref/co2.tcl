wipe
puts "System"
model basic -ndm 3 -ndf 6
puts "restraint"
node 1 0.000E+000 0.000E+000 9.000E+003
node 2 0.000E+000 0.000E+000 1.200E+004
node 3 0.000E+000 6.000E+003 9.000E+003
node 4 0.000E+000 6.000E+003 1.200E+004
node 5 6.000E+003 0.000E+000 9.000E+003
node 6 6.000E+003 0.000E+000 1.200E+004
node 7 6.000E+003 6.000E+003 9.000E+003
node 8 6.000E+003 6.000E+003 1.200E+004
node 9 1.200E+004 0.000E+000 9.000E+003
node 10 1.200E+004 0.000E+000 1.200E+004
node 11 1.200E+004 6.000E+003 9.000E+003
node 12 1.200E+004 6.000E+003 1.200E+004
node 13 0.000E+000 0.000E+000 6.000E+003
node 14 0.000E+000 6.000E+003 6.000E+003
node 15 6.000E+003 0.000E+000 6.000E+003
node 16 6.000E+003 6.000E+003 6.000E+003
node 17 1.200E+004 0.000E+000 6.000E+003
node 18 1.200E+004 6.000E+003 6.000E+003
node 19 0.000E+000 0.000E+000 3.000E+003
node 20 0.000E+000 6.000E+003 3.000E+003
node 21 6.000E+003 0.000E+000 3.000E+003
node 22 6.000E+003 6.000E+003 3.000E+003
node 23 1.200E+004 0.000E+000 3.000E+003
node 24 1.200E+004 6.000E+003 3.000E+003
node 25 0.000E+000 0.000E+000 0.000E+000
node 26 0.000E+000 6.000E+003 0.000E+000
node 27 6.000E+003 0.000E+000 0.000E+000
node 28 6.000E+003 6.000E+003 0.000E+000
node 29 1.200E+004 0.000E+000 0.000E+000
node 30 1.200E+004 6.000E+003 0.000E+000
puts "rigidDiaphragm"
puts "mass"
mass 1 4.178E+000 4.178E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 2 3.277E+000 3.277E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 3 4.178E+000 4.178E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 4 3.277E+000 3.277E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 5 5.366E+000 5.366E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 6 4.466E+000 4.466E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 7 5.366E+000 5.366E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 8 4.466E+000 4.466E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 9 4.178E+000 4.178E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 10 3.277E+000 3.277E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 11 4.178E+000 4.178E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 12 3.277E+000 3.277E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 13 4.178E+000 4.178E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 14 4.178E+000 4.178E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 15 5.366E+000 5.366E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 16 5.366E+000 5.366E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 17 4.178E+000 4.178E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 18 4.178E+000 4.178E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 19 4.178E+000 4.178E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 20 4.178E+000 4.178E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 21 5.366E+000 5.366E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 22 5.366E+000 5.366E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 23 4.178E+000 4.178E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 24 4.178E+000 4.178E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 25 9.004E-001 9.004E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 26 9.004E-001 9.004E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 27 9.004E-001 9.004E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 28 9.004E-001 9.004E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 29 9.004E-001 9.004E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 30 9.004E-001 9.004E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
puts "node"
fix 25 1 1 1 1 1 1;
fix 26 1 1 1 1 1 1;
fix 27 1 1 1 1 1 1;
fix 28 1 1 1 1 1 1;
fix 29 1 1 1 1 1 1;
fix 30 1 1 1 1 1 1;
puts "Equal DOF"
puts "material"
uniaxialMaterial Steel01 1 300 206000 0.01 
uniaxialMaterial Concrete02 2 -20.0 -0.002 -5 -0.0033 0.1 2.2 1100
uniaxialMaterial Elastic 3 1.999E+005
##HC500X500 
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
##HB300X600 
section Fiber 2 {
fiber -1.200E+002 -2.400E+002 7.200E+003 2
fiber -6.000E+001 -2.400E+002 7.200E+003 2
fiber 0.000E+000 -2.400E+002 7.200E+003 2
fiber 6.000E+001 -2.400E+002 7.200E+003 2
fiber 1.200E+002 -2.400E+002 7.200E+003 2
fiber -1.200E+002 -1.200E+002 7.200E+003 2
fiber -6.000E+001 -1.200E+002 7.200E+003 2
fiber 0.000E+000 -1.200E+002 7.200E+003 2
fiber 6.000E+001 -1.200E+002 7.200E+003 2
fiber 1.200E+002 -1.200E+002 7.200E+003 2
fiber -1.200E+002 0.000E+000 7.200E+003 2
fiber -6.000E+001 0.000E+000 7.200E+003 2
fiber 0.000E+000 0.000E+000 7.200E+003 2
fiber 6.000E+001 0.000E+000 7.200E+003 2
fiber 1.200E+002 0.000E+000 7.200E+003 2
fiber -1.200E+002 1.200E+002 7.200E+003 2
fiber -6.000E+001 1.200E+002 7.200E+003 2
fiber 0.000E+000 1.200E+002 7.200E+003 2
fiber 6.000E+001 1.200E+002 7.200E+003 2
fiber 1.200E+002 1.200E+002 7.200E+003 2
fiber -1.200E+002 2.400E+002 7.200E+003 2
fiber -6.000E+001 2.400E+002 7.200E+003 2
fiber 0.000E+000 2.400E+002 7.200E+003 2
fiber 6.000E+001 2.400E+002 7.200E+003 2
fiber 1.200E+002 2.400E+002 7.200E+003 2
fiber -1.150E+002 -2.650E+002 2.000E+002 1
fiber -5.750E+001 -2.650E+002 2.000E+002 1
fiber 0.000E+000 -2.650E+002 2.000E+002 1
fiber 5.750E+001 -2.650E+002 2.000E+002 1
fiber 1.150E+002 -2.650E+002 2.000E+002 1
fiber -1.150E+002 2.650E+002 2.000E+002 1
fiber -5.750E+001 2.650E+002 2.000E+002 1
fiber 0.000E+000 2.650E+002 2.000E+002 1
fiber 5.750E+001 2.650E+002 2.000E+002 1
fiber 1.150E+002 2.650E+002 2.000E+002 1
fiber -1.150E+002 -1.767E+002 2.000E+002 1
fiber -1.150E+002 -8.833E+001 2.000E+002 1
fiber -1.150E+002 0.000E+000 2.000E+002 1
fiber -1.150E+002 8.833E+001 2.000E+002 1
fiber -1.150E+002 1.767E+002 2.000E+002 1
fiber 1.150E+002 -1.767E+002 2.000E+002 1
fiber 1.150E+002 -8.833E+001 2.000E+002 1
fiber 1.150E+002 0.000E+000 2.000E+002 1
fiber 1.150E+002 8.833E+001 2.000E+002 1
fiber 1.150E+002 1.767E+002 2.000E+002 1
}

puts "transformation"
geomTransf Linear 1 1.000 0.000 0.000 
geomTransf Linear 2 1.000 0.000 0.000 
geomTransf Linear 3 1.000 0.000 0.000 
geomTransf Linear 4 1.000 0.000 0.000 
geomTransf Linear 5 1.000 0.000 0.000 
geomTransf Linear 6 1.000 0.000 0.000 
geomTransf Linear 7 0.000 0.000 1.000 
geomTransf Linear 8 0.000 0.000 1.000 
geomTransf Linear 9 0.000 0.000 1.000 
geomTransf Linear 10 0.000 0.000 1.000 
geomTransf Linear 11 0.000 0.000 1.000 
geomTransf Linear 12 0.000 0.000 1.000 
geomTransf Linear 13 0.000 0.000 1.000 
geomTransf Linear 14 1.000 0.000 0.000 
geomTransf Linear 15 1.000 0.000 0.000 
geomTransf Linear 16 1.000 0.000 0.000 
geomTransf Linear 17 1.000 0.000 0.000 
geomTransf Linear 18 1.000 0.000 0.000 
geomTransf Linear 19 1.000 0.000 0.000 
geomTransf Linear 20 0.000 0.000 1.000 
geomTransf Linear 21 0.000 0.000 1.000 
geomTransf Linear 22 0.000 0.000 1.000 
geomTransf Linear 23 0.000 0.000 1.000 
geomTransf Linear 24 0.000 0.000 1.000 
geomTransf Linear 25 0.000 0.000 1.000 
geomTransf Linear 26 0.000 0.000 1.000 
geomTransf Linear 27 1.000 0.000 0.000 
geomTransf Linear 28 1.000 0.000 0.000 
geomTransf Linear 29 1.000 0.000 0.000 
geomTransf Linear 30 1.000 0.000 0.000 
geomTransf Linear 31 1.000 0.000 0.000 
geomTransf Linear 32 1.000 0.000 0.000 
geomTransf Linear 33 0.000 0.000 1.000 
geomTransf Linear 34 0.000 0.000 1.000 
geomTransf Linear 35 0.000 0.000 1.000 
geomTransf Linear 36 0.000 0.000 1.000 
geomTransf Linear 37 0.000 0.000 1.000 
geomTransf Linear 38 0.000 0.000 1.000 
geomTransf Linear 39 0.000 0.000 1.000 
geomTransf Linear 40 1.000 0.000 0.000 
geomTransf Linear 41 1.000 0.000 0.000 
geomTransf Linear 42 1.000 0.000 0.000 
geomTransf Linear 43 1.000 0.000 0.000 
geomTransf Linear 44 1.000 0.000 0.000 
geomTransf Linear 45 1.000 0.000 0.000 
geomTransf Linear 46 0.000 0.000 1.000 
geomTransf Linear 47 0.000 0.000 1.000 
geomTransf Linear 48 0.000 0.000 1.000 
geomTransf Linear 49 0.000 0.000 1.000 
geomTransf Linear 50 0.000 0.000 1.000 
geomTransf Linear 51 0.000 0.000 1.000 
geomTransf Linear 52 0.000 0.000 1.000 
puts "element"
element nonlinearBeamColumn 1 1 2 3 1 1
element nonlinearBeamColumn 2 3 4 3 1 2
element nonlinearBeamColumn 3 5 6 3 1 3
element nonlinearBeamColumn 4 7 8 3 1 4
element nonlinearBeamColumn 5 9 10 3 1 5
element nonlinearBeamColumn 6 11 12 3 1 6
element nonlinearBeamColumn 7 2 4 3 2 7
element nonlinearBeamColumn 8 6 8 3 2 8
element nonlinearBeamColumn 9 10 12 3 2 9
element nonlinearBeamColumn 10 2 6 3 2 10
element nonlinearBeamColumn 11 6 10 3 2 11
element nonlinearBeamColumn 12 4 8 3 2 12
element nonlinearBeamColumn 13 8 12 3 2 13
element nonlinearBeamColumn 14 13 1 3 1 14
element nonlinearBeamColumn 15 14 3 3 1 15
element nonlinearBeamColumn 16 15 5 3 1 16
element nonlinearBeamColumn 17 16 7 3 1 17
element nonlinearBeamColumn 18 17 9 3 1 18
element nonlinearBeamColumn 19 18 11 3 1 19
element nonlinearBeamColumn 20 1 3 3 2 20
element nonlinearBeamColumn 21 5 7 3 2 21
element nonlinearBeamColumn 22 9 11 3 2 22
element nonlinearBeamColumn 23 1 5 3 2 23
element nonlinearBeamColumn 24 5 9 3 2 24
element nonlinearBeamColumn 25 3 7 3 2 25
element nonlinearBeamColumn 26 7 11 3 2 26
element nonlinearBeamColumn 27 19 13 3 1 27
element nonlinearBeamColumn 28 20 14 3 1 28
element nonlinearBeamColumn 29 21 15 3 1 29
element nonlinearBeamColumn 30 22 16 3 1 30
element nonlinearBeamColumn 31 23 17 3 1 31
element nonlinearBeamColumn 32 24 18 3 1 32
element nonlinearBeamColumn 33 13 14 3 2 33
element nonlinearBeamColumn 34 15 16 3 2 34
element nonlinearBeamColumn 35 17 18 3 2 35
element nonlinearBeamColumn 36 13 15 3 2 36
element nonlinearBeamColumn 37 15 17 3 2 37
element nonlinearBeamColumn 38 14 16 3 2 38
element nonlinearBeamColumn 39 16 18 3 2 39
element nonlinearBeamColumn 40 25 19 3 1 40
element nonlinearBeamColumn 41 26 20 3 1 41
element nonlinearBeamColumn 42 27 21 3 1 42
element nonlinearBeamColumn 43 28 22 3 1 43
element nonlinearBeamColumn 44 29 23 3 1 44
element nonlinearBeamColumn 45 30 24 3 1 45
element nonlinearBeamColumn 46 19 20 3 2 46
element nonlinearBeamColumn 47 21 22 3 2 47
element nonlinearBeamColumn 48 23 24 3 2 48
element nonlinearBeamColumn 49 19 21 3 2 49
element nonlinearBeamColumn 50 21 23 3 2 50
element nonlinearBeamColumn 51 20 22 3 2 51
element nonlinearBeamColumn 52 22 24 3 2 52
puts "shell element"
puts "SOLID element"
puts "recorder"
recorder Node -file node0.out -time -nodeRange 1 30 -dof 1 2 3 disp
recorder Node -file node2.out -time -node 2 -dof 1 2 3 disp
puts "loading"
## Load Case = PUSH
pattern Plain 1 Linear {
load 2 4.000E+005 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
load 4 4.000E+005 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
load 1 3.000E+005 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
load 3 3.000E+005 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
load 13 2.000E+005 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
load 14 2.000E+005 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
load 19 1.000E+005 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
load 20 1.000E+005 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
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
