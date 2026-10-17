wipe
puts "System"
model basic -ndm 3 -ndf 6
puts "restraint"
node 1 0.000E+000 0.000E+000 3.000E+003
node 2 0.000E+000 0.000E+000 0.000E+000
node 3 0.000E+000 4.000E+003 3.000E+003
node 4 0.000E+000 8.000E+003 0.000E+000
node 5 0.000E+000 1.200E+004 3.000E+003
node 6 0.000E+000 1.600E+004 0.000E+000
node 7 0.000E+000 4.000E+003 0.000E+000
node 8 0.000E+000 8.000E+003 3.000E+003
node 9 0.000E+000 1.200E+004 0.000E+000
node 10 0.000E+000 1.600E+004 3.000E+003
node 11 0.000E+000 0.000E+000 0.000E+000
node 12 0.000E+000 0.000E+000 3.000E+003
node 13 0.000E+000 4.000E+003 0.000E+000
node 14 0.000E+000 4.000E+003 3.000E+003
node 15 0.000E+000 8.000E+003 0.000E+000
node 16 0.000E+000 8.000E+003 3.000E+003
node 17 0.000E+000 1.200E+004 0.000E+000
node 18 0.000E+000 1.200E+004 3.000E+003
node 19 0.000E+000 1.600E+004 0.000E+000
node 20 0.000E+000 1.600E+004 3.000E+003
node 21 4.000E+003 0.000E+000 3.000E+003
node 22 4.000E+003 0.000E+000 0.000E+000
node 23 4.000E+003 4.000E+003 3.000E+003
node 24 4.000E+003 8.000E+003 0.000E+000
node 25 4.000E+003 1.200E+004 3.000E+003
node 26 4.000E+003 1.600E+004 0.000E+000
node 27 4.000E+003 4.000E+003 0.000E+000
node 28 4.000E+003 8.000E+003 3.000E+003
node 29 4.000E+003 1.200E+004 0.000E+000
node 30 4.000E+003 1.600E+004 3.000E+003
node 31 4.000E+003 0.000E+000 0.000E+000
node 32 4.000E+003 0.000E+000 3.000E+003
node 33 4.000E+003 4.000E+003 0.000E+000
node 34 4.000E+003 4.000E+003 3.000E+003
node 35 4.000E+003 8.000E+003 0.000E+000
node 36 4.000E+003 8.000E+003 3.000E+003
node 37 4.000E+003 1.200E+004 0.000E+000
node 38 4.000E+003 1.200E+004 3.000E+003
node 39 4.000E+003 1.600E+004 0.000E+000
node 40 4.000E+003 1.600E+004 3.000E+003
puts "rigidDiaphragm"
puts "mass"
mass 1 1.020E+000 1.020E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 3 1.020E+000 1.020E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 5 1.020E+000 1.020E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 8 1.020E+000 1.020E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 10 1.020E+000 1.020E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 21 1.020E+000 1.020E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 23 1.020E+000 1.020E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 25 1.020E+000 1.020E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 28 1.020E+000 1.020E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 30 1.020E+000 1.020E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
puts "node"
fix 2 1 1 1 1 1 1;
fix 6 1 1 1 1 1 1;
fix 22 1 1 1 1 1 1;
fix 26 1 1 1 1 1 1;
puts "Equal DOF"
equalDOF 2 11 1 2 3
equalDOF 1 12 1 2 3
equalDOF 7 13 1 2 3
equalDOF 3 14 1 2 3
equalDOF 4 15 1 2 3
equalDOF 8 16 1 2 3
equalDOF 9 17 1 2 3
equalDOF 5 18 1 2 3
equalDOF 6 19 1 2 3
equalDOF 10 20 1 2 3
equalDOF 22 31 1 2 3
equalDOF 21 32 1 2 3
equalDOF 27 33 1 2 3
equalDOF 23 34 1 2 3
equalDOF 24 35 1 2 3
equalDOF 28 36 1 2 3
equalDOF 29 37 1 2 3
equalDOF 25 38 1 2 3
equalDOF 26 39 1 2 3
equalDOF 30 40 1 2 3
puts "material"
####################################################################OTHER 材料设为小值
uniaxialMaterial Elastic 1 1.0
uniaxialMaterial Elastic 2 2.550E+004
uniaxialMaterial Elastic 3 2.060E+005
##DH200X500 
section Fiber 1 {
fiber -8.000E+001 -2.400E+002 8.000E+002 3
fiber -4.000E+001 -2.400E+002 8.000E+002 3
fiber 0.000E+000 -2.400E+002 8.000E+002 3
fiber 4.000E+001 -2.400E+002 8.000E+002 3
fiber 8.000E+001 -2.400E+002 8.000E+002 3
fiber -8.000E+001 2.400E+002 8.000E+002 3
fiber -4.000E+001 2.400E+002 8.000E+002 3
fiber 0.000E+000 2.400E+002 8.000E+002 3
fiber 4.000E+001 2.400E+002 8.000E+002 3
fiber 8.000E+001 2.400E+002 8.000E+002 3
fiber 0.000E+000 -1.840E+002 1.840E+003 3
fiber 0.000E+000 -9.200E+001 1.840E+003 3
fiber 0.000E+000 0.000E+000 1.840E+003 3
fiber 0.000E+000 9.200E+001 1.840E+003 3
fiber 0.000E+000 1.840E+002 1.840E+003 3
}
##DH200X200 
section Fiber 2 {
fiber -8.000E+001 -9.400E+001 4.800E+002 3
fiber -4.000E+001 -9.400E+001 4.800E+002 3
fiber 0.000E+000 -9.400E+001 4.800E+002 3
fiber 4.000E+001 -9.400E+001 4.800E+002 3
fiber 8.000E+001 -9.400E+001 4.800E+002 3
fiber -8.000E+001 9.400E+001 4.800E+002 3
fiber -4.000E+001 9.400E+001 4.800E+002 3
fiber 0.000E+000 9.400E+001 4.800E+002 3
fiber 4.000E+001 9.400E+001 4.800E+002 3
fiber 8.000E+001 9.400E+001 4.800E+002 3
fiber 0.000E+000 -7.040E+001 4.224E+002 3
fiber 0.000E+000 -3.520E+001 4.224E+002 3
fiber 0.000E+000 0.000E+000 4.224E+002 3
fiber 0.000E+000 3.520E+001 4.224E+002 3
fiber 0.000E+000 7.040E+001 4.224E+002 3
}
puts "transformation"
geomTransf Linear 1 0.000 0.000 1.000 
geomTransf Linear 2 0.000 0.000 1.000 
geomTransf Linear 3 0.000 0.000 1.000 
geomTransf Linear 4 0.000 0.000 1.000 
geomTransf Linear 6 1.000 0.000 0.000 
geomTransf Linear 9 1.000 0.000 0.000 
geomTransf Linear 12 1.000 0.000 0.000 
geomTransf Linear 15 1.000 0.000 0.000 
geomTransf Linear 18 1.000 0.000 0.000 
geomTransf Linear 20 0.000 0.000 1.000 
geomTransf Linear 21 0.000 0.000 1.000 
geomTransf Linear 22 0.000 0.000 1.000 
geomTransf Linear 23 0.000 0.000 1.000 
geomTransf Linear 25 1.000 0.000 0.000 
geomTransf Linear 28 1.000 0.000 0.000 
geomTransf Linear 31 1.000 0.000 0.000 
geomTransf Linear 34 1.000 0.000 0.000 
geomTransf Linear 37 1.000 0.000 0.000 
geomTransf Linear 39 0.000 0.000 1.000 
geomTransf Linear 40 0.000 0.000 1.000 
geomTransf Linear 41 0.000 0.000 1.000 
geomTransf Linear 42 0.000 0.000 1.000 
geomTransf Linear 43 0.000 0.000 1.000 
geomTransf Linear 44 0.000 0.000 1.000 
geomTransf Linear 45 0.000 0.000 1.000 
geomTransf Linear 46 0.000 0.000 1.000 
geomTransf Linear 47 0.000 0.000 1.000 
geomTransf Linear 48 0.000 0.000 1.000 
geomTransf Linear 49 0.000 0.000 1.000 
geomTransf Linear 50 0.000 0.000 1.000 
geomTransf Linear 51 0.000 0.000 1.000 
geomTransf Linear 52 0.000 0.000 1.000 
geomTransf Linear 53 0.000 0.000 1.000 
geomTransf Linear 54 0.000 0.000 1.000 
geomTransf Linear 55 0.000 0.000 1.000 
geomTransf Linear 56 0.000 0.000 1.000 
puts "element"
element dispBeamColumn 1 10 5 3 1 1
element dispBeamColumn 2 5 8 3 1 2
element dispBeamColumn 3 8 3 3 1 3
element dispBeamColumn 4 3 1 3 1 4
element zeroLength 5 2 11 -mat 1 1 1 -dir 4 5 6
element dispBeamColumn 6 11 12 3 2 6
element zeroLength 7 12 1 -mat 1 1 1 -dir 4 5 6
element zeroLength 8 7 13 -mat 1 1 1 -dir 4 5 6
element dispBeamColumn 9 13 14 3 2 9
element zeroLength 10 14 3 -mat 1 1 1 -dir 4 5 6
element zeroLength 11 4 15 -mat 1 1 1 -dir 4 5 6
element dispBeamColumn 12 15 16 3 2 12
element zeroLength 13 16 8 -mat 1 1 1 -dir 4 5 6
element zeroLength 14 9 17 -mat 1 1 1 -dir 4 5 6
element dispBeamColumn 15 17 18 3 2 15
element zeroLength 16 18 5 -mat 1 1 1 -dir 4 5 6
element zeroLength 17 6 19 -mat 1 1 1 -dir 4 5 6
element dispBeamColumn 18 19 20 3 2 18
element zeroLength 19 20 10 -mat 1 1 1 -dir 4 5 6
element dispBeamColumn 20 30 25 3 1 20
element dispBeamColumn 21 25 28 3 1 21
element dispBeamColumn 22 28 23 3 1 22
element dispBeamColumn 23 23 21 3 1 23
element zeroLength 24 22 31 -mat 1 1 1 -dir 4 5 6
element dispBeamColumn 25 31 32 3 2 25
element zeroLength 26 32 21 -mat 1 1 1 -dir 4 5 6
element zeroLength 27 27 33 -mat 1 1 1 -dir 4 5 6
element dispBeamColumn 28 33 34 3 2 28
element zeroLength 29 34 23 -mat 1 1 1 -dir 4 5 6
element zeroLength 30 24 35 -mat 1 1 1 -dir 4 5 6
element dispBeamColumn 31 35 36 3 2 31
element zeroLength 32 36 28 -mat 1 1 1 -dir 4 5 6
element zeroLength 33 29 37 -mat 1 1 1 -dir 4 5 6
element dispBeamColumn 34 37 38 3 2 34
element zeroLength 35 38 25 -mat 1 1 1 -dir 4 5 6
element zeroLength 36 26 39 -mat 1 1 1 -dir 4 5 6
element dispBeamColumn 37 39 40 3 2 37
element zeroLength 38 40 30 -mat 1 1 1 -dir 4 5 6
element dispBeamColumn 39 10 30 3 2 39
element dispBeamColumn 40 5 25 3 2 40
element dispBeamColumn 41 8 28 3 2 41
element dispBeamColumn 42 3 23 3 2 42
element dispBeamColumn 43 1 21 3 2 43
element dispBeamColumn 44 6 9 3 1 44
element dispBeamColumn 45 9 4 3 1 45
element dispBeamColumn 46 4 7 3 1 46
element dispBeamColumn 47 7 2 3 1 47
element dispBeamColumn 48 26 29 3 1 48
element dispBeamColumn 49 29 24 3 1 49
element dispBeamColumn 50 24 27 3 1 50
element dispBeamColumn 51 27 22 3 1 51
element dispBeamColumn 52 6 26 3 2 52
element dispBeamColumn 53 9 29 3 2 53
element dispBeamColumn 54 4 24 3 2 54
element dispBeamColumn 55 7 27 3 2 55
element dispBeamColumn 56 2 22 3 2 56
puts "shell element"
puts "recorder"
recorder Node -file node0.out -time -nodeRange 1 40 -dof 1 2 3 disp
recorder Element -file ele0.out -time -eleRange 1 56 localForce
####################################################################记录跨中的竖向位移与ETABS 进行对比
recorder Node -file node8.out -time -node 8 -dof 1 2 3 disp

puts "loading"
## Load Case = DEAD
pattern Plain 1 Linear {
load 1 0.000E+000 0.000E+000 -1.000E+004 0.000E+000 0.000E+000 0.000E+000
load 3 0.000E+000 0.000E+000 -1.000E+004 0.000E+000 0.000E+000 0.000E+000
load 5 0.000E+000 0.000E+000 -1.000E+004 0.000E+000 0.000E+000 0.000E+000
load 8 0.000E+000 0.000E+000 -1.000E+004 0.000E+000 0.000E+000 0.000E+000
load 10 0.000E+000 0.000E+000 -1.000E+004 0.000E+000 0.000E+000 0.000E+000
load 21 0.000E+000 0.000E+000 -1.000E+004 0.000E+000 0.000E+000 0.000E+000
load 23 0.000E+000 0.000E+000 -1.000E+004 0.000E+000 0.000E+000 0.000E+000
load 25 0.000E+000 0.000E+000 -1.000E+004 0.000E+000 0.000E+000 0.000E+000
load 28 0.000E+000 0.000E+000 -1.000E+004 0.000E+000 0.000E+000 0.000E+000
load 30 0.000E+000 0.000E+000 -1.000E+004 0.000E+000 0.000E+000 0.000E+000
}
puts "analysis"
constraints Plain
numberer Plain
system BandGeneral
test EnergyIncr 1.0e-6 200
algorithm Newton
integrator LoadControl 1.000E+000
analysis Static
analyze 1
