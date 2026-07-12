wipe
puts "System"
model basic -ndm 3 -ndf 6
puts "restraint"
node 1 6.000E+003 6.000E+003 0
node 2 6.000E+003 6.000E+003 600
node 3 6.000E+003 6.000E+003 1200
node 4 6.000E+003 6.000E+003 1800
node 5 6.000E+003 6.000E+003 2400
node 100 6.000E+003 6.000E+003 3000


fix 1 1 1 1 1 1 1;
fix 100 0 1 0 0 0 0;
puts "Equal DOF"
puts "material"
uniaxialMaterial Concrete01 1 -26.8 -0.002 -15 -0.008
uniaxialMaterial Steel01 3 400 200000 0.001 


uniaxialMaterial Elastic 2 1.999E+005
uniaxialMaterial Elastic 201 2.155E+015
uniaxialMaterial Elastic 301 2.155E+015
uniaxialMaterial Elastic 401 9.103E+015
##DB500X500 
source section_fiber.tcl



section Aggregator 1001 201 Vy 301 Vz 401 T -section 1


puts "transformation"
geomTransf Linear 1 1.000 0.000 0.000 
geomTransf Linear 2 1.000 0.000 0.000 
geomTransf Linear 3 1.000 0.000 0.000 
geomTransf Linear 4 1.000 0.000 0.000 
geomTransf Linear 5 1.000 0.000 0.000 
puts "element"
element dispBeamColumn 1 1 2 3 1001 1
element dispBeamColumn 2 2 3 3 1001 2
element dispBeamColumn 3 3 4 3 1001 3
element dispBeamColumn 4 4 5 3 1001 4
element dispBeamColumn 5 5 100 3 1001 5
puts "shell element"
puts "SOLID element"

puts "loading"




pattern Plain 1 Linear {
load 100 0.0 0.0 -19125000.00 0E+000 0.000E+000 0.000E+000
}
constraints Plain
numberer Plain
system BandGeneral
test EnergyIncr 1.0e-6 200
algorithm Newton
integrator LoadControl 0.1
analysis Static
analyze 10
loadConst 0.0

puts "recorder"
recorder Node -file node2.out -time -node 100 -dof 1 disp


## Load Case = push
pattern Plain 2 Linear {
load 100 1.000E+005 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
}
puts "analysis"
constraints Plain
numberer Plain
system BandGeneral
test EnergyIncr 1.0e-3 1000
algorithm Newton
analysis Static

array set kdisps {
0	0.1
1	-0.2
2	0.3
3	-0.4
4	0.5
5	-0.6
6	0.7
7	-0.8
8	0.9
9	-1
10	1.1
}

for {set i 0} {$i < 10} {incr i} {
  integrator DisplacementControl 100 1 [expr $kdisps($i)*0.5]
  analyze 100
}



