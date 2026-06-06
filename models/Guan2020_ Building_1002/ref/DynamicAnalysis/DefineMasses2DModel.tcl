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


# Level2 
mass	1211	$NodalMassFloor2	$Negligible	$Negligible 
mass	2211	$NodalMassFloor2	$Negligible	$Negligible 
mass	3211	$NodalMassFloor2	$Negligible	$Negligible 
mass	4211	$NodalMassFloor2	$Negligible	$Negligible 
mass	52	$NodalMassFloor2	$Negligible	$Negligible 

# Level3 
mass	1311	$NodalMassFloor3	$Negligible	$Negligible 
mass	2311	$NodalMassFloor3	$Negligible	$Negligible 
mass	3311	$NodalMassFloor3	$Negligible	$Negligible 
mass	4311	$NodalMassFloor3	$Negligible	$Negligible 
mass	53	$NodalMassFloor3	$Negligible	$Negligible 

# Level4 
mass	1411	$NodalMassFloor4	$Negligible	$Negligible 
mass	2411	$NodalMassFloor4	$Negligible	$Negligible 
mass	3411	$NodalMassFloor4	$Negligible	$Negligible 
mass	4411	$NodalMassFloor4	$Negligible	$Negligible 
mass	54	$NodalMassFloor4	$Negligible	$Negligible 

# Level5 
mass	1511	$NodalMassFloor5	$Negligible	$Negligible 
mass	2511	$NodalMassFloor5	$Negligible	$Negligible 
mass	3511	$NodalMassFloor5	$Negligible	$Negligible 
mass	4511	$NodalMassFloor5	$Negligible	$Negligible 
mass	55	$NodalMassFloor5	$Negligible	$Negligible 

# Level6 
mass	1611	$NodalMassFloor6	$Negligible	$Negligible 
mass	2611	$NodalMassFloor6	$Negligible	$Negligible 
mass	3611	$NodalMassFloor6	$Negligible	$Negligible 
mass	4611	$NodalMassFloor6	$Negligible	$Negligible 
mass	56	$NodalMassFloor6	$Negligible	$Negligible 

# Level7 
mass	1711	$NodalMassFloor7	$Negligible	$Negligible 
mass	2711	$NodalMassFloor7	$Negligible	$Negligible 
mass	3711	$NodalMassFloor7	$Negligible	$Negligible 
mass	4711	$NodalMassFloor7	$Negligible	$Negligible 
mass	57	$NodalMassFloor7	$Negligible	$Negligible 

# Level8 
mass	1811	$NodalMassFloor8	$Negligible	$Negligible 
mass	2811	$NodalMassFloor8	$Negligible	$Negligible 
mass	3811	$NodalMassFloor8	$Negligible	$Negligible 
mass	4811	$NodalMassFloor8	$Negligible	$Negligible 
mass	58	$NodalMassFloor8	$Negligible	$Negligible 

# Level9 
mass	1911	$NodalMassFloor9	$Negligible	$Negligible 
mass	2911	$NodalMassFloor9	$Negligible	$Negligible 
mass	3911	$NodalMassFloor9	$Negligible	$Negligible 
mass	4911	$NodalMassFloor9	$Negligible	$Negligible 
mass	59	$NodalMassFloor9	$Negligible	$Negligible 

# Level10 
mass	11011	$NodalMassFloor10	$Negligible	$Negligible 
mass	21011	$NodalMassFloor10	$Negligible	$Negligible 
mass	31011	$NodalMassFloor10	$Negligible	$Negligible 
mass	41011	$NodalMassFloor10	$Negligible	$Negligible 
mass	510	$NodalMassFloor10	$Negligible	$Negligible 

puts "Nodal mass defined"