# This file will be used to define all nodes 
# Units: inch 


# Set bay width and story height 
set	BayWidth	[expr 20.00*12]; 
set	FirstStory	[expr 19.50*12]; 
set	TypicalStory	[expr 13.00*12]; 


# Define nodes at corner of frames 
# Level 1 
node	111	[expr 0*$BayWidth]	[expr 0*$FirstStory];	 # Column #1 
node	211	[expr 1*$BayWidth]	[expr 0*$FirstStory];	 # Column #2 

# Level 2 
node	121	[expr 0*$BayWidth]	[expr 1*$FirstStory];	 # Column #1 
node	221	[expr 1*$BayWidth]	[expr 1*$FirstStory];	 # Column #2 

# puts "Nodes at frame corner defined" 

# Define nodes for leaning column 
node	31	[expr 2*$BayWidth]	[expr 0*$FirstStory]; 	# Level 1
node	32	[expr 2*$BayWidth]	[expr 1*$FirstStory]; 	# Level 2

# puts "Nodes for leaning column defined" 

# Define extra nodes needed to define leaning column springs 
node	322	[expr 2*$BayWidth]	[expr 1*$FirstStory+0*$TypicalStory];	# Node below floor level 2

# puts "Extra nodes for leaning column springs defined"
