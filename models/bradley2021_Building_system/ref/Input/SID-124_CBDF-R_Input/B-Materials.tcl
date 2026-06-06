# ===================================================================================================================================================================================
# This script defines all the material properties of the building models' elements, sections, and fibers.
uniaxialMaterial	Elastic     	1  	+2.900000e-04	             	             	             	             	             	             	             	               	;# E*10^-8
uniaxialMaterial	Elastic     	2  	+2.900000e-03	             	             	             	             	             	             	             	               	;# E*10^-7
uniaxialMaterial	Elastic     	3  	+2.900000e-02	             	             	             	             	             	             	             	               	;# E*10^-6
uniaxialMaterial	Elastic     	4  	+2.900000e-01	             	             	             	             	             	             	             	               	;# E*10^-5
uniaxialMaterial	Elastic     	5  	+2.900000e+00	             	             	             	             	             	             	             	               	;# E*10^-4
uniaxialMaterial	Elastic     	6  	+2.900000e+01	             	             	             	             	             	             	             	               	;# E*10^-3
uniaxialMaterial	Elastic     	7  	+2.900000e+02	             	             	             	             	             	             	             	               	;# E*10^-2
uniaxialMaterial	Elastic     	8  	+2.900000e+03	             	             	             	             	             	             	             	               	;# E*10^-1
uniaxialMaterial	Elastic     	9  	+2.900000e+04	             	             	             	             	             	             	             	               	;# E*10^+0
uniaxialMaterial	Elastic     	10 	+2.900000e+07	             	             	             	             	             	             	             	               	;# E*10^+3
uniaxialMaterial	ENT         	11 	+2.900000e+07	             	             	             	             	             	             	             	               	;# Bolt Bearing
uniaxialMaterial	ElasticPPGap	12 	+2.900000e+02	-5.500000e+01	-5.000000e-01	             	             	             	             	             	               	;# B2C Gap
uniaxialMaterial	ElasticPPGap	13 	+2.900000e+02	-4.680000e+01	-5.000000e-01	             	             	             	             	             	               	;# G2C Gap
uniaxialMaterial	Parallel    	14 	12 3         	             	             	             	             	             	             	             	               	;# B2C Contact
uniaxialMaterial	Parallel    	15 	13 3         	             	             	             	             	             	             	             	               	;# G2C Contact
uniaxialMaterial	SteelMPF    	16 	+2.163846e+01	+2.163846e+01	+1.987230e+03	+1.290000e-02	+1.290000e-02	+1.118000e+00	-9.440000e-01	+2.283465e-01	               	;# TC1-L6X4X3/8
uniaxialMaterial	Fatigue     	17 	16           	-E0          	+1.785000e+00	             	             	             	             	             	               	;# TC1-L6X4X3/8
uniaxialMaterial	MinMax      	18 	17           	-min         	-1.000000e+09	-max         	+1.000000e+00	             	             	             	               	;# TC1-L6X4X3/8
uniaxialMaterial	Parallel    	19 	3 11 18      	             	             	             	             	             	             	             	               	;# TC1-L6X4X3/8
uniaxialMaterial	SteelMPF    	20 	+1.782383e+01	+1.782383e+01	+1.770234e+03	+1.550000e-02	+1.550000e-02	+1.114000e+00	-1.306000e+00	+1.771654e-01	               	;# TC2-L6X6X3/8
uniaxialMaterial	Fatigue     	21 	20           	-E0          	+1.980000e+00	             	             	             	             	             	               	;# TC2-L6X6X3/8
uniaxialMaterial	MinMax      	22 	21           	-min         	-1.000000e+09	-max         	+1.318898e+00	             	             	             	               	;# TC2-L6X6X3/8
uniaxialMaterial	Parallel    	23 	3 11 22      	             	             	             	             	             	             	             	               	;# TC2-L6X6X3/8
uniaxialMaterial	SteelMPF    	24 	+4.412014e+01	+4.412014e+01	+5.156520e+03	+1.700000e-02	+1.700000e-02	+1.803000e+00	-6.330000e-01	+1.023622e-01	               	;# TC3-L8X4X1/2
uniaxialMaterial	Fatigue     	25 	24           	-E0          	+1.200000e+00	             	             	             	             	             	               	;# TC3-L8X4X1/2
uniaxialMaterial	MinMax      	26 	25           	-min         	-1.000000e+09	-max         	+7.047244e-01	             	             	             	               	;# TC3-L8X4X1/2
uniaxialMaterial	Parallel    	27 	3 11 26      	             	             	             	             	             	             	             	               	;# TC3-L8X4X1/2
uniaxialMaterial	SteelMPF    	28 	+4.114240e+01	+4.114240e+01	+3.117896e+03	+1.370000e-02	+1.370000e-02	+1.451000e+00	-7.330000e-01	+2.007874e-01	               	;# TC4-L8X6X1/2
uniaxialMaterial	Fatigue     	29 	28           	-E0          	+1.785000e+00	             	             	             	             	             	               	;# TC4-L8X6X1/2
uniaxialMaterial	MinMax      	30 	29           	-min         	-1.000000e+09	-max         	+1.543307e+00	             	             	             	               	;# TC4-L8X6X1/2
uniaxialMaterial	Parallel    	31 	3 11 30      	             	             	             	             	             	             	             	               	;# TC4-L8X6X1/2
uniaxialMaterial	SteelMPF    	32 	+6.027185e+01	+6.027185e+01	+1.245445e+04	+4.600000e-03	+4.600000e-03	+1.625000e+00	-1.030000e+00	+1.574803e-01	               	;# TC5-L8X6X5/8
uniaxialMaterial	Fatigue     	33 	32           	-E0          	+1.955000e+00	             	             	             	             	             	               	;# TC5-L8X6X5/8
uniaxialMaterial	MinMax      	34 	33           	-min         	-1.000000e+09	-max         	+1.374016e+00	             	             	             	               	;# TC5-L8X6X5/8
uniaxialMaterial	Parallel    	35 	3 11 34      	             	             	             	             	             	             	             	               	;# TC5-L8X6X5/8
uniaxialMaterial	SteelMPF    	36 	+8.490335e+01	+8.490335e+01	+1.134663e+04	+4.100000e-03	+4.100000e-03	+1.311000e+00	-9.320000e-01	+1.417323e-01	               	;# TC6-L8X6X3/4
uniaxialMaterial	Fatigue     	37 	36           	-E0          	+1.565000e+00	             	             	             	             	             	               	;# TC6-L8X6X3/4
uniaxialMaterial	MinMax      	38 	37           	-min         	-1.000000e+09	-max         	+1.086614e+00	             	             	             	               	;# TC6-L8X6X3/4
uniaxialMaterial	Parallel    	39 	3 11 38      	             	             	             	             	             	             	             	               	;# TC6-L8X6X3/4
uniaxialMaterial	SteelMPF    	40 	+1.686769e+01	+1.686769e+01	+8.223022e+02	+2.410000e-02	+2.410000e-02	+1.314000e+00	-1.140000e+00	+2.559055e-01	               	;# TC7-L6X6X3/8
uniaxialMaterial	Fatigue     	41 	40           	-E0          	+2.190000e+00	             	             	             	             	             	               	;# TC7-L6X6X3/8
uniaxialMaterial	MinMax      	42 	41           	-min         	-1.000000e+09	-max         	+1.370079e+00	             	             	             	               	;# TC7-L6X6X3/8
uniaxialMaterial	Parallel    	43 	3 11 42      	             	             	             	             	             	             	             	               	;# TC7-L6X6X3/8
uniaxialMaterial	SteelMPF    	44 	+1.587423e+01	+1.587423e+01	+7.937500e+02	+1.580000e-02	+1.580000e-02	+9.390000e-01	-1.323000e+00	+2.283465e-01	               	;# TC8-L6X6X3/8
uniaxialMaterial	Fatigue     	45 	44           	-E0          	+2.612000e+00	             	             	             	             	             	               	;# TC8-L6X6X3/8
uniaxialMaterial	MinMax      	46 	45           	-min         	-1.000000e+09	-max         	+1.452756e+00	             	             	             	               	;# TC8-L6X6X3/8
uniaxialMaterial	Parallel    	47 	3 11 46      	             	             	             	             	             	             	             	               	;# TC8-L6X6X3/8
uniaxialMaterial	SteelMPF    	48 	+3.474998e+01	+3.474998e+01	+2.158543e+03	+1.330000e-02	+1.330000e-02	+1.687000e+00	-5.180000e-01	+2.165354e-01	               	;# TC9-L8X6X1/2
uniaxialMaterial	Fatigue     	49 	48           	-E0          	+2.185000e+00	             	             	             	             	             	               	;# TC9-L8X6X1/2
uniaxialMaterial	MinMax      	50 	49           	-min         	-1.000000e+09	-max         	+1.799213e+00	             	             	             	               	;# TC9-L8X6X1/2
uniaxialMaterial	Parallel    	51 	3 11 50      	             	             	             	             	             	             	             	               	;# TC9-L8X6X1/2
uniaxialMaterial	SteelMPF    	52 	+2.614896e+01	+2.614896e+01	+2.272752e+03	+1.250000e-02	+1.250000e-02	+1.751000e+00	-6.390000e-01	+2.322835e-01	               	;# TC10-L8X6X1/2
uniaxialMaterial	Fatigue     	53 	52           	-E0          	+2.390000e+00	             	             	             	             	             	               	;# TC10-L8X6X1/2
uniaxialMaterial	MinMax      	54 	53           	-min         	-1.000000e+09	-max         	+1.559055e+00	             	             	             	               	;# TC10-L8X6X1/2
uniaxialMaterial	Parallel    	55 	3 11 54      	             	             	             	             	             	             	             	               	;# TC10-L8X6X1/2
uniaxialMaterial	SteelMPF    	56 	+4.947856e+01	+4.947856e+01	+5.127968e+03	+1.050000e-02	+1.050000e-02	+1.211000e+00	-9.350000e-01	+2.125984e-01	               	;# TC11-L8X6X5/8
uniaxialMaterial	Fatigue     	57 	56           	-E0          	+1.840000e+00	             	             	             	             	             	               	;# TC11-L8X6X5/8
uniaxialMaterial	MinMax      	58 	57           	-min         	-1.000000e+09	-max         	+6.062992e-01	             	             	             	               	;# TC11-L8X6X5/8
uniaxialMaterial	Parallel    	59 	3 11 58      	             	             	             	             	             	             	             	               	;# TC11-L8X6X5/8
uniaxialMaterial	SteelMPF    	60 	+4.215443e+01	+4.215443e+01	+5.476304e+03	+7.800000e-03	+7.800000e-03	+1.218000e+00	-8.610000e-01	+2.165354e-01	               	;# TC12-L8X6X5/8
uniaxialMaterial	Fatigue     	61 	60           	-E0          	+1.960000e+00	             	             	             	             	             	               	;# TC12-L8X6X5/8
uniaxialMaterial	MinMax      	62 	61           	-min         	-1.000000e+09	-max         	+1.405512e+00	             	             	             	               	;# TC12-L8X6X5/8
uniaxialMaterial	Parallel    	63 	3 11 62      	             	             	             	             	             	             	             	               	;# TC12-L8X6X5/8
uniaxialMaterial	SteelMPF    	64 	+6.940074e+01	+6.940074e+01	+9.679182e+03	+7.700000e-03	+7.700000e-03	+8.950000e-01	-1.162000e+00	+1.653543e-01	               	;# TC13-L8X6X3/4
uniaxialMaterial	Fatigue     	65 	64           	-E0          	+1.960000e+00	             	             	             	             	             	               	;# TC13-L8X6X3/4
uniaxialMaterial	MinMax      	66 	65           	-min         	-1.000000e+09	-max         	+1.003937e+00	             	             	             	               	;# TC13-L8X6X3/4
uniaxialMaterial	Parallel    	67 	3 11 66      	             	             	             	             	             	             	             	               	;# TC13-L8X6X3/4
uniaxialMaterial	SteelMPF    	68 	+5.711590e+01	+5.711590e+01	+7.149460e+03	+1.000000e-02	+1.000000e-02	+1.079000e+00	-1.088000e+00	+2.165354e-01	               	;# TC14-L8X6X3/4
uniaxialMaterial	Fatigue     	69 	68           	-E0          	+1.840000e+00	             	             	             	             	             	               	;# TC14-L8X6X3/4
uniaxialMaterial	MinMax      	70 	69           	-min         	-1.000000e+09	-max         	+8.700787e-01	             	             	             	               	;# TC14-L8X6X3/4
uniaxialMaterial	Parallel    	71 	3 11 70      	             	             	             	             	             	             	             	               	;# TC14-L8X6X3/4
uniaxialMaterial	SteelMPF    	72 	+1.116810e+01	+1.116810e+01	+4.054406e+02	+2.630000e-02	+2.630000e-02	+1.179000e+00	-1.369000e+00	+2.716535e-01	               	;# TC15-L6X6X3/8
uniaxialMaterial	Fatigue     	73 	72           	-E0          	+2.390000e+00	             	             	             	             	             	               	;# TC15-L6X6X3/8
uniaxialMaterial	MinMax      	74 	73           	-min         	-1.000000e+09	-max         	+1.905512e+00	             	             	             	               	;# TC15-L6X6X3/8
uniaxialMaterial	Parallel    	75 	3 11 74      	             	             	             	             	             	             	             	               	;# TC15-L6X6X3/8
uniaxialMaterial	SteelMPF    	76 	+2.369175e+01	+2.369175e+01	+2.095728e+03	+1.160000e-02	+1.160000e-02	+1.218000e+00	-8.760000e-01	+2.874016e-01	               	;# TC16-L8X6X1/2
uniaxialMaterial	Fatigue     	77 	76           	-E0          	+1.785000e+00	             	             	             	             	             	               	;# TC16-L8X6X1/2
uniaxialMaterial	MinMax      	78 	77           	-min         	-1.000000e+09	-max         	+1.500000e+00	             	             	             	               	;# TC16-L8X6X1/2
uniaxialMaterial	Parallel    	79 	3 11 78      	             	             	             	             	             	             	             	               	;# TC16-L8X6X1/2
uniaxialMaterial	SteelMPF    	80 	+3.542065e+01	+3.542065e+01	+4.277113e+03	+6.500000e-03	+6.500000e-03	+1.492000e+00	-6.770000e-01	+1.929134e-01	               	;# TC17-L8X6X5/8
uniaxialMaterial	Fatigue     	81 	80           	-E0          	+2.610000e+00	             	             	             	             	             	               	;# TC17-L8X6X5/8
uniaxialMaterial	MinMax      	82 	81           	-min         	-1.000000e+09	-max         	+1.960630e+00	             	             	             	               	;# TC17-L8X6X5/8
uniaxialMaterial	Parallel    	83 	3 11 82      	             	             	             	             	             	             	             	               	;# TC17-L8X6X5/8
uniaxialMaterial	SteelMPF    	84 	+4.678394e+01	+4.678394e+01	+5.653327e+03	+5.500000e-03	+5.500000e-03	+1.526000e+00	-2.740000e-01	+1.889764e-01	               	;# TC18-L8X6X3/4
uniaxialMaterial	Fatigue     	85 	84           	-E0          	+2.610000e+00	             	             	             	             	             	               	;# TC18-L8X6X3/4
uniaxialMaterial	MinMax      	86 	85           	-min         	-1.000000e+09	-max         	+1.712598e+00	             	             	             	               	;# TC18-L8X6X3/4
uniaxialMaterial	Parallel    	87 	3 11 86      	             	             	             	             	             	             	             	               	;# TC18-L8X6X3/4
uniaxialMaterial	SteelMPF    	88 	+1.481612e+01	+1.481612e+01	+1.479002e+03	+1.150000e-02	+1.150000e-02	+1.433000e+00	-1.194000e+00	+1.889764e-01	               	;# TC19-L4X4X5/16
uniaxialMaterial	Fatigue     	89 	88           	-E0          	+1.785000e+00	             	             	             	             	             	               	;# TC19-L4X4X5/16
uniaxialMaterial	MinMax      	90 	89           	-min         	-1.000000e+09	-max         	+1.251969e+00	             	             	             	               	;# TC19-L4X4X5/16
uniaxialMaterial	Parallel    	91 	3 11 90      	             	             	             	             	             	             	             	               	;# TC19-L4X4X5/16
uniaxialMaterial	Steel02     	96 	+1.949101e+02	+1.263668e+04	+1.000000e-02	+2.000000e+01	+9.250000e-01	+1.500000e-01	+5e-04 +1e-02	+5e-04 +1e-02	               	;# S1 Left Gusset
uniaxialMaterial	Steel02     	97 	+1.949101e+02	+1.263668e+04	+1.000000e-02	+2.000000e+01	+9.250000e-01	+1.500000e-01	+5e-04 +1e-02	+5e-04 +1e-02	               	;# S1 Right Gusset
uniaxialMaterial	Steel02     	92 	+7.256250e+01	+2.089041e+03	+1.000000e-02	+2.000000e+01	+9.250000e-01	+1.500000e-01	+5e-04 +1e-02	+5e-04 +1e-02	               	;# S2 Left Gusset
uniaxialMaterial	Steel02     	93 	+7.256250e+01	+2.089041e+03	+1.000000e-02	+2.000000e+01	+9.250000e-01	+1.500000e-01	+5e-04 +1e-02	+5e-04 +1e-02	               	;# S2 Right Gusset
uniaxialMaterial	Steel02     	94 	+4.556250e+01	+1.240640e+03	+1.000000e-02	+2.000000e+01	+9.250000e-01	+1.500000e-01	+5e-04 +1e-02	+5e-04 +1e-02	               	;# S3 Left Gusset
uniaxialMaterial	Steel02     	95 	+4.556250e+01	+1.240640e+03	+1.000000e-02	+2.000000e+01	+9.250000e-01	+1.500000e-01	+5e-04 +1e-02	+5e-04 +1e-02	               	;# S3 Right Gusset
uniaxialMaterial	Steel02     	98 	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Fatigue     	99 	98           	-E0          	+8.733237e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Elastic     	100	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Parallel    	101	99 100       	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Steel02     	102	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Fatigue     	103	102          	-E0          	+8.833755e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Elastic     	104	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Parallel    	105	103 104      	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Steel02     	106	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Fatigue     	107	106          	-E0          	+8.829339e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Elastic     	108	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Parallel    	109	107 108      	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Bilin       	110	+2.983802e+06	+2.313671e-03	+2.313671e-03	+4.692082e+03	-4.692082e+03	+1.811313e+01	+1.811313e+01	+1.811313e+01	+1.811313e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+6.953886e-02	+6.953886e-02	+1.637042e-01	+1.637042e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W12X65(S)
uniaxialMaterial	Bilin       	111	+6.268276e+06	+1.607980e-03	+1.607980e-03	+5.359448e+03	-5.359448e+03	+1.811313e+01	+1.811313e+01	+1.811313e+01	+1.811313e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+5.402802e-02	+5.402802e-02	+1.637042e-01	+1.637042e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W12X65(S)
uniaxialMaterial	Bilin       	112	+6.222397e+06	+1.722003e-03	+1.722003e-03	+5.705327e+03	-5.705327e+03	+1.811313e+01	+1.811313e+01	+1.811313e+01	+1.811313e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+5.416313e-02	+5.416313e-02	+1.637042e-01	+1.637042e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W12X65(S)
uniaxialMaterial	Bilin       	113	+1.204453e+07	+1.079191e-03	+1.079191e-03	+6.181180e+03	-6.181180e+03	+2.844785e+01	+2.844785e+01	+2.844785e+01	+2.844785e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+4.806678e-02	+4.806678e-02	+2.511901e-01	+2.511901e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W14X82(S)
uniaxialMaterial	Bilin       	114	+1.194217e+07	+1.348083e-03	+1.348083e-03	+7.657544e+03	-7.657544e+03	+2.844785e+01	+2.844785e+01	+2.844785e+01	+2.844785e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+4.820646e-02	+4.820646e-02	+2.511901e-01	+2.511901e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W14X82(S)
uniaxialMaterial	Bilin       	115	+1.144373e+07	+1.489346e-03	+1.489346e-03	+8.213785e+03	-8.213785e+03	+2.844785e+01	+2.844785e+01	+2.844785e+01	+2.844785e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+4.891032e-02	+4.891032e-02	+2.511901e-01	+2.511901e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W14X82(S)
uniaxialMaterial	Steel02     	116	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Fatigue     	117	116          	-E0          	+8.733237e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Elastic     	118	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Parallel    	119	117 118      	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Steel02     	120	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Fatigue     	121	120          	-E0          	+8.833755e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Elastic     	122	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Parallel    	123	121 122      	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Steel02     	124	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Fatigue     	125	124          	-E0          	+8.829339e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Elastic     	126	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Parallel    	127	125 126      	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Steel02     	128	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Fatigue     	129	128          	-E0          	+8.733237e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Elastic     	130	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Parallel    	131	129 130      	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Steel02     	132	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Fatigue     	133	132          	-E0          	+8.833755e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Elastic     	134	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Parallel    	135	133 134      	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Steel02     	136	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Fatigue     	137	136          	-E0          	+8.829339e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Elastic     	138	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Parallel    	139	137 138      	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Steel02     	140	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W14X82(W)
uniaxialMaterial	Fatigue     	141	140          	-E0          	+9.760808e-02	-m           	-3.000000e-01	             	             	             	               	;# W14X82(W)
uniaxialMaterial	Elastic     	142	+2.900000e-02	             	             	             	             	             	             	             	               	;# W14X82(W)
uniaxialMaterial	Parallel    	143	141 142      	             	             	             	             	             	             	             	               	;# W14X82(W)
uniaxialMaterial	Steel02     	144	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W14X82(W)
uniaxialMaterial	Fatigue     	145	144          	-E0          	+9.873154e-02	-m           	-3.000000e-01	             	             	             	               	;# W14X82(W)
uniaxialMaterial	Elastic     	146	+2.900000e-02	             	             	             	             	             	             	             	               	;# W14X82(W)
uniaxialMaterial	Parallel    	147	145 146      	             	             	             	             	             	             	             	               	;# W14X82(W)
uniaxialMaterial	Steel02     	148	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W14X82(W)
uniaxialMaterial	Fatigue     	149	148          	-E0          	+9.868217e-02	-m           	-3.000000e-01	             	             	             	               	;# W14X82(W)
uniaxialMaterial	Elastic     	150	+2.900000e-02	             	             	             	             	             	             	             	               	;# W14X82(W)
uniaxialMaterial	Parallel    	151	149 150      	             	             	             	             	             	             	             	               	;# W14X82(W)
uniaxialMaterial	Bilin       	152	+2.178038e+06	+1.471526e-03	+1.471526e-03	+2.260601e+03	-2.260601e+03	+2.143095e+01	+2.143095e+01	+2.143095e+01	+2.143095e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+7.157060e-02	+7.157060e-02	+2.246953e-01	+2.246953e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W12X50(S)
uniaxialMaterial	Bilin       	153	+4.574413e+06	+1.330887e-03	+1.330887e-03	+3.341163e+03	-3.341163e+03	+2.143095e+01	+2.143095e+01	+2.143095e+01	+2.143095e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+5.561128e-02	+5.561128e-02	+2.246953e-01	+2.246953e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W12X50(S)
uniaxialMaterial	Bilin       	154	+4.564648e+06	+1.656802e-03	+1.656802e-03	+4.140186e+03	-4.140186e+03	+2.143095e+01	+2.143095e+01	+2.143095e+01	+2.143095e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+5.565171e-02	+5.565171e-02	+2.246953e-01	+2.246953e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W12X50(S)
uniaxialMaterial	Steel02     	155	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W14X82(W)
uniaxialMaterial	Fatigue     	156	155          	-E0          	+9.760808e-02	-m           	-3.000000e-01	             	             	             	               	;# W14X82(W)
uniaxialMaterial	Elastic     	157	+2.900000e-02	             	             	             	             	             	             	             	               	;# W14X82(W)
uniaxialMaterial	Parallel    	158	156 157      	             	             	             	             	             	             	             	               	;# W14X82(W)
uniaxialMaterial	Steel02     	159	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W14X82(W)
uniaxialMaterial	Fatigue     	160	159          	-E0          	+9.873154e-02	-m           	-3.000000e-01	             	             	             	               	;# W14X82(W)
uniaxialMaterial	Elastic     	161	+2.900000e-02	             	             	             	             	             	             	             	               	;# W14X82(W)
uniaxialMaterial	Parallel    	162	160 161      	             	             	             	             	             	             	             	               	;# W14X82(W)
uniaxialMaterial	Steel02     	163	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W14X82(W)
uniaxialMaterial	Fatigue     	164	163          	-E0          	+9.868217e-02	-m           	-3.000000e-01	             	             	             	               	;# W14X82(W)
uniaxialMaterial	Elastic     	165	+2.900000e-02	             	             	             	             	             	             	             	               	;# W14X82(W)
uniaxialMaterial	Parallel    	166	164 165      	             	             	             	             	             	             	             	               	;# W14X82(W)
uniaxialMaterial	Steel02     	167	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Fatigue     	168	167          	-E0          	+8.733237e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Elastic     	169	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Parallel    	170	168 169      	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Steel02     	171	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Fatigue     	172	171          	-E0          	+8.833755e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Elastic     	173	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Parallel    	174	172 173      	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Steel02     	175	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Fatigue     	176	175          	-E0          	+8.829339e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Elastic     	177	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Parallel    	178	176 177      	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Bilin       	179	+1.595933e+06	+1.773463e-03	+1.773463e-03	+1.735475e+03	-1.735475e+03	+1.433851e+01	+1.433851e+01	+1.433851e+01	+1.433851e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+6.240454e-02	+6.240454e-02	+1.884644e-01	+1.884644e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W12X35(S)
uniaxialMaterial	Bilin       	180	+3.371384e+06	+1.515207e-03	+1.515207e-03	+2.435205e+03	-2.435205e+03	+1.433851e+01	+1.433851e+01	+1.433851e+01	+1.433851e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+4.839343e-02	+4.839343e-02	+1.884644e-01	+1.884644e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W12X35(S)
uniaxialMaterial	Bilin       	181	+3.366183e+06	+1.833096e-03	+1.833096e-03	+2.933920e+03	-2.933920e+03	+1.433851e+01	+1.433851e+01	+1.433851e+01	+1.433851e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+4.841884e-02	+4.841884e-02	+1.884644e-01	+1.884644e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W12X35(S)
uniaxialMaterial	Bilin       	182	+1.719128e+06	+1.824842e-03	+1.824842e-03	+2.025263e+03	-2.025263e+03	+1.408769e+01	+1.408769e+01	+1.408769e+01	+1.408769e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+6.573573e-02	+6.573573e-02	+1.690638e-01	+1.690638e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W12X40(S)
uniaxialMaterial	Bilin       	183	+3.631632e+06	+1.513149e-03	+1.513149e-03	+2.759516e+03	-2.759516e+03	+1.408769e+01	+1.408769e+01	+1.408769e+01	+1.408769e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+5.097670e-02	+5.097670e-02	+1.690638e-01	+1.690638e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W12X40(S)
uniaxialMaterial	Bilin       	184	+3.626029e+06	+1.807009e-03	+1.807009e-03	+3.282567e+03	-3.282567e+03	+1.408769e+01	+1.408769e+01	+1.408769e+01	+1.408769e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+5.100346e-02	+5.100346e-02	+1.690638e-01	+1.690638e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W12X40(S)
uniaxialMaterial	Steel02     	185	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Fatigue     	186	185          	-E0          	+8.743977e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Elastic     	187	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Parallel    	188	186 187      	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Steel02     	189	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Fatigue     	190	189          	-E0          	+8.856654e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Elastic     	191	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Parallel    	192	190 191      	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Steel02     	193	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Fatigue     	194	193          	-E0          	+8.853455e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Elastic     	195	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Parallel    	196	194 195      	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Steel02     	197	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Fatigue     	198	197          	-E0          	+8.743977e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Elastic     	199	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Parallel    	200	198 199      	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Steel02     	201	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Fatigue     	202	201          	-E0          	+8.856654e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Elastic     	203	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Parallel    	204	202 203      	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Steel02     	205	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Fatigue     	206	205          	-E0          	+8.853455e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Elastic     	207	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Parallel    	208	206 207      	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Steel02     	209	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X35(W)
uniaxialMaterial	Fatigue     	210	209          	-E0          	+9.060927e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X35(W)
uniaxialMaterial	Elastic     	211	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X35(W)
uniaxialMaterial	Parallel    	212	210 211      	             	             	             	             	             	             	             	               	;# W12X35(W)
uniaxialMaterial	Steel02     	213	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X35(W)
uniaxialMaterial	Fatigue     	214	213          	-E0          	+9.177688e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X35(W)
uniaxialMaterial	Elastic     	215	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X35(W)
uniaxialMaterial	Parallel    	216	214 215      	             	             	             	             	             	             	             	               	;# W12X35(W)
uniaxialMaterial	Steel02     	217	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X35(W)
uniaxialMaterial	Fatigue     	218	217          	-E0          	+9.174373e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X35(W)
uniaxialMaterial	Elastic     	219	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X35(W)
uniaxialMaterial	Parallel    	220	218 219      	             	             	             	             	             	             	             	               	;# W12X35(W)
uniaxialMaterial	Bilin       	221	+3.524832e+06	+3.498030e-03	+3.498030e-03	+6.352500e+03	-6.352500e+03	+1.873781e+01	+1.873781e+01	+1.873781e+01	+1.873781e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+5.332303e-02	+5.332303e-02	+2.226478e-01	+2.226478e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W16X57(S)
uniaxialMaterial	Bilin       	222	+1.399702e+06	+4.666922e-03	+4.666922e-03	+2.674100e+03	-2.674100e+03	+6.817471e+00	+6.817471e+00	+6.817471e+00	+6.817471e+00 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+4.284705e-02	+4.284705e-02	+1.136469e-01	+1.136469e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W16X26(S)
uniaxialMaterial	Bilin       	223	+3.576556e+06	+3.463400e-03	+3.463400e-03	+6.352500e+03	-6.352500e+03	+1.873781e+01	+1.873781e+01	+1.873781e+01	+1.873781e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+5.305958e-02	+5.305958e-02	+2.226478e-01	+2.226478e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W16X57(S)
uniaxialMaterial	Bilin       	224	+1.420242e+06	+4.620203e-03	+4.620203e-03	+2.674100e+03	-2.674100e+03	+6.817471e+00	+6.817471e+00	+6.817471e+00	+6.817471e+00 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+4.263535e-02	+4.263535e-02	+1.136469e-01	+1.136469e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W16X26(S)
uniaxialMaterial	Bilin       	225	+3.628844e+06	+3.429249e-03	+3.429249e-03	+6.352500e+03	-6.352500e+03	+1.873781e+01	+1.873781e+01	+1.873781e+01	+1.873781e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+5.279839e-02	+5.279839e-02	+2.226478e-01	+2.226478e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W16X57(S)
uniaxialMaterial	Bilin       	226	+1.441006e+06	+4.574142e-03	+4.574142e-03	+2.674100e+03	-2.674100e+03	+6.817471e+00	+6.817471e+00	+6.817471e+00	+6.817471e+00 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+4.242547e-02	+4.242547e-02	+1.136469e-01	+1.136469e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W16X26(S)
uniaxialMaterial	Bilin       	227	+3.575168e+06	+3.464318e-03	+3.464318e-03	+6.352500e+03	-6.352500e+03	+1.873781e+01	+1.873781e+01	+1.873781e+01	+1.873781e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+5.306658e-02	+5.306658e-02	+2.226478e-01	+2.226478e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W16X57(S)
uniaxialMaterial	Bilin       	228	+1.419691e+06	+4.621442e-03	+4.621442e-03	+2.674100e+03	-2.674100e+03	+6.817471e+00	+6.817471e+00	+6.817471e+00	+6.817471e+00 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+4.264098e-02	+4.264098e-02	+1.136469e-01	+1.136469e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W16X26(S)
uniaxialMaterial	Bilin       	229	+1.769635e+07	+1.948517e-03	+1.948517e-03	+7.097935e+03	-7.097935e+03	+1.291564e+01	+1.291564e+01	+1.291564e+01	+1.291564e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+2.098578e-02	+2.098578e-02	+1.460467e-01	+1.460467e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W21X62(S)
uniaxialMaterial	Bilin       	230	+1.177752e+07	+1.995378e-03	+1.995378e-03	+5.306861e+03	-5.306861e+03	+6.665635e+00	+6.665635e+00	+6.665635e+00	+6.665635e+00 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+2.303240e-02	+2.303240e-02	+9.493601e-02	+9.493601e-02	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W21X48(S)
uniaxialMaterial	Bilin       	231	+3.131706e+06	+1.984135e-03	+1.984135e-03	+2.413324e+03	-2.413324e+03	+8.745115e+00	+8.745115e+00	+8.745115e+00	+8.745115e+00 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+3.960920e-02	+3.960920e-02	+1.244142e-01	+1.244142e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W14X30(S)
uniaxialMaterial	Bilin       	232	+4.271464e+06	+3.858086e-03	+3.858086e-03	+6.776000e+03	-6.776000e+03	+1.247891e+01	+1.247891e+01	+1.247891e+01	+1.247891e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+4.270366e-02	+4.270366e-02	+1.650640e-01	+1.650640e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W18X55(S)
uniaxialMaterial	Bilin       	233	+3.637944e+06	+3.423392e-03	+3.423392e-03	+6.352500e+03	-6.352500e+03	+1.873781e+01	+1.873781e+01	+1.873781e+01	+1.873781e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+5.275345e-02	+5.275345e-02	+2.226478e-01	+2.226478e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W16X57(S)
uniaxialMaterial	Bilin       	234	+1.444619e+06	+4.566242e-03	+4.566242e-03	+2.674100e+03	-2.674100e+03	+6.817471e+00	+6.817471e+00	+6.817471e+00	+6.817471e+00 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+4.238937e-02	+4.238937e-02	+1.136469e-01	+1.136469e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W16X26(S)
uniaxialMaterial	Bilin       	235	+4.710795e+06	+3.716595e-03	+3.716595e-03	+7.441500e+03	-7.441500e+03	+1.439241e+01	+1.439241e+01	+1.439241e+01	+1.439241e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+4.408281e-02	+4.408281e-02	+1.843210e-01	+1.843210e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W18X60(S)
uniaxialMaterial	Bilin       	236	+2.441571e+06	+4.429667e-03	+4.429667e-03	+4.023250e+03	-4.023250e+03	+7.947889e+00	+7.947889e+00	+7.947889e+00	+7.947889e+00 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+3.884727e-02	+3.884727e-02	+1.253297e-01	+1.253297e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W18X35(S)
uniaxialMaterial	Bilin       	237	+4.639971e+06	+3.755342e-03	+3.755342e-03	+7.441500e+03	-7.441500e+03	+1.439241e+01	+1.439241e+01	+1.439241e+01	+1.439241e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+4.431045e-02	+4.431045e-02	+1.843210e-01	+1.843210e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W18X60(S)
uniaxialMaterial	Bilin       	238	+2.404863e+06	+4.476170e-03	+4.476170e-03	+4.023250e+03	-4.023250e+03	+7.947889e+00	+7.947889e+00	+7.947889e+00	+7.947889e+00 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+3.904787e-02	+3.904787e-02	+1.253297e-01	+1.253297e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W18X35(S)
uniaxialMaterial	Bilin       	239	+4.574576e+06	+3.792028e-03	+3.792028e-03	+7.441500e+03	-7.441500e+03	+1.439241e+01	+1.439241e+01	+1.439241e+01	+1.439241e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+4.452481e-02	+4.452481e-02	+1.843210e-01	+1.843210e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W18X60(S)
uniaxialMaterial	Bilin       	240	+2.370970e+06	+4.520205e-03	+4.520205e-03	+4.023250e+03	-4.023250e+03	+7.947889e+00	+7.947889e+00	+7.947889e+00	+7.947889e+00 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+3.923677e-02	+3.923677e-02	+1.253297e-01	+1.253297e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W18X35(S)
uniaxialMaterial	Bilin       	241	+4.640000e+06	+3.755326e-03	+3.755326e-03	+7.441500e+03	-7.441500e+03	+1.439241e+01	+1.439241e+01	+1.439241e+01	+1.439241e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+4.431035e-02	+4.431035e-02	+1.843210e-01	+1.843210e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W18X60(S)
uniaxialMaterial	Bilin       	242	+2.404878e+06	+4.476151e-03	+4.476151e-03	+4.023250e+03	-4.023250e+03	+7.947889e+00	+7.947889e+00	+7.947889e+00	+7.947889e+00 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+3.904778e-02	+3.904778e-02	+1.253297e-01	+1.253297e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W18X35(S)
uniaxialMaterial	Steel02     	243	+6.440000e+01	+2.900000e+04	+1.000000e-03	+2.200000e+01	+9.250000e-01	+2.500000e-01	+0.03 +1.00  	+0.02 +1.00  	               	;# BR1
uniaxialMaterial	Fatigue     	244	243          	-E0          	+3.678538e-02	-m           	-3.000000e-01	             	             	             	               	;# BR1
uniaxialMaterial	Elastic     	245	+2.900000e-02	             	             	             	             	             	             	             	               	;# BR1
uniaxialMaterial	Parallel    	246	244 245      	             	             	             	             	             	             	             	               	;# BR1
uniaxialMaterial	Steel02     	247	+6.440000e+01	+2.900000e+04	+1.000000e-03	+2.200000e+01	+9.250000e-01	+2.500000e-01	+0.03 +1.00  	+0.02 +1.00  	               	;# BR2
uniaxialMaterial	Fatigue     	248	247          	-E0          	+3.486368e-02	-m           	-3.000000e-01	             	             	             	               	;# BR2
uniaxialMaterial	Elastic     	249	+2.900000e-02	             	             	             	             	             	             	             	               	;# BR2
uniaxialMaterial	Parallel    	250	248 249      	             	             	             	             	             	             	             	               	;# BR2
uniaxialMaterial	Steel02     	251	+6.440000e+01	+2.900000e+04	+1.000000e-03	+2.200000e+01	+9.250000e-01	+2.500000e-01	+0.03 +1.00  	+0.02 +1.00  	               	;# BR3
uniaxialMaterial	Fatigue     	252	251          	-E0          	+3.648650e-02	-m           	-3.000000e-01	             	             	             	               	;# BR3
uniaxialMaterial	Elastic     	253	+2.900000e-02	             	             	             	             	             	             	             	               	;# BR3
uniaxialMaterial	Parallel    	254	252 253      	             	             	             	             	             	             	             	               	;# BR3
uniaxialMaterial	Steel02     	255	+6.440000e+01	+2.900000e+04	+1.000000e-03	+2.200000e+01	+9.250000e-01	+2.500000e-01	+0.03 +1.00  	+0.02 +1.00  	               	;# BR4
uniaxialMaterial	Fatigue     	256	255          	-E0          	+3.678538e-02	-m           	-3.000000e-01	             	             	             	               	;# BR4
uniaxialMaterial	Elastic     	257	+2.900000e-02	             	             	             	             	             	             	             	               	;# BR4
uniaxialMaterial	Parallel    	258	256 257      	             	             	             	             	             	             	             	               	;# BR4
uniaxialMaterial	Steel02     	259	+6.440000e+01	+2.900000e+04	+1.000000e-03	+2.200000e+01	+9.250000e-01	+2.500000e-01	+0.03 +1.00  	+0.02 +1.00  	               	;# BR5
uniaxialMaterial	Fatigue     	260	259          	-E0          	+3.486368e-02	-m           	-3.000000e-01	             	             	             	               	;# BR5
uniaxialMaterial	Elastic     	261	+2.900000e-02	             	             	             	             	             	             	             	               	;# BR5
uniaxialMaterial	Parallel    	262	260 261      	             	             	             	             	             	             	             	               	;# BR5
uniaxialMaterial	Steel02     	263	+6.440000e+01	+2.900000e+04	+1.000000e-03	+2.200000e+01	+9.250000e-01	+2.500000e-01	+0.03 +1.00  	+0.02 +1.00  	               	;# BR6
uniaxialMaterial	Fatigue     	264	263          	-E0          	+3.648650e-02	-m           	-3.000000e-01	             	             	             	               	;# BR6
uniaxialMaterial	Elastic     	265	+2.900000e-02	             	             	             	             	             	             	             	               	;# BR6
uniaxialMaterial	Parallel    	266	264 265      	             	             	             	             	             	             	             	               	;# BR6
# ===================================================================================================================================================================================
