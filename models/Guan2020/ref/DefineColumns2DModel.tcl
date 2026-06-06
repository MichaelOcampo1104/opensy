# This file will be used to define columns 


# Define exterior column section sizes 
set	ExteriorColumnStory1	[SectionProperty W14X370]; 


# Define interior column section sizes 
set	InteriorColumnStory1	[SectionProperty W14X455]; 


# Define columns
# Story 1 
element	elasticBeamColumn	3111121	111	121	[lindex $ExteriorColumnStory1 2]	$Es	[lindex $ExteriorColumnStory1 6]	$PDeltaTransf; 
element	elasticBeamColumn	3211221	211	221	[lindex $ExteriorColumnStory1 2]	$Es	[lindex $ExteriorColumnStory1 6]	$PDeltaTransf; 
element	elasticBeamColumn	331322	31	322	$AreaRigid	$Es	$IRigid	$PDeltaTransf; 

# puts "Columns defined"