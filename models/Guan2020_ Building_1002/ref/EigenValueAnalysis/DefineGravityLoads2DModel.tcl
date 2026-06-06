# Define expected gravity loads


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

# Assign point live load values on leaning column: kip
set	LeaningColumnLiveLoadFloor2	562.500000; 
set	LeaningColumnLiveLoadFloor3	562.500000; 
set	LeaningColumnLiveLoadFloor4	562.500000; 
set	LeaningColumnLiveLoadFloor5	562.500000; 
set	LeaningColumnLiveLoadFloor6	562.500000; 
set	LeaningColumnLiveLoadFloor7	562.500000; 
set	LeaningColumnLiveLoadFloor8	562.500000; 
set	LeaningColumnLiveLoadFloor9	562.500000; 
set	LeaningColumnLiveLoadFloor10	562.500000; 

# Define uniform loads on beams
# Load combinations:
# 104 Expected gravity loads: 1.05 DL + 0.25 LL
pattern	Plain	104	Constant	{

# Level2
eleLoad	-ele	2121221	-type	-beamUniform	[expr -1.05*$BeamDeadLoadFloor2 - 0.25*$BeamLiveLoadFloor2];
eleLoad	-ele	2221321	-type	-beamUniform	[expr -1.05*$BeamDeadLoadFloor2 - 0.25*$BeamLiveLoadFloor2];
eleLoad	-ele	2321421	-type	-beamUniform	[expr -1.05*$BeamDeadLoadFloor2 - 0.25*$BeamLiveLoadFloor2];

# Level3
eleLoad	-ele	2131231	-type	-beamUniform	[expr -1.05*$BeamDeadLoadFloor3 - 0.25*$BeamLiveLoadFloor3];
eleLoad	-ele	2231331	-type	-beamUniform	[expr -1.05*$BeamDeadLoadFloor3 - 0.25*$BeamLiveLoadFloor3];
eleLoad	-ele	2331431	-type	-beamUniform	[expr -1.05*$BeamDeadLoadFloor3 - 0.25*$BeamLiveLoadFloor3];

# Level4
eleLoad	-ele	2141241	-type	-beamUniform	[expr -1.05*$BeamDeadLoadFloor4 - 0.25*$BeamLiveLoadFloor4];
eleLoad	-ele	2241341	-type	-beamUniform	[expr -1.05*$BeamDeadLoadFloor4 - 0.25*$BeamLiveLoadFloor4];
eleLoad	-ele	2341441	-type	-beamUniform	[expr -1.05*$BeamDeadLoadFloor4 - 0.25*$BeamLiveLoadFloor4];

# Level5
eleLoad	-ele	2151251	-type	-beamUniform	[expr -1.05*$BeamDeadLoadFloor5 - 0.25*$BeamLiveLoadFloor5];
eleLoad	-ele	2251351	-type	-beamUniform	[expr -1.05*$BeamDeadLoadFloor5 - 0.25*$BeamLiveLoadFloor5];
eleLoad	-ele	2351451	-type	-beamUniform	[expr -1.05*$BeamDeadLoadFloor5 - 0.25*$BeamLiveLoadFloor5];

# Level6
eleLoad	-ele	2161261	-type	-beamUniform	[expr -1.05*$BeamDeadLoadFloor6 - 0.25*$BeamLiveLoadFloor6];
eleLoad	-ele	2261361	-type	-beamUniform	[expr -1.05*$BeamDeadLoadFloor6 - 0.25*$BeamLiveLoadFloor6];
eleLoad	-ele	2361461	-type	-beamUniform	[expr -1.05*$BeamDeadLoadFloor6 - 0.25*$BeamLiveLoadFloor6];

# Level7
eleLoad	-ele	2171271	-type	-beamUniform	[expr -1.05*$BeamDeadLoadFloor7 - 0.25*$BeamLiveLoadFloor7];
eleLoad	-ele	2271371	-type	-beamUniform	[expr -1.05*$BeamDeadLoadFloor7 - 0.25*$BeamLiveLoadFloor7];
eleLoad	-ele	2371471	-type	-beamUniform	[expr -1.05*$BeamDeadLoadFloor7 - 0.25*$BeamLiveLoadFloor7];

# Level8
eleLoad	-ele	2181281	-type	-beamUniform	[expr -1.05*$BeamDeadLoadFloor8 - 0.25*$BeamLiveLoadFloor8];
eleLoad	-ele	2281381	-type	-beamUniform	[expr -1.05*$BeamDeadLoadFloor8 - 0.25*$BeamLiveLoadFloor8];
eleLoad	-ele	2381481	-type	-beamUniform	[expr -1.05*$BeamDeadLoadFloor8 - 0.25*$BeamLiveLoadFloor8];

# Level9
eleLoad	-ele	2191291	-type	-beamUniform	[expr -1.05*$BeamDeadLoadFloor9 - 0.25*$BeamLiveLoadFloor9];
eleLoad	-ele	2291391	-type	-beamUniform	[expr -1.05*$BeamDeadLoadFloor9 - 0.25*$BeamLiveLoadFloor9];
eleLoad	-ele	2391491	-type	-beamUniform	[expr -1.05*$BeamDeadLoadFloor9 - 0.25*$BeamLiveLoadFloor9];

# Level10
eleLoad	-ele	211012101	-type	-beamUniform	[expr -1.05*$BeamDeadLoadFloor10 - 0.25*$BeamLiveLoadFloor10];
eleLoad	-ele	221013101	-type	-beamUniform	[expr -1.05*$BeamDeadLoadFloor10 - 0.25*$BeamLiveLoadFloor10];
eleLoad	-ele	231014101	-type	-beamUniform	[expr -1.05*$BeamDeadLoadFloor10 - 0.25*$BeamLiveLoadFloor10];


# Define point loads on leaning column
load	52	0	[expr -1*$LeaningColumnDeadLoadFloor2 - 0.25*$LeaningColumnLiveLoadFloor2]	0;
load	53	0	[expr -1*$LeaningColumnDeadLoadFloor3 - 0.25*$LeaningColumnLiveLoadFloor3]	0;
load	54	0	[expr -1*$LeaningColumnDeadLoadFloor4 - 0.25*$LeaningColumnLiveLoadFloor4]	0;
load	55	0	[expr -1*$LeaningColumnDeadLoadFloor5 - 0.25*$LeaningColumnLiveLoadFloor5]	0;
load	56	0	[expr -1*$LeaningColumnDeadLoadFloor6 - 0.25*$LeaningColumnLiveLoadFloor6]	0;
load	57	0	[expr -1*$LeaningColumnDeadLoadFloor7 - 0.25*$LeaningColumnLiveLoadFloor7]	0;
load	58	0	[expr -1*$LeaningColumnDeadLoadFloor8 - 0.25*$LeaningColumnLiveLoadFloor8]	0;
load	59	0	[expr -1*$LeaningColumnDeadLoadFloor9 - 0.25*$LeaningColumnLiveLoadFloor9]	0;
load	510	0	[expr -1*$LeaningColumnDeadLoadFloor10 - 0.25*$LeaningColumnLiveLoadFloor10]	0;

}
puts "Expected gravity loads defined"