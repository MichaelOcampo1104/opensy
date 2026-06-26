#Created by Zhaohui Yang (zhyang@ucsd.edu)
#
#plane strain,  shear-beam type mesh with single material,  
#dynamic analysis,  SI units (m, s, KN, ton)
#input motion may be from a file, or a sinusoidal wave. 
#
wipe
#
#some user defined variables
# 
set matOpt   2      ;# 1 = drained, pressure depend;  2 = undrained, pressure depend; 
                    ;# 3 = undrained, pressure independ; 4 = elastic 
set mass  2.0      ;# saturated mass density
set fmass 1.0      ;# fluid mass density
set G     6.e4     ;
set B     2.4e5    ;
set press   0.    ;# isotropic consolidation pressure on quad element(s)
set accMul  2.       ;# acc. multiplier (m/s/s)
set accNam  myACC      ;# acc. file name if imposed motion is read from file 
                       ;# - YOU MUST CHANGE IT TO THE RIGHT NAME
set accDt   0.0166     ;# dt for input acc.
set loadBias .07     ;# Static shear load, in percentage of gravity load (=sin(inclination))
set period   1.0      ;# Period if imposed motion is Sine wave
set deltaT   0.01    ;# time step for analysis, does not have to be the same as accDt.
set numSteps 2000    ;# number of time steps
set gamma    0.6    ;# Newmark integration parameter

set massProportionalDamping   0.0 ;
set InitStiffnessProportionalDamping 0.002;

set numXele 1      ;# number of elements in x (H) direction
set numYele 10      ;# number of elements in y (V) direction
set xSize 1.0       ;# x direction element size
set ySize 1.0       ;# y direction element size

#############################################################
# BUILD MODEL

#create the ModelBuilder
model basic -ndm 2 -ndf 2

# define material and properties
switch $matOpt {
  1 {
    nDMaterial PressureDependMultiYield 1 2 $mass $G $B  31.4 .1 80 0.5 \
                                        26.5 0.17 0.4 10 10 0.015 1.0 
      updateMaterialStage -material 1 -stage 0
    
    set gravY [expr -9.81*$mass]  ;#gravity
    set gravX [expr -$gravY*$loadBias]
  }
  2 {
    nDMaterial PressureDependMultiYield 1 2 $mass $G  $B  31.4 .1 80 0.5 \
                                        26.5 0.17 0.4 10 10 0.015 1.0 
    nDMaterial FluidSolidPorous 2 2 1 2.2e6
    
    set gravY [expr -9.81*($mass-$fmass)]  ;# buoyant unit weight
    set gravX [expr -$gravY*$loadBias]
  }
  3 {
    nDMaterial PressureIndependMultiYield 1 2 $mass 4.e4 2.e5 20 .1 
    nDMaterial FluidSolidPorous 3 2 1 2.2e6

      updateMaterialStage -material 1 -stage 0
      updateMaterialStage -material 3 -stage 0
    
    set gravY [expr -9.81*($mass-fmass)]  ;# buoyant unit weight
    set gravX [expr -$gravY*$loadBias]
  }
  4 {
    nDMaterial ElasticIsotropic 4 2000 0.3 $mass
    set gravY [expr -9.81*$mass]  ;#gravity
    set gravX [expr -$gravY*$loadBias]
  }
}

# define the nodes
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
                                    #   thick  material        maTag    press density gravity    
    element quad $eleNum $n1 $n2 $n4 $n3 1.0  "PlaneStrain"   $matOpt  $press 0.0  $gravX $gravY 
  }
}  

updateMaterialStage -material 1 -stage 0
updateMaterialStage -material 2 -stage 0

# fix the base 
for {set i 1} {$i <= $numXnode} {incr i 1} {
  fix $i 1 1
}

# tie two lateral sides
for {set i 1} {$i < $numYnode} {incr i 1} {
  set nodeNum1 [expr $i*$numXnode + 1]
  set nodeNum2 [expr ($i+1)*$numXnode]
  equalDOF $nodeNum1 $nodeNum2 1 2
}

#############################################################
# GRAVITY APPLICATION (elastic behavior)

# create the SOE, ConstraintHandler, Integrator, Algorithm and Numberer
system ProfileSPD
test NormDispIncr 1.e-5 10 0
algorithm ModifiedNewton
constraints Transformation
integrator LoadControl 1 1 1 1
numberer RCM

# create the Analysis
analysis Static 

analyze 2

# switch material stage from elastic (gravity) to plastic
  switch $matOpt {
   1 {
    updateMaterialStage -material 1 -stage 1
    updateMaterials -material 1 bulkModulus [expr $G*2/3.]
   }
   2 {
    updateMaterialStage -material 1 -stage 1
    updateMaterialStage -material 2 -stage 1
    updateMaterials -material 1 bulkModulus [expr $G*2/3.]
   }
   3 {
    updateMaterialStage -material 1 -stage 1
    updateMaterialStage -material 3 -stage 1
   }
   4  ;# do nothing
  }


#############################################################
# NOW APPLY LOADING SEQUENCE AND ANALYZE (plastic)
print MODEL
# rezero time
setTime 0.0
wipeAnalysis

#                                    
#Sinusoidal motion, comment next line if using input motion file
pattern UniformExcitation    1    1    -accel "Sine 0 10 $period -factor $accMul"

#decomment next line if using input motion file
#pattern UniformExcitation    1    1  -accel "Series -factor $accMul -filePath $accNam -dt $accDt"

#recorder for nodal displacement along the vertical center line.
set nodeList {}
for {set i 0} {$i < $numYnode} {incr i 1} {
  lappend nodeList [expr $numXnode/2 + $i*$numXnode]
}
eval "recorder Node -file disp  -time -node $nodeList -dof 1 2 -dT $deltaT disp"
eval "recorder Node -file acc  -time -node $nodeList -dof 1 2 -dT $deltaT accel"

#recorder for element output along the vertical center line.
set name1 "stress";   set name2 "strain";   set name3 "press"
for {set i 1} {$i < $numYnode} {incr i 1} {
  set ele [expr $numXele-$numXele/2+($i-1)*$numXele] 
  set name11 [join [list $name1 $i] {}]
  set name22 [join [list $name2 $i] {}]  
  set name33 [join [list $name3 $i] {}] 
  recorder Element -ele $ele  -time -file $name11 material 1 stress
  recorder Element -ele $ele  -time -file $name22 material 1 strain
  if { $matOpt == 2 || $matOpt == 3 } {   ;#excess pore pressure ouput
    recorder Element -ele $ele -time -file $name33 material 1 pressure
  }
}

constraints Transformation
test NormDispIncr 1.e-4 10 0
numberer RCM
algorithm Newton 
system ProfileSPD
rayleigh $massProportionalDamping 0.0 $InitStiffnessProportionalDamping 0.
integrator Newmark $gamma  [expr pow($gamma+0.5, 2)/4]  
analysis VariableTransient 

#analyze 
set startT [clock seconds]
analyze $numSteps $deltaT [expr $deltaT/100] $deltaT 5
set endT [clock seconds]
puts "Execution time: [expr $endT-$startT] seconds."

wipe  #flush ouput stream