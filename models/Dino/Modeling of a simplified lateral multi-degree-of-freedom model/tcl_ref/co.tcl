wipe
puts "System"
model basic -ndm 3 -ndf 6
puts "restraint"
node 1 0.000E+000 0.000E+000 3.600E+004
node 2 0.000E+000 0.000E+000 3.300E+004
node 3 0.000E+000 0.000E+000 3.000E+004
node 4 0.000E+000 0.000E+000 2.700E+004
node 5 0.000E+000 0.000E+000 2.400E+004
node 6 0.000E+000 0.000E+000 2.100E+004
node 7 0.000E+000 0.000E+000 1.800E+004
node 8 0.000E+000 0.000E+000 1.500E+004
node 9 0.000E+000 0.000E+000 1.200E+004
node 10 0.000E+000 0.000E+000 9.000E+003
node 11 0.000E+000 0.000E+000 6.000E+003
node 12 0.000E+000 0.000E+000 3.000E+003
node 13 0.000E+000 0.000E+000 0.000E+000
puts "rigidDiaphragm"
puts "mass"
mass 1 1.00E+002 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 2 1.00E+002 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 3 1.00E+002 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 4 1.00E+002 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 5 1.00E+002 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 6 1.00E+002 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 7 1.00E+002 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 8 1.00E+002 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 9 1.00E+002 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 10 1.00E+002 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 11 1.00E+002 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 12 1.00E+002 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 13 1.00E+002 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
puts "node"
fix 1 0 1 1 1 1 1;
fix 2 0 1 1 1 1 1;
fix 3 0 1 1 1 1 1;
fix 4 0 1 1 1 1 1;
fix 5 0 1 1 1 1 1;
fix 6 0 1 1 1 1 1;
fix 7 0 1 1 1 1 1;
fix 8 0 1 1 1 1 1;
fix 9 0 1 1 1 1 1;
fix 10 0 1 1 1 1 1;
fix 11 0 1 1 1 1 1;
fix 12 0 1 1 1 1 1;
fix 13 1 1 1 1 1 1;
puts "Equal DOF"
puts "material"
uniaxialMaterial Elastic 1 1.999E+005
uniaxialMaterial Elastic 2 2.482E+004
uniaxialMaterial Elastic 3 1.999E+005

geomTransf Linear 1 1.000 0.000 0.000 
geomTransf Linear 2 1.000 0.000 0.000 
geomTransf Linear 3 1.000 0.000 0.000 
geomTransf Linear 4 1.000 0.000 0.000 
geomTransf Linear 5 1.000 0.000 0.000 
geomTransf Linear 6 1.000 0.000 0.000 
geomTransf Linear 7 1.000 0.000 0.000 
geomTransf Linear 8 1.000 0.000 0.000 
geomTransf Linear 9 1.000 0.000 0.000 
geomTransf Linear 10 1.000 0.000 0.000 
geomTransf Linear 11 1.000 0.000 0.000 
geomTransf Linear 12 1.000 0.000 0.000 
puts "transformation"
puts "element"
element	ElasticTimoshenkoBeam	1	2	1	1.00E+05	1.00E+05	1.00E+20	1.00E+20	1.00E+20	1.00E+20	3.00E+03	3.00E+03	1
element	ElasticTimoshenkoBeam	2	3	2	1.00E+05	1.00E+05	1.00E+20	1.00E+20	1.00E+20	1.00E+20	3.00E+03	3.00E+03	2
element	ElasticTimoshenkoBeam	3	4	3	1.00E+05	1.00E+05	1.00E+20	1.00E+20	1.00E+20	1.00E+20	3.00E+03	3.00E+03	3
element	ElasticTimoshenkoBeam	4	5	4	1.00E+05	1.00E+05	1.00E+20	1.00E+20	1.00E+20	1.00E+20	3.00E+03	3.00E+03	4
element	ElasticTimoshenkoBeam	5	6	5	1.00E+05	1.00E+05	1.00E+20	1.00E+20	1.00E+20	1.00E+20	3.00E+03	3.00E+03	5
element	ElasticTimoshenkoBeam	6	7	6	1.00E+05	1.00E+05	1.00E+20	1.00E+20	1.00E+20	1.00E+20	3.00E+03	3.00E+03	6
element	ElasticTimoshenkoBeam	7	8	7	1.00E+05	1.00E+05	1.00E+20	1.00E+20	1.00E+20	1.00E+20	3.00E+03	3.00E+03	7
element	ElasticTimoshenkoBeam	8	9	8	1.00E+05	1.00E+05	1.00E+20	1.00E+20	1.00E+20	1.00E+20	3.00E+03	3.00E+03	8
element	ElasticTimoshenkoBeam	9	10	9	1.00E+05	1.00E+05	1.00E+20	1.00E+20	1.00E+20	1.00E+20	3.00E+03	3.00E+03	9
element	ElasticTimoshenkoBeam	10	11	10	1.00E+05	1.00E+05	1.00E+20	1.00E+20	1.00E+20	1.00E+20	3.00E+03	3.00E+03	10
element	ElasticTimoshenkoBeam	11	12	11	1.00E+05	1.00E+05	1.00E+20	1.00E+20	1.00E+20	1.00E+20	3.00E+03	3.00E+03	11
element	ElasticTimoshenkoBeam	12	13	12	1.00E+05	1.00E+05	1.00E+20	1.00E+20	1.00E+20	1.00E+20	3.00E+03	3.00E+03	12

recorder Node -file node0.out -time -nodeRange 1 13 -dof 1 2 3 disp
recorder Node -file eigen1_node0.out -time -nodeRange 1 13 -dof 1 2 3 "eigen 1"
recorder Node -file eigen2_node0.out -time -nodeRange 1 13 -dof 1 2 3 "eigen 2"
recorder Node -file eigen3_node0.out -time -nodeRange 1 13 -dof 1 2 3 "eigen 3"
recorder Node -file eigen4_node0.out -time -nodeRange 1 13 -dof 1 2 3 "eigen 4"
recorder Node -file eigen5_node0.out -time -nodeRange 1 13 -dof 1 2 3 "eigen 5"
recorder Node -file eigen6_node0.out -time -nodeRange 1 13 -dof 1 2 3 "eigen 6"
recorder Node -file eigen7_node0.out -time -nodeRange 1 13 -dof 1 2 3 "eigen 7"
recorder Node -file eigen8_node0.out -time -nodeRange 1 13 -dof 1 2 3 "eigen 8"
recorder Node -file eigen9_node0.out -time -nodeRange 1 13 -dof 1 2 3 "eigen 9"
recorder Node -file eigen10_node0.out -time -nodeRange 1 13 -dof 1 2 3 "eigen 10"
set numModes 10
set lambda [eigen  $numModes]
set period "Periods.txt"
set Periods [open $period "w"]
puts $Periods " $lambda"
close $Periods
record

