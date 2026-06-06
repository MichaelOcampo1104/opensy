# This file will be used to define beam elements 


# Define beam section sizes 
set	BeamLevel2	[SectionProperty W36X160]; 


# Define beams 
# Level 2
element	elasticBeamColumn	2121221	121	221	[lindex $BeamLevel2 2]	$Es	[lindex $BeamLevel2 6]	$LinearTransf; 
element	truss	222132	221	32	$AreaRigid	$TrussMatID; 

# puts "Beams defined"