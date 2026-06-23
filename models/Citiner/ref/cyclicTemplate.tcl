#########################################################################
#                                                                       #
#                           Cyclic Loading                              #
#                           (Units: kN, m)                              #
#                                                                       #
#########################################################################
wipe;
model basic -ndm 2 -ndf 3;

## Constants ##
set pi   3.14;

## Section and Material Properties ##
set B      0.35;
set H      0.25;
set L      2.01;
set db     0.02;
set nb     8;
set fy     520000;
set PHL    0.2775;   ## Determined from the AdaBoost model
set dbv    0.01;
set Es     210000000;
set k      0.02;
set Ecc    30000000;
set fpc    -90000;
set epsc0  -0.003;
set fpcu   -60000;
set epscu  -0.02;

## Computed Section Properties ## 
set ast    [expr 2*$dbv+$db/2];
set bt1     [expr $B-2*$ast];
set bt2     [expr $H-2*$ast];

set As     [expr $pi*$db*$db/4];

set A [expr $B*$H];                                 # Cross-sectional area
set Iz [expr 1./12.*$B*pow($H,3)];                  # Moment of inertia
set Ec [expr (($A-$nb*$As)*$Ecc+$nb*$As*$Es)/$A];   # Equivalent concrete elastic modulus

## System Geometry ##
node 1 0.0 0.0;
node 2 0.0 $L;
fix  1 1 1 1;

## Material Models ##
uniaxialMaterial Steel02 1 $fy $Es $k 18 0.925 0.15;
uniaxialMaterial Concrete02 2 $fpc $epsc0 $fpcu $epscu 0.1 9e3 10e6

## Fiber Column Section ##
section Fiber 1 {
patch rect 2  20   20   [expr -$bt2/2] [expr -$bt1/2] [expr  $bt2/2]  [expr  $bt1/2] 

patch rect 2   1   12   [expr  -$H/2] [expr  -$B/2] [expr  -$bt2/2] [expr   $B/2] 
patch rect 2   1   12  [expr   $H/2] [expr   $B/2] [expr   $bt2/2] [expr  -$B/2] 
patch rect 2  12    1   [expr -$bt2/2] [expr  -$B/2] [expr   $bt2/2] [expr -$bt1/2] 
patch rect 2  12    1   [expr -$bt2/2] [expr  $bt1/2] [expr   $bt2/2] [expr   $B/2] 

fiber      [expr -$bt2/2]   [expr -$bt1/2]   $As 1
fiber      [expr -$bt2/2]   [expr  $bt1/2]   $As 1
fiber      [expr -$bt2/2]   0.   $As 1

fiber      [expr $bt2/2]   [expr -$bt1/2]   $As 1
fiber      [expr $bt2/2]   [expr  $bt1/2]   $As 1
fiber      [expr $bt2/2]   0.   $As 1

fiber      0.  [expr $bt1/2]    $As 1
fiber      0.  [expr -$bt1/2]    $As 1
}

## Column Element ##
geomTransf PDelta 2;
element beamWithHinges 1 1 2 1 $PHL 1 $PHL $Ec $A $Iz 2;

## Vertical Loading ##

pattern Plain 1 Linear {
load 2 0 [expr $A*$fpc*0.32] 0
}
constraints Plain
numberer    RCM                                         
system      BandGeneral                                     
test        EnergyIncr 1.0e-2 20
algorithm   Newton                                      
integrator  LoadControl 0.1;                              
analysis    Static                                          
analyze 10;
puts "-----------------------------------------"                                              
puts "      Vertical loading completed..."
loadConst -time 0.0;

## Horizontal Loading ##

pattern Plain 2 Linear {
load 2 1 0 0
}

recorder Node    -file NodeDisp.out     -time -node 2 -dof     1 disp;

constraints Plain
numberer    RCM
test        EnergyIncr 1.0e-3 200
algorithm Newton
system      BandGeneral
analysis    Static

set Nstep 100;
puts "-------Horizontal loading - Step 1-------"
set Dmax -2.5e-3
set D_i [expr ($Dmax/$Nstep)]
integrator  DisplacementControl 2 1 [expr $D_i] 
analyze $Nstep

puts "-------Horizontal loading - Step 2-------"
set Dmax 5.e-3
set D_i [expr ($Dmax/$Nstep)]
integrator  DisplacementControl 2 1 [expr $D_i]
analyze $Nstep

puts "-------Horizontal loading - Step 3-------"
set Dmax -7.5e-3
set D_i [expr ($Dmax/$Nstep)]
integrator  DisplacementControl 2 1 [expr $D_i]
analyze $Nstep

puts "-------Horizontal loading - Step 4-------"
set Dmax 10.e-3
set D_i [expr ($Dmax/$Nstep)]
integrator  DisplacementControl 2 1 [expr $D_i]
analyze $Nstep

puts "-------Horizontal loading - Step 5-------"
set Dmax -12.5e-3
set D_i [expr ($Dmax/$Nstep)]
integrator  DisplacementControl 2 1 [expr $D_i]
analyze $Nstep

puts "-------Horizontal loading - Step 6-------"
set Dmax 15.e-3
set D_i [expr ($Dmax/$Nstep)]
integrator  DisplacementControl 2 1 [expr $D_i]
analyze $Nstep

puts "-------Horizontal loading - Step 7-------"
set Dmax -17.5e-3
set D_i [expr ($Dmax/$Nstep)]
integrator  DisplacementControl 2 1 [expr $D_i]
analyze $Nstep

puts "-------Horizontal loading - Step 8-------"
set Dmax 20.e-3
set D_i [expr ($Dmax/$Nstep)]
integrator  DisplacementControl 2 1 [expr $D_i]
analyze $Nstep

puts "-------Horizontal loading - Step 9-------"
set Dmax -25.e-3
set D_i [expr ($Dmax/$Nstep)]
integrator  DisplacementControl 2 1 [expr $D_i]
analyze $Nstep

puts "------ Horizontal loading - Step 10------"
set Dmax 30.e-3
set D_i [expr ($Dmax/$Nstep)]
integrator  DisplacementControl 2 1 [expr $D_i]
analyze $Nstep

puts "-------Horizontal loading - Step 11------"
set Dmax -40.e-3
set D_i [expr ($Dmax/$Nstep)]
integrator  DisplacementControl 2 1 [expr $D_i]
analyze $Nstep

puts "-------Horizontal loading - Step 12------"
set Dmax 50.e-3
set D_i [expr ($Dmax/$Nstep)]
integrator  DisplacementControl 2 1 [expr $D_i]
analyze $Nstep

puts "-------Horizontal loading - Step 13------"
set Dmax -60.e-3
set D_i [expr ($Dmax/$Nstep)]
integrator  DisplacementControl 2 1 [expr $D_i]
analyze $Nstep

puts "-------Horizontal loading - Step 14------"
set Dmax 70.e-3
set D_i [expr ($Dmax/$Nstep)]
integrator  DisplacementControl 2 1 [expr $D_i]
analyze $Nstep

puts "-------Horizontal loading - Step 15------"
set Dmax -85.e-3
set D_i [expr ($Dmax/$Nstep)]
integrator  DisplacementControl 2 1 [expr $D_i]
analyze $Nstep

puts "-------Horizontal loading - Step 16------"
set Dmax 100.e-3
set D_i [expr ($Dmax/$Nstep)]
integrator  DisplacementControl 2 1 [expr $D_i]
analyze $Nstep

puts "-------Horizontal loading - Step 17------"
set Dmax -118.e-3
set D_i [expr ($Dmax/$Nstep)]
integrator  DisplacementControl 2 1 [expr $D_i]
analyze $Nstep

puts "-------Horizontal loading - Step 18------"
set Dmax 136.e-3
set D_i [expr ($Dmax/$Nstep)]
integrator  DisplacementControl 2 1 [expr $D_i]
analyze $Nstep

puts "-------Horizontal loading - Step 19------"
set Dmax -153.e-3
set D_i [expr ($Dmax/$Nstep)]
integrator  DisplacementControl 2 1 [expr $D_i]
analyze $Nstep

puts "-------Horizontal loading - Step 20------"
set Dmax 170.e-3
set D_i [expr ($Dmax/$Nstep)]
integrator  DisplacementControl 2 1 [expr $D_i]
analyze $Nstep

puts "-------Horizontal loading - Step 21------"
set Dmax -193.e-3
set D_i [expr ($Dmax/$Nstep)]
integrator  DisplacementControl 2 1 [expr $D_i]
analyze $Nstep

puts "-------Horizontal loading - Step 22------"
set Dmax 216.e-3
set D_i [expr ($Dmax/$Nstep)]
integrator  DisplacementControl 2 1 [expr $D_i]
analyze $Nstep

puts "-------Horizontal loading - Step 23------"
set Dmax -158.e-3
set D_i [expr ($Dmax/$Nstep)]
integrator  DisplacementControl 2 1 [expr $D_i]
analyze $Nstep

wipe;