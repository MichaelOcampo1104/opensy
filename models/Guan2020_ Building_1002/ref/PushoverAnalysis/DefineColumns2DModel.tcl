# This file will be used to define columns 


# Define exterior column section sizes 
set	ExteriorColumnStory1	[SectionProperty W14X730];
set	ExteriorColumnStory2	[SectionProperty W14X730];
set	ExteriorColumnStory3	[SectionProperty W14X455];
set	ExteriorColumnStory4	[SectionProperty W14X455];
set	ExteriorColumnStory5	[SectionProperty W14X398];
set	ExteriorColumnStory6	[SectionProperty W14X398];
set	ExteriorColumnStory7	[SectionProperty W14X342];
set	ExteriorColumnStory8	[SectionProperty W14X342];
set	ExteriorColumnStory9	[SectionProperty W14X132];


# Define interior column section sizes 
set	InteriorColumnStory1	[SectionProperty W14X730];
set	InteriorColumnStory2	[SectionProperty W14X730];
set	InteriorColumnStory3	[SectionProperty W14X550];
set	InteriorColumnStory4	[SectionProperty W14X550];
set	InteriorColumnStory5	[SectionProperty W14X500];
set	InteriorColumnStory6	[SectionProperty W14X500];
set	InteriorColumnStory7	[SectionProperty W14X426];
set	InteriorColumnStory8	[SectionProperty W14X426];
set	InteriorColumnStory9	[SectionProperty W14X176];


# Define columns
# Story 1 
element	elasticBeamColumn	3111121	1114	1216	[lindex $ExteriorColumnStory1 2]	$Es	[expr ($n+1.0)/$n*[lindex $ExteriorColumnStory1 6]]	$PDeltaTransf; 
element	elasticBeamColumn	3211221	2114	2216	[lindex $InteriorColumnStory1 2]	$Es	[expr ($n+1.0)/$n*[lindex $InteriorColumnStory1 6]]	$PDeltaTransf; 
element	elasticBeamColumn	3311321	3114	3216	[lindex $InteriorColumnStory1 2]	$Es	[expr ($n+1.0)/$n*[lindex $InteriorColumnStory1 6]]	$PDeltaTransf; 
element	elasticBeamColumn	3411421	4114	4216	[lindex $ExteriorColumnStory1 2]	$Es	[expr ($n+1.0)/$n*[lindex $ExteriorColumnStory1 6]]	$PDeltaTransf; 
element	elasticBeamColumn	351522	51	522	$AreaRigid	$Es	$IRigid	$PDeltaTransf; 

# Story 2 
element	elasticBeamColumn	3121131	1214	1316	[lindex $ExteriorColumnStory2 2]	$Es	[expr ($n+1.0)/$n*[lindex $ExteriorColumnStory2 6]]	$PDeltaTransf; 
element	elasticBeamColumn	3221231	2214	2316	[lindex $InteriorColumnStory2 2]	$Es	[expr ($n+1.0)/$n*[lindex $InteriorColumnStory2 6]]	$PDeltaTransf; 
element	elasticBeamColumn	3321331	3214	3316	[lindex $InteriorColumnStory2 2]	$Es	[expr ($n+1.0)/$n*[lindex $InteriorColumnStory2 6]]	$PDeltaTransf; 
element	elasticBeamColumn	3421431	4214	4316	[lindex $ExteriorColumnStory2 2]	$Es	[expr ($n+1.0)/$n*[lindex $ExteriorColumnStory2 6]]	$PDeltaTransf; 
element	elasticBeamColumn	3524532	524	532	$AreaRigid	$Es	$IRigid	$PDeltaTransf; 

# Story 3 
element	elasticBeamColumn	3131141	1314	1416	[lindex $ExteriorColumnStory3 2]	$Es	[expr ($n+1.0)/$n*[lindex $ExteriorColumnStory3 6]]	$PDeltaTransf; 
element	elasticBeamColumn	3231241	2314	2416	[lindex $InteriorColumnStory3 2]	$Es	[expr ($n+1.0)/$n*[lindex $InteriorColumnStory3 6]]	$PDeltaTransf; 
element	elasticBeamColumn	3331341	3314	3416	[lindex $InteriorColumnStory3 2]	$Es	[expr ($n+1.0)/$n*[lindex $InteriorColumnStory3 6]]	$PDeltaTransf; 
element	elasticBeamColumn	3431441	4314	4416	[lindex $ExteriorColumnStory3 2]	$Es	[expr ($n+1.0)/$n*[lindex $ExteriorColumnStory3 6]]	$PDeltaTransf; 
element	elasticBeamColumn	3534542	534	542	$AreaRigid	$Es	$IRigid	$PDeltaTransf; 

# Story 4 
element	elasticBeamColumn	3141151	1414	1516	[lindex $ExteriorColumnStory4 2]	$Es	[expr ($n+1.0)/$n*[lindex $ExteriorColumnStory4 6]]	$PDeltaTransf; 
element	elasticBeamColumn	3241251	2414	2516	[lindex $InteriorColumnStory4 2]	$Es	[expr ($n+1.0)/$n*[lindex $InteriorColumnStory4 6]]	$PDeltaTransf; 
element	elasticBeamColumn	3341351	3414	3516	[lindex $InteriorColumnStory4 2]	$Es	[expr ($n+1.0)/$n*[lindex $InteriorColumnStory4 6]]	$PDeltaTransf; 
element	elasticBeamColumn	3441451	4414	4516	[lindex $ExteriorColumnStory4 2]	$Es	[expr ($n+1.0)/$n*[lindex $ExteriorColumnStory4 6]]	$PDeltaTransf; 
element	elasticBeamColumn	3544552	544	552	$AreaRigid	$Es	$IRigid	$PDeltaTransf; 

# Story 5 
element	elasticBeamColumn	3151161	1514	1616	[lindex $ExteriorColumnStory5 2]	$Es	[expr ($n+1.0)/$n*[lindex $ExteriorColumnStory5 6]]	$PDeltaTransf; 
element	elasticBeamColumn	3251261	2514	2616	[lindex $InteriorColumnStory5 2]	$Es	[expr ($n+1.0)/$n*[lindex $InteriorColumnStory5 6]]	$PDeltaTransf; 
element	elasticBeamColumn	3351361	3514	3616	[lindex $InteriorColumnStory5 2]	$Es	[expr ($n+1.0)/$n*[lindex $InteriorColumnStory5 6]]	$PDeltaTransf; 
element	elasticBeamColumn	3451461	4514	4616	[lindex $ExteriorColumnStory5 2]	$Es	[expr ($n+1.0)/$n*[lindex $ExteriorColumnStory5 6]]	$PDeltaTransf; 
element	elasticBeamColumn	3554562	554	562	$AreaRigid	$Es	$IRigid	$PDeltaTransf; 

# Story 6 
element	elasticBeamColumn	3161171	1614	1716	[lindex $ExteriorColumnStory6 2]	$Es	[expr ($n+1.0)/$n*[lindex $ExteriorColumnStory6 6]]	$PDeltaTransf; 
element	elasticBeamColumn	3261271	2614	2716	[lindex $InteriorColumnStory6 2]	$Es	[expr ($n+1.0)/$n*[lindex $InteriorColumnStory6 6]]	$PDeltaTransf; 
element	elasticBeamColumn	3361371	3614	3716	[lindex $InteriorColumnStory6 2]	$Es	[expr ($n+1.0)/$n*[lindex $InteriorColumnStory6 6]]	$PDeltaTransf; 
element	elasticBeamColumn	3461471	4614	4716	[lindex $ExteriorColumnStory6 2]	$Es	[expr ($n+1.0)/$n*[lindex $ExteriorColumnStory6 6]]	$PDeltaTransf; 
element	elasticBeamColumn	3564572	564	572	$AreaRigid	$Es	$IRigid	$PDeltaTransf; 

# Story 7 
element	elasticBeamColumn	3171181	1714	1816	[lindex $ExteriorColumnStory7 2]	$Es	[expr ($n+1.0)/$n*[lindex $ExteriorColumnStory7 6]]	$PDeltaTransf; 
element	elasticBeamColumn	3271281	2714	2816	[lindex $InteriorColumnStory7 2]	$Es	[expr ($n+1.0)/$n*[lindex $InteriorColumnStory7 6]]	$PDeltaTransf; 
element	elasticBeamColumn	3371381	3714	3816	[lindex $InteriorColumnStory7 2]	$Es	[expr ($n+1.0)/$n*[lindex $InteriorColumnStory7 6]]	$PDeltaTransf; 
element	elasticBeamColumn	3471481	4714	4816	[lindex $ExteriorColumnStory7 2]	$Es	[expr ($n+1.0)/$n*[lindex $ExteriorColumnStory7 6]]	$PDeltaTransf; 
element	elasticBeamColumn	3574582	574	582	$AreaRigid	$Es	$IRigid	$PDeltaTransf; 

# Story 8 
element	elasticBeamColumn	3181191	1814	1916	[lindex $ExteriorColumnStory8 2]	$Es	[expr ($n+1.0)/$n*[lindex $ExteriorColumnStory8 6]]	$PDeltaTransf; 
element	elasticBeamColumn	3281291	2814	2916	[lindex $InteriorColumnStory8 2]	$Es	[expr ($n+1.0)/$n*[lindex $InteriorColumnStory8 6]]	$PDeltaTransf; 
element	elasticBeamColumn	3381391	3814	3916	[lindex $InteriorColumnStory8 2]	$Es	[expr ($n+1.0)/$n*[lindex $InteriorColumnStory8 6]]	$PDeltaTransf; 
element	elasticBeamColumn	3481491	4814	4916	[lindex $ExteriorColumnStory8 2]	$Es	[expr ($n+1.0)/$n*[lindex $ExteriorColumnStory8 6]]	$PDeltaTransf; 
element	elasticBeamColumn	3584592	584	592	$AreaRigid	$Es	$IRigid	$PDeltaTransf; 

# Story 9 
element	elasticBeamColumn	31911101	1914	11016	[lindex $ExteriorColumnStory9 2]	$Es	[expr ($n+1.0)/$n*[lindex $ExteriorColumnStory9 6]]	$PDeltaTransf; 
element	elasticBeamColumn	32912101	2914	21016	[lindex $InteriorColumnStory9 2]	$Es	[expr ($n+1.0)/$n*[lindex $InteriorColumnStory9 6]]	$PDeltaTransf; 
element	elasticBeamColumn	33913101	3914	31016	[lindex $InteriorColumnStory9 2]	$Es	[expr ($n+1.0)/$n*[lindex $InteriorColumnStory9 6]]	$PDeltaTransf; 
element	elasticBeamColumn	34914101	4914	41016	[lindex $ExteriorColumnStory9 2]	$Es	[expr ($n+1.0)/$n*[lindex $ExteriorColumnStory9 6]]	$PDeltaTransf; 
element	elasticBeamColumn	35945102	594	5102	$AreaRigid	$Es	$IRigid	$PDeltaTransf; 

puts "Columns defined"