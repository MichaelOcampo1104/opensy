# This file will be used to define all nodes 
# Units: inch


# Set bay width and story height
set	BayWidth	[expr 40.00*12]; 
set	FirstStory	[expr 26.00*12]; 
set	TypicalStory	[expr 13.00*12]; 

# Set panel zone size as column depth and beam depth
# Level 1 
set	PanelSizeLevel1Column1	[list 0 0];# No panel zone on ground floor so using [0, 0] is okay
set	PanelSizeLevel1Column2	[list 0 0];# No panel zone on ground floor so using [0, 0] is okay
set	PanelSizeLevel1Column3	[list 0 0];# No panel zone on ground floor so using [0, 0] is okay
set	PanelSizeLevel1Column4	[list 0 0];# No panel zone on ground floor so using [0, 0] is okay
# Level 2 
set	PanelSizeLevel2Column1	[list 22.4 36.9];
set	PanelSizeLevel2Column2	[list 22.4 36.9];
set	PanelSizeLevel2Column3	[list 22.4 36.9];
set	PanelSizeLevel2Column4	[list 22.4 36.9];
# Level 3 
set	PanelSizeLevel3Column1	[list 22.4 36.9];
set	PanelSizeLevel3Column2	[list 22.4 36.9];
set	PanelSizeLevel3Column3	[list 22.4 36.9];
set	PanelSizeLevel3Column4	[list 22.4 36.9];
# Level 4 
set	PanelSizeLevel4Column1	[list 19.0 36.5];
set	PanelSizeLevel4Column2	[list 20.2 36.5];
set	PanelSizeLevel4Column3	[list 20.2 36.5];
set	PanelSizeLevel4Column4	[list 19.0 36.5];
# Level 5 
set	PanelSizeLevel5Column1	[list 19.0 36.5];
set	PanelSizeLevel5Column2	[list 20.2 36.5];
set	PanelSizeLevel5Column3	[list 20.2 36.5];
set	PanelSizeLevel5Column4	[list 19.0 36.5];
# Level 6 
set	PanelSizeLevel6Column1	[list 18.3 28.4];
set	PanelSizeLevel6Column2	[list 19.6 28.4];
set	PanelSizeLevel6Column3	[list 19.6 28.4];
set	PanelSizeLevel6Column4	[list 18.3 28.4];
# Level 7 
set	PanelSizeLevel7Column1	[list 18.3 28.4];
set	PanelSizeLevel7Column2	[list 19.6 28.4];
set	PanelSizeLevel7Column3	[list 19.6 28.4];
set	PanelSizeLevel7Column4	[list 18.3 28.4];
# Level 8 
set	PanelSizeLevel8Column1	[list 17.5 27.8];
set	PanelSizeLevel8Column2	[list 18.7 27.8];
set	PanelSizeLevel8Column3	[list 18.7 27.8];
set	PanelSizeLevel8Column4	[list 17.5 27.8];
# Level 9 
set	PanelSizeLevel9Column1	[list 17.5 27.8];
set	PanelSizeLevel9Column2	[list 18.7 27.8];
set	PanelSizeLevel9Column3	[list 18.7 27.8];
set	PanelSizeLevel9Column4	[list 17.5 27.8];
# Level 10 
set	PanelSizeLevel10Column1	[list 14.7 21.6];
set	PanelSizeLevel10Column2	[list 15.2 21.6];
set	PanelSizeLevel10Column3	[list 15.2 21.6];
set	PanelSizeLevel10Column4	[list 14.7 21.6];

# Set max number of columns (excluding leaning column) and floors (counting 1 for ground)
set	MaximumFloor	10; 
set	MaximumCol	4; 

# Define nodes for the frame 
# Level 1 
NodesAroundPanelZone	1	1	[expr 0*$BayWidth]	[expr 0*$FirstStory+0*$TypicalStory]	$PanelSizeLevel1Column1	$MaximumFloor	$MaximumCol; 
NodesAroundPanelZone	2	1	[expr 1*$BayWidth]	[expr 0*$FirstStory+0*$TypicalStory]	$PanelSizeLevel1Column2	$MaximumFloor	$MaximumCol; 
NodesAroundPanelZone	3	1	[expr 2*$BayWidth]	[expr 0*$FirstStory+0*$TypicalStory]	$PanelSizeLevel1Column3	$MaximumFloor	$MaximumCol; 
NodesAroundPanelZone	4	1	[expr 3*$BayWidth]	[expr 0*$FirstStory+0*$TypicalStory]	$PanelSizeLevel1Column4	$MaximumFloor	$MaximumCol; 
# Level 2 
NodesAroundPanelZone	1	2	[expr 0*$BayWidth]	[expr 1*$FirstStory+0*$TypicalStory]	$PanelSizeLevel2Column1	$MaximumFloor	$MaximumCol; 
NodesAroundPanelZone	2	2	[expr 1*$BayWidth]	[expr 1*$FirstStory+0*$TypicalStory]	$PanelSizeLevel2Column2	$MaximumFloor	$MaximumCol; 
NodesAroundPanelZone	3	2	[expr 2*$BayWidth]	[expr 1*$FirstStory+0*$TypicalStory]	$PanelSizeLevel2Column3	$MaximumFloor	$MaximumCol; 
NodesAroundPanelZone	4	2	[expr 3*$BayWidth]	[expr 1*$FirstStory+0*$TypicalStory]	$PanelSizeLevel2Column4	$MaximumFloor	$MaximumCol; 
# Level 3 
NodesAroundPanelZone	1	3	[expr 0*$BayWidth]	[expr 1*$FirstStory+1*$TypicalStory]	$PanelSizeLevel3Column1	$MaximumFloor	$MaximumCol; 
NodesAroundPanelZone	2	3	[expr 1*$BayWidth]	[expr 1*$FirstStory+1*$TypicalStory]	$PanelSizeLevel3Column2	$MaximumFloor	$MaximumCol; 
NodesAroundPanelZone	3	3	[expr 2*$BayWidth]	[expr 1*$FirstStory+1*$TypicalStory]	$PanelSizeLevel3Column3	$MaximumFloor	$MaximumCol; 
NodesAroundPanelZone	4	3	[expr 3*$BayWidth]	[expr 1*$FirstStory+1*$TypicalStory]	$PanelSizeLevel3Column4	$MaximumFloor	$MaximumCol; 
# Level 4 
NodesAroundPanelZone	1	4	[expr 0*$BayWidth]	[expr 1*$FirstStory+2*$TypicalStory]	$PanelSizeLevel4Column1	$MaximumFloor	$MaximumCol; 
NodesAroundPanelZone	2	4	[expr 1*$BayWidth]	[expr 1*$FirstStory+2*$TypicalStory]	$PanelSizeLevel4Column2	$MaximumFloor	$MaximumCol; 
NodesAroundPanelZone	3	4	[expr 2*$BayWidth]	[expr 1*$FirstStory+2*$TypicalStory]	$PanelSizeLevel4Column3	$MaximumFloor	$MaximumCol; 
NodesAroundPanelZone	4	4	[expr 3*$BayWidth]	[expr 1*$FirstStory+2*$TypicalStory]	$PanelSizeLevel4Column4	$MaximumFloor	$MaximumCol; 
# Level 5 
NodesAroundPanelZone	1	5	[expr 0*$BayWidth]	[expr 1*$FirstStory+3*$TypicalStory]	$PanelSizeLevel5Column1	$MaximumFloor	$MaximumCol; 
NodesAroundPanelZone	2	5	[expr 1*$BayWidth]	[expr 1*$FirstStory+3*$TypicalStory]	$PanelSizeLevel5Column2	$MaximumFloor	$MaximumCol; 
NodesAroundPanelZone	3	5	[expr 2*$BayWidth]	[expr 1*$FirstStory+3*$TypicalStory]	$PanelSizeLevel5Column3	$MaximumFloor	$MaximumCol; 
NodesAroundPanelZone	4	5	[expr 3*$BayWidth]	[expr 1*$FirstStory+3*$TypicalStory]	$PanelSizeLevel5Column4	$MaximumFloor	$MaximumCol; 
# Level 6 
NodesAroundPanelZone	1	6	[expr 0*$BayWidth]	[expr 1*$FirstStory+4*$TypicalStory]	$PanelSizeLevel6Column1	$MaximumFloor	$MaximumCol; 
NodesAroundPanelZone	2	6	[expr 1*$BayWidth]	[expr 1*$FirstStory+4*$TypicalStory]	$PanelSizeLevel6Column2	$MaximumFloor	$MaximumCol; 
NodesAroundPanelZone	3	6	[expr 2*$BayWidth]	[expr 1*$FirstStory+4*$TypicalStory]	$PanelSizeLevel6Column3	$MaximumFloor	$MaximumCol; 
NodesAroundPanelZone	4	6	[expr 3*$BayWidth]	[expr 1*$FirstStory+4*$TypicalStory]	$PanelSizeLevel6Column4	$MaximumFloor	$MaximumCol; 
# Level 7 
NodesAroundPanelZone	1	7	[expr 0*$BayWidth]	[expr 1*$FirstStory+5*$TypicalStory]	$PanelSizeLevel7Column1	$MaximumFloor	$MaximumCol; 
NodesAroundPanelZone	2	7	[expr 1*$BayWidth]	[expr 1*$FirstStory+5*$TypicalStory]	$PanelSizeLevel7Column2	$MaximumFloor	$MaximumCol; 
NodesAroundPanelZone	3	7	[expr 2*$BayWidth]	[expr 1*$FirstStory+5*$TypicalStory]	$PanelSizeLevel7Column3	$MaximumFloor	$MaximumCol; 
NodesAroundPanelZone	4	7	[expr 3*$BayWidth]	[expr 1*$FirstStory+5*$TypicalStory]	$PanelSizeLevel7Column4	$MaximumFloor	$MaximumCol; 
# Level 8 
NodesAroundPanelZone	1	8	[expr 0*$BayWidth]	[expr 1*$FirstStory+6*$TypicalStory]	$PanelSizeLevel8Column1	$MaximumFloor	$MaximumCol; 
NodesAroundPanelZone	2	8	[expr 1*$BayWidth]	[expr 1*$FirstStory+6*$TypicalStory]	$PanelSizeLevel8Column2	$MaximumFloor	$MaximumCol; 
NodesAroundPanelZone	3	8	[expr 2*$BayWidth]	[expr 1*$FirstStory+6*$TypicalStory]	$PanelSizeLevel8Column3	$MaximumFloor	$MaximumCol; 
NodesAroundPanelZone	4	8	[expr 3*$BayWidth]	[expr 1*$FirstStory+6*$TypicalStory]	$PanelSizeLevel8Column4	$MaximumFloor	$MaximumCol; 
# Level 9 
NodesAroundPanelZone	1	9	[expr 0*$BayWidth]	[expr 1*$FirstStory+7*$TypicalStory]	$PanelSizeLevel9Column1	$MaximumFloor	$MaximumCol; 
NodesAroundPanelZone	2	9	[expr 1*$BayWidth]	[expr 1*$FirstStory+7*$TypicalStory]	$PanelSizeLevel9Column2	$MaximumFloor	$MaximumCol; 
NodesAroundPanelZone	3	9	[expr 2*$BayWidth]	[expr 1*$FirstStory+7*$TypicalStory]	$PanelSizeLevel9Column3	$MaximumFloor	$MaximumCol; 
NodesAroundPanelZone	4	9	[expr 3*$BayWidth]	[expr 1*$FirstStory+7*$TypicalStory]	$PanelSizeLevel9Column4	$MaximumFloor	$MaximumCol; 
# Level 10 
NodesAroundPanelZone	1	10	[expr 0*$BayWidth]	[expr 1*$FirstStory+8*$TypicalStory]	$PanelSizeLevel10Column1	$MaximumFloor	$MaximumCol; 
NodesAroundPanelZone	2	10	[expr 1*$BayWidth]	[expr 1*$FirstStory+8*$TypicalStory]	$PanelSizeLevel10Column2	$MaximumFloor	$MaximumCol; 
NodesAroundPanelZone	3	10	[expr 2*$BayWidth]	[expr 1*$FirstStory+8*$TypicalStory]	$PanelSizeLevel10Column3	$MaximumFloor	$MaximumCol; 
NodesAroundPanelZone	4	10	[expr 3*$BayWidth]	[expr 1*$FirstStory+8*$TypicalStory]	$PanelSizeLevel10Column4	$MaximumFloor	$MaximumCol; 

puts "Nodes for frame defined" 

# Define nodes for leaning column 
node	 51	[expr 4*$BayWidth]	[expr 0*$FirstStory+0*$TypicalStory];	#Level 1
node	 52	[expr 4*$BayWidth]	[expr 1*$FirstStory+0*$TypicalStory];	#Level 2
node	 53	[expr 4*$BayWidth]	[expr 1*$FirstStory+1*$TypicalStory];	# Level 3
node	 54	[expr 4*$BayWidth]	[expr 1*$FirstStory+2*$TypicalStory];	# Level 4
node	 55	[expr 4*$BayWidth]	[expr 1*$FirstStory+3*$TypicalStory];	# Level 5
node	 56	[expr 4*$BayWidth]	[expr 1*$FirstStory+4*$TypicalStory];	# Level 6
node	 57	[expr 4*$BayWidth]	[expr 1*$FirstStory+5*$TypicalStory];	# Level 7
node	 58	[expr 4*$BayWidth]	[expr 1*$FirstStory+6*$TypicalStory];	# Level 8
node	 59	[expr 4*$BayWidth]	[expr 1*$FirstStory+7*$TypicalStory];	# Level 9
node	 510	[expr 4*$BayWidth]	[expr 1*$FirstStory+8*$TypicalStory];	# Level 10

puts "Nodes for leaning column defined" 

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

puts "Extra nodes for leaning column springs defined"
