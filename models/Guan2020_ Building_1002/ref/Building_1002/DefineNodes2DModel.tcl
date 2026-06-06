# This file will be used to define all nodes 
# Units: inch 


# Set bay width and story height 
set	BayWidth	[expr 40.00*12]; 
set	FirstStory	[expr 26.00*12]; 
set	TypicalStory	[expr 13.00*12]; 


# Define nodes at corner of frames 
# Level 1 
node	111	[expr 0*$BayWidth]	[expr 0*$FirstStory];	 # Column #1 
node	211	[expr 1*$BayWidth]	[expr 0*$FirstStory];	 # Column #2 
node	311	[expr 2*$BayWidth]	[expr 0*$FirstStory];	 # Column #3 
node	411	[expr 3*$BayWidth]	[expr 0*$FirstStory];	 # Column #4 

# Level 2 
node	121	[expr 0*$BayWidth]	[expr 1*$FirstStory];	 # Column #1 
node	221	[expr 1*$BayWidth]	[expr 1*$FirstStory];	 # Column #2 
node	321	[expr 2*$BayWidth]	[expr 1*$FirstStory];	 # Column #3 
node	421	[expr 3*$BayWidth]	[expr 1*$FirstStory];	 # Column #4 

# Level 3 
node	131	[expr 0*$BayWidth]	[expr 1*$FirstStory+1*$TypicalStory];	 # Column #1 
node	231	[expr 1*$BayWidth]	[expr 1*$FirstStory+1*$TypicalStory];	 # Column #2 
node	331	[expr 2*$BayWidth]	[expr 1*$FirstStory+1*$TypicalStory];	 # Column #3 
node	431	[expr 3*$BayWidth]	[expr 1*$FirstStory+1*$TypicalStory];	 # Column #4 

# Level 4 
node	141	[expr 0*$BayWidth]	[expr 1*$FirstStory+2*$TypicalStory];	 # Column #1 
node	241	[expr 1*$BayWidth]	[expr 1*$FirstStory+2*$TypicalStory];	 # Column #2 
node	341	[expr 2*$BayWidth]	[expr 1*$FirstStory+2*$TypicalStory];	 # Column #3 
node	441	[expr 3*$BayWidth]	[expr 1*$FirstStory+2*$TypicalStory];	 # Column #4 

# Level 5 
node	151	[expr 0*$BayWidth]	[expr 1*$FirstStory+3*$TypicalStory];	 # Column #1 
node	251	[expr 1*$BayWidth]	[expr 1*$FirstStory+3*$TypicalStory];	 # Column #2 
node	351	[expr 2*$BayWidth]	[expr 1*$FirstStory+3*$TypicalStory];	 # Column #3 
node	451	[expr 3*$BayWidth]	[expr 1*$FirstStory+3*$TypicalStory];	 # Column #4 

# Level 6 
node	161	[expr 0*$BayWidth]	[expr 1*$FirstStory+4*$TypicalStory];	 # Column #1 
node	261	[expr 1*$BayWidth]	[expr 1*$FirstStory+4*$TypicalStory];	 # Column #2 
node	361	[expr 2*$BayWidth]	[expr 1*$FirstStory+4*$TypicalStory];	 # Column #3 
node	461	[expr 3*$BayWidth]	[expr 1*$FirstStory+4*$TypicalStory];	 # Column #4 

# Level 7 
node	171	[expr 0*$BayWidth]	[expr 1*$FirstStory+5*$TypicalStory];	 # Column #1 
node	271	[expr 1*$BayWidth]	[expr 1*$FirstStory+5*$TypicalStory];	 # Column #2 
node	371	[expr 2*$BayWidth]	[expr 1*$FirstStory+5*$TypicalStory];	 # Column #3 
node	471	[expr 3*$BayWidth]	[expr 1*$FirstStory+5*$TypicalStory];	 # Column #4 

# Level 8 
node	181	[expr 0*$BayWidth]	[expr 1*$FirstStory+6*$TypicalStory];	 # Column #1 
node	281	[expr 1*$BayWidth]	[expr 1*$FirstStory+6*$TypicalStory];	 # Column #2 
node	381	[expr 2*$BayWidth]	[expr 1*$FirstStory+6*$TypicalStory];	 # Column #3 
node	481	[expr 3*$BayWidth]	[expr 1*$FirstStory+6*$TypicalStory];	 # Column #4 

# Level 9 
node	191	[expr 0*$BayWidth]	[expr 1*$FirstStory+7*$TypicalStory];	 # Column #1 
node	291	[expr 1*$BayWidth]	[expr 1*$FirstStory+7*$TypicalStory];	 # Column #2 
node	391	[expr 2*$BayWidth]	[expr 1*$FirstStory+7*$TypicalStory];	 # Column #3 
node	491	[expr 3*$BayWidth]	[expr 1*$FirstStory+7*$TypicalStory];	 # Column #4 

# Level 10 
node	1101	[expr 0*$BayWidth]	[expr 1*$FirstStory+8*$TypicalStory];	 # Column #1 
node	2101	[expr 1*$BayWidth]	[expr 1*$FirstStory+8*$TypicalStory];	 # Column #2 
node	3101	[expr 2*$BayWidth]	[expr 1*$FirstStory+8*$TypicalStory];	 # Column #3 
node	4101	[expr 3*$BayWidth]	[expr 1*$FirstStory+8*$TypicalStory];	 # Column #4 

# puts "Nodes at frame corner defined" 

# Define nodes for leaning column 
node	51	[expr 4*$BayWidth]	[expr 0*$FirstStory]; 	# Level 1
node	52	[expr 4*$BayWidth]	[expr 1*$FirstStory]; 	# Level 2
node	53	[expr 4*$BayWidth]	[expr 1*$FirstStory+1*$TypicalStory];	# Level 3
node	54	[expr 4*$BayWidth]	[expr 1*$FirstStory+2*$TypicalStory];	# Level 4
node	55	[expr 4*$BayWidth]	[expr 1*$FirstStory+3*$TypicalStory];	# Level 5
node	56	[expr 4*$BayWidth]	[expr 1*$FirstStory+4*$TypicalStory];	# Level 6
node	57	[expr 4*$BayWidth]	[expr 1*$FirstStory+5*$TypicalStory];	# Level 7
node	58	[expr 4*$BayWidth]	[expr 1*$FirstStory+6*$TypicalStory];	# Level 8
node	59	[expr 4*$BayWidth]	[expr 1*$FirstStory+7*$TypicalStory];	# Level 9
node	510	[expr 4*$BayWidth]	[expr 1*$FirstStory+8*$TypicalStory];	# Level 10

# puts "Nodes for leaning column defined" 

# Define extra nodes needed to define leaning column springs 
node	522	[expr 4*$BayWidth]	[expr 1*$FirstStory+0*$TypicalStory];	# Node below floor level 2
node	524	[expr 4*$BayWidth]	[expr 1*$FirstStory+0*$TypicalStory];	# Node above floor level 2
node	532	[expr 4*$BayWidth]	[expr 1*$FirstStory+1*$TypicalStory];	# Node below floor level 3
node	534	[expr 4*$BayWidth]	[expr 1*$FirstStory+1*$TypicalStory];	# Node above floor level 3
node	542	[expr 4*$BayWidth]	[expr 1*$FirstStory+2*$TypicalStory];	# Node below floor level 4
node	544	[expr 4*$BayWidth]	[expr 1*$FirstStory+2*$TypicalStory];	# Node above floor level 4
node	552	[expr 4*$BayWidth]	[expr 1*$FirstStory+3*$TypicalStory];	# Node below floor level 5
node	554	[expr 4*$BayWidth]	[expr 1*$FirstStory+3*$TypicalStory];	# Node above floor level 5
node	562	[expr 4*$BayWidth]	[expr 1*$FirstStory+4*$TypicalStory];	# Node below floor level 6
node	564	[expr 4*$BayWidth]	[expr 1*$FirstStory+4*$TypicalStory];	# Node above floor level 6
node	572	[expr 4*$BayWidth]	[expr 1*$FirstStory+5*$TypicalStory];	# Node below floor level 7
node	574	[expr 4*$BayWidth]	[expr 1*$FirstStory+5*$TypicalStory];	# Node above floor level 7
node	582	[expr 4*$BayWidth]	[expr 1*$FirstStory+6*$TypicalStory];	# Node below floor level 8
node	584	[expr 4*$BayWidth]	[expr 1*$FirstStory+6*$TypicalStory];	# Node above floor level 8
node	592	[expr 4*$BayWidth]	[expr 1*$FirstStory+7*$TypicalStory];	# Node below floor level 9
node	594	[expr 4*$BayWidth]	[expr 1*$FirstStory+7*$TypicalStory];	# Node above floor level 9
node	5102	[expr 4*$BayWidth]	[expr 1*$FirstStory+8*$TypicalStory];	# Node below floor level 10

# puts "Extra nodes for leaning column springs defined"
