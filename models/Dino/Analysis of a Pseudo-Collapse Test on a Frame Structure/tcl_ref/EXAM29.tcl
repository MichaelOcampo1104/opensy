wipe
puts "System"
model basic -ndm 3 -ndf 6
puts "restraint"
node 1 0.000E+000 1.200E+004 9.000E+003
node 2 0.000E+000 1.200E+004 1.200E+004
node 3 6.000E+003 1.200E+004 9.000E+003
node 4 6.000E+003 1.200E+004 1.200E+004
node 5 1.200E+004 1.200E+004 9.000E+003
node 6 1.200E+004 1.200E+004 1.200E+004
node 7 1.200E+004 6.000E+003 9.000E+003
node 8 1.200E+004 6.000E+003 1.200E+004
node 9 1.200E+004 0.000E+000 9.000E+003
node 10 1.200E+004 0.000E+000 1.200E+004
node 11 6.000E+003 0.000E+000 9.000E+003
node 12 6.000E+003 0.000E+000 1.200E+004
node 13 6.000E+003 6.000E+003 9.000E+003
node 14 6.000E+003 6.000E+003 1.200E+004
node 15 0.000E+000 0.000E+000 9.000E+003
node 16 0.000E+000 0.000E+000 1.200E+004
node 17 0.000E+000 6.000E+003 9.000E+003
node 18 0.000E+000 6.000E+003 1.200E+004
node 19 0.000E+000 1.200E+004 6.000E+003
node 20 6.000E+003 1.200E+004 6.000E+003
node 21 1.200E+004 1.200E+004 6.000E+003
node 22 1.200E+004 6.000E+003 6.000E+003
node 23 1.200E+004 0.000E+000 6.000E+003
node 24 6.000E+003 0.000E+000 6.000E+003
node 25 6.000E+003 6.000E+003 6.000E+003
node 26 0.000E+000 0.000E+000 6.000E+003
node 27 0.000E+000 6.000E+003 6.000E+003
node 28 0.000E+000 1.200E+004 3.000E+003
node 29 6.000E+003 1.200E+004 3.000E+003
node 30 1.200E+004 1.200E+004 3.000E+003
node 31 1.200E+004 6.000E+003 3.000E+003
node 32 1.200E+004 0.000E+000 3.000E+003
node 33 6.000E+003 0.000E+000 3.000E+003
node 34 6.000E+003 6.000E+003 3.000E+003
node 35 0.000E+000 0.000E+000 3.000E+003
node 36 0.000E+000 6.000E+003 3.000E+003
node 37 0.000E+000 1.200E+004 0.000E+000
node 38 6.000E+003 1.200E+004 0.000E+000
node 39 1.200E+004 1.200E+004 0.000E+000
node 40 1.200E+004 6.000E+003 0.000E+000
node 41 1.200E+004 0.000E+000 0.000E+000
node 42 6.000E+003 0.000E+000 0.000E+000
node 43 6.000E+003 6.000E+003 0.000E+000
node 44 0.000E+000 6.000E+003 0.000E+000
puts "rigidDiaphragm"
puts "mass"
mass 1 9.775E+000 9.775E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 2 8.857E+000 8.857E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 3 1.650E+001 1.650E+001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 4 1.558E+001 1.558E+001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 5 9.775E+000 9.775E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 6 8.857E+000 8.857E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 7 1.650E+001 1.650E+001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 8 1.558E+001 1.558E+001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 9 9.775E+000 9.775E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 10 8.857E+000 8.857E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 11 1.650E+001 1.650E+001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 12 1.558E+001 1.558E+001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 13 2.874E+001 2.874E+001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 14 2.782E+001 2.782E+001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 15 9.775E+000 9.775E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 16 8.857E+000 8.857E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 17 1.650E+001 1.650E+001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 18 1.558E+001 1.558E+001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 19 9.775E+000 9.775E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 20 1.650E+001 1.650E+001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 21 9.775E+000 9.775E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 22 1.650E+001 1.650E+001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 23 9.775E+000 9.775E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 24 1.650E+001 1.650E+001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 25 2.874E+001 2.874E+001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 26 9.775E+000 9.775E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 27 1.650E+001 1.650E+001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 28 9.775E+000 9.775E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 29 1.650E+001 1.650E+001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 30 9.775E+000 9.775E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 31 1.650E+001 1.650E+001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 32 9.775E+000 9.775E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 33 1.656E+001 1.656E+001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 34 2.874E+001 2.874E+001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 35 8.967E+000 8.967E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 36 1.656E+001 1.656E+001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 37 9.187E-001 9.187E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 38 9.187E-001 9.187E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 39 9.187E-001 9.187E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 40 9.187E-001 9.187E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 41 9.187E-001 9.187E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 42 9.187E-001 9.187E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 43 9.187E-001 9.187E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 44 9.187E-001 9.187E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
puts "node"
fix 37 1 1 1 0 0 0;
fix 38 1 1 1 0 0 0;
fix 39 1 1 1 0 0 0;
fix 40 1 1 1 0 0 0;
fix 41 1 1 1 0 0 0;
fix 42 1 1 1 0 0 0;
fix 43 1 1 1 0 0 0;
fix 44 1 1 1 0 0 0;
puts "Equal DOF"
puts "material"

uniaxialMaterial Steel01 1 300 206000 0.01 
uniaxialMaterial Concrete02 2 -20.0 -0.002 -5 -0.0033 0.1 2.2 1100


uniaxialMaterial Elastic 3 1.999E+005
uniaxialMaterial Elastic 201 2.170E+009
uniaxialMaterial Elastic 301 2.170E+009
uniaxialMaterial Elastic 401 9.169E+013
uniaxialMaterial Elastic 202 1.562E+009
uniaxialMaterial Elastic 302 1.562E+009
uniaxialMaterial Elastic 402 3.862E+013
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
fiber -2.150E+002 -2.150E+002 3.140E+002 1
fiber -1.075E+002 -2.150E+002 3.140E+002 1
fiber 0.000E+000 -2.150E+002 3.140E+002 1
fiber 1.075E+002 -2.150E+002 3.140E+002 1
fiber 2.150E+002 -2.150E+002 3.140E+002 1
fiber -2.150E+002 2.150E+002 3.140E+002 1
fiber -1.075E+002 2.150E+002 3.140E+002 1
fiber 0.000E+000 2.150E+002 3.140E+002 1
fiber 1.075E+002 2.150E+002 3.140E+002 1
fiber 2.150E+002 2.150E+002 3.140E+002 1
fiber -2.150E+002 -1.075E+002 3.140E+002 1
fiber -2.150E+002 0.000E+000 3.140E+002 1
fiber -2.150E+002 1.075E+002 3.140E+002 1
fiber 2.150E+002 -1.075E+002 3.140E+002 1
fiber 2.150E+002 0.000E+000 3.140E+002 1
fiber 2.150E+002 1.075E+002 3.140E+002 1
}
##NB300X600 
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
fiber -1.150E+002 2.650E+002 3.140E+002 1
fiber 0.000E+000 2.650E+002 3.140E+002 1
fiber 1.150E+002 2.650E+002 3.140E+002 1
fiber -1.150E+002 -2.650E+002 3.140E+002 1
fiber 0.000E+000 -2.650E+002 3.140E+002 1
fiber 1.150E+002 -2.650E+002 3.140E+002 1
}
section Aggregator 1001 201 Vy 301 Vz 401 T -section 1
section Aggregator 1002 202 Vy 302 Vz 402 T -section 2

##WALL1 

puts "transformation"
geomTransf Linear 1 1.000 0.000 0.000 
geomTransf Linear 2 1.000 0.000 0.000 
geomTransf Linear 3 1.000 0.000 0.000 
geomTransf Linear 4 1.000 0.000 0.000 
geomTransf Linear 5 1.000 0.000 0.000 
geomTransf Linear 6 1.000 0.000 0.000 
geomTransf Linear 7 1.000 0.000 0.000 
geomTransf Linear 8 1.000 0.000 0.000 
geomTransf Linear 9 1.000 0.000 0.000 
geomTransf Linear 10 0.000 0.000 1.000 
geomTransf Linear 11 0.000 0.000 1.000 
geomTransf Linear 12 0.000 0.000 1.000 
geomTransf Linear 13 0.000 0.000 1.000 
geomTransf Linear 14 0.000 0.000 1.000 
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
geomTransf Linear 28 1.000 0.000 0.000 
geomTransf Linear 29 1.000 0.000 0.000 
geomTransf Linear 30 1.000 0.000 0.000 
geomTransf Linear 31 0.000 0.000 1.000 
geomTransf Linear 32 0.000 0.000 1.000 
geomTransf Linear 33 0.000 0.000 1.000 
geomTransf Linear 34 0.000 0.000 1.000 
geomTransf Linear 35 0.000 0.000 1.000 
geomTransf Linear 36 0.000 0.000 1.000 
geomTransf Linear 37 0.000 0.000 1.000 
geomTransf Linear 38 0.000 0.000 1.000 
geomTransf Linear 39 0.000 0.000 1.000 
geomTransf Linear 40 0.000 0.000 1.000 
geomTransf Linear 41 0.000 0.000 1.000 
geomTransf Linear 42 0.000 0.000 1.000 
geomTransf Linear 43 1.000 0.000 0.000 
geomTransf Linear 44 1.000 0.000 0.000 
geomTransf Linear 45 1.000 0.000 0.000 
geomTransf Linear 46 1.000 0.000 0.000 
geomTransf Linear 47 1.000 0.000 0.000 
geomTransf Linear 48 1.000 0.000 0.000 
geomTransf Linear 49 1.000 0.000 0.000 
geomTransf Linear 50 1.000 0.000 0.000 
geomTransf Linear 51 1.000 0.000 0.000 
geomTransf Linear 52 0.000 0.000 1.000 
geomTransf Linear 53 0.000 0.000 1.000 
geomTransf Linear 54 0.000 0.000 1.000 
geomTransf Linear 55 0.000 0.000 1.000 
geomTransf Linear 56 0.000 0.000 1.000 
geomTransf Linear 57 0.000 0.000 1.000 
geomTransf Linear 58 0.000 0.000 1.000 
geomTransf Linear 59 0.000 0.000 1.000 
geomTransf Linear 60 0.000 0.000 1.000 
geomTransf Linear 61 0.000 0.000 1.000 
geomTransf Linear 62 0.000 0.000 1.000 
geomTransf Linear 63 0.000 0.000 1.000 
geomTransf Linear 64 1.000 0.000 0.000 
geomTransf Linear 65 1.000 0.000 0.000 
geomTransf Linear 66 1.000 0.000 0.000 
geomTransf Linear 67 1.000 0.000 0.000 
geomTransf Linear 68 1.000 0.000 0.000 
geomTransf Linear 69 1.000 0.000 0.000 
geomTransf Linear 70 1.000 0.000 0.000 
geomTransf Linear 71 1.000 0.000 0.000 
geomTransf Linear 72 0.000 0.000 1.000 
geomTransf Linear 73 0.000 0.000 1.000 
geomTransf Linear 74 0.000 0.000 1.000 
geomTransf Linear 75 0.000 0.000 1.000 
geomTransf Linear 76 0.000 0.000 1.000 
geomTransf Linear 77 0.000 0.000 1.000 
geomTransf Linear 78 0.000 0.000 1.000 
geomTransf Linear 79 0.000 0.000 1.000 
geomTransf Linear 80 0.000 0.000 1.000 
geomTransf Linear 81 0.000 0.000 1.000 
geomTransf Linear 82 0.000 0.000 1.000 
geomTransf Linear 83 0.000 0.000 1.000 
puts "element"
element nonlinearBeamColumn 1 1 2 3 1001 1
element nonlinearBeamColumn 2 3 4 3 1001 2
element nonlinearBeamColumn 3 5 6 3 1001 3
element nonlinearBeamColumn 4 7 8 3 1001 4
element nonlinearBeamColumn 5 9 10 3 1001 5
element nonlinearBeamColumn 6 11 12 3 1001 6
element nonlinearBeamColumn 7 13 14 3 1001 7
element nonlinearBeamColumn 8 15 16 3 1001 8
element nonlinearBeamColumn 9 17 18 3 1001 9
element nonlinearBeamColumn 10 16 18 3 1002 10
element nonlinearBeamColumn 11 18 2 3 1002 11
element nonlinearBeamColumn 12 12 14 3 1002 12
element nonlinearBeamColumn 13 14 4 3 1002 13
element nonlinearBeamColumn 14 10 8 3 1002 14
element nonlinearBeamColumn 15 8 6 3 1002 15
element nonlinearBeamColumn 16 16 12 3 1002 16
element nonlinearBeamColumn 17 12 10 3 1002 17
element nonlinearBeamColumn 18 18 14 3 1002 18
element nonlinearBeamColumn 19 14 8 3 1002 19
element nonlinearBeamColumn 20 2 4 3 1002 20
element nonlinearBeamColumn 21 4 6 3 1002 21
element nonlinearBeamColumn 22 19 1 3 1001 22
element nonlinearBeamColumn 23 20 3 3 1001 23
element nonlinearBeamColumn 24 21 5 3 1001 24
element nonlinearBeamColumn 25 22 7 3 1001 25
element nonlinearBeamColumn 26 23 9 3 1001 26
element nonlinearBeamColumn 27 24 11 3 1001 27
element nonlinearBeamColumn 28 25 13 3 1001 28
element nonlinearBeamColumn 29 26 15 3 1001 29
element nonlinearBeamColumn 30 27 17 3 1001 30
element nonlinearBeamColumn 31 15 17 3 1002 31
element nonlinearBeamColumn 32 17 1 3 1002 32
element nonlinearBeamColumn 33 11 13 3 1002 33
element nonlinearBeamColumn 34 13 3 3 1002 34
element nonlinearBeamColumn 35 9 7 3 1002 35
element nonlinearBeamColumn 36 7 5 3 1002 36
element nonlinearBeamColumn 37 15 11 3 1002 37
element nonlinearBeamColumn 38 11 9 3 1002 38
element nonlinearBeamColumn 39 17 13 3 1002 39
element nonlinearBeamColumn 40 13 7 3 1002 40
element nonlinearBeamColumn 41 1 3 3 1002 41
element nonlinearBeamColumn 42 3 5 3 1002 42
element nonlinearBeamColumn 43 28 19 3 1001 43
element nonlinearBeamColumn 44 29 20 3 1001 44
element nonlinearBeamColumn 45 30 21 3 1001 45
element nonlinearBeamColumn 46 31 22 3 1001 46
element nonlinearBeamColumn 47 32 23 3 1001 47
element nonlinearBeamColumn 48 33 24 3 1001 48
element nonlinearBeamColumn 49 34 25 3 1001 49
element nonlinearBeamColumn 50 35 26 3 1001 50
element nonlinearBeamColumn 51 36 27 3 1001 51
element nonlinearBeamColumn 52 26 27 3 1002 52
element nonlinearBeamColumn 53 27 19 3 1002 53
element nonlinearBeamColumn 54 24 25 3 1002 54
element nonlinearBeamColumn 55 25 20 3 1002 55
element nonlinearBeamColumn 56 23 22 3 1002 56
element nonlinearBeamColumn 57 22 21 3 1002 57
element nonlinearBeamColumn 58 26 24 3 1002 58
element nonlinearBeamColumn 59 24 23 3 1002 59
element nonlinearBeamColumn 60 27 25 3 1002 60
element nonlinearBeamColumn 61 25 22 3 1002 61
element nonlinearBeamColumn 62 19 20 3 1002 62
element nonlinearBeamColumn 63 20 21 3 1002 63
element nonlinearBeamColumn 64 37 28 3 1001 64
element nonlinearBeamColumn 65 38 29 3 1001 65
element nonlinearBeamColumn 66 39 30 3 1001 66
element nonlinearBeamColumn 67 40 31 3 1001 67
element nonlinearBeamColumn 68 41 32 3 1001 68
element nonlinearBeamColumn 69 42 33 3 1001 69
element nonlinearBeamColumn 70 43 34 3 1001 70
element nonlinearBeamColumn 71 44 36 3 1001 71
element nonlinearBeamColumn 72 35 36 3 1002 72
element nonlinearBeamColumn 73 36 28 3 1002 73
element nonlinearBeamColumn 74 33 34 3 1002 74
element nonlinearBeamColumn 75 34 29 3 1002 75
element nonlinearBeamColumn 76 32 31 3 1002 76
element nonlinearBeamColumn 77 31 30 3 1002 77
element nonlinearBeamColumn 78 35 33 3 1002 78
element nonlinearBeamColumn 79 33 32 3 1002 79
element nonlinearBeamColumn 80 36 34 3 1002 80
element nonlinearBeamColumn 81 34 31 3 1002 81
element nonlinearBeamColumn 82 28 29 3 1002 82
element nonlinearBeamColumn 83 29 30 3 1002 83
puts "shell element"
puts "SOLID element"
puts "recorder"
recorder Node -file node35.out -time -node 35 -dof 1 2 3 disp
puts "loading"
## Load Case = DL
pattern Plain 1 Linear {
load 35 0.000E+000 0.000E+000 3.000E+005 0.000E+000 0.000E+000 0.000E+000
eleLoad -ele 11 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 11 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 18 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 18 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 13 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 13 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 20 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 20 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 13 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 13 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 19 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 19 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 15 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 15 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 21 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 21 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 12 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 12 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 17 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 17 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 14 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 14 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 19 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 19 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 10 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 10 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 16 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 16 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 12 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 12 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 18 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 18 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 32 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 32 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 39 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 39 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 34 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 34 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 41 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 41 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 34 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 34 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 40 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 40 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 36 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 36 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 42 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 42 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 33 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 33 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 38 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 38 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 35 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 35 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 40 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 40 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 31 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 31 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 37 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 37 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 33 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 33 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 39 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 39 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 53 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 53 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 60 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 60 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 55 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 55 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 62 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 62 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 55 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 55 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 61 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 61 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 57 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 57 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 63 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 63 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 54 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 54 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 59 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 59 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 56 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 56 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 61 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 61 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 52 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 52 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 58 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 58 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 54 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 54 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 60 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 60 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 73 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 73 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 80 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 80 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 75 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 75 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 82 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 82 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 75 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 75 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 81 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 81 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 77 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 77 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 83 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 83 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 74 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 74 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 79 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 79 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 76 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 76 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 81 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 81 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 72 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 72 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 78 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 78 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 74 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 74 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 80 -type -beamUniform 0 -6.375E+000 0
eleLoad -ele 80 -type -beamUniform 0 -6.375E+000 0
}
puts "analysis"
constraints Plain
numberer Plain
system BandGeneral
test EnergyIncr 1.0e-6 200
algorithm Newton
integrator LoadControl 0.1
analysis Static
analyze 10


loadConst  -time 0
pattern Plain 2 Linear {
load 35 0.000E+000 0.000E+000 -3.000E+005 0.000E+000 0.000E+000 0.000E+000
}
puts "analysis"
constraints Plain
numberer Plain
system BandGeneral
test EnergyIncr 1.0e-6 200
algorithm Newton
integrator LoadControl 0.01
analysis Static
analyze 100


