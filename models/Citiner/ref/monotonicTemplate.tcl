#########################################################################
#                                                                       #
#                         Monotonic Loading                             #
#                          (Units: kN, m)                               #
#                                                                       #
#########################################################################
wipe;
model basic -ndm 2 -ndf 3;

## Constants ##
set pi   3.14;

## Section and Material Properties ##
set B      0.15;
set H      0.14;
set L      1.5;
set db     0.01;
set nb     6;
set fy     557000;
set PHL    0.09982;   ## Determined from the AdaBoost model
set dbv    0.006;
set Es     200000000;
set k      0.002;
set Ecc    20000000;
set fpc    -52000;
set epsc0  -0.01;
set fpcu   -5000;
set epscu  -0.1;

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
uniaxialMaterial Concrete01 2 $fpc $epsc0 $fpcu $epscu

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
geomTransf Linear 2;
element beamWithHinges 1 1 2 1 $PHL 1 $PHL $Ec $A $Iz 2;

## Vertical Loading ##

pattern Plain 1 Linear {
load 2 0 [expr $A*$fpc*0.1] 0
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
test        EnergyIncr 1.0e-2 200
algorithm Newton
system      BandGeneral
analysis    Static

set Nstep 100;

puts "-----------Horizontal loading------------"
set Dmax 72.e-3
set D_i [expr ($Dmax/$Nstep)]
integrator  DisplacementControl 2 1 [expr $D_i] 
analyze $Nstep

wipe;