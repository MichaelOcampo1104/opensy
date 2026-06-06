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
element	elasticBeamColumn	3111121	111	121	[lindex $ExteriorColumnStory1 2]	$Es	[lindex $ExteriorColumnStory1 6]	$PDeltaTransf; 
element	elasticBeamColumn	3211221	211	221	[lindex $InteriorColumnStory1 2]	$Es	[lindex $InteriorColumnStory1 6]	$PDeltaTransf; 
element	elasticBeamColumn	3311321	311	321	[lindex $InteriorColumnStory1 2]	$Es	[lindex $InteriorColumnStory1 6]	$PDeltaTransf; 
element	elasticBeamColumn	3411421	411	421	[lindex $ExteriorColumnStory1 2]	$Es	[lindex $ExteriorColumnStory1 6]	$PDeltaTransf; 
element	elasticBeamColumn	351522	51	522	$AreaRigid	$Es	$IRigid	$PDeltaTransf; 

# Story 2 
element	elasticBeamColumn	3121131	121	131	[lindex $ExteriorColumnStory2 2]	$Es	[lindex $ExteriorColumnStory2 6]	$PDeltaTransf; 
element	elasticBeamColumn	3221231	221	231	[lindex $InteriorColumnStory2 2]	$Es	[lindex $InteriorColumnStory2 6]	$PDeltaTransf; 
element	elasticBeamColumn	3321331	321	331	[lindex $InteriorColumnStory2 2]	$Es	[lindex $InteriorColumnStory2 6]	$PDeltaTransf; 
element	elasticBeamColumn	3421431	421	431	[lindex $ExteriorColumnStory2 2]	$Es	[lindex $ExteriorColumnStory2 6]	$PDeltaTransf; 
element	elasticBeamColumn	3524532	524	532	$AreaRigid	$Es	$IRigid	$PDeltaTransf; 

# Story 3 
element	elasticBeamColumn	3131141	131	141	[lindex $ExteriorColumnStory3 2]	$Es	[lindex $ExteriorColumnStory3 6]	$PDeltaTransf; 
element	elasticBeamColumn	3231241	231	241	[lindex $InteriorColumnStory3 2]	$Es	[lindex $InteriorColumnStory3 6]	$PDeltaTransf; 
element	elasticBeamColumn	3331341	331	341	[lindex $InteriorColumnStory3 2]	$Es	[lindex $InteriorColumnStory3 6]	$PDeltaTransf; 
element	elasticBeamColumn	3431441	431	441	[lindex $ExteriorColumnStory3 2]	$Es	[lindex $ExteriorColumnStory3 6]	$PDeltaTransf; 
element	elasticBeamColumn	3534542	534	542	$AreaRigid	$Es	$IRigid	$PDeltaTransf; 

# Story 4 
element	elasticBeamColumn	3141151	141	151	[lindex $ExteriorColumnStory4 2]	$Es	[lindex $ExteriorColumnStory4 6]	$PDeltaTransf; 
element	elasticBeamColumn	3241251	241	251	[lindex $InteriorColumnStory4 2]	$Es	[lindex $InteriorColumnStory4 6]	$PDeltaTransf; 
element	elasticBeamColumn	3341351	341	351	[lindex $InteriorColumnStory4 2]	$Es	[lindex $InteriorColumnStory4 6]	$PDeltaTransf; 
element	elasticBeamColumn	3441451	441	451	[lindex $ExteriorColumnStory4 2]	$Es	[lindex $ExteriorColumnStory4 6]	$PDeltaTransf; 
element	elasticBeamColumn	3544552	544	552	$AreaRigid	$Es	$IRigid	$PDeltaTransf; 

# Story 5 
element	elasticBeamColumn	3151161	151	161	[lindex $ExteriorColumnStory5 2]	$Es	[lindex $ExteriorColumnStory5 6]	$PDeltaTransf; 
element	elasticBeamColumn	3251261	251	261	[lindex $InteriorColumnStory5 2]	$Es	[lindex $InteriorColumnStory5 6]	$PDeltaTransf; 
element	elasticBeamColumn	3351361	351	361	[lindex $InteriorColumnStory5 2]	$Es	[lindex $InteriorColumnStory5 6]	$PDeltaTransf; 
element	elasticBeamColumn	3451461	451	461	[lindex $ExteriorColumnStory5 2]	$Es	[lindex $ExteriorColumnStory5 6]	$PDeltaTransf; 
element	elasticBeamColumn	3554562	554	562	$AreaRigid	$Es	$IRigid	$PDeltaTransf; 

# Story 6 
element	elasticBeamColumn	3161171	161	171	[lindex $ExteriorColumnStory6 2]	$Es	[lindex $ExteriorColumnStory6 6]	$PDeltaTransf; 
element	elasticBeamColumn	3261271	261	271	[lindex $InteriorColumnStory6 2]	$Es	[lindex $InteriorColumnStory6 6]	$PDeltaTransf; 
element	elasticBeamColumn	3361371	361	371	[lindex $InteriorColumnStory6 2]	$Es	[lindex $InteriorColumnStory6 6]	$PDeltaTransf; 
element	elasticBeamColumn	3461471	461	471	[lindex $ExteriorColumnStory6 2]	$Es	[lindex $ExteriorColumnStory6 6]	$PDeltaTransf; 
element	elasticBeamColumn	3564572	564	572	$AreaRigid	$Es	$IRigid	$PDeltaTransf; 

# Story 7 
element	elasticBeamColumn	3171181	171	181	[lindex $ExteriorColumnStory7 2]	$Es	[lindex $ExteriorColumnStory7 6]	$PDeltaTransf; 
element	elasticBeamColumn	3271281	271	281	[lindex $InteriorColumnStory7 2]	$Es	[lindex $InteriorColumnStory7 6]	$PDeltaTransf; 
element	elasticBeamColumn	3371381	371	381	[lindex $InteriorColumnStory7 2]	$Es	[lindex $InteriorColumnStory7 6]	$PDeltaTransf; 
element	elasticBeamColumn	3471481	471	481	[lindex $ExteriorColumnStory7 2]	$Es	[lindex $ExteriorColumnStory7 6]	$PDeltaTransf; 
element	elasticBeamColumn	3574582	574	582	$AreaRigid	$Es	$IRigid	$PDeltaTransf; 

# Story 8 
element	elasticBeamColumn	3181191	181	191	[lindex $ExteriorColumnStory8 2]	$Es	[lindex $ExteriorColumnStory8 6]	$PDeltaTransf; 
element	elasticBeamColumn	3281291	281	291	[lindex $InteriorColumnStory8 2]	$Es	[lindex $InteriorColumnStory8 6]	$PDeltaTransf; 
element	elasticBeamColumn	3381391	381	391	[lindex $InteriorColumnStory8 2]	$Es	[lindex $InteriorColumnStory8 6]	$PDeltaTransf; 
element	elasticBeamColumn	3481491	481	491	[lindex $ExteriorColumnStory8 2]	$Es	[lindex $ExteriorColumnStory8 6]	$PDeltaTransf; 
element	elasticBeamColumn	3584592	584	592	$AreaRigid	$Es	$IRigid	$PDeltaTransf; 

# Story 9 
element	elasticBeamColumn	31911101	191	1101	[lindex $ExteriorColumnStory9 2]	$Es	[lindex $ExteriorColumnStory9 6]	$PDeltaTransf; 
element	elasticBeamColumn	32912101	291	2101	[lindex $InteriorColumnStory9 2]	$Es	[lindex $InteriorColumnStory9 6]	$PDeltaTransf; 
element	elasticBeamColumn	33913101	391	3101	[lindex $InteriorColumnStory9 2]	$Es	[lindex $InteriorColumnStory9 6]	$PDeltaTransf; 
element	elasticBeamColumn	34914101	491	4101	[lindex $ExteriorColumnStory9 2]	$Es	[lindex $ExteriorColumnStory9 6]	$PDeltaTransf; 
element	elasticBeamColumn	35945102	594	5102	$AreaRigid	$Es	$IRigid	$PDeltaTransf; 

# puts "Columns defined"