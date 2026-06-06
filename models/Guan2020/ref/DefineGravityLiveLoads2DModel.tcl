# Define gravity live loads


# Assign uniform beam dead load values (kip/inch)
set	BeamDeadLoadFloor2	0.066667; 

# Assign uniform beam live load values (kip/inch)
set	BeamLiveLoadFloor2	0.041667; 

# Assign point dead load values on leaning column: kip
set	LeaningColumnDeadLoadFloor2	900.000000; 

# Assign point live load values on leaning column (kip)
set	LeaningColumnLiveLoadFloor2	562.500000; 

# Assign lateral load values caused by earthquake (kip)
set	LateralLoad	[list	159.952126];


# Define uniform loads on beams
# Load combinations:
# 101 Dead load only
# 102 Live load only
# 103 Earthquake load only
# 104 Gravity and earthquake (for calculation of drift)
pattern	Plain	102	Constant	{# Level2
eleLoad	-ele	2121221	-type	-beamUniform	[expr -1*$BeamLiveLoadFloor2]; 



# Define point loads on leaning column
load	32	0	[expr -1*$LeaningColumnLiveLoadFloor2]	0; 

}
# puts "Live load defined"