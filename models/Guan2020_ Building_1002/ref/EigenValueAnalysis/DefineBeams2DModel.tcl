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
# Level2
element	elasticBeamColumn	2121221	1215	2213	[lindex $BeamLevel2 2]	$Es	[expr ($n+1.0)/$n*[lindex $BeamLevel2 6]]	$LinearTransf; 
element	elasticBeamColumn	2221321	2215	3213	[lindex $BeamLevel2 2]	$Es	[expr ($n+1.0)/$n*[lindex $BeamLevel2 6]]	$LinearTransf; 
element	elasticBeamColumn	2321421	3215	4213	[lindex $BeamLevel2 2]	$Es	[expr ($n+1.0)/$n*[lindex $BeamLevel2 6]]	$LinearTransf; 
element	truss	242152	4211	52	$AreaRigid	$TrussMatID; 

# Level3
element	elasticBeamColumn	2131231	1315	2313	[lindex $BeamLevel3 2]	$Es	[expr ($n+1.0)/$n*[lindex $BeamLevel3 6]]	$LinearTransf; 
element	elasticBeamColumn	2231331	2315	3313	[lindex $BeamLevel3 2]	$Es	[expr ($n+1.0)/$n*[lindex $BeamLevel3 6]]	$LinearTransf; 
element	elasticBeamColumn	2331431	3315	4313	[lindex $BeamLevel3 2]	$Es	[expr ($n+1.0)/$n*[lindex $BeamLevel3 6]]	$LinearTransf; 
element	truss	243153	4311	53	$AreaRigid	$TrussMatID; 

# Level4
element	elasticBeamColumn	2141241	1415	2413	[lindex $BeamLevel4 2]	$Es	[expr ($n+1.0)/$n*[lindex $BeamLevel4 6]]	$LinearTransf; 
element	elasticBeamColumn	2241341	2415	3413	[lindex $BeamLevel4 2]	$Es	[expr ($n+1.0)/$n*[lindex $BeamLevel4 6]]	$LinearTransf; 
element	elasticBeamColumn	2341441	3415	4413	[lindex $BeamLevel4 2]	$Es	[expr ($n+1.0)/$n*[lindex $BeamLevel4 6]]	$LinearTransf; 
element	truss	244154	4411	54	$AreaRigid	$TrussMatID; 

# Level5
element	elasticBeamColumn	2151251	1515	2513	[lindex $BeamLevel5 2]	$Es	[expr ($n+1.0)/$n*[lindex $BeamLevel5 6]]	$LinearTransf; 
element	elasticBeamColumn	2251351	2515	3513	[lindex $BeamLevel5 2]	$Es	[expr ($n+1.0)/$n*[lindex $BeamLevel5 6]]	$LinearTransf; 
element	elasticBeamColumn	2351451	3515	4513	[lindex $BeamLevel5 2]	$Es	[expr ($n+1.0)/$n*[lindex $BeamLevel5 6]]	$LinearTransf; 
element	truss	245155	4511	55	$AreaRigid	$TrussMatID; 

# Level6
element	elasticBeamColumn	2161261	1615	2613	[lindex $BeamLevel6 2]	$Es	[expr ($n+1.0)/$n*[lindex $BeamLevel6 6]]	$LinearTransf; 
element	elasticBeamColumn	2261361	2615	3613	[lindex $BeamLevel6 2]	$Es	[expr ($n+1.0)/$n*[lindex $BeamLevel6 6]]	$LinearTransf; 
element	elasticBeamColumn	2361461	3615	4613	[lindex $BeamLevel6 2]	$Es	[expr ($n+1.0)/$n*[lindex $BeamLevel6 6]]	$LinearTransf; 
element	truss	246156	4611	56	$AreaRigid	$TrussMatID; 

# Level7
element	elasticBeamColumn	2171271	1715	2713	[lindex $BeamLevel7 2]	$Es	[expr ($n+1.0)/$n*[lindex $BeamLevel7 6]]	$LinearTransf; 
element	elasticBeamColumn	2271371	2715	3713	[lindex $BeamLevel7 2]	$Es	[expr ($n+1.0)/$n*[lindex $BeamLevel7 6]]	$LinearTransf; 
element	elasticBeamColumn	2371471	3715	4713	[lindex $BeamLevel7 2]	$Es	[expr ($n+1.0)/$n*[lindex $BeamLevel7 6]]	$LinearTransf; 
element	truss	247157	4711	57	$AreaRigid	$TrussMatID; 

# Level8
element	elasticBeamColumn	2181281	1815	2813	[lindex $BeamLevel8 2]	$Es	[expr ($n+1.0)/$n*[lindex $BeamLevel8 6]]	$LinearTransf; 
element	elasticBeamColumn	2281381	2815	3813	[lindex $BeamLevel8 2]	$Es	[expr ($n+1.0)/$n*[lindex $BeamLevel8 6]]	$LinearTransf; 
element	elasticBeamColumn	2381481	3815	4813	[lindex $BeamLevel8 2]	$Es	[expr ($n+1.0)/$n*[lindex $BeamLevel8 6]]	$LinearTransf; 
element	truss	248158	4811	58	$AreaRigid	$TrussMatID; 

# Level9
element	elasticBeamColumn	2191291	1915	2913	[lindex $BeamLevel9 2]	$Es	[expr ($n+1.0)/$n*[lindex $BeamLevel9 6]]	$LinearTransf; 
element	elasticBeamColumn	2291391	2915	3913	[lindex $BeamLevel9 2]	$Es	[expr ($n+1.0)/$n*[lindex $BeamLevel9 6]]	$LinearTransf; 
element	elasticBeamColumn	2391491	3915	4913	[lindex $BeamLevel9 2]	$Es	[expr ($n+1.0)/$n*[lindex $BeamLevel9 6]]	$LinearTransf; 
element	truss	249159	4911	59	$AreaRigid	$TrussMatID; 

# Level10
element	elasticBeamColumn	211012101	11015	21013	[lindex $BeamLevel10 2]	$Es	[expr ($n+1.0)/$n*[lindex $BeamLevel10 6]]	$LinearTransf; 
element	elasticBeamColumn	221013101	21015	31013	[lindex $BeamLevel10 2]	$Es	[expr ($n+1.0)/$n*[lindex $BeamLevel10 6]]	$LinearTransf; 
element	elasticBeamColumn	231014101	31015	41013	[lindex $BeamLevel10 2]	$Es	[expr ($n+1.0)/$n*[lindex $BeamLevel10 6]]	$LinearTransf; 
element	truss	24101510	41011	510	$AreaRigid	$TrussMatID; 

puts "Beams defined"