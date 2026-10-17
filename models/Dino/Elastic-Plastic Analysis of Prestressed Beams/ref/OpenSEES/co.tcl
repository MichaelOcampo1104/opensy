wipe
puts "System"
model basic -ndm 3 -ndf 6
puts "restraint"
node 1 0.000E+000 0.000E+000 8.000E+003
node 2 2.000E+003 0.000E+000 7.847E+003
node 3 4.000E+003 0.000E+000 7.722E+003
node 4 6.000E+003 0.000E+000 7.625E+003
node 5 8.000E+003 0.000E+000 7.556E+003
node 6 1.000E+004 0.000E+000 7.514E+003
node 7 1.200E+004 0.000E+000 7.500E+003
node 8 2.400E+004 0.000E+000 8.000E+003
node 9 2.200E+004 0.000E+000 7.847E+003
node 10 2.000E+004 0.000E+000 7.722E+003
node 11 1.800E+004 0.000E+000 7.625E+003
node 12 1.600E+004 0.000E+000 7.556E+003
node 13 1.400E+004 0.000E+000 7.514E+003
node 14 2.000E+003 0.000E+000 8.000E+003
node 15 4.000E+003 0.000E+000 8.000E+003
node 16 6.000E+003 0.000E+000 8.000E+003
node 17 8.000E+003 0.000E+000 8.000E+003
node 18 1.000E+004 0.000E+000 8.000E+003
node 19 1.200E+004 0.000E+000 8.000E+003
node 20 1.400E+004 0.000E+000 8.000E+003
node 21 1.600E+004 0.000E+000 8.000E+003
node 22 1.800E+004 0.000E+000 8.000E+003
node 23 2.000E+004 0.000E+000 8.000E+003
node 24 2.200E+004 0.000E+000 8.000E+003
puts "rigidDiaphragm"
puts "mass"
puts "node"
fix 1 1 1 1 1 0 1;
fix 2 0 1 0 1 0 1;
fix 3 0 1 0 1 0 1;
fix 4 0 1 0 1 0 1;
fix 5 0 1 0 1 0 1;
fix 6 0 1 0 1 0 1;
fix 7 0 1 0 1 0 1;
fix 8 1 1 1 1 0 1;
fix 9 0 1 0 1 0 1;
fix 10 0 1 0 1 0 1;
fix 11 0 1 0 1 0 1;
fix 12 0 1 0 1 0 1;
fix 13 0 1 0 1 0 1;
fix 14 0 1 0 1 0 1;
fix 15 0 1 0 1 0 1;
fix 16 0 1 0 1 0 1;
fix 17 0 1 0 1 0 1;
fix 18 0 1 0 1 0 1;
fix 19 0 1 0 1 0 1;
fix 20 0 1 0 1 0 1;
fix 21 0 1 0 1 0 1;
fix 22 0 1 0 1 0 1;
fix 23 0 1 0 1 0 1;
fix 24 0 1 0 1 0 1;
puts "Equal DOF"
puts "material"
###################################################修改材料
uniaxialMaterial Steel01 1 200 200000 0.02
uniaxialMaterial Elastic 2 2.482E+004
uniaxialMaterial Elastic 3 1.999E+005
uniaxialMaterial Concrete02 4  -26.8  -0.002 -10 -0.005 0.1 2.68 1000
##uniaxialMaterial Steel02 5 1600 206000 0.02 18 0.925 0.15 0 1 0 1 1100
##用于模拟不施加预应力时的情况
uniaxialMaterial Steel01 5 1600 206000 0.02				
##DC40B600X1600 
section Fiber 1 {
fiber -2.400E+002 -6.400E+002 3.840E+004 4
fiber -1.200E+002 -6.400E+002 3.840E+004 4
fiber 0.000E+000 -6.400E+002 3.840E+004 4
fiber 1.200E+002 -6.400E+002 3.840E+004 4
fiber 2.400E+002 -6.400E+002 3.840E+004 4
fiber -2.400E+002 -3.200E+002 3.840E+004 4
fiber -1.200E+002 -3.200E+002 3.840E+004 4
fiber 0.000E+000 -3.200E+002 3.840E+004 4
fiber 1.200E+002 -3.200E+002 3.840E+004 4
fiber 2.400E+002 -3.200E+002 3.840E+004 4
fiber -2.400E+002 0.000E+000 3.840E+004 4
fiber -1.200E+002 0.000E+000 3.840E+004 4
fiber 0.000E+000 0.000E+000 3.840E+004 4
fiber 1.200E+002 0.000E+000 3.840E+004 4
fiber 2.400E+002 0.000E+000 3.840E+004 4
fiber -2.400E+002 3.200E+002 3.840E+004 4
fiber -1.200E+002 3.200E+002 3.840E+004 4
fiber 0.000E+000 3.200E+002 3.840E+004 4
fiber 1.200E+002 3.200E+002 3.840E+004 4
fiber 2.400E+002 3.200E+002 3.840E+004 4
fiber -2.400E+002 6.400E+002 3.840E+004 4
fiber -1.200E+002 6.400E+002 3.840E+004 4
fiber 0.000E+000 6.400E+002 3.840E+004 4
fiber 1.200E+002 6.400E+002 3.840E+004 4
fiber 2.400E+002 6.400E+002 3.840E+004 4
fiber -2.650E+002 7.650E+002 1.500E+003 1
fiber 2.650E+002 7.650E+002 1.500E+003 1
fiber -2.650E+002 -7.650E+002 3.925E+003 1
fiber 2.650E+002 -7.650E+002 3.925E+003 1
}
##DBAR 
#################################################定义预应力钢筋纤维截面
section Fiber 3 {
fiber 5.000E+001 0.000E+000 1.186E+002 5
fiber 4.755E+001 1.545E+001 1.186E+002 5
fiber 4.045E+001 2.939E+001 1.186E+002 5
fiber 2.939E+001 4.045E+001 1.186E+002 5
fiber 1.545E+001 4.755E+001 1.186E+002 5
fiber -1.355E-018 5.000E+001 1.186E+002 5
fiber -1.545E+001 4.755E+001 1.186E+002 5
fiber -2.939E+001 4.045E+001 1.186E+002 5
fiber -4.045E+001 2.939E+001 1.186E+002 5
fiber -4.755E+001 1.545E+001 1.186E+002 5
fiber -5.000E+001 -2.711E-018 1.186E+002 5
fiber -4.755E+001 -1.545E+001 1.186E+002 5
fiber -4.045E+001 -2.939E+001 1.186E+002 5
fiber -2.939E+001 -4.045E+001 1.186E+002 5
fiber -1.545E+001 -4.755E+001 1.186E+002 5
fiber 9.487E-018 -5.000E+001 1.186E+002 5
fiber 1.545E+001 -4.755E+001 1.186E+002 5
fiber 2.939E+001 -4.045E+001 1.186E+002 5
fiber 4.045E+001 -2.939E+001 1.186E+002 5
fiber 4.755E+001 -1.545E+001 1.186E+002 5
}
puts "transformation"
geomTransf Linear 1 0.076 0.000 0.997 
geomTransf Linear 2 0.062 0.000 0.998 
geomTransf Linear 3 0.048 0.000 0.999 
geomTransf Linear 4 0.034 0.000 0.999 
geomTransf Linear 5 0.021 0.000 1.000 
geomTransf Linear 6 0.007 0.000 1.000 
geomTransf Linear 7 -0.076 0.000 0.997 
geomTransf Linear 8 -0.062 0.000 0.998 
geomTransf Linear 9 -0.048 0.000 0.999 
geomTransf Linear 10 -0.034 0.000 0.999 
geomTransf Linear 11 -0.021 0.000 1.000 
geomTransf Linear 12 -0.007 0.000 1.000 
geomTransf Linear 13 0.000 0.000 1.000 
geomTransf Linear 14 0.000 0.000 1.000 
geomTransf Linear 15 0.000 0.000 1.000 
geomTransf Linear 16 0.000 0.000 1.000 
geomTransf Linear 17 0.000 0.000 1.000 
geomTransf Linear 18 0.000 0.000 1.000 
geomTransf Linear 19 0.000 0.000 1.000 
geomTransf Linear 20 0.000 0.000 1.000 
geomTransf Linear 21 0.000 0.000 1.000 
geomTransf Linear 22 0.000 0.000 1.000 
geomTransf Linear 23 0.000 0.000 1.000 
geomTransf Linear 24 0.000 0.000 1.000 
geomTransf Linear 25 1.000 0.000 0.000 
geomTransf Linear 26 1.000 0.000 0.000 
geomTransf Linear 27 1.000 0.000 0.000 
geomTransf Linear 28 1.000 0.000 0.000 
geomTransf Linear 29 1.000 0.000 0.000 
geomTransf Linear 30 1.000 0.000 0.000 
geomTransf Linear 31 1.000 0.000 0.000 
geomTransf Linear 32 1.000 0.000 0.000 
geomTransf Linear 33 1.000 0.000 0.000 
geomTransf Linear 34 1.000 0.000 0.000 
geomTransf Linear 35 1.000 0.000 0.000 
puts "element"
element dispBeamColumn 1 2 1 3 3 1
element dispBeamColumn 2 3 2 3 3 2
element dispBeamColumn 3 4 3 3 3 3
element dispBeamColumn 4 5 4 3 3 4
element dispBeamColumn 5 6 5 3 3 5
element dispBeamColumn 6 6 7 3 3 6
element dispBeamColumn 7 9 8 3 3 7
element dispBeamColumn 8 10 9 3 3 8
element dispBeamColumn 9 11 10 3 3 9
element dispBeamColumn 10 12 11 3 3 10
element dispBeamColumn 11 13 12 3 3 11
element dispBeamColumn 12 7 13 3 3 12
element dispBeamColumn 13 1 14 3 1 13
element dispBeamColumn 14 14 15 3 1 14
element dispBeamColumn 15 15 16 3 1 15
element dispBeamColumn 16 16 17 3 1 16
element dispBeamColumn 17 17 18 3 1 17
element dispBeamColumn 18 18 19 3 1 18
element dispBeamColumn 19 19 20 3 1 19
element dispBeamColumn 20 20 21 3 1 20
element dispBeamColumn 21 21 22 3 1 21
element dispBeamColumn 22 22 23 3 1 22
element dispBeamColumn 23 23 24 3 1 23
element dispBeamColumn 24 24 8 3 1 24
###########################################################################################################增大刚臂的弹性模量1.999E+005——>1.999E+010
element elasticBeamColumn 25 2 14 1.520E+004 1.999E+08 7.690E+004 2.133E+006 3.955E+008 2.693E+007 25
element elasticBeamColumn 26 3 15 1.520E+004 1.999E+08 7.690E+004 2.133E+006 3.955E+008 2.693E+007 26
element elasticBeamColumn 27 4 16 1.520E+004 1.999E+08 7.690E+004 2.133E+006 3.955E+008 2.693E+007 27
element elasticBeamColumn 28 5 17 1.520E+004 1.999E+08 7.690E+004 2.133E+006 3.955E+008 2.693E+007 28
element elasticBeamColumn 29 6 18 1.520E+004 1.999E+08 7.690E+004 2.133E+006 3.955E+008 2.693E+007 29
element elasticBeamColumn 30 7 19 1.520E+004 1.999E+08 7.690E+004 2.133E+006 3.955E+008 2.693E+007 30
element elasticBeamColumn 31 13 20 1.520E+004 1.999E+08 7.690E+004 2.133E+006 3.955E+008 2.693E+007 31
element elasticBeamColumn 32 12 21 1.520E+004 1.999E+08 7.690E+004 2.133E+006 3.955E+008 2.693E+007 32
element elasticBeamColumn 33 11 22 1.520E+004 1.999E+08 7.690E+004 2.133E+006 3.955E+008 2.693E+007 33
element elasticBeamColumn 34 10 23 1.520E+004 1.999E+08 7.690E+004 2.133E+006 3.955E+008 2.693E+007 34
element elasticBeamColumn 35 9 24 1.520E+004 1.999E+08 7.690E+004 2.133E+006 3.955E+008 2.693E+007 35
puts "shell element"
puts "recorder"
recorder Node -file node0.out -time -nodeRange 1 24 -dof 1 2 3 disp
###########################################################################################################记录节点19位移
recorder Node -file node19.out -time -node 19 -dof 1 2 3 disp
puts "loading"
###########################################################################################################增加施工模拟荷载
## Load Case =  Construction simulation 
pattern Plain 1 Linear {
load 3 0.000E+000 0.000E+000 0 0.000E+000 0.000E+000 0.000E+000
}
puts "analysis"
constraints Plain
numberer Plain
system BandGeneral
test EnergyIncr 1.0e-6 200
algorithm Newton
integrator LoadControl 1
analysis Static
analyze 1


## Load Case = DEAD
pattern Plain 2 Linear {
load 19 0.000E+000 0.000E+000 -1.000E+003 0.000E+000 0.000E+000 0.000E+000
}
puts "analysis"
constraints Plain
numberer Plain
system BandGeneral
test EnergyIncr 1.0e-6 200
algorithm Newton
analysis Static
integrator DisplacementControl 19 3 -1.000E+000
analyze 360		
