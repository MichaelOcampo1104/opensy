wipe
puts "System"
model basic -ndm 3 -ndf 6
puts "restraint"
node 1 0.000E+000 1.200E+004 3.000E+003
node 2 0.000E+000 0.000E+000 3.000E+003
node 3 0.000E+000 1.100E+004 3.000E+003
node 4 0.000E+000 1.000E+004 3.000E+003
node 5 0.000E+000 9.000E+003 3.000E+003
node 6 0.000E+000 8.000E+003 3.000E+003
node 7 0.000E+000 7.000E+003 3.000E+003
node 8 0.000E+000 6.000E+003 3.000E+003
node 9 0.000E+000 5.000E+003 3.000E+003
node 10 0.000E+000 4.000E+003 3.000E+003
node 11 0.000E+000 3.000E+003 3.000E+003
node 12 0.000E+000 2.000E+003 3.000E+003
node 13 0.000E+000 1.000E+003 3.000E+003
node 14 0.000E+000 1.100E+004 3.400E+003
node 15 0.000E+000 1.000E+004 3.400E+003
node 16 0.000E+000 9.000E+003 3.400E+003
node 17 0.000E+000 8.000E+003 3.400E+003
node 18 0.000E+000 7.000E+003 3.400E+003
node 19 0.000E+000 6.000E+003 3.400E+003
node 20 0.000E+000 5.000E+003 3.400E+003
node 21 0.000E+000 4.000E+003 3.400E+003
node 22 0.000E+000 3.000E+003 3.400E+003
node 23 0.000E+000 2.000E+003 3.400E+003
node 24 0.000E+000 1.000E+003 3.400E+003
node 25 0.000E+000 1.150E+004 3.400E+003
node 26 0.000E+000 5.000E+002 3.400E+003
node 27 0.000E+000 1.150E+004 3.000E+003
node 28 0.000E+000 5.000E+002 3.000E+003
puts "rigidDiaphragm"
puts "mass"
mass 1 7.866E-002 7.866E-002 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 2 7.866E-002 7.866E-002 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 3 2.360E-001 2.360E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 4 3.146E-001 3.146E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 5 3.146E-001 3.146E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 6 3.146E-001 3.146E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 7 3.146E-001 3.146E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 8 3.146E-001 3.146E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 9 3.146E-001 3.146E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 10 3.146E-001 3.146E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 11 3.146E-001 3.146E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 12 3.146E-001 3.146E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 13 2.360E-001 2.360E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 14 7.202E-001 7.202E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 15 9.603E-001 9.603E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 16 9.603E-001 9.603E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 17 9.603E-001 9.603E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 18 9.603E-001 9.603E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 19 9.603E-001 9.603E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 20 9.603E-001 9.603E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 21 9.603E-001 9.603E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 22 9.603E-001 9.603E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 23 9.603E-001 9.603E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 24 7.202E-001 7.202E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 25 2.401E-001 2.401E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 26 2.401E-001 2.401E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 27 1.573E-001 1.573E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 28 1.573E-001 1.573E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
puts "node"
fix 1 0 0 1 0 0 0;
fix 2 1 1 1 0 0 0;
puts "Equal DOF"
puts "material"

uniaxialMaterial Elastic 1 2.05E+005
##uniaxialMaterial Steel01 1 450 2.05e5 0.0001 
uniaxialMaterial Elastic 2 2.482E+004
uniaxialMaterial Elastic 3 1.999E+005
##uniaxialMaterial Elastic 4 2.050E+006
uniaxialMaterial Elastic 4 2.050E+006
##uniaxialMaterial Steel01 4 1000 2.05e6 0.00001 
##uniaxialMaterial Steel01 4 500 2.05e6 0.00001 

uniaxialMaterial Elastic 201 1.154E+009
uniaxialMaterial Elastic 301 1.538E+009
uniaxialMaterial Elastic 401 9.690E+011
uniaxialMaterial Elastic 202 3.447E+009
uniaxialMaterial Elastic 302 3.447E+009
uniaxialMaterial Elastic 402 5.168E+013

uniaxialMaterial Elastic 203 2.725E+010
uniaxialMaterial Elastic 303 2.725E+010

uniaxialMaterial Elastic 403 8.310E+013
##DB400X600X30 
section Fiber 1 {
fiber -1.600E+002 -2.850E+002 2.400E+003 1
fiber -8.000E+001 -2.850E+002 2.400E+003 1
fiber 0.000E+000 -2.850E+002 2.400E+003 1
fiber 8.000E+001 -2.850E+002 2.400E+003 1
fiber 1.600E+002 -2.850E+002 2.400E+003 1
fiber -1.600E+002 2.850E+002 2.400E+003 1
fiber -8.000E+001 2.850E+002 2.400E+003 1
fiber 0.000E+000 2.850E+002 2.400E+003 1
fiber 8.000E+001 2.850E+002 2.400E+003 1
fiber 1.600E+002 2.850E+002 2.400E+003 1
fiber 0.000E+000 -2.160E+002 3.240E+003 1
fiber 0.000E+000 -1.080E+002 3.240E+003 1
fiber 0.000E+000 0.000E+000 3.240E+003 1
fiber 0.000E+000 1.080E+002 3.240E+003 1
fiber 0.000E+000 2.160E+002 3.240E+003 1
}
##DB2000X200 
section Fiber 2 {
fiber -8.000E+002 -8.000E+001 1.600E+004 2
fiber -4.000E+002 -8.000E+001 1.600E+004 2
fiber 0.000E+000 -8.000E+001 1.600E+004 2
fiber 4.000E+002 -8.000E+001 1.600E+004 2
fiber 8.000E+002 -8.000E+001 1.600E+004 2
fiber -8.000E+002 -4.000E+001 1.600E+004 2
fiber -4.000E+002 -4.000E+001 1.600E+004 2
fiber 0.000E+000 -4.000E+001 1.600E+004 2
fiber 4.000E+002 -4.000E+001 1.600E+004 2
fiber 8.000E+002 -4.000E+001 1.600E+004 2
fiber -8.000E+002 0.000E+000 1.600E+004 2
fiber -4.000E+002 0.000E+000 1.600E+004 2
fiber 0.000E+000 0.000E+000 1.600E+004 2
fiber 4.000E+002 0.000E+000 1.600E+004 2
fiber 8.000E+002 0.000E+000 1.600E+004 2
fiber -8.000E+002 4.000E+001 1.600E+004 2
fiber -4.000E+002 4.000E+001 1.600E+004 2
fiber 0.000E+000 4.000E+001 1.600E+004 2
fiber 4.000E+002 4.000E+001 1.600E+004 2
fiber 8.000E+002 4.000E+001 1.600E+004 2
fiber -8.000E+002 8.000E+001 1.600E+004 2
fiber -4.000E+002 8.000E+001 1.600E+004 2
fiber 0.000E+000 8.000E+001 1.600E+004 2
fiber 4.000E+002 8.000E+001 1.600E+004 2
fiber 8.000E+002 8.000E+001 1.600E+004 2
fiber -9.650E+002 -6.500E+001 2.000E+002 1
fiber -4.825E+002 -6.500E+001 2.000E+002 1
fiber 0.000E+000 -6.500E+001 2.000E+002 1
fiber 4.825E+002 -6.500E+001 2.000E+002 1
fiber 9.650E+002 -6.500E+001 2.000E+002 1
fiber -9.650E+002 6.500E+001 2.000E+002 1
fiber -4.825E+002 6.500E+001 2.000E+002 1
fiber 0.000E+000 6.500E+001 2.000E+002 1
fiber 4.825E+002 6.500E+001 2.000E+002 1
fiber 9.650E+002 6.500E+001 2.000E+002 1
fiber -9.650E+002 -4.333E+001 0.000E+000 1
fiber -9.650E+002 -2.167E+001 0.000E+000 1
fiber -9.650E+002 0.000E+000 0.000E+000 1
fiber -9.650E+002 2.167E+001 0.000E+000 1
fiber -9.650E+002 4.333E+001 0.000E+000 1
fiber 9.650E+002 -4.333E+001 0.000E+000 1
fiber 9.650E+002 -2.167E+001 0.000E+000 1
fiber 9.650E+002 0.000E+000 0.000E+000 1
fiber 9.650E+002 2.167E+001 0.000E+000 1
fiber 9.650E+002 4.333E+001 0.000E+000 1
}
##DB120X10 
section Fiber 3 {
fiber 5.500E+001 0.000E+000 1.728E+002 4
fiber 5.231E+001 1.700E+001 1.728E+002 4
fiber 4.450E+001 3.233E+001 1.728E+002 4
fiber 3.233E+001 4.450E+001 1.728E+002 4
fiber 1.700E+001 5.231E+001 1.728E+002 4
fiber -1.491E-018 5.500E+001 1.728E+002 4
fiber -1.700E+001 5.231E+001 1.728E+002 4
fiber -3.233E+001 4.450E+001 1.728E+002 4
fiber -4.450E+001 3.233E+001 1.728E+002 4
fiber -5.231E+001 1.700E+001 1.728E+002 4
fiber -5.500E+001 -2.982E-018 1.728E+002 4
fiber -5.231E+001 -1.700E+001 1.728E+002 4
fiber -4.450E+001 -3.233E+001 1.728E+002 4
fiber -3.233E+001 -4.450E+001 1.728E+002 4
fiber -1.700E+001 -5.231E+001 1.728E+002 4
fiber 1.044E-017 -5.500E+001 1.728E+002 4
fiber 1.700E+001 -5.231E+001 1.728E+002 4
fiber 3.233E+001 -4.450E+001 1.728E+002 4
fiber 4.450E+001 -3.233E+001 1.728E+002 4
fiber 5.231E+001 -1.700E+001 1.728E+002 4
}
section Aggregator 1001 201 Vy 301 Vz 401 T -section 1
section Aggregator 1002 202 Vy 302 Vz 402 T -section 2
section Aggregator 1003 203 Vy 303 Vz 403 T -section 3


puts "transformation"
geomTransf Linear 1 0.000 0.000 1.000 
geomTransf Linear 2 0.000 0.000 1.000 
geomTransf Linear 3 0.000 0.000 1.000 
geomTransf Linear 4 0.000 0.000 1.000 
geomTransf Linear 5 0.000 0.000 1.000 
geomTransf Linear 6 0.000 0.000 1.000 
geomTransf Linear 7 0.000 0.000 1.000 
geomTransf Linear 8 0.000 0.000 1.000 
geomTransf Linear 9 0.000 0.000 1.000 
geomTransf Linear 10 0.000 0.000 1.000 
geomTransf Linear 11 1.000 0.000 0.000 
geomTransf Linear 12 1.000 0.000 0.000 
geomTransf Linear 13 1.000 0.000 0.000 
geomTransf Linear 14 1.000 0.000 0.000 
geomTransf Linear 15 1.000 0.000 0.000 
geomTransf Linear 16 1.000 0.000 0.000 
geomTransf Linear 17 1.000 0.000 0.000 
geomTransf Linear 18 1.000 0.000 0.000 
geomTransf Linear 19 1.000 0.000 0.000 
geomTransf Linear 20 1.000 0.000 0.000 
geomTransf Linear 21 1.000 0.000 0.000 
geomTransf Linear 22 0.000 0.000 1.000 
geomTransf Linear 23 0.000 0.000 1.000 
geomTransf Linear 24 1.000 0.000 0.000 
geomTransf Linear 25 1.000 0.000 0.000 
geomTransf Linear 26 0.000 0.000 1.000 
geomTransf Linear 27 0.000 0.000 1.000 
geomTransf Linear 28 0.000 0.000 1.000 
geomTransf Linear 29 0.000 0.000 1.000 
geomTransf Linear 30 0.000 0.000 1.000 
geomTransf Linear 31 0.000 0.000 1.000 
geomTransf Linear 32 0.000 0.000 1.000 
geomTransf Linear 33 0.000 0.000 1.000 
geomTransf Linear 34 0.000 0.000 1.000 
geomTransf Linear 35 0.000 0.000 1.000 
geomTransf Linear 36 0.000 0.000 1.000 
geomTransf Linear 37 0.000 0.000 1.000 
geomTransf Linear 38 0.000 0.000 1.000 
geomTransf Linear 39 0.000 0.000 1.000 
puts "element"
element dispBeamColumn 1 14 15 3 1002 1
element dispBeamColumn 2 15 16 3 1002 2
element dispBeamColumn 3 16 17 3 1002 3
element dispBeamColumn 4 17 18 3 1002 4
element dispBeamColumn 5 18 19 3 1002 5
element dispBeamColumn 6 19 20 3 1002 6
element dispBeamColumn 7 20 21 3 1002 7
element dispBeamColumn 8 21 22 3 1002 8
element dispBeamColumn 9 22 23 3 1002 9
element dispBeamColumn 10 23 24 3 1002 10
element dispBeamColumn 11 13 24 3 1003 11
element dispBeamColumn 12 12 23 3 1003 12
element dispBeamColumn 13 11 22 3 1003 13
element dispBeamColumn 14 10 21 3 1003 14
element dispBeamColumn 15 9 20 3 1003 15
element dispBeamColumn 16 8 19 3 1003 16
element dispBeamColumn 17 7 18 3 1003 17
element dispBeamColumn 18 6 17 3 1003 18
element dispBeamColumn 19 5 16 3 1003 19
element dispBeamColumn 20 4 15 3 1003 20
element dispBeamColumn 21 3 14 3 1003 21
element dispBeamColumn 22 25 14 3 1002 22
element dispBeamColumn 23 24 26 3 1002 23
element dispBeamColumn 24 28 26 3 1003 24
element dispBeamColumn 25 27 25 3 1003 25
element dispBeamColumn 26 3 4 3 1001 26
element dispBeamColumn 27 4 5 3 1001 27
element dispBeamColumn 28 5 6 3 1001 28
element dispBeamColumn 29 6 7 3 1001 29
element dispBeamColumn 30 7 8 3 1001 30
element dispBeamColumn 31 8 9 3 1001 31
element dispBeamColumn 32 9 10 3 1001 32
element dispBeamColumn 33 10 11 3 1001 33
element dispBeamColumn 34 11 12 3 1001 34
element dispBeamColumn 35 12 13 3 1001 35
element dispBeamColumn 36 1 27 3 1001 36
element dispBeamColumn 37 27 3 3 1001 37
element dispBeamColumn 38 13 28 3 1001 38
element dispBeamColumn 39 28 2 3 1001 39
puts "shell element"
puts "SOLID element"
puts "recorder"
recorder Node -file node8.out -time -node 8 -dof 1 2 3 disp
puts "loading"
## Load Case = DEAD
pattern Plain 1 Linear {
load 8 0.000E+000 0.000E+000 -1.000E+005 0.000E+000 0.000E+000 0.000E+000
}
puts "analysis"
constraints Plain
numberer Plain
system BandGeneral
test EnergyIncr 1.0e-6 200
algorithm Newton

integrator DisplacementControl 8 3 -15.000E-001
analysis Static
analyze 100




