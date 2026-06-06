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
uniaxialMaterial	Steel02     	96 	+9.554649e+01	+4.533528e+03	+1.000000e-02	+2.000000e+01	+9.250000e-01	+1.500000e-01	+5e-04 +1e-02	+5e-04 +1e-02	               	;# S1 Left Gusset
uniaxialMaterial	Steel02     	97 	+9.554649e+01	+4.533528e+03	+1.000000e-02	+2.000000e+01	+9.250000e-01	+1.500000e-01	+5e-04 +1e-02	+5e-04 +1e-02	               	;# S1 Right Gusset
uniaxialMaterial	Steel02     	92 	+8.943750e+01	+1.819958e+03	+1.000000e-02	+2.000000e+01	+9.250000e-01	+1.500000e-01	+5e-04 +1e-02	+5e-04 +1e-02	               	;# S2 Left Gusset
uniaxialMaterial	Steel02     	93 	+8.943750e+01	+1.819958e+03	+1.000000e-02	+2.000000e+01	+9.250000e-01	+1.500000e-01	+5e-04 +1e-02	+5e-04 +1e-02	               	;# S2 Right Gusset
uniaxialMaterial	Steel02     	94 	+7.382405e+01	+2.505995e+03	+1.000000e-02	+2.000000e+01	+9.250000e-01	+1.500000e-01	+5e-04 +1e-02	+5e-04 +1e-02	               	;# S3 Left Gusset
uniaxialMaterial	Steel02     	95 	+7.382405e+01	+2.505995e+03	+1.000000e-02	+2.000000e+01	+9.250000e-01	+1.500000e-01	+5e-04 +1e-02	+5e-04 +1e-02	               	;# S3 Right Gusset
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
uniaxialMaterial	Bilin       	110	+2.178038e+06	+1.471526e-03	+1.471526e-03	+2.260601e+03	-2.260601e+03	+2.143095e+01	+2.143095e+01	+2.143095e+01	+2.143095e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+7.157060e-02	+7.157060e-02	+2.246953e-01	+2.246953e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W12X50(S)
uniaxialMaterial	Bilin       	111	+4.574413e+06	+1.330887e-03	+1.330887e-03	+3.341163e+03	-3.341163e+03	+2.143095e+01	+2.143095e+01	+2.143095e+01	+2.143095e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+5.561128e-02	+5.561128e-02	+2.246953e-01	+2.246953e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W12X50(S)
uniaxialMaterial	Bilin       	112	+4.564648e+06	+1.656802e-03	+1.656802e-03	+4.140186e+03	-4.140186e+03	+2.143095e+01	+2.143095e+01	+2.143095e+01	+2.143095e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+5.565171e-02	+5.565171e-02	+2.246953e-01	+2.246953e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W12X50(S)
uniaxialMaterial	Bilin       	113	+5.742676e+06	+8.106761e-04	+8.106761e-04	+2.314605e+03	-2.314605e+03	+1.652800e+01	+1.652800e+01	+1.652800e+01	+1.652800e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+5.012123e-02	+5.012123e-02	+1.692939e-01	+1.692939e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W12X53(S)
uniaxialMaterial	Bilin       	114	+6.125377e+06	+1.279130e-03	+1.279130e-03	+3.793349e+03	-3.793349e+03	+1.652800e+01	+1.652800e+01	+1.652800e+01	+1.652800e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+4.903379e-02	+4.903379e-02	+1.692939e-01	+1.692939e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W12X53(S)
uniaxialMaterial	Bilin       	115	+5.696429e+06	+1.612828e-03	+1.612828e-03	+4.544204e+03	-4.544204e+03	+1.652800e+01	+1.652800e+01	+1.652800e+01	+1.652800e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+5.025921e-02	+5.025921e-02	+1.692939e-01	+1.692939e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W12X53(S)
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
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X53(W)
uniaxialMaterial	Fatigue     	141	140          	-E0          	+8.703721e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X53(W)
uniaxialMaterial	Elastic     	142	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X53(W)
uniaxialMaterial	Parallel    	143	141 142      	             	             	             	             	             	             	             	               	;# W12X53(W)
uniaxialMaterial	Steel02     	144	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X53(W)
uniaxialMaterial	Fatigue     	145	144          	-E0          	+8.803900e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X53(W)
uniaxialMaterial	Elastic     	146	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X53(W)
uniaxialMaterial	Parallel    	147	145 146      	             	             	             	             	             	             	             	               	;# W12X53(W)
uniaxialMaterial	Steel02     	148	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X53(W)
uniaxialMaterial	Fatigue     	149	148          	-E0          	+8.799498e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X53(W)
uniaxialMaterial	Elastic     	150	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X53(W)
uniaxialMaterial	Parallel    	151	149 150      	             	             	             	             	             	             	             	               	;# W12X53(W)
uniaxialMaterial	Steel02     	152	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X53(W)
uniaxialMaterial	Fatigue     	153	152          	-E0          	+8.703721e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X53(W)
uniaxialMaterial	Elastic     	154	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X53(W)
uniaxialMaterial	Parallel    	155	153 154      	             	             	             	             	             	             	             	               	;# W12X53(W)
uniaxialMaterial	Steel02     	156	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X53(W)
uniaxialMaterial	Fatigue     	157	156          	-E0          	+8.803900e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X53(W)
uniaxialMaterial	Elastic     	158	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X53(W)
uniaxialMaterial	Parallel    	159	157 158      	             	             	             	             	             	             	             	               	;# W12X53(W)
uniaxialMaterial	Steel02     	160	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X53(W)
uniaxialMaterial	Fatigue     	161	160          	-E0          	+8.799498e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X53(W)
uniaxialMaterial	Elastic     	162	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X53(W)
uniaxialMaterial	Parallel    	163	161 162      	             	             	             	             	             	             	             	               	;# W12X53(W)
uniaxialMaterial	Steel02     	164	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Fatigue     	165	164          	-E0          	+8.733237e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Elastic     	166	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Parallel    	167	165 166      	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Steel02     	168	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Fatigue     	169	168          	-E0          	+8.833755e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Elastic     	170	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Parallel    	171	169 170      	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Steel02     	172	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Fatigue     	173	172          	-E0          	+8.829339e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Elastic     	174	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Parallel    	175	173 174      	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Bilin       	176	+1.595933e+06	+1.773463e-03	+1.773463e-03	+1.735475e+03	-1.735475e+03	+1.433851e+01	+1.433851e+01	+1.433851e+01	+1.433851e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+6.240454e-02	+6.240454e-02	+1.884644e-01	+1.884644e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W12X35(S)
uniaxialMaterial	Bilin       	177	+3.371384e+06	+1.515207e-03	+1.515207e-03	+2.435205e+03	-2.435205e+03	+1.433851e+01	+1.433851e+01	+1.433851e+01	+1.433851e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+4.839343e-02	+4.839343e-02	+1.884644e-01	+1.884644e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W12X35(S)
uniaxialMaterial	Bilin       	178	+3.366183e+06	+1.833096e-03	+1.833096e-03	+2.933920e+03	-2.933920e+03	+1.433851e+01	+1.433851e+01	+1.433851e+01	+1.433851e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+4.841884e-02	+4.841884e-02	+1.884644e-01	+1.884644e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W12X35(S)
uniaxialMaterial	Bilin       	179	+1.719128e+06	+1.824842e-03	+1.824842e-03	+2.025263e+03	-2.025263e+03	+1.408769e+01	+1.408769e+01	+1.408769e+01	+1.408769e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+6.573573e-02	+6.573573e-02	+1.690638e-01	+1.690638e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W12X40(S)
uniaxialMaterial	Bilin       	180	+3.631632e+06	+1.513149e-03	+1.513149e-03	+2.759516e+03	-2.759516e+03	+1.408769e+01	+1.408769e+01	+1.408769e+01	+1.408769e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+5.097670e-02	+5.097670e-02	+1.690638e-01	+1.690638e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W12X40(S)
uniaxialMaterial	Bilin       	181	+3.626029e+06	+1.807009e-03	+1.807009e-03	+3.282567e+03	-3.282567e+03	+1.408769e+01	+1.408769e+01	+1.408769e+01	+1.408769e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+5.100346e-02	+5.100346e-02	+1.690638e-01	+1.690638e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W12X40(S)
uniaxialMaterial	Steel02     	182	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Fatigue     	183	182          	-E0          	+8.743977e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Elastic     	184	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Parallel    	185	183 184      	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Steel02     	186	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Fatigue     	187	186          	-E0          	+8.856654e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Elastic     	188	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Parallel    	189	187 188      	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Steel02     	190	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Fatigue     	191	190          	-E0          	+8.853455e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Elastic     	192	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Parallel    	193	191 192      	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Steel02     	194	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Fatigue     	195	194          	-E0          	+8.743977e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Elastic     	196	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Parallel    	197	195 196      	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Steel02     	198	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Fatigue     	199	198          	-E0          	+8.856654e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Elastic     	200	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Parallel    	201	199 200      	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Steel02     	202	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Fatigue     	203	202          	-E0          	+8.853455e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Elastic     	204	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Parallel    	205	203 204      	             	             	             	             	             	             	             	               	;# W12X40(W)
uniaxialMaterial	Steel02     	206	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X35(W)
uniaxialMaterial	Fatigue     	207	206          	-E0          	+9.060927e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X35(W)
uniaxialMaterial	Elastic     	208	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X35(W)
uniaxialMaterial	Parallel    	209	207 208      	             	             	             	             	             	             	             	               	;# W12X35(W)
uniaxialMaterial	Steel02     	210	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X35(W)
uniaxialMaterial	Fatigue     	211	210          	-E0          	+9.177688e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X35(W)
uniaxialMaterial	Elastic     	212	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X35(W)
uniaxialMaterial	Parallel    	213	211 212      	             	             	             	             	             	             	             	               	;# W12X35(W)
uniaxialMaterial	Steel02     	214	+5.500000e+01	+2.900000e+04	+1.000000e-03	+2.000000e+01	+9.250000e-01	+2.500000e-01	+1.000000e-02	+1.000000e+00	+2.000000e-02 \
                	            	   	+1.000000e+00	             	             	             	             	             	             	             	               	;# W12X35(W)
uniaxialMaterial	Fatigue     	215	214          	-E0          	+9.174373e-02	-m           	-3.000000e-01	             	             	             	               	;# W12X35(W)
uniaxialMaterial	Elastic     	216	+2.900000e-02	             	             	             	             	             	             	             	               	;# W12X35(W)
uniaxialMaterial	Parallel    	217	215 216      	             	             	             	             	             	             	             	               	;# W12X35(W)
uniaxialMaterial	Bilin       	218	+3.524126e+06	+3.498509e-03	+3.498509e-03	+6.352500e+03	-6.352500e+03	+1.873781e+01	+1.873781e+01	+1.873781e+01	+1.873781e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+5.332667e-02	+5.332667e-02	+2.226478e-01	+2.226478e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W16X57(S)
uniaxialMaterial	Bilin       	219	+1.399422e+06	+4.667568e-03	+4.667568e-03	+2.674100e+03	-2.674100e+03	+6.817471e+00	+6.817471e+00	+6.817471e+00	+6.817471e+00 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+4.284997e-02	+4.284997e-02	+1.136469e-01	+1.136469e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W16X26(S)
uniaxialMaterial	Bilin       	220	+3.575829e+06	+3.463881e-03	+3.463881e-03	+6.352500e+03	-6.352500e+03	+1.873781e+01	+1.873781e+01	+1.873781e+01	+1.873781e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+5.306325e-02	+5.306325e-02	+2.226478e-01	+2.226478e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W16X57(S)
uniaxialMaterial	Bilin       	221	+1.419953e+06	+4.620852e-03	+4.620852e-03	+2.674100e+03	-2.674100e+03	+6.817471e+00	+6.817471e+00	+6.817471e+00	+6.817471e+00 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+4.263830e-02	+4.263830e-02	+1.136469e-01	+1.136469e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W16X26(S)
uniaxialMaterial	Bilin       	222	+3.628844e+06	+3.429249e-03	+3.429249e-03	+6.352500e+03	-6.352500e+03	+1.873781e+01	+1.873781e+01	+1.873781e+01	+1.873781e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+5.279839e-02	+5.279839e-02	+2.226478e-01	+2.226478e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W16X57(S)
uniaxialMaterial	Bilin       	223	+1.441006e+06	+4.574142e-03	+4.574142e-03	+2.674100e+03	-2.674100e+03	+6.817471e+00	+6.817471e+00	+6.817471e+00	+6.817471e+00 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+4.242547e-02	+4.242547e-02	+1.136469e-01	+1.136469e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W16X26(S)
uniaxialMaterial	Bilin       	224	+3.575608e+06	+3.464026e-03	+3.464026e-03	+6.352500e+03	-6.352500e+03	+1.873781e+01	+1.873781e+01	+1.873781e+01	+1.873781e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+5.306436e-02	+5.306436e-02	+2.226478e-01	+2.226478e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W16X57(S)
uniaxialMaterial	Bilin       	225	+1.419866e+06	+4.621048e-03	+4.621048e-03	+2.674100e+03	-2.674100e+03	+6.817471e+00	+6.817471e+00	+6.817471e+00	+6.817471e+00 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+4.263919e-02	+4.263919e-02	+1.136469e-01	+1.136469e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W16X26(S)
uniaxialMaterial	Bilin       	226	+4.012431e+07	+2.004054e-03	+2.004054e-03	+1.328952e+04	-1.328952e+04	+1.050982e+01	+1.050982e+01	+1.050982e+01	+1.050982e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+1.685814e-02	+1.685814e-02	+1.194336e-01	+1.194336e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W27X84(S)
uniaxialMaterial	Bilin       	227	+2.391683e+07	+2.125320e-03	+2.125320e-03	+8.992972e+03	-8.992972e+03	+1.067822e+01	+1.067822e+01	+1.067822e+01	+1.067822e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+1.806794e-02	+1.806794e-02	+1.231561e-01	+1.231561e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W24X68(S)
uniaxialMaterial	Bilin       	228	+3.165524e+06	+9.968669e-04	+9.968669e-04	+1.233062e+03	-1.233062e+03	+8.745115e+00	+8.745115e+00	+8.745115e+00	+8.745115e+00 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+3.946481e-02	+3.946481e-02	+1.244142e-01	+1.244142e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W14X30(S)
uniaxialMaterial	Bilin       	229	+3.628391e+06	+3.429542e-03	+3.429542e-03	+6.352500e+03	-6.352500e+03	+1.873781e+01	+1.873781e+01	+1.873781e+01	+1.873781e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+5.280063e-02	+5.280063e-02	+2.226478e-01	+2.226478e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W16X57(S)
uniaxialMaterial	Bilin       	230	+1.440825e+06	+4.574536e-03	+4.574536e-03	+2.674100e+03	-2.674100e+03	+6.817471e+00	+6.817471e+00	+6.817471e+00	+6.817471e+00 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+4.242728e-02	+4.242728e-02	+1.136469e-01	+1.136469e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W16X26(S)
uniaxialMaterial	Bilin       	231	+4.710795e+06	+3.716595e-03	+3.716595e-03	+7.441500e+03	-7.441500e+03	+1.439241e+01	+1.439241e+01	+1.439241e+01	+1.439241e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+4.408281e-02	+4.408281e-02	+1.843210e-01	+1.843210e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W18X60(S)
uniaxialMaterial	Bilin       	232	+2.441571e+06	+4.429667e-03	+4.429667e-03	+4.023250e+03	-4.023250e+03	+7.947889e+00	+7.947889e+00	+7.947889e+00	+7.947889e+00 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+3.884727e-02	+3.884727e-02	+1.253297e-01	+1.253297e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W18X35(S)
uniaxialMaterial	Bilin       	233	+4.639971e+06	+3.755342e-03	+3.755342e-03	+7.441500e+03	-7.441500e+03	+1.439241e+01	+1.439241e+01	+1.439241e+01	+1.439241e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+4.431045e-02	+4.431045e-02	+1.843210e-01	+1.843210e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W18X60(S)
uniaxialMaterial	Bilin       	234	+2.404863e+06	+4.476170e-03	+4.476170e-03	+4.023250e+03	-4.023250e+03	+7.947889e+00	+7.947889e+00	+7.947889e+00	+7.947889e+00 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+3.904787e-02	+3.904787e-02	+1.253297e-01	+1.253297e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W18X35(S)
uniaxialMaterial	Bilin       	235	+4.574576e+06	+3.792028e-03	+3.792028e-03	+7.441500e+03	-7.441500e+03	+1.439241e+01	+1.439241e+01	+1.439241e+01	+1.439241e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+4.452481e-02	+4.452481e-02	+1.843210e-01	+1.843210e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W18X60(S)
uniaxialMaterial	Bilin       	236	+2.370970e+06	+4.520205e-03	+4.520205e-03	+4.023250e+03	-4.023250e+03	+7.947889e+00	+7.947889e+00	+7.947889e+00	+7.947889e+00 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+3.923677e-02	+3.923677e-02	+1.253297e-01	+1.253297e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W18X35(S)
uniaxialMaterial	Bilin       	237	+4.640000e+06	+3.755326e-03	+3.755326e-03	+7.441500e+03	-7.441500e+03	+1.439241e+01	+1.439241e+01	+1.439241e+01	+1.439241e+01 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+4.431035e-02	+4.431035e-02	+1.843210e-01	+1.843210e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W18X60(S)
uniaxialMaterial	Bilin       	238	+2.404878e+06	+4.476151e-03	+4.476151e-03	+4.023250e+03	-4.023250e+03	+7.947889e+00	+7.947889e+00	+7.947889e+00	+7.947889e+00 \
                	            	   	+1.0 +1.0    	+1.0 +1.0    	+3.904778e-02	+3.904778e-02	+1.253297e-01	+1.253297e-01	+0.40 +0.40  	+0.12 +0.12  	+1.00 +1.00    	;# W18X35(S)
uniaxialMaterial	Steel02     	239	+6.440000e+01	+2.900000e+04	+1.000000e-03	+2.200000e+01	+9.250000e-01	+2.500000e-01	+0.03 +1.00  	+0.02 +1.00  	               	;# BR1
uniaxialMaterial	Fatigue     	240	239          	-E0          	+4.499452e-02	-m           	-3.000000e-01	             	             	             	               	;# BR1
uniaxialMaterial	Elastic     	241	+2.900000e-02	             	             	             	             	             	             	             	               	;# BR1
uniaxialMaterial	Parallel    	242	240 241      	             	             	             	             	             	             	             	               	;# BR1
uniaxialMaterial	Steel02     	243	+6.440000e+01	+2.900000e+04	+1.000000e-03	+2.200000e+01	+9.250000e-01	+2.500000e-01	+0.03 +1.00  	+0.02 +1.00  	               	;# BR2
uniaxialMaterial	Fatigue     	244	243          	-E0          	+4.660027e-02	-m           	-3.000000e-01	             	             	             	               	;# BR2
uniaxialMaterial	Elastic     	245	+2.900000e-02	             	             	             	             	             	             	             	               	;# BR2
uniaxialMaterial	Parallel    	246	244 245      	             	             	             	             	             	             	             	               	;# BR2
uniaxialMaterial	Steel02     	247	+6.440000e+01	+2.900000e+04	+1.000000e-03	+2.200000e+01	+9.250000e-01	+2.500000e-01	+0.03 +1.00  	+0.02 +1.00  	               	;# BR3
uniaxialMaterial	Fatigue     	248	247          	-E0          	+4.503494e-02	-m           	-3.000000e-01	             	             	             	               	;# BR3
uniaxialMaterial	Elastic     	249	+2.900000e-02	             	             	             	             	             	             	             	               	;# BR3
uniaxialMaterial	Parallel    	250	248 249      	             	             	             	             	             	             	             	               	;# BR3
uniaxialMaterial	Steel02     	251	+6.440000e+01	+2.900000e+04	+1.000000e-03	+2.200000e+01	+9.250000e-01	+2.500000e-01	+0.03 +1.00  	+0.02 +1.00  	               	;# BR4
uniaxialMaterial	Fatigue     	252	251          	-E0          	+4.499452e-02	-m           	-3.000000e-01	             	             	             	               	;# BR4
uniaxialMaterial	Elastic     	253	+2.900000e-02	             	             	             	             	             	             	             	               	;# BR4
uniaxialMaterial	Parallel    	254	252 253      	             	             	             	             	             	             	             	               	;# BR4
uniaxialMaterial	Steel02     	255	+6.440000e+01	+2.900000e+04	+1.000000e-03	+2.200000e+01	+9.250000e-01	+2.500000e-01	+0.03 +1.00  	+0.02 +1.00  	               	;# BR5
uniaxialMaterial	Fatigue     	256	255          	-E0          	+4.660027e-02	-m           	-3.000000e-01	             	             	             	               	;# BR5
uniaxialMaterial	Elastic     	257	+2.900000e-02	             	             	             	             	             	             	             	               	;# BR5
uniaxialMaterial	Parallel    	258	256 257      	             	             	             	             	             	             	             	               	;# BR5
uniaxialMaterial	Steel02     	259	+6.440000e+01	+2.900000e+04	+1.000000e-03	+2.200000e+01	+9.250000e-01	+2.500000e-01	+0.03 +1.00  	+0.02 +1.00  	               	;# BR6
uniaxialMaterial	Fatigue     	260	259          	-E0          	+4.503494e-02	-m           	-3.000000e-01	             	             	             	               	;# BR6
uniaxialMaterial	Elastic     	261	+2.900000e-02	             	             	             	             	             	             	             	               	;# BR6
uniaxialMaterial	Parallel    	262	260 261      	             	             	             	             	             	             	             	               	;# BR6
# ===================================================================================================================================================================================
