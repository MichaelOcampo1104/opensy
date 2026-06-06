# This file will be used to define all nodal masses 

# Define floor weights and each nodal mass 
set	Floor2Weight	1800.00; 
set	FrameTributaryMassRatio	0.5; 
set	TotalNodesPerFloor	3; 
set	NodalMassFloor2	[expr $Floor2Weight*$FrameTributaryMassRatio/$TotalNodesPerFloor/$g]; 


# Level 2 
mass	121	$NodalMassFloor2	$Negligible	$Negligible
mass	221	$NodalMassFloor2	$Negligible	$Negligible
mass	32	$NodalMassFloor2	$Negligible	$Negligible

# puts "Nodal mass defined"