# This file will be used to define all nodal masses 

# Define floor weights and each nodal mass 
set	Floor2Weight	1125.00; 
set	Floor3Weight	1125.00; 
set	Floor4Weight	1125.00; 
set	Floor5Weight	1125.00; 
set	Floor6Weight	1125.00; 
set	Floor7Weight	1125.00; 
set	Floor8Weight	1125.00; 
set	Floor9Weight	1125.00; 
set	Floor10Weight	1518.75; 
set	FrameTributaryMassRatio	0.5; 
set	TotalNodesPerFloor	5; 
set	NodalMassFloor2	[expr $Floor2Weight*$FrameTributaryMassRatio/$TotalNodesPerFloor/$g]; 
set	NodalMassFloor3	[expr $Floor3Weight*$FrameTributaryMassRatio/$TotalNodesPerFloor/$g]; 
set	NodalMassFloor4	[expr $Floor4Weight*$FrameTributaryMassRatio/$TotalNodesPerFloor/$g]; 
set	NodalMassFloor5	[expr $Floor5Weight*$FrameTributaryMassRatio/$TotalNodesPerFloor/$g]; 
set	NodalMassFloor6	[expr $Floor6Weight*$FrameTributaryMassRatio/$TotalNodesPerFloor/$g]; 
set	NodalMassFloor7	[expr $Floor7Weight*$FrameTributaryMassRatio/$TotalNodesPerFloor/$g]; 
set	NodalMassFloor8	[expr $Floor8Weight*$FrameTributaryMassRatio/$TotalNodesPerFloor/$g]; 
set	NodalMassFloor9	[expr $Floor9Weight*$FrameTributaryMassRatio/$TotalNodesPerFloor/$g]; 
set	NodalMassFloor10	[expr $Floor10Weight*$FrameTributaryMassRatio/$TotalNodesPerFloor/$g]; 


# Level 2 
mass	121	$NodalMassFloor2	$Negligible	$Negligible
mass	221	$NodalMassFloor2	$Negligible	$Negligible
mass	321	$NodalMassFloor2	$Negligible	$Negligible
mass	421	$NodalMassFloor2	$Negligible	$Negligible
mass	52	$NodalMassFloor2	$Negligible	$Negligible

# Level 3 
mass	131	$NodalMassFloor3	$Negligible	$Negligible
mass	231	$NodalMassFloor3	$Negligible	$Negligible
mass	331	$NodalMassFloor3	$Negligible	$Negligible
mass	431	$NodalMassFloor3	$Negligible	$Negligible
mass	53	$NodalMassFloor3	$Negligible	$Negligible

# Level 4 
mass	141	$NodalMassFloor4	$Negligible	$Negligible
mass	241	$NodalMassFloor4	$Negligible	$Negligible
mass	341	$NodalMassFloor4	$Negligible	$Negligible
mass	441	$NodalMassFloor4	$Negligible	$Negligible
mass	54	$NodalMassFloor4	$Negligible	$Negligible

# Level 5 
mass	151	$NodalMassFloor5	$Negligible	$Negligible
mass	251	$NodalMassFloor5	$Negligible	$Negligible
mass	351	$NodalMassFloor5	$Negligible	$Negligible
mass	451	$NodalMassFloor5	$Negligible	$Negligible
mass	55	$NodalMassFloor5	$Negligible	$Negligible

# Level 6 
mass	161	$NodalMassFloor6	$Negligible	$Negligible
mass	261	$NodalMassFloor6	$Negligible	$Negligible
mass	361	$NodalMassFloor6	$Negligible	$Negligible
mass	461	$NodalMassFloor6	$Negligible	$Negligible
mass	56	$NodalMassFloor6	$Negligible	$Negligible

# Level 7 
mass	171	$NodalMassFloor7	$Negligible	$Negligible
mass	271	$NodalMassFloor7	$Negligible	$Negligible
mass	371	$NodalMassFloor7	$Negligible	$Negligible
mass	471	$NodalMassFloor7	$Negligible	$Negligible
mass	57	$NodalMassFloor7	$Negligible	$Negligible

# Level 8 
mass	181	$NodalMassFloor8	$Negligible	$Negligible
mass	281	$NodalMassFloor8	$Negligible	$Negligible
mass	381	$NodalMassFloor8	$Negligible	$Negligible
mass	481	$NodalMassFloor8	$Negligible	$Negligible
mass	58	$NodalMassFloor8	$Negligible	$Negligible

# Level 9 
mass	191	$NodalMassFloor9	$Negligible	$Negligible
mass	291	$NodalMassFloor9	$Negligible	$Negligible
mass	391	$NodalMassFloor9	$Negligible	$Negligible
mass	491	$NodalMassFloor9	$Negligible	$Negligible
mass	59	$NodalMassFloor9	$Negligible	$Negligible

# Level 10 
mass	1101	$NodalMassFloor10	$Negligible	$Negligible
mass	2101	$NodalMassFloor10	$Negligible	$Negligible
mass	3101	$NodalMassFloor10	$Negligible	$Negligible
mass	4101	$NodalMassFloor10	$Negligible	$Negligible
mass	510	$NodalMassFloor10	$Negligible	$Negligible

# puts "Nodal mass defined"