# This file will be used to define beam elements 


# Define beam section sizes 
set	BeamLevel2	[SectionProperty W36X262]; 
set	BeamLevel3	[SectionProperty W36X262]; 
set	BeamLevel4	[SectionProperty W36X194]; 
set	BeamLevel5	[SectionProperty W36X194]; 
set	BeamLevel6	[SectionProperty W27X217]; 
set	BeamLevel7	[SectionProperty W27X217]; 
set	BeamLevel8	[SectionProperty W27X178]; 
set	BeamLevel9	[SectionProperty W27X178]; 
set	BeamLevel10	[SectionProperty W21X93]; 


# Define beams 
# Level 2
element	elasticBeamColumn	2121221	121	221	[lindex $BeamLevel2 2]	$Es	[lindex $BeamLevel2 6]	$LinearTransf; 
element	elasticBeamColumn	2221321	221	321	[lindex $BeamLevel2 2]	$Es	[lindex $BeamLevel2 6]	$LinearTransf; 
element	elasticBeamColumn	2321421	321	421	[lindex $BeamLevel2 2]	$Es	[lindex $BeamLevel2 6]	$LinearTransf; 
element	truss	242152	421	52	$AreaRigid	$TrussMatID; 

# Level 3
element	elasticBeamColumn	2131231	131	231	[lindex $BeamLevel3 2]	$Es	[lindex $BeamLevel3 6]	$LinearTransf; 
element	elasticBeamColumn	2231331	231	331	[lindex $BeamLevel3 2]	$Es	[lindex $BeamLevel3 6]	$LinearTransf; 
element	elasticBeamColumn	2331431	331	431	[lindex $BeamLevel3 2]	$Es	[lindex $BeamLevel3 6]	$LinearTransf; 
element	truss	243153	431	53	$AreaRigid	$TrussMatID; 

# Level 4
element	elasticBeamColumn	2141241	141	241	[lindex $BeamLevel4 2]	$Es	[lindex $BeamLevel4 6]	$LinearTransf; 
element	elasticBeamColumn	2241341	241	341	[lindex $BeamLevel4 2]	$Es	[lindex $BeamLevel4 6]	$LinearTransf; 
element	elasticBeamColumn	2341441	341	441	[lindex $BeamLevel4 2]	$Es	[lindex $BeamLevel4 6]	$LinearTransf; 
element	truss	244154	441	54	$AreaRigid	$TrussMatID; 

# Level 5
element	elasticBeamColumn	2151251	151	251	[lindex $BeamLevel5 2]	$Es	[lindex $BeamLevel5 6]	$LinearTransf; 
element	elasticBeamColumn	2251351	251	351	[lindex $BeamLevel5 2]	$Es	[lindex $BeamLevel5 6]	$LinearTransf; 
element	elasticBeamColumn	2351451	351	451	[lindex $BeamLevel5 2]	$Es	[lindex $BeamLevel5 6]	$LinearTransf; 
element	truss	245155	451	55	$AreaRigid	$TrussMatID; 

# Level 6
element	elasticBeamColumn	2161261	161	261	[lindex $BeamLevel6 2]	$Es	[lindex $BeamLevel6 6]	$LinearTransf; 
element	elasticBeamColumn	2261361	261	361	[lindex $BeamLevel6 2]	$Es	[lindex $BeamLevel6 6]	$LinearTransf; 
element	elasticBeamColumn	2361461	361	461	[lindex $BeamLevel6 2]	$Es	[lindex $BeamLevel6 6]	$LinearTransf; 
element	truss	246156	461	56	$AreaRigid	$TrussMatID; 

# Level 7
element	elasticBeamColumn	2171271	171	271	[lindex $BeamLevel7 2]	$Es	[lindex $BeamLevel7 6]	$LinearTransf; 
element	elasticBeamColumn	2271371	271	371	[lindex $BeamLevel7 2]	$Es	[lindex $BeamLevel7 6]	$LinearTransf; 
element	elasticBeamColumn	2371471	371	471	[lindex $BeamLevel7 2]	$Es	[lindex $BeamLevel7 6]	$LinearTransf; 
element	truss	247157	471	57	$AreaRigid	$TrussMatID; 

# Level 8
element	elasticBeamColumn	2181281	181	281	[lindex $BeamLevel8 2]	$Es	[lindex $BeamLevel8 6]	$LinearTransf; 
element	elasticBeamColumn	2281381	281	381	[lindex $BeamLevel8 2]	$Es	[lindex $BeamLevel8 6]	$LinearTransf; 
element	elasticBeamColumn	2381481	381	481	[lindex $BeamLevel8 2]	$Es	[lindex $BeamLevel8 6]	$LinearTransf; 
element	truss	248158	481	58	$AreaRigid	$TrussMatID; 

# Level 9
element	elasticBeamColumn	2191291	191	291	[lindex $BeamLevel9 2]	$Es	[lindex $BeamLevel9 6]	$LinearTransf; 
element	elasticBeamColumn	2291391	291	391	[lindex $BeamLevel9 2]	$Es	[lindex $BeamLevel9 6]	$LinearTransf; 
element	elasticBeamColumn	2391491	391	491	[lindex $BeamLevel9 2]	$Es	[lindex $BeamLevel9 6]	$LinearTransf; 
element	truss	249159	491	59	$AreaRigid	$TrussMatID; 

# Level 10
element	elasticBeamColumn	211012101	1101	2101	[lindex $BeamLevel10 2]	$Es	[lindex $BeamLevel10 6]	$LinearTransf; 
element	elasticBeamColumn	221013101	2101	3101	[lindex $BeamLevel10 2]	$Es	[lindex $BeamLevel10 6]	$LinearTransf; 
element	elasticBeamColumn	231014101	3101	4101	[lindex $BeamLevel10 2]	$Es	[lindex $BeamLevel10 6]	$LinearTransf; 
element	truss	24101510	4101	510	$AreaRigid	$TrussMatID; 

# puts "Beams defined"