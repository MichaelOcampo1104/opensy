wipe
puts "System"
model basic -ndm 3 -ndf 6
puts "restraint"
node 1 0.000E+000 0.000E+000 0.000E+000
node 2 0.000E+000 0.000E+000 3.000E+003
node 3 0.000E+000 0.000E+000 6.000E+003
node 4 0.000E+000 0.000E+000 9.000E+003
node 5 0.000E+000 0.000E+000 1.200E+004
node 6 6.000E+003 0.000E+000 1.200E+004
node 7 6.000E+003 0.000E+000 0.000E+000
node 8 6.000E+003 0.000E+000 3.000E+003
node 9 6.000E+003 0.000E+000 6.000E+003
node 10 6.000E+003 0.000E+000 9.000E+003
node 11 1.200E+004 0.000E+000 1.200E+004
node 12 1.200E+004 0.000E+000 0.000E+000
node 13 1.200E+004 0.000E+000 3.000E+003
node 14 1.200E+004 0.000E+000 6.000E+003
node 15 1.200E+004 0.000E+000 9.000E+003
node 16 1.800E+004 0.000E+000 1.200E+004
node 17 1.800E+004 0.000E+000 0.000E+000
node 18 1.800E+004 0.000E+000 3.000E+003
node 19 1.800E+004 0.000E+000 6.000E+003
node 20 1.800E+004 0.000E+000 9.000E+003
node 21 0.000E+000 6.000E+003 0.000E+000
node 22 0.000E+000 6.000E+003 3.000E+003
node 23 0.000E+000 6.000E+003 6.000E+003
node 24 0.000E+000 6.000E+003 9.000E+003
node 25 0.000E+000 6.000E+003 1.200E+004
node 26 6.000E+003 6.000E+003 1.200E+004
node 27 6.000E+003 6.000E+003 0.000E+000
node 28 6.000E+003 6.000E+003 3.000E+003
node 29 6.000E+003 6.000E+003 6.000E+003
node 30 6.000E+003 6.000E+003 9.000E+003
node 31 1.200E+004 6.000E+003 1.200E+004
node 32 1.200E+004 6.000E+003 0.000E+000
node 33 1.200E+004 6.000E+003 3.000E+003
node 34 1.200E+004 6.000E+003 6.000E+003
node 35 1.200E+004 6.000E+003 9.000E+003
node 36 1.800E+004 6.000E+003 1.200E+004
node 37 1.800E+004 6.000E+003 0.000E+000
node 38 1.800E+004 6.000E+003 3.000E+003
node 39 1.800E+004 6.000E+003 6.000E+003
node 40 1.800E+004 6.000E+003 9.000E+003
node 41 7.000E+003 6.000E+003 9.500E+003
node 42 8.000E+003 6.000E+003 1.000E+004
node 43 9.000E+003 6.000E+003 1.050E+004
node 44 1.000E+004 6.000E+003 1.100E+004
node 45 1.100E+004 6.000E+003 1.150E+004
node 46 7.000E+003 6.000E+003 6.500E+003
node 47 8.000E+003 6.000E+003 7.000E+003
node 48 9.000E+003 6.000E+003 7.500E+003
node 49 1.000E+004 6.000E+003 8.000E+003
node 50 1.100E+004 6.000E+003 8.500E+003
node 51 7.000E+003 6.000E+003 3.500E+003
node 52 8.000E+003 6.000E+003 4.000E+003
node 53 9.000E+003 6.000E+003 4.500E+003
node 54 1.000E+004 6.000E+003 5.000E+003
node 55 1.100E+004 6.000E+003 5.500E+003
node 56 7.000E+003 6.000E+003 5.000E+002
node 57 8.000E+003 6.000E+003 1.000E+003
node 58 9.000E+003 6.000E+003 1.500E+003
node 59 1.000E+004 6.000E+003 2.000E+003
node 60 1.100E+004 6.000E+003 2.500E+003
node 61 7.000E+003 0.000E+000 9.500E+003
node 62 8.000E+003 0.000E+000 1.000E+004
node 63 9.000E+003 0.000E+000 1.050E+004
node 64 1.000E+004 0.000E+000 1.100E+004
node 65 1.100E+004 0.000E+000 1.150E+004
node 66 7.000E+003 0.000E+000 6.500E+003
node 67 8.000E+003 0.000E+000 7.000E+003
node 68 9.000E+003 0.000E+000 7.500E+003
node 69 1.000E+004 0.000E+000 8.000E+003
node 70 1.100E+004 0.000E+000 8.500E+003
node 71 7.000E+003 0.000E+000 3.500E+003
node 72 8.000E+003 0.000E+000 4.000E+003
node 73 9.000E+003 0.000E+000 4.500E+003
node 74 1.000E+004 0.000E+000 5.000E+003
node 75 1.100E+004 0.000E+000 5.500E+003
node 76 7.000E+003 0.000E+000 5.000E+002
node 77 8.000E+003 0.000E+000 1.000E+003
node 78 9.000E+003 0.000E+000 1.500E+003
node 79 1.000E+004 0.000E+000 2.000E+003
node 80 1.100E+004 0.000E+000 2.500E+003
puts "rigidDiaphragm"
puts "mass"
mass 1 5.876E-001 5.876E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 2 2.654E+000 2.654E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 3 2.654E+000 2.654E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 4 2.654E+000 2.654E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 5 2.067E+000 2.067E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 6 2.806E+000 2.806E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 7 6.891E-001 6.891E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 8 3.495E+000 3.495E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 9 3.495E+000 3.495E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 10 3.495E+000 3.495E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 11 2.908E+000 2.908E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 12 5.876E-001 5.876E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 13 3.495E+000 3.495E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 14 3.495E+000 3.495E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 15 3.495E+000 3.495E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 16 2.067E+000 2.067E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 17 5.876E-001 5.876E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 18 2.654E+000 2.654E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 19 2.654E+000 2.654E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 20 2.654E+000 2.654E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 21 5.876E-001 5.876E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 22 2.654E+000 2.654E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 23 2.654E+000 2.654E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 24 2.654E+000 2.654E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 25 2.067E+000 2.067E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 26 2.806E+000 2.806E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 27 6.891E-001 6.891E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 28 3.495E+000 3.495E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 29 3.495E+000 3.495E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 30 3.495E+000 3.495E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 31 2.908E+000 2.908E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 32 5.876E-001 5.876E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 33 3.495E+000 3.495E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 34 3.495E+000 3.495E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 35 3.495E+000 3.495E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 36 2.067E+000 2.067E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 37 5.876E-001 5.876E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 38 2.654E+000 2.654E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 39 2.654E+000 2.654E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 40 2.654E+000 2.654E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 41 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 42 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 43 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 44 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 45 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 46 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 47 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 48 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 49 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 50 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 51 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 52 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 53 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 54 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 55 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 56 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 57 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 58 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 59 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 60 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 61 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 62 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 63 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 64 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 65 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 66 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 67 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 68 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 69 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 70 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 71 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 72 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 73 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 74 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 75 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 76 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 77 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 78 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 79 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
mass 80 2.030E-001 2.030E-001 0.000E+000 0.000E+000 0.000E+000 0.000E+000
puts "node"
fix 1 1 1 1 1 1 1;
fix 7 1 1 1 1 1 1;
fix 12 1 1 1 1 1 1;
fix 17 1 1 1 1 1 1;
fix 21 1 1 1 1 1 1;
fix 27 1 1 1 1 1 1;
fix 32 1 1 1 1 1 1;
fix 37 1 1 1 1 1 1;
puts "Equal DOF"
puts "material"
uniaxialMaterial Elastic 1 1.999E+005
uniaxialMaterial Elastic 2 2.482E+004
##uniaxialMaterial Elastic 3 1.999E+005


uniaxialMaterial Steel01 3 295 206000 0.05


uniaxialMaterial Elastic 201 4.614E+008
uniaxialMaterial Elastic 301 1.794E+009
uniaxialMaterial Elastic 401 9.058E+011
uniaxialMaterial Elastic 202 1.122E+009
uniaxialMaterial Elastic 302 2.243E+009
uniaxialMaterial Elastic 402 1.649E+012
uniaxialMaterial Elastic 203 5.127E+008
uniaxialMaterial Elastic 303 1.025E+009
uniaxialMaterial Elastic 403 2.461E+011

##DH300X300X35X12 
section Fiber 1 {
fiber -1.200E+002 -1.325E+002 2.100E+003 1
fiber -6.000E+001 -1.325E+002 2.100E+003 1
fiber 0.000E+000 -1.325E+002 2.100E+003 1
fiber 6.000E+001 -1.325E+002 2.100E+003 1
fiber 1.200E+002 -1.325E+002 2.100E+003 1
fiber -1.200E+002 1.325E+002 2.100E+003 1
fiber -6.000E+001 1.325E+002 2.100E+003 1
fiber 0.000E+000 1.325E+002 2.100E+003 1
fiber 6.000E+001 1.325E+002 2.100E+003 1
fiber 1.200E+002 1.325E+002 2.100E+003 1
fiber 0.000E+000 -9.200E+001 5.520E+002 1
fiber 0.000E+000 -4.600E+001 5.520E+002 1
fiber 0.000E+000 0.000E+000 5.520E+002 1
fiber 0.000E+000 4.600E+001 5.520E+002 1
fiber 0.000E+000 9.200E+001 5.520E+002 1
}
##DH300X300X35X35 
section Fiber 2 {
fiber -1.200E+002 -1.325E+002 2.100E+003 1
fiber -6.000E+001 -1.325E+002 2.100E+003 1
fiber 0.000E+000 -1.325E+002 2.100E+003 1
fiber 6.000E+001 -1.325E+002 2.100E+003 1
fiber 1.200E+002 -1.325E+002 2.100E+003 1
fiber -1.200E+002 1.325E+002 2.100E+003 1
fiber -6.000E+001 1.325E+002 2.100E+003 1
fiber 0.000E+000 1.325E+002 2.100E+003 1
fiber 6.000E+001 1.325E+002 2.100E+003 1
fiber 1.200E+002 1.325E+002 2.100E+003 1
fiber 0.000E+000 -9.200E+001 1.610E+003 1
fiber 0.000E+000 -4.600E+001 1.610E+003 1
fiber 0.000E+000 0.000E+000 1.610E+003 1
fiber 0.000E+000 4.600E+001 1.610E+003 1
fiber 0.000E+000 9.200E+001 1.610E+003 1
}
##DB400X400X20 
section Fiber 3 {
fiber -1.600E+002 -1.900E+002 1.600E+003 3
fiber -8.000E+001 -1.900E+002 1.600E+003 3
fiber 0.000E+000 -1.900E+002 1.600E+003 3
fiber 8.000E+001 -1.900E+002 1.600E+003 3
fiber 1.600E+002 -1.900E+002 1.600E+003 3
fiber -1.600E+002 1.900E+002 1.600E+003 3
fiber -8.000E+001 1.900E+002 1.600E+003 3
fiber 0.000E+000 1.900E+002 1.600E+003 3
fiber 8.000E+001 1.900E+002 1.600E+003 3
fiber 1.600E+002 1.900E+002 1.600E+003 3
fiber 0.000E+000 -1.440E+002 1.440E+003 3
fiber 0.000E+000 -7.200E+001 1.440E+003 3
fiber 0.000E+000 0.000E+000 1.440E+003 3
fiber 0.000E+000 7.200E+001 1.440E+003 3
fiber 0.000E+000 1.440E+002 1.440E+003 3
}

section Aggregator 1001 201 Vy 301 Vz 401 T -section 1
section Aggregator 1002 202 Vy 302 Vz 402 T -section 2
section Aggregator 1003 203 Vy 303 Vz 403 T -section 3

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
geomTransf Linear 14 -0.447 0.000 0.894 
geomTransf Linear 15 -0.447 0.000 0.894 
geomTransf Linear 16 -0.447 0.000 0.894 
geomTransf Linear 17 -0.447 0.000 0.894 
geomTransf Linear 18 -0.447 0.000 0.894 
geomTransf Linear 19 -0.447 0.000 0.894 
geomTransf Linear 20 1.000 0.000 0.000 
geomTransf Linear 21 1.000 0.000 0.000 
geomTransf Linear 22 0.000 0.000 1.000 
geomTransf Linear 23 0.000 0.000 1.000 
geomTransf Linear 24 0.000 0.000 1.000 
geomTransf Linear 25 -0.447 0.000 0.894 
geomTransf Linear 26 -0.447 0.000 0.894 
geomTransf Linear 27 -0.447 0.000 0.894 
geomTransf Linear 28 -0.447 0.000 0.894 
geomTransf Linear 29 -0.447 0.000 0.894 
geomTransf Linear 30 -0.447 0.000 0.894 
geomTransf Linear 31 1.000 0.000 0.000 
geomTransf Linear 32 1.000 0.000 0.000 
geomTransf Linear 33 1.000 0.000 0.000 
geomTransf Linear 34 1.000 0.000 0.000 
geomTransf Linear 35 1.000 0.000 0.000 
geomTransf Linear 36 1.000 0.000 0.000 
geomTransf Linear 37 0.000 0.000 1.000 
geomTransf Linear 38 0.000 0.000 1.000 
geomTransf Linear 39 0.000 0.000 1.000 
geomTransf Linear 40 0.000 0.000 1.000 
geomTransf Linear 41 0.000 0.000 1.000 
geomTransf Linear 42 0.000 0.000 1.000 
geomTransf Linear 43 0.000 0.000 1.000 
geomTransf Linear 44 -0.447 0.000 0.894 
geomTransf Linear 45 -0.447 0.000 0.894 
geomTransf Linear 46 -0.447 0.000 0.894 
geomTransf Linear 47 -0.447 0.000 0.894 
geomTransf Linear 48 -0.447 0.000 0.894 
geomTransf Linear 49 -0.447 0.000 0.894 
geomTransf Linear 50 1.000 0.000 0.000 
geomTransf Linear 51 1.000 0.000 0.000 
geomTransf Linear 52 0.000 0.000 1.000 
geomTransf Linear 53 0.000 0.000 1.000 
geomTransf Linear 54 0.000 0.000 1.000 
geomTransf Linear 55 -0.447 0.000 0.894 
geomTransf Linear 56 -0.447 0.000 0.894 
geomTransf Linear 57 -0.447 0.000 0.894 
geomTransf Linear 58 -0.447 0.000 0.894 
geomTransf Linear 59 -0.447 0.000 0.894 
geomTransf Linear 60 -0.447 0.000 0.894 
geomTransf Linear 61 1.000 0.000 0.000 
geomTransf Linear 62 1.000 0.000 0.000 
geomTransf Linear 63 1.000 0.000 0.000 
geomTransf Linear 64 1.000 0.000 0.000 
geomTransf Linear 65 1.000 0.000 0.000 
geomTransf Linear 66 1.000 0.000 0.000 
geomTransf Linear 67 0.000 0.000 1.000 
geomTransf Linear 68 0.000 0.000 1.000 
geomTransf Linear 69 0.000 0.000 1.000 
geomTransf Linear 70 0.000 0.000 1.000 
geomTransf Linear 71 0.000 0.000 1.000 
geomTransf Linear 72 0.000 0.000 1.000 
geomTransf Linear 73 0.000 0.000 1.000 
geomTransf Linear 74 -0.447 0.000 0.894 
geomTransf Linear 75 -0.447 0.000 0.894 
geomTransf Linear 76 -0.447 0.000 0.894 
geomTransf Linear 77 -0.447 0.000 0.894 
geomTransf Linear 78 -0.447 0.000 0.894 
geomTransf Linear 79 -0.447 0.000 0.894 
geomTransf Linear 80 1.000 0.000 0.000 
geomTransf Linear 81 1.000 0.000 0.000 
geomTransf Linear 82 0.000 0.000 1.000 
geomTransf Linear 83 0.000 0.000 1.000 
geomTransf Linear 84 0.000 0.000 1.000 
geomTransf Linear 85 -0.447 0.000 0.894 
geomTransf Linear 86 -0.447 0.000 0.894 
geomTransf Linear 87 -0.447 0.000 0.894 
geomTransf Linear 88 -0.447 0.000 0.894 
geomTransf Linear 89 -0.447 0.000 0.894 
geomTransf Linear 90 -0.447 0.000 0.894 
geomTransf Linear 91 1.000 0.000 0.000 
geomTransf Linear 92 1.000 0.000 0.000 
geomTransf Linear 93 1.000 0.000 0.000 
geomTransf Linear 94 1.000 0.000 0.000 
geomTransf Linear 95 1.000 0.000 0.000 
geomTransf Linear 96 1.000 0.000 0.000 
geomTransf Linear 97 1.000 0.000 0.000 
geomTransf Linear 98 1.000 0.000 0.000 
geomTransf Linear 99 0.000 0.000 1.000 
geomTransf Linear 100 0.000 0.000 1.000 
geomTransf Linear 101 0.000 0.000 1.000 
geomTransf Linear 102 0.000 0.000 1.000 
geomTransf Linear 103 0.000 0.000 1.000 
geomTransf Linear 104 0.000 0.000 1.000 
geomTransf Linear 105 0.000 0.000 1.000 
geomTransf Linear 106 -0.447 0.000 0.894 
geomTransf Linear 107 -0.447 0.000 0.894 
geomTransf Linear 108 -0.447 0.000 0.894 
geomTransf Linear 109 -0.447 0.000 0.894 
geomTransf Linear 110 -0.447 0.000 0.894 
geomTransf Linear 111 -0.447 0.000 0.894 
geomTransf Linear 112 0.000 0.000 1.000 
geomTransf Linear 113 0.000 0.000 1.000 
geomTransf Linear 114 0.000 0.000 1.000 
geomTransf Linear 115 -0.447 0.000 0.894 
geomTransf Linear 116 -0.447 0.000 0.894 
geomTransf Linear 117 -0.447 0.000 0.894 
geomTransf Linear 118 -0.447 0.000 0.894 
geomTransf Linear 119 -0.447 0.000 0.894 
geomTransf Linear 120 -0.447 0.000 0.894 
puts "element"
element dispBeamColumn 1 4 5 3 1002 1
element dispBeamColumn 2 10 6 3 1002 2
element dispBeamColumn 3 15 11 3 1002 3
element dispBeamColumn 4 20 16 3 1002 4
element dispBeamColumn 5 24 25 3 1002 5
element dispBeamColumn 6 40 36 3 1002 6
element dispBeamColumn 7 5 25 3 1001 7
element dispBeamColumn 8 6 26 3 1001 8
element dispBeamColumn 9 11 31 3 1001 9
element dispBeamColumn 10 16 36 3 1001 10
element dispBeamColumn 11 25 26 3 1001 11
element dispBeamColumn 12 26 31 3 1001 12
element dispBeamColumn 13 31 36 3 1001 13
element dispBeamColumn 14 30 41 3 1003 14
element dispBeamColumn 15 41 42 3 1003 15
element dispBeamColumn 16 42 43 3 1003 16
element dispBeamColumn 17 43 44 3 1003 17
element dispBeamColumn 18 44 45 3 1003 18
element dispBeamColumn 19 45 31 3 1003 19
element dispBeamColumn 20 35 31 3 1002 20
element dispBeamColumn 21 30 26 3 1002 21
element dispBeamColumn 22 5 6 3 1001 22
element dispBeamColumn 23 6 11 3 1001 23
element dispBeamColumn 24 11 16 3 1001 24
element dispBeamColumn 25 10 61 3 1003 25
element dispBeamColumn 26 61 62 3 1003 26
element dispBeamColumn 27 62 63 3 1003 27
element dispBeamColumn 28 63 64 3 1003 28
element dispBeamColumn 29 64 65 3 1003 29
element dispBeamColumn 30 65 11 3 1003 30
element dispBeamColumn 31 3 4 3 1002 31
element dispBeamColumn 32 9 10 3 1002 32
element dispBeamColumn 33 14 15 3 1002 33
element dispBeamColumn 34 19 20 3 1002 34
element dispBeamColumn 35 23 24 3 1002 35
element dispBeamColumn 36 39 40 3 1002 36
element dispBeamColumn 37 4 24 3 1001 37
element dispBeamColumn 38 10 30 3 1001 38
element dispBeamColumn 39 15 35 3 1001 39
element dispBeamColumn 40 20 40 3 1001 40
element dispBeamColumn 41 24 30 3 1001 41
element dispBeamColumn 42 30 35 3 1001 42
element dispBeamColumn 43 35 40 3 1001 43
element dispBeamColumn 44 29 46 3 1003 44
element dispBeamColumn 45 46 47 3 1003 45
element dispBeamColumn 46 47 48 3 1003 46
element dispBeamColumn 47 48 49 3 1003 47
element dispBeamColumn 48 49 50 3 1003 48
element dispBeamColumn 49 50 35 3 1003 49
element dispBeamColumn 50 34 35 3 1002 50
element dispBeamColumn 51 29 30 3 1002 51
element dispBeamColumn 52 4 10 3 1001 52
element dispBeamColumn 53 10 15 3 1001 53
element dispBeamColumn 54 15 20 3 1001 54
element dispBeamColumn 55 9 66 3 1003 55
element dispBeamColumn 56 66 67 3 1003 56
element dispBeamColumn 57 67 68 3 1003 57
element dispBeamColumn 58 68 69 3 1003 58
element dispBeamColumn 59 69 70 3 1003 59
element dispBeamColumn 60 70 15 3 1003 60
element dispBeamColumn 61 2 3 3 1002 61
element dispBeamColumn 62 8 9 3 1002 62
element dispBeamColumn 63 13 14 3 1002 63
element dispBeamColumn 64 18 19 3 1002 64
element dispBeamColumn 65 22 23 3 1002 65
element dispBeamColumn 66 38 39 3 1002 66
element dispBeamColumn 67 3 23 3 1001 67
element dispBeamColumn 68 9 29 3 1001 68
element dispBeamColumn 69 14 34 3 1001 69
element dispBeamColumn 70 19 39 3 1001 70
element dispBeamColumn 71 23 29 3 1001 71
element dispBeamColumn 72 29 34 3 1001 72
element dispBeamColumn 73 34 39 3 1001 73
element dispBeamColumn 74 28 51 3 1003 74
element dispBeamColumn 75 51 52 3 1003 75
element dispBeamColumn 76 52 53 3 1003 76
element dispBeamColumn 77 53 54 3 1003 77
element dispBeamColumn 78 54 55 3 1003 78
element dispBeamColumn 79 55 34 3 1003 79
element dispBeamColumn 80 33 34 3 1002 80
element dispBeamColumn 81 28 29 3 1002 81
element dispBeamColumn 82 3 9 3 1001 82
element dispBeamColumn 83 9 14 3 1001 83
element dispBeamColumn 84 14 19 3 1001 84
element dispBeamColumn 85 8 71 3 1003 85
element dispBeamColumn 86 71 72 3 1003 86
element dispBeamColumn 87 72 73 3 1003 87
element dispBeamColumn 88 73 74 3 1003 88
element dispBeamColumn 89 74 75 3 1003 89
element dispBeamColumn 90 75 14 3 1003 90
element dispBeamColumn 91 1 2 3 1002 91
element dispBeamColumn 92 7 8 3 1002 92
element dispBeamColumn 93 12 13 3 1002 93
element dispBeamColumn 94 17 18 3 1002 94
element dispBeamColumn 95 21 22 3 1002 95
element dispBeamColumn 96 27 28 3 1002 96
element dispBeamColumn 97 32 33 3 1002 97
element dispBeamColumn 98 37 38 3 1002 98
element dispBeamColumn 99 2 22 3 1001 99
element dispBeamColumn 100 8 28 3 1001 100
element dispBeamColumn 101 13 33 3 1001 101
element dispBeamColumn 102 18 38 3 1001 102
element dispBeamColumn 103 22 28 3 1001 103
element dispBeamColumn 104 28 33 3 1001 104
element dispBeamColumn 105 33 38 3 1001 105
element dispBeamColumn 106 27 56 3 1003 106
element dispBeamColumn 107 56 57 3 1003 107
element dispBeamColumn 108 57 58 3 1003 108
element dispBeamColumn 109 58 59 3 1003 109
element dispBeamColumn 110 59 60 3 1003 110
element dispBeamColumn 111 60 33 3 1003 111
element dispBeamColumn 112 2 8 3 1001 112
element dispBeamColumn 113 8 13 3 1001 113
element dispBeamColumn 114 13 18 3 1001 114
element dispBeamColumn 115 7 76 3 1003 115
element dispBeamColumn 116 76 77 3 1003 116
element dispBeamColumn 117 77 78 3 1003 117
element dispBeamColumn 118 78 79 3 1003 118
element dispBeamColumn 119 79 80 3 1003 119
element dispBeamColumn 120 80 13 3 1003 120
puts "shell element"
puts "SOLID element"
puts "recorder"

puts "gravity"
## Load Case = DEAD
pattern Plain 1 Linear {
eleLoad -ele 7 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 7 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 7 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 8 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 8 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 8 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 9 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 9 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 9 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 10 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 10 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 10 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 37 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 37 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 37 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 38 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 38 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 38 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 39 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 39 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 39 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 40 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 40 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 40 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 67 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 67 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 67 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 68 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 68 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 68 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 69 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 69 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 69 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 70 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 70 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 70 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 99 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 99 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 99 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 100 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 100 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 100 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 101 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 101 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 101 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 102 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 102 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 102 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 11 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 11 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 11 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 12 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 12 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 12 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 13 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 13 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 13 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 103 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 103 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 103 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 104 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 104 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 104 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 105 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 105 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 105 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 71 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 71 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 71 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 72 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 72 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 72 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 73 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 73 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 73 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 41 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 41 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 41 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 42 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 42 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 42 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 43 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 43 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 43 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 22 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 22 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 22 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 23 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 23 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 23 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 24 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 24 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 24 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 112 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 112 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 112 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 113 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 113 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 113 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 114 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 114 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 114 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 82 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 82 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 82 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 83 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 83 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 83 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 84 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 84 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 84 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 52 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 52 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 52 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 53 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 53 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 53 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 54 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 54 -type -beamUniform 0 -4.000E+000 0
eleLoad -ele 54 -type -beamUniform 0 -4.000E+000 0
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

loadConst -time 0.0

recorder Node -file node0.out -time -nodeRange 1 80 -dof 1 2 3 disp
recorder Node -file node25.out -time -node 25 -dof 1 2 3 disp

recorder Element -file ele85a.out -time -ele 85 localForce
recorder Element -file ele85b.out -time -ele 85 section 1 deformation


puts "pushover"
## Load Case = PUSH
pattern Plain 3 Linear {
load 5 4.000E+005 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
load 25 4.000E+005 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
load 4 3.000E+005 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
load 24 3.000E+005 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
load 3 2.000E+005 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
load 23 2.000E+005 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
load 2 1.000E+005 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
load 22 1.000E+005 0.000E+000 0.000E+000 0.000E+000 0.000E+000 0.000E+000
}
puts "analysis"
constraints Plain
numberer Plain
system BandGeneral
test EnergyIncr 1.0e-6 200
algorithm Newton
integrator DisplacementControl 25 1 4
analysis Static
analyze 50

integrator DisplacementControl 25 1 -8
analyze 50
integrator DisplacementControl 25 1 12
analyze 50
integrator DisplacementControl 25 1 -16
analyze 50