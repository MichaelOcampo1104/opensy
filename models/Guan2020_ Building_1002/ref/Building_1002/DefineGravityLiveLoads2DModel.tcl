# Define gravity live loads


# Assign uniform beam dead load values (kip/inch)
set	BeamDeadLoadFloor2	0.083333; 
set	BeamDeadLoadFloor3	0.083333; 
set	BeamDeadLoadFloor4	0.083333; 
set	BeamDeadLoadFloor5	0.083333; 
set	BeamDeadLoadFloor6	0.083333; 
set	BeamDeadLoadFloor7	0.083333; 
set	BeamDeadLoadFloor8	0.083333; 
set	BeamDeadLoadFloor9	0.083333; 
set	BeamDeadLoadFloor10	0.112500; 

# Assign uniform beam live load values (kip/inch)
set	BeamLiveLoadFloor2	0.083333; 
set	BeamLiveLoadFloor3	0.083333; 
set	BeamLiveLoadFloor4	0.083333; 
set	BeamLiveLoadFloor5	0.083333; 
set	BeamLiveLoadFloor6	0.083333; 
set	BeamLiveLoadFloor7	0.083333; 
set	BeamLiveLoadFloor8	0.083333; 
set	BeamLiveLoadFloor9	0.083333; 
set	BeamLiveLoadFloor10	0.033333; 

# Assign point dead load values on leaning column: kip
set	LeaningColumnDeadLoadFloor2	562.500000; 
set	LeaningColumnDeadLoadFloor3	562.500000; 
set	LeaningColumnDeadLoadFloor4	562.500000; 
set	LeaningColumnDeadLoadFloor5	562.500000; 
set	LeaningColumnDeadLoadFloor6	562.500000; 
set	LeaningColumnDeadLoadFloor7	562.500000; 
set	LeaningColumnDeadLoadFloor8	562.500000; 
set	LeaningColumnDeadLoadFloor9	562.500000; 
set	LeaningColumnDeadLoadFloor10	759.375000; 

# Assign point live load values on leaning column (kip)
set	LeaningColumnLiveLoadFloor2	562.500000; 
set	LeaningColumnLiveLoadFloor3	562.500000; 
set	LeaningColumnLiveLoadFloor4	562.500000; 
set	LeaningColumnLiveLoadFloor5	562.500000; 
set	LeaningColumnLiveLoadFloor6	562.500000; 
set	LeaningColumnLiveLoadFloor7	562.500000; 
set	LeaningColumnLiveLoadFloor8	562.500000; 
set	LeaningColumnLiveLoadFloor9	562.500000; 
set	LeaningColumnLiveLoadFloor10	562.500000; 

# Assign lateral load values caused by earthquake (kip)
set	LateralLoad	[list	4.866954	9.745798	15.950627	23.374284	31.940224	41.589703	52.275514	63.958481	103.417165];


# Define uniform loads on beams
# Load combinations:
# 101 Dead load only
# 102 Live load only
# 103 Earthquake load only
# 104 Gravity and earthquake (for calculation of drift)
pattern	Plain	102	Constant	{# Level2
eleLoad	-ele	2121221	-type	-beamUniform	[expr -1*$BeamLiveLoadFloor2]; 
eleLoad	-ele	2221321	-type	-beamUniform	[expr -1*$BeamLiveLoadFloor2]; 
eleLoad	-ele	2321421	-type	-beamUniform	[expr -1*$BeamLiveLoadFloor2]; 

# Level3
eleLoad	-ele	2131231	-type	-beamUniform	[expr -1*$BeamLiveLoadFloor3]; 
eleLoad	-ele	2231331	-type	-beamUniform	[expr -1*$BeamLiveLoadFloor3]; 
eleLoad	-ele	2331431	-type	-beamUniform	[expr -1*$BeamLiveLoadFloor3]; 

# Level4
eleLoad	-ele	2141241	-type	-beamUniform	[expr -1*$BeamLiveLoadFloor4]; 
eleLoad	-ele	2241341	-type	-beamUniform	[expr -1*$BeamLiveLoadFloor4]; 
eleLoad	-ele	2341441	-type	-beamUniform	[expr -1*$BeamLiveLoadFloor4]; 

# Level5
eleLoad	-ele	2151251	-type	-beamUniform	[expr -1*$BeamLiveLoadFloor5]; 
eleLoad	-ele	2251351	-type	-beamUniform	[expr -1*$BeamLiveLoadFloor5]; 
eleLoad	-ele	2351451	-type	-beamUniform	[expr -1*$BeamLiveLoadFloor5]; 

# Level6
eleLoad	-ele	2161261	-type	-beamUniform	[expr -1*$BeamLiveLoadFloor6]; 
eleLoad	-ele	2261361	-type	-beamUniform	[expr -1*$BeamLiveLoadFloor6]; 
eleLoad	-ele	2361461	-type	-beamUniform	[expr -1*$BeamLiveLoadFloor6]; 

# Level7
eleLoad	-ele	2171271	-type	-beamUniform	[expr -1*$BeamLiveLoadFloor7]; 
eleLoad	-ele	2271371	-type	-beamUniform	[expr -1*$BeamLiveLoadFloor7]; 
eleLoad	-ele	2371471	-type	-beamUniform	[expr -1*$BeamLiveLoadFloor7]; 

# Level8
eleLoad	-ele	2181281	-type	-beamUniform	[expr -1*$BeamLiveLoadFloor8]; 
eleLoad	-ele	2281381	-type	-beamUniform	[expr -1*$BeamLiveLoadFloor8]; 
eleLoad	-ele	2381481	-type	-beamUniform	[expr -1*$BeamLiveLoadFloor8]; 

# Level9
eleLoad	-ele	2191291	-type	-beamUniform	[expr -1*$BeamLiveLoadFloor9]; 
eleLoad	-ele	2291391	-type	-beamUniform	[expr -1*$BeamLiveLoadFloor9]; 
eleLoad	-ele	2391491	-type	-beamUniform	[expr -1*$BeamLiveLoadFloor9]; 

# Level10
eleLoad	-ele	211012101	-type	-beamUniform	[expr -1*$BeamLiveLoadFloor10]; 
eleLoad	-ele	221013101	-type	-beamUniform	[expr -1*$BeamLiveLoadFloor10]; 
eleLoad	-ele	231014101	-type	-beamUniform	[expr -1*$BeamLiveLoadFloor10]; 



# Define point loads on leaning column
load	52	0	[expr -1*$LeaningColumnLiveLoadFloor2]	0; 
load	53	0	[expr -1*$LeaningColumnLiveLoadFloor3]	0; 
load	54	0	[expr -1*$LeaningColumnLiveLoadFloor4]	0; 
load	55	0	[expr -1*$LeaningColumnLiveLoadFloor5]	0; 
load	56	0	[expr -1*$LeaningColumnLiveLoadFloor6]	0; 
load	57	0	[expr -1*$LeaningColumnLiveLoadFloor7]	0; 
load	58	0	[expr -1*$LeaningColumnLiveLoadFloor8]	0; 
load	59	0	[expr -1*$LeaningColumnLiveLoadFloor9]	0; 
load	510	0	[expr -1*$LeaningColumnLiveLoadFloor10]	0; 

}
# puts "Live load defined"