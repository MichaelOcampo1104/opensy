# =========================================================================
# This script defines the control node (for the displacement protocol) as
# well as the load pattern used in the pushover analyses. The pushover
# loads are applied at floor levels and distributed vertically over the
# height of the structure as defined by the ELFP of ASCE 7-10.
 
## Define the control node and ELFP load ratios
set cNode 54;
set lat1 2.137474e+01
set lat2 4.358698e+01
set lat3 3.306335e+01
 
## Define the load pattern
pattern Plain 200 Linear {
load 44 $lat1 0.0 0.0
load 49 $lat2 0.0 0.0
load 54 $lat3 0.0 0.0
load 60 $lat1 0.0 0.0
load 65 $lat2 0.0 0.0
load 70 $lat3 0.0 0.0
}
# =========================================================================
