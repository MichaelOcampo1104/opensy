# Define node displacement recorders


cd	$baseDir/$dataDir/NodeDisplacements

recorder	Node	-file	NodeDisplacementLevel1.out	-time	-node	111	211	-dof	1	2	3	disp; 
recorder	Node	-file	NodeDisplacementLevel2.out	-time	-node	121	221	-dof	1	2	3	disp; 
