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
pattern	Plain	103	Linear	{

load	121	[lindex $LateralLoad 0] 0.0 0.0;	# Level2
load	131	[lindex $LateralLoad 1] 0.0 0.0;	# Level3
load	141	[lindex $LateralLoad 2] 0.0 0.0;	# Level4
load	151	[lindex $LateralLoad 3] 0.0 0.0;	# Level5
load	161	[lindex $LateralLoad 4] 0.0 0.0;	# Level6
load	171	[lindex $LateralLoad 5] 0.0 0.0;	# Level7
load	181	[lindex $LateralLoad 6] 0.0 0.0;	# Level8
load	191	[lindex $LateralLoad 7] 0.0 0.0;	# Level9
load	1101	[lindex $LateralLoad 8] 0.0 0.0;	# Level10

}
# puts "Earthquake load defined"