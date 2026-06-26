#Created by Zhaohui Yang (zhyang@ucsd.edu)
#
#fully coupled, u-p formulation
#
#plane strain,  shear-beam type mesh with single material,  
#dynamic analysis,  SI units (m, s, KN, ton)
#
wipe
#
#some user defined variables
# 
set matOpt   1      ;# 1 = pressure depend; 
                    ;# 2 = pressure independ; 
set fmass  1      ;# fluid mass density
set smass  2      ;# saturated soil mass density
set G     6.e4     ;
set B     2.4e5    ;
set bulk   2.2e6  ;#fluid-solid combined bulk modulus
set vperm  5.e-4  ;#vertical permeability (m/s)
set hperm  5.e-4  ;#horizontal permeability (m/s)
set accGravity  9.81    ;#acceleration of gravity
set vperm  [expr $vperm/$accGravity/$fmass]  ;#actual value used in computation
set hperm  [expr $hperm/$accGravity/$fmass]  ;#actual value used in computation
set press   0.    ;# isotropic consolidation pressure on quad element(s)
set loadBias 0.07     ;# Static shear load, in percentage of gravity load (=sin(inclination angle))

set accMul  2.  ;# acc. multiplier
set accNam  whatever.acc  ;# file name for input acc. record 
set accDt   0.0166   ;# dt of input acc. record
set period   1.0      ;# Period for applied Sine wave
set deltaT   0.01    ;# time step for analysis
set numSteps 2400    ;# number of time steps
set gamma    0.6    ;# Newmark integration parameter

set massProportionalDamping   0. ;
set InitStiffnessProportionalDamping 0.002;

set numXele 1      ;# number of elements in x (H) direction
set numYele 10      ;# number of elements in y (V) direction
set xSize 1.0       ;# x direction element size
set ySize 1.0       ;# y direction element size

#############################################################
# BUILD MODEL

#create the ModelBuilder
model basic -ndm 2 -ndf 3

# define material and properties
switch $matOpt {
  1 {
    nDMaterial PressureDependMultiYield 1 2 $smass $G $B 31.4 .1 80 0.5\
                                        26.5 0.1 .2 5 10 0.015 1.
  }
  2 {
    nDMaterial PressureIndependMultiYield 2 2 1.8 4.e4 2.e5 40 .1
  }
}

set gravY -$accGravity                 ;#calc. gravity
set gravX [expr -$gravY*$loadBias]

# define nodes
set numXnode  [expr $numXele+1]
set numYnode  [expr $numYele+1]

for {set i 1} {$i <= $numXnode} {incr i 1} {
  for {set j 1} {$j <= $numYnode} {incr j 1} {
    set xdim [expr ($i-1)*$xSize]
    set ydim [expr ($j-1)*$ySize] 
    set nodeNum [expr $i + ($j-1)*$numXnode] 
    node $nodeNum $xdim $ydim 
  }
}

# define elements
for {set i 1} {$i <= $numXele} {incr i 1} {
  for {set j 1} {$j <= $numYele} {incr j 1} {
    set eleNum [expr $i + ($j-1)*$numXele] 
    set n1  [expr $i + ($j-1)*$numXnode] 
    set n2  [expr $i + ($j-1)*$numXnode + 1] 
    set n4  [expr $i + $j*$numXnode + 1] 
    set n3  [expr $i + $j*$numXnode] 
                                    #      thick maTag  bulk  mDensity  perm1  perm2  gravity      press   
    element quadUP $eleNum $n1 $n2 $n4 $n3 1.0  $matOpt $bulk $fmass  $hperm  $vperm $gravX $gravY $press   
  }
}  

#set material to elastic for gravity loading
updateMaterialStage -material $matOpt -stage 0  

# fix the base, and free surface drainage
for {set i 1} {$i <= $numXnode} {incr i 1} {
  fix $i 1 1 0
  set surfnode [expr ($numYnode-1)*$numXnode + $i] 
  fix $surfnode 0 0 1
}

# tie all disp. DOFs at same level
for {set i 1} {$i < $numYnode} {incr i 1} {
  set nodeNum1 [expr $i*$numXnode + 1]
  for {set j 2} {$j <= $numXnode} {incr j 1} {
    set nodeNum2 [expr $i*$numXnode + $j]
    equalDOF $nodeNum1 $nodeNum2 1 2 
  }
}

#############################################################
# GRAVITY APPLICATION (elastic behavior)

# create the SOE, ConstraintHandler, Integrator, Algorithm and Numberer
numberer RCM
system ProfileSPD
test NormDispIncr 1.0e-8 25 2
algorithm Newton
constraints Penalty 1.e18 1.e18
integrator Newmark 1.5  1.  
analysis Transient 

analyze 3 5.e3

# switch material stage from elastic (gravity) to plastic
switch $matOpt {
  1 {
     updateMaterialStage -material $matOpt -stage 1
  }
  2 {
     updateMaterialStage -material $matOpt -stage 1
  }
}
analyze 5 5.e3
# rezero time
wipeAnalysis
setTime 0.0
#loadConst -time 0.0
#############################################################
# NOW APPLY LOADING SEQUENCE AND ANALYZE (plastic)

#   base input motion                     
pattern UniformExcitation  1  1    -accel "Sine 0. 10. $period -factor $accMul"

#input motion through data file
#pattern UniformExcitation  1  1  -accel "Series -factor $accMul -filePath $accNam -dt $accDt"

#recorder for nodal variables along the vertical center line.
set nodeList {}
for {set i 0} {$i < $numYnode} {incr i 1} {
  lappend nodeList [expr $numXnode/2 + $i*$numXnode]
}

#define recorders for disp., excess pore pressure, and acc.
#Note: disp and acc outputs are relative to the base
eval "recorder Node -file disp  -time -node $nodeList -dof 1 2 -dT $deltaT disp"
eval "recorder Node -file pwp  -time -node $nodeList -dof 3 -dT $deltaT vel"
eval "recorder Node -file acc  -time -node $nodeList -dof 1 2 -dT $deltaT accel"

#stress/strain output at Gauss point 1 of each element along center line
set name1 "stress";   set name2 "strain";  
for {set i 1} {$i < $numYnode} {incr i 1} {
  set ele [expr $numXele-$numXele/2+($i-1)*$numXele] 
  set name11 [join [list $name1 $i] {}]
  set name21 [join [list $name2 $i] {}] 
  recorder Element -ele $ele  -time -file $name11  -dT $deltaT material 1 stress
  recorder Element -ele $ele  -time -file $name21  -dT $deltaT material 1 strain
}

#analysis options
constraints Penalty 1.e18 1.e18
test NormDispIncr 1.e-5 25 0
numberer RCM
algorithm Newton
system ProfileSPD
#some mass proportional and initial-stiffness proportional damping
rayleigh $massProportionalDamping 0.0 $InitStiffnessProportionalDamping 0.0
integrator Newmark $gamma  [expr pow($gamma+0.5, 2)/4]  
analysis VariableTransient 

#analyze 
set startT [clock seconds]
analyze $numSteps $deltaT [expr $deltaT/100] $deltaT 15
set endT [clock seconds]
puts "Execution time: [expr $endT-$startT] seconds."

wipe  #flush ouput stream