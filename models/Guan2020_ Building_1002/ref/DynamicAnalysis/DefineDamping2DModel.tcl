# This file will be used to define damping

# A damping ratio of 2% is used for steel buildings
set	dampingRatio	0.02;
# Define the value for pi
set	pi	[expr 2.0*asin(1.0)];

# Defining damping parameters
set	omegaI	[expr (2.0*$pi) / $periodForRayleighDamping_1];
set	omegaJ	[expr (2.0*$pi) / $periodForRayleighDamping_2];
set	alpha0	[expr ($dampingRatio*2.0*$omegaI*$omegaJ) / ($omegaI+$omegaJ)];
set	alpha1	[expr ($dampingRatio*2.0) / ($omegaI+$omegaJ) * ($n+1.0) / $n];	 # (n+1.0)/n factor is because stiffness for elastic elements have been modified

# Assign damping to beam elements
region	1	-ele	2121221	2221321	2321421	2131231	2231331	2331431	2141241	2241341	2341441	2151251	2251351	2351451	2161261	2261361	2361461	2171271	2271371	2371471	2181281	2281381	2381481	2191291	2291391	2391491	211012101	221013101	231014101	-rayleigh	0.0	0.0	$alpha1	0.0;
# Assign damping to column elements
region	2	-ele	3111121	3211221	3311321	3411421	3121131	3221231	3321331	3421431	3131141	3231241	3331341	3431441	3141151	3241251	3341351	3441451	3151161	3251261	3351361	3451461	3161171	3261271	3361371	3461471	3171181	3271281	3371381	3471481	3181191	3281291	3381391	3481491	31911101	32912101	33913101	34914101	-rayleigh	0.0	0.0	$alpha1	0.0;
# Assign damping to nodes
region	3	-node	1211	2211	3211	4211	52	1311	2311	3311	4311	53	1411	2411	3411	4411	54	1511	2511	3511	4511	55	1611	2611	3611	4611	56	1711	2711	3711	4711	57	1811	2811	3811	4811	58	1911	2911	3911	4911	59	11011	21011	31011	41011	510	-rayleigh	$alpha0	0.0	0.0	0.0;

puts "Rayleigh damping defined"