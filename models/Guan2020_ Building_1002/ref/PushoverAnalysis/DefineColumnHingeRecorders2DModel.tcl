# Define column hinge force-deformation recorders


cd	$baseDir/$dataDir/ColumnHingeMoment

# Column hinge element force recorders
recorder	Element	-file	ColumnHingeForcesStory1.out	-time	-ele	6111014	6121216	6211014	6221216	6311014	6321216	6411014	6421216	force;
recorder	Element	-file	ColumnHingeForcesStory2.out	-time	-ele	6121014	6131216	6221014	6231216	6321014	6331216	6421014	6431216	force;
recorder	Element	-file	ColumnHingeForcesStory3.out	-time	-ele	6131014	6141216	6231014	6241216	6331014	6341216	6431014	6441216	force;
recorder	Element	-file	ColumnHingeForcesStory4.out	-time	-ele	6141014	6151216	6241014	6251216	6341014	6351216	6441014	6451216	force;
recorder	Element	-file	ColumnHingeForcesStory5.out	-time	-ele	6151014	6161216	6251014	6261216	6351014	6361216	6451014	6461216	force;
recorder	Element	-file	ColumnHingeForcesStory6.out	-time	-ele	6161014	6171216	6261014	6271216	6361014	6371216	6461014	6471216	force;
recorder	Element	-file	ColumnHingeForcesStory7.out	-time	-ele	6171014	6181216	6271014	6281216	6371014	6381216	6471014	6481216	force;
recorder	Element	-file	ColumnHingeForcesStory8.out	-time	-ele	6181014	6191216	6281014	6291216	6381014	6391216	6481014	6491216	force;
recorder	Element	-file	ColumnHingeForcesStory9.out	-time	-ele	6191014	61101216	6291014	62101216	6391014	63101216	6491014	64101216	force;

cd	$baseDir/$dataDir/ColumnHingeDeformations

# Column hinge element deformation recorders
recorder	Element	-file	ColumnHingeForcesStory1.out	-time	-ele	6111014	6121216	6211014	6221216	6311014	6321216	6411014	6421216	deformation;recorder	Element	-file	ColumnHingeForcesStory2.out	-time	-ele	6121014	6131216	6221014	6231216	6321014	6331216	6421014	6431216	deformation;recorder	Element	-file	ColumnHingeForcesStory3.out	-time	-ele	6131014	6141216	6231014	6241216	6331014	6341216	6431014	6441216	deformation;recorder	Element	-file	ColumnHingeForcesStory4.out	-time	-ele	6141014	6151216	6241014	6251216	6341014	6351216	6441014	6451216	deformation;recorder	Element	-file	ColumnHingeForcesStory5.out	-time	-ele	6151014	6161216	6251014	6261216	6351014	6361216	6451014	6461216	deformation;recorder	Element	-file	ColumnHingeForcesStory6.out	-time	-ele	6161014	6171216	6261014	6271216	6361014	6371216	6461014	6471216	deformation;recorder	Element	-file	ColumnHingeForcesStory7.out	-time	-ele	6171014	6181216	6271014	6281216	6371014	6381216	6471014	6481216	deformation;recorder	Element	-file	ColumnHingeForcesStory8.out	-time	-ele	6181014	6191216	6281014	6291216	6381014	6391216	6481014	6491216	deformation;recorder	Element	-file	ColumnHingeForcesStory9.out	-time	-ele	6191014	61101216	6291014	62101216	6391014	63101216	6491014	64101216	deformation;
