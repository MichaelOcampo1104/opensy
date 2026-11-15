wipe
puts "System"
model basic -ndm 3 -ndf 6
puts "restraint"
node 1 4.500E+003 5.000E+003 1.050E+004
node 2 4.500E+003 5.000E+003 1.350E+004
node 3 4.500E+003 0.000E+000 1.050E+004
node 4 4.500E+003 0.000E+000 1.350E+004
node 5 0.000E+000 0.000E+000 1.050E+004
node 6 0.000E+000 0.000E+000 1.350E+004
node 7 0.000E+000 5.000E+003 1.050E+004
node 8 0.000E+000 5.000E+003 1.350E+004
node 9 4.500E+003 0.000E+000 7.500E+003
node 10 4.500E+003 5.000E+003 7.500E+003
node 11 0.000E+000 0.000E+000 7.500E+003
node 12 0.000E+000 5.000E+003 7.500E+003
node 13 9.000E+003 0.000E+000 7.500E+003
node 14 9.000E+003 0.000E+000 1.050E+004
node 15 9.000E+003 5.000E+003 7.500E+003
node 16 9.000E+003 5.000E+003 1.050E+004
node 17 4.500E+003 0.000E+000 4.500E+003
node 18 4.500E+003 5.000E+003 4.500E+003
node 19 0.000E+000 0.000E+000 4.500E+003
node 20 0.000E+000 5.000E+003 4.500E+003
node 21 9.000E+003 0.000E+000 4.500E+003
node 22 9.000E+003 5.000E+003 4.500E+003
node 23 4.500E+003 0.000E+000 0.000E+000
node 24 4.500E+003 5.000E+003 0.000E+000
node 25 0.000E+000 0.000E+000 0.000E+000
node 26 0.000E+000 5.000E+003 0.000E+000
node 27 9.000E+003 0.000E+000 0.000E+000
node 28 9.000E+003 5.000E+003 0.000E+000
puts "rigidDiaphragm"
puts "mass"
mass 1 8.604E+000 8.604E+000 8.604E+000 0.000E+000 0.000E+000 0.000E+000
mass 2 4.302E+000 4.302E+000 4.302E+000 0.000E+000 0.000E+000 0.000E+000
mass 3 8.604E+000 8.604E+000 8.604E+000 0.000E+000 0.000E+000 0.000E+000
mass 4 4.302E+000 4.302E+000 4.302E+000 0.000E+000 0.000E+000 0.000E+000
mass 5 4.302E+000 4.302E+000 4.302E+000 0.000E+000 0.000E+000 0.000E+000
mass 6 4.302E+000 4.302E+000 4.302E+000 0.000E+000 0.000E+000 0.000E+000
mass 7 4.302E+000 4.302E+000 4.302E+000 0.000E+000 0.000E+000 0.000E+000
mass 8 4.302E+000 4.302E+000 4.302E+000 0.000E+000 0.000E+000 0.000E+000
mass 9 8.604E+000 8.604E+000 8.604E+000 0.000E+000 0.000E+000 0.000E+000
mass 10 8.604E+000 8.604E+000 8.604E+000 0.000E+000 0.000E+000 0.000E+000
mass 11 4.302E+000 4.302E+000 4.302E+000 0.000E+000 0.000E+000 0.000E+000
mass 12 4.302E+000 4.302E+000 4.302E+000 0.000E+000 0.000E+000 0.000E+000
mass 13 4.302E+000 4.302E+000 4.302E+000 0.000E+000 0.000E+000 0.000E+000
mass 14 4.302E+000 4.302E+000 4.302E+000 0.000E+000 0.000E+000 0.000E+000
mass 15 4.302E+000 4.302E+000 4.302E+000 0.000E+000 0.000E+000 0.000E+000
mass 16 4.302E+000 4.302E+000 4.302E+000 0.000E+000 0.000E+000 0.000E+000
mass 17 8.604E+000 8.604E+000 8.604E+000 0.000E+000 0.000E+000 0.000E+000
mass 18 8.604E+000 8.604E+000 8.604E+000 0.000E+000 0.000E+000 0.000E+000
mass 19 4.302E+000 4.302E+000 4.302E+000 0.000E+000 0.000E+000 0.000E+000
mass 20 4.302E+000 4.302E+000 4.302E+000 0.000E+000 0.000E+000 0.000E+000
mass 21 4.302E+000 4.302E+000 4.302E+000 0.000E+000 0.000E+000 0.000E+000
mass 22 4.302E+000 4.302E+000 4.302E+000 0.000E+000 0.000E+000 0.000E+000
puts "node"
fix 23 1 1 1 1 1 1;
fix 24 1 1 1 1 1 1;
fix 25 1 1 1 1 1 1;
fix 26 1 1 1 1 1 1;
fix 27 1 1 1 1 1 1;
fix 28 1 1 1 1 1 1;
puts "material"
uniaxialMaterial Elastic 1 1.999E+005
uniaxialMaterial Elastic 2 2.680E+004
uniaxialMaterial Elastic 3 1.999E+005
puts "transformation"
geomTransf Linear 1 1.000 0.000 0.000 
geomTransf Linear 2 1.000 0.000 0.000 
geomTransf Linear 3 1.000 0.000 0.000 
geomTransf Linear 4 1.000 0.000 0.000 
geomTransf Linear 5 0.000 0.000 1.000 
geomTransf Linear 6 0.000 0.000 1.000 
geomTransf Linear 7 0.000 0.000 1.000 
geomTransf Linear 8 0.000 0.000 1.000 
geomTransf Linear 9 1.000 0.000 0.000 
geomTransf Linear 10 1.000 0.000 0.000 
geomTransf Linear 11 1.000 0.000 0.000 
geomTransf Linear 12 1.000 0.000 0.000 
geomTransf Linear 13 1.000 0.000 0.000 
geomTransf Linear 14 1.000 0.000 0.000 
geomTransf Linear 15 0.000 0.000 1.000 
geomTransf Linear 16 0.000 0.000 1.000 
geomTransf Linear 17 0.000 0.000 1.000 
geomTransf Linear 18 0.000 0.000 1.000 
geomTransf Linear 19 0.000 0.000 1.000 
geomTransf Linear 20 0.000 0.000 1.000 
geomTransf Linear 21 0.000 0.000 1.000 
geomTransf Linear 22 1.000 0.000 0.000 
geomTransf Linear 23 1.000 0.000 0.000 
geomTransf Linear 24 1.000 0.000 0.000 
geomTransf Linear 25 1.000 0.000 0.000 
geomTransf Linear 26 1.000 0.000 0.000 
geomTransf Linear 27 1.000 0.000 0.000 
geomTransf Linear 28 0.000 0.000 1.000 
geomTransf Linear 29 0.000 0.000 1.000 
geomTransf Linear 30 0.000 0.000 1.000 
geomTransf Linear 31 0.000 0.000 1.000 
geomTransf Linear 32 0.000 0.000 1.000 
geomTransf Linear 33 0.000 0.000 1.000 
geomTransf Linear 34 0.000 0.000 1.000 
geomTransf Linear 35 1.000 0.000 0.000 
geomTransf Linear 36 1.000 0.000 0.000 
geomTransf Linear 37 1.000 0.000 0.000 
geomTransf Linear 38 1.000 0.000 0.000 
geomTransf Linear 39 1.000 0.000 0.000 
geomTransf Linear 40 1.000 0.000 0.000 
geomTransf Linear 41 0.000 0.000 1.000 
geomTransf Linear 42 0.000 0.000 1.000 
geomTransf Linear 43 0.000 0.000 1.000 
geomTransf Linear 44 0.000 0.000 1.000 
geomTransf Linear 45 0.000 0.000 1.000 
geomTransf Linear 46 0.000 0.000 1.000 
geomTransf Linear 47 0.000 0.000 1.000 
puts "element"
element elasticBeamColumn 1 1 2 1.600E+005 2.680E+004 1.117E+004 3.605E+009 2.133E+009 2.133E+009 1
element elasticBeamColumn 2 3 4 1.600E+005 2.680E+004 1.117E+004 3.605E+009 2.133E+009 2.133E+009 2
element elasticBeamColumn 3 5 6 1.600E+005 2.680E+004 1.117E+004 3.605E+009 2.133E+009 2.133E+009 3
element elasticBeamColumn 4 7 8 1.600E+005 2.680E+004 1.117E+004 3.605E+009 2.133E+009 2.133E+009 4
element elasticBeamColumn 5 6 8 1.800E+005 2.680E+004 1.117E+004 3.708E+009 5.400E+009 1.350E+009 5
element elasticBeamColumn 6 4 2 1.800E+005 2.680E+004 1.117E+004 3.708E+009 5.400E+009 1.350E+009 6
element elasticBeamColumn 7 8 2 1.500E+005 2.680E+004 1.117E+004 2.817E+009 3.125E+009 1.125E+009 7
element elasticBeamColumn 8 6 4 1.500E+005 2.680E+004 1.117E+004 2.817E+009 3.125E+009 1.125E+009 8
element elasticBeamColumn 9 9 3 1.600E+005 2.680E+004 1.117E+004 3.605E+009 2.133E+009 2.133E+009 9
element elasticBeamColumn 10 10 1 1.600E+005 2.680E+004 1.117E+004 3.605E+009 2.133E+009 2.133E+009 10
element elasticBeamColumn 11 11 5 2.400E+005 2.680E+004 1.117E+004 7.512E+009 7.200E+009 3.200E+009 11
element elasticBeamColumn 12 12 7 2.400E+005 2.680E+004 1.117E+004 7.512E+009 7.200E+009 3.200E+009 12
element elasticBeamColumn 13 13 14 2.400E+005 2.680E+004 1.117E+004 7.512E+009 7.200E+009 3.200E+009 13
element elasticBeamColumn 14 15 16 2.400E+005 2.680E+004 1.117E+004 7.512E+009 7.200E+009 3.200E+009 14
element elasticBeamColumn 15 7 1 1.500E+005 2.680E+004 1.117E+004 2.817E+009 3.125E+009 1.125E+009 15
element elasticBeamColumn 16 1 16 1.500E+005 2.680E+004 1.117E+004 2.817E+009 3.125E+009 1.125E+009 16
element elasticBeamColumn 17 3 14 1.500E+005 2.680E+004 1.117E+004 2.817E+009 3.125E+009 1.125E+009 17
element elasticBeamColumn 18 5 3 1.500E+005 2.680E+004 1.117E+004 2.817E+009 3.125E+009 1.125E+009 18
element elasticBeamColumn 19 3 1 1.800E+005 2.680E+004 1.117E+004 3.708E+009 5.400E+009 1.350E+009 19
element elasticBeamColumn 20 14 16 1.800E+005 2.680E+004 1.117E+004 3.708E+009 5.400E+009 1.350E+009 20
element elasticBeamColumn 21 5 7 1.800E+005 2.680E+004 1.117E+004 3.708E+009 5.400E+009 1.350E+009 21
element elasticBeamColumn 22 17 9 1.600E+005 2.680E+004 1.117E+004 3.605E+009 2.133E+009 2.133E+009 22
element elasticBeamColumn 23 18 10 1.600E+005 2.680E+004 1.117E+004 3.605E+009 2.133E+009 2.133E+009 23
element elasticBeamColumn 24 19 11 2.400E+005 2.680E+004 1.117E+004 7.512E+009 7.200E+009 3.200E+009 24
element elasticBeamColumn 25 20 12 2.400E+005 2.680E+004 1.117E+004 7.512E+009 7.200E+009 3.200E+009 25
element elasticBeamColumn 26 21 13 2.400E+005 2.680E+004 1.117E+004 7.512E+009 7.200E+009 3.200E+009 26
element elasticBeamColumn 27 22 15 2.400E+005 2.680E+004 1.117E+004 7.512E+009 7.200E+009 3.200E+009 27
element elasticBeamColumn 28 12 10 1.500E+005 2.680E+004 1.117E+004 2.817E+009 3.125E+009 1.125E+009 28
element elasticBeamColumn 29 10 15 1.500E+005 2.680E+004 1.117E+004 2.817E+009 3.125E+009 1.125E+009 29
element elasticBeamColumn 30 9 13 1.500E+005 2.680E+004 1.117E+004 2.817E+009 3.125E+009 1.125E+009 30
element elasticBeamColumn 31 11 9 1.500E+005 2.680E+004 1.117E+004 2.817E+009 3.125E+009 1.125E+009 31
element elasticBeamColumn 32 9 10 1.800E+005 2.680E+004 1.117E+004 3.708E+009 5.400E+009 1.350E+009 32
element elasticBeamColumn 33 13 15 1.800E+005 2.680E+004 1.117E+004 3.708E+009 5.400E+009 1.350E+009 33
element elasticBeamColumn 34 11 12 1.800E+005 2.680E+004 1.117E+004 3.708E+009 5.400E+009 1.350E+009 34
element elasticBeamColumn 35 23 17 1.600E+005 2.680E+004 1.117E+004 3.605E+009 2.133E+009 2.133E+009 35
element elasticBeamColumn 36 24 18 1.600E+005 2.680E+004 1.117E+004 3.605E+009 2.133E+009 2.133E+009 36
element elasticBeamColumn 37 25 19 2.400E+005 2.680E+004 1.117E+004 7.512E+009 7.200E+009 3.200E+009 37
element elasticBeamColumn 38 26 20 2.400E+005 2.680E+004 1.117E+004 7.512E+009 7.200E+009 3.200E+009 38
element elasticBeamColumn 39 27 21 2.400E+005 2.680E+004 1.117E+004 7.512E+009 7.200E+009 3.200E+009 39
element elasticBeamColumn 40 28 22 2.400E+005 2.680E+004 1.117E+004 7.512E+009 7.200E+009 3.200E+009 40
element elasticBeamColumn 41 20 18 1.500E+005 2.680E+004 1.117E+004 2.817E+009 3.125E+009 1.125E+009 41
element elasticBeamColumn 42 18 22 1.500E+005 2.680E+004 1.117E+004 2.817E+009 3.125E+009 1.125E+009 42
element elasticBeamColumn 43 17 21 1.500E+005 2.680E+004 1.117E+004 2.817E+009 3.125E+009 1.125E+009 43
element elasticBeamColumn 44 19 17 1.500E+005 2.680E+004 1.117E+004 2.817E+009 3.125E+009 1.125E+009 44
element elasticBeamColumn 45 17 18 1.800E+005 2.680E+004 1.117E+004 3.708E+009 5.400E+009 1.350E+009 45
element elasticBeamColumn 46 21 22 1.800E+005 2.680E+004 1.117E+004 3.708E+009 5.400E+009 1.350E+009 46
element elasticBeamColumn 47 19 20 1.800E+005 2.680E+004 1.117E+004 3.708E+009 5.400E+009 1.350E+009 47
puts "recorder"
recorder Node -file eigen1_node0.out -time -nodeRange 1 28 -dof 1 2 3 "eigen 1"
recorder Node -file eigen2_node0.out -time -nodeRange 1 28 -dof 1 2 3 "eigen 2"
recorder Node -file eigen3_node0.out -time -nodeRange 1 28 -dof 1 2 3 "eigen 3"
recorder Node -file eigen4_node0.out -time -nodeRange 1 28 -dof 1 2 3 "eigen 4"
recorder Node -file eigen5_node0.out -time -nodeRange 1 28 -dof 1 2 3 "eigen 5"
recorder Node -file eigen6_node0.out -time -nodeRange 1 28 -dof 1 2 3 "eigen 6"
recorder Node -file eigen7_node0.out -time -nodeRange 1 28 -dof 1 2 3 "eigen 7"
recorder Node -file eigen8_node0.out -time -nodeRange 1 28 -dof 1 2 3 "eigen 8"
recorder Node -file eigen9_node0.out -time -nodeRange 1 28 -dof 1 2 3 "eigen 9"
recorder Node -file eigen10_node0.out -time -nodeRange 1 28 -dof 1 2 3 "eigen 10"
recorder Node -file eigen11_node0.out -time -nodeRange 1 28 -dof 1 2 3 "eigen 11"
recorder Node -file eigen12_node0.out -time -nodeRange 1 28 -dof 1 2 3 "eigen 12"
set numModes 12
set lambda [eigen  $numModes]
set period "Periods.txt"
set Periods [open $period "w"]
puts $Periods " $lambda"
close $Periods
record
