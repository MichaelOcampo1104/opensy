# ===================================================================================================================================================================================
# This script defines all the material properties used to model bolted-bolted angles based on tests by (*@\cite{Beland2017}??@*).
uniaxialMaterial	Elastic     	1 	+2.900000e-04	             	             	             	             	             	             	             	;# E*10^-8                	
uniaxialMaterial	Elastic     	2 	+2.900000e-03	             	             	             	             	             	             	             	;# E*10^-7                	
uniaxialMaterial	Elastic     	3 	+2.900000e-02	             	             	             	             	             	             	             	;# E*10^-6                	
uniaxialMaterial	Elastic     	4 	+2.900000e-01	             	             	             	             	             	             	             	;# E*10^-5                	
uniaxialMaterial	Elastic     	5 	+2.900000e+00	             	             	             	             	             	             	             	;# E*10^-4                	
uniaxialMaterial	Elastic     	6 	+2.900000e+01	             	             	             	             	             	             	             	;# E*10^-3                	
uniaxialMaterial	Elastic     	7 	+2.900000e+02	             	             	             	             	             	             	             	;# E*10^-2                	
uniaxialMaterial	Elastic     	8 	+2.900000e+03	             	             	             	             	             	             	             	;# E*10^-1                	
uniaxialMaterial	Elastic     	9 	+2.900000e+04	             	             	             	             	             	             	             	;# E*10^+0                	
uniaxialMaterial	Elastic     	10	+2.900000e+07	             	             	             	             	             	             	             	;# E*10^+3                	
uniaxialMaterial	ENT         	11	+2.900000e+07	             	             	             	             	             	             	             	;# Bolt Bearing           	
uniaxialMaterial	ElasticPPGap	12	+2.900000e+02	-5.500000e+01	-5.000000e-01	             	             	             	             	             	;# B2C Gap                	
uniaxialMaterial	ElasticPPGap	13	+2.900000e+02	-4.680000e+01	-5.000000e-01	             	             	             	             	             	;# G2C Gap                	
uniaxialMaterial	Parallel    	14	12 3         	             	             	             	             	             	             	             	;# B2C Contact            	
uniaxialMaterial	Parallel    	15	13 3         	             	             	             	             	             	             	             	;# G2C Contact            	
uniaxialMaterial	SteelMPF    	16	+2.163846e+01	+2.163846e+01	+1.987230e+03	+1.290000e-02	+1.290000e-02	+1.118000e+00	-9.440000e-01	+2.283465e-01	;# TC1-L6X4X3/8           	
uniaxialMaterial	Fatigue     	17	16           	-E0          	+1.785000e+00	             	             	             	             	             	;# TC1-L6X4X3/8           	
uniaxialMaterial	MinMax      	18	17           	-min         	-1.000000e+09	-max         	+1.000000e+00	             	             	             	;# TC1-L6X4X3/8           	
uniaxialMaterial	Parallel    	19	3 11 18      	             	             	             	             	             	             	             	;# TC1-L6X4X3/8           	
uniaxialMaterial	SteelMPF    	20	+1.782383e+01	+1.782383e+01	+1.770234e+03	+1.550000e-02	+1.550000e-02	+1.114000e+00	-1.306000e+00	+1.771654e-01	;# TC2-L6X6X3/8           	
uniaxialMaterial	Fatigue     	21	20           	-E0          	+1.980000e+00	             	             	             	             	             	;# TC2-L6X6X3/8           	
uniaxialMaterial	MinMax      	22	21           	-min         	-1.000000e+09	-max         	+1.318898e+00	             	             	             	;# TC2-L6X6X3/8           	
uniaxialMaterial	Parallel    	23	3 11 22      	             	             	             	             	             	             	             	;# TC2-L6X6X3/8           	
uniaxialMaterial	SteelMPF    	24	+4.412014e+01	+4.412014e+01	+5.156520e+03	+1.700000e-02	+1.700000e-02	+1.803000e+00	-6.330000e-01	+1.023622e-01	;# TC3-L8X4X1/2           	
uniaxialMaterial	Fatigue     	25	24           	-E0          	+1.200000e+00	             	             	             	             	             	;# TC3-L8X4X1/2           	
uniaxialMaterial	MinMax      	26	25           	-min         	-1.000000e+09	-max         	+7.047244e-01	             	             	             	;# TC3-L8X4X1/2           	
uniaxialMaterial	Parallel    	27	3 11 26      	             	             	             	             	             	             	             	;# TC3-L8X4X1/2           	
uniaxialMaterial	SteelMPF    	28	+4.114240e+01	+4.114240e+01	+3.117896e+03	+1.370000e-02	+1.370000e-02	+1.451000e+00	-7.330000e-01	+2.007874e-01	;# TC4-L8X6X1/2           	
uniaxialMaterial	Fatigue     	29	28           	-E0          	+1.785000e+00	             	             	             	             	             	;# TC4-L8X6X1/2           	
uniaxialMaterial	MinMax      	30	29           	-min         	-1.000000e+09	-max         	+1.543307e+00	             	             	             	;# TC4-L8X6X1/2           	
uniaxialMaterial	Parallel    	31	3 11 30      	             	             	             	             	             	             	             	;# TC4-L8X6X1/2           	
uniaxialMaterial	SteelMPF    	32	+6.027185e+01	+6.027185e+01	+1.245445e+04	+4.600000e-03	+4.600000e-03	+1.625000e+00	-1.030000e+00	+1.574803e-01	;# TC5-L8X6X5/8           	
uniaxialMaterial	Fatigue     	33	32           	-E0          	+1.955000e+00	             	             	             	             	             	;# TC5-L8X6X5/8           	
uniaxialMaterial	MinMax      	34	33           	-min         	-1.000000e+09	-max         	+1.374016e+00	             	             	             	;# TC5-L8X6X5/8           	
uniaxialMaterial	Parallel    	35	3 11 34      	             	             	             	             	             	             	             	;# TC5-L8X6X5/8           	
uniaxialMaterial	SteelMPF    	36	+8.490335e+01	+8.490335e+01	+1.134663e+04	+4.100000e-03	+4.100000e-03	+1.311000e+00	-9.320000e-01	+1.417323e-01	;# TC6-L8X6X3/4           	
uniaxialMaterial	Fatigue     	37	36           	-E0          	+1.565000e+00	             	             	             	             	             	;# TC6-L8X6X3/4           	
uniaxialMaterial	MinMax      	38	37           	-min         	-1.000000e+09	-max         	+1.086614e+00	             	             	             	;# TC6-L8X6X3/4           	
uniaxialMaterial	Parallel    	39	3 11 38      	             	             	             	             	             	             	             	;# TC6-L8X6X3/4           	
uniaxialMaterial	SteelMPF    	40	+1.686769e+01	+1.686769e+01	+8.223022e+02	+2.410000e-02	+2.410000e-02	+1.314000e+00	-1.140000e+00	+2.559055e-01	;# TC7-L6X6X3/8           	
uniaxialMaterial	Fatigue     	41	40           	-E0          	+2.190000e+00	             	             	             	             	             	;# TC7-L6X6X3/8           	
uniaxialMaterial	MinMax      	42	41           	-min         	-1.000000e+09	-max         	+1.370079e+00	             	             	             	;# TC7-L6X6X3/8           	
uniaxialMaterial	Parallel    	43	3 11 42      	             	             	             	             	             	             	             	;# TC7-L6X6X3/8           	
uniaxialMaterial	SteelMPF    	44	+1.587423e+01	+1.587423e+01	+7.937500e+02	+1.580000e-02	+1.580000e-02	+9.390000e-01	-1.323000e+00	+2.283465e-01	;# TC8-L6X6X3/8           	
uniaxialMaterial	Fatigue     	45	44           	-E0          	+2.612000e+00	             	             	             	             	             	;# TC8-L6X6X3/8           	
uniaxialMaterial	MinMax      	46	45           	-min         	-1.000000e+09	-max         	+1.452756e+00	             	             	             	;# TC8-L6X6X3/8           	
uniaxialMaterial	Parallel    	47	3 11 46      	             	             	             	             	             	             	             	;# TC8-L6X6X3/8           	
uniaxialMaterial	SteelMPF    	48	+3.474998e+01	+3.474998e+01	+2.158543e+03	+1.330000e-02	+1.330000e-02	+1.687000e+00	-5.180000e-01	+2.165354e-01	;# TC9-L8X6X1/2           	
uniaxialMaterial	Fatigue     	49	48           	-E0          	+2.185000e+00	             	             	             	             	             	;# TC9-L8X6X1/2           	
uniaxialMaterial	MinMax      	50	49           	-min         	-1.000000e+09	-max         	+1.799213e+00	             	             	             	;# TC9-L8X6X1/2           	
uniaxialMaterial	Parallel    	51	3 11 50      	             	             	             	             	             	             	             	;# TC9-L8X6X1/2           	
uniaxialMaterial	SteelMPF    	52	+2.614896e+01	+2.614896e+01	+2.272752e+03	+1.250000e-02	+1.250000e-02	+1.751000e+00	-6.390000e-01	+2.322835e-01	;# TC10-L8X6X1/2          	
uniaxialMaterial	Fatigue     	53	52           	-E0          	+2.390000e+00	             	             	             	             	             	;# TC10-L8X6X1/2          	
uniaxialMaterial	MinMax      	54	53           	-min         	-1.000000e+09	-max         	+1.559055e+00	             	             	             	;# TC10-L8X6X1/2          	
uniaxialMaterial	Parallel    	55	3 11 54      	             	             	             	             	             	             	             	;# TC10-L8X6X1/2          	
uniaxialMaterial	SteelMPF    	56	+4.947856e+01	+4.947856e+01	+5.127968e+03	+1.050000e-02	+1.050000e-02	+1.211000e+00	-9.350000e-01	+2.125984e-01	;# TC11-L8X6X5/8          	
uniaxialMaterial	Fatigue     	57	56           	-E0          	+1.840000e+00	             	             	             	             	             	;# TC11-L8X6X5/8          	
uniaxialMaterial	MinMax      	58	57           	-min         	-1.000000e+09	-max         	+6.062992e-01	             	             	             	;# TC11-L8X6X5/8          	
uniaxialMaterial	Parallel    	59	3 11 58      	             	             	             	             	             	             	             	;# TC11-L8X6X5/8          	
uniaxialMaterial	SteelMPF    	60	+4.215443e+01	+4.215443e+01	+5.476304e+03	+7.800000e-03	+7.800000e-03	+1.218000e+00	-8.610000e-01	+2.165354e-01	;# TC12-L8X6X5/8          	
uniaxialMaterial	Fatigue     	61	60           	-E0          	+1.960000e+00	             	             	             	             	             	;# TC12-L8X6X5/8          	
uniaxialMaterial	MinMax      	62	61           	-min         	-1.000000e+09	-max         	+1.405512e+00	             	             	             	;# TC12-L8X6X5/8          	
uniaxialMaterial	Parallel    	63	3 11 62      	             	             	             	             	             	             	             	;# TC12-L8X6X5/8          	
uniaxialMaterial	SteelMPF    	64	+6.940074e+01	+6.940074e+01	+9.679182e+03	+7.700000e-03	+7.700000e-03	+8.950000e-01	-1.162000e+00	+1.653543e-01	;# TC13-L8X6X3/4          	
uniaxialMaterial	Fatigue     	65	64           	-E0          	+1.960000e+00	             	             	             	             	             	;# TC13-L8X6X3/4          	
uniaxialMaterial	MinMax      	66	65           	-min         	-1.000000e+09	-max         	+1.003937e+00	             	             	             	;# TC13-L8X6X3/4          	
uniaxialMaterial	Parallel    	67	3 11 66      	             	             	             	             	             	             	             	;# TC13-L8X6X3/4          	
uniaxialMaterial	SteelMPF    	68	+5.711590e+01	+5.711590e+01	+7.149460e+03	+1.000000e-02	+1.000000e-02	+1.079000e+00	-1.088000e+00	+2.165354e-01	;# TC14-L8X6X3/4          	
uniaxialMaterial	Fatigue     	69	68           	-E0          	+1.840000e+00	             	             	             	             	             	;# TC14-L8X6X3/4          	
uniaxialMaterial	MinMax      	70	69           	-min         	-1.000000e+09	-max         	+8.700787e-01	             	             	             	;# TC14-L8X6X3/4          	
uniaxialMaterial	Parallel    	71	3 11 70      	             	             	             	             	             	             	             	;# TC14-L8X6X3/4          	
uniaxialMaterial	SteelMPF    	72	+1.116810e+01	+1.116810e+01	+4.054406e+02	+2.630000e-02	+2.630000e-02	+1.179000e+00	-1.369000e+00	+2.716535e-01	;# TC15-L6X6X3/8          	
uniaxialMaterial	Fatigue     	73	72           	-E0          	+2.390000e+00	             	             	             	             	             	;# TC15-L6X6X3/8          	
uniaxialMaterial	MinMax      	74	73           	-min         	-1.000000e+09	-max         	+1.905512e+00	             	             	             	;# TC15-L6X6X3/8          	
uniaxialMaterial	Parallel    	75	3 11 74      	             	             	             	             	             	             	             	;# TC15-L6X6X3/8          	
uniaxialMaterial	SteelMPF    	76	+2.369175e+01	+2.369175e+01	+2.095728e+03	+1.160000e-02	+1.160000e-02	+1.218000e+00	-8.760000e-01	+2.874016e-01	;# TC16-L8X6X1/2          	
uniaxialMaterial	Fatigue     	77	76           	-E0          	+1.785000e+00	             	             	             	             	             	;# TC16-L8X6X1/2          	
uniaxialMaterial	MinMax      	78	77           	-min         	-1.000000e+09	-max         	+1.500000e+00	             	             	             	;# TC16-L8X6X1/2          	
uniaxialMaterial	Parallel    	79	3 11 78      	             	             	             	             	             	             	             	;# TC16-L8X6X1/2          	
uniaxialMaterial	SteelMPF    	80	+3.542065e+01	+3.542065e+01	+4.277113e+03	+6.500000e-03	+6.500000e-03	+1.492000e+00	-6.770000e-01	+1.929134e-01	;# TC17-L8X6X5/8          	
uniaxialMaterial	Fatigue     	81	80           	-E0          	+2.610000e+00	             	             	             	             	             	;# TC17-L8X6X5/8          	
uniaxialMaterial	MinMax      	82	81           	-min         	-1.000000e+09	-max         	+1.960630e+00	             	             	             	;# TC17-L8X6X5/8          	
uniaxialMaterial	Parallel    	83	3 11 82      	             	             	             	             	             	             	             	;# TC17-L8X6X5/8          	
uniaxialMaterial	SteelMPF    	84	+4.678394e+01	+4.678394e+01	+5.653327e+03	+5.500000e-03	+5.500000e-03	+1.526000e+00	-2.740000e-01	+1.889764e-01	;# TC18-L8X6X3/4          	
uniaxialMaterial	Fatigue     	85	84           	-E0          	+2.610000e+00	             	             	             	             	             	;# TC18-L8X6X3/4          	
uniaxialMaterial	MinMax      	86	85           	-min         	-1.000000e+09	-max         	+1.712598e+00	             	             	             	;# TC18-L8X6X3/4          	
uniaxialMaterial	Parallel    	87	3 11 86      	             	             	             	             	             	             	             	;# TC18-L8X6X3/4          	
uniaxialMaterial	SteelMPF    	88	+1.481612e+01	+1.481612e+01	+1.479002e+03	+1.150000e-02	+1.150000e-02	+1.433000e+00	-1.194000e+00	+1.889764e-01	;# TC19-L4X4X5/16         	
uniaxialMaterial	Fatigue     	89	88           	-E0          	+1.785000e+00	             	             	             	             	             	;# TC19-L4X4X5/16         	
uniaxialMaterial	MinMax      	90	89           	-min         	-1.000000e+09	-max         	+1.251969e+00	             	             	             	;# TC19-L4X4X5/16         	
uniaxialMaterial	Parallel    	91	3 11 90      	             	             	             	             	             	             	             	;# TC19-L4X4X5/16         	
# ===================================================================================================================================================================================
