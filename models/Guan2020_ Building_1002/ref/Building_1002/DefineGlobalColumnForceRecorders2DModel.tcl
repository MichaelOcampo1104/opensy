# Define global column force recorders


cd	$baseDir/$dataDir/GlobalColumnForces

# X-Direction frame column element global force recorders
recorder	Element	-file	GlobalColumnForcesStory1.out	-time	-ele	3111121	3211221	3311321	3411421	force;
recorder	Element	-file	GlobalColumnForcesStory2.out	-time	-ele	3121131	3221231	3321331	3421431	force;
recorder	Element	-file	GlobalColumnForcesStory3.out	-time	-ele	3131141	3231241	3331341	3431441	force;
recorder	Element	-file	GlobalColumnForcesStory4.out	-time	-ele	3141151	3241251	3341351	3441451	force;
recorder	Element	-file	GlobalColumnForcesStory5.out	-time	-ele	3151161	3251261	3351361	3451461	force;
recorder	Element	-file	GlobalColumnForcesStory6.out	-time	-ele	3161171	3261271	3361371	3461471	force;
recorder	Element	-file	GlobalColumnForcesStory7.out	-time	-ele	3171181	3271281	3371381	3471481	force;
recorder	Element	-file	GlobalColumnForcesStory8.out	-time	-ele	3181191	3281291	3381391	3481491	force;
recorder	Element	-file	GlobalColumnForcesStory9.out	-time	-ele	31911101	32912101	33913101	34914101	force;
