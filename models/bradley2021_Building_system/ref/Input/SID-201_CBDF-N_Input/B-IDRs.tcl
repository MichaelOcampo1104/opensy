# =========================================================================
# This script obtains the displacments of the braced frame column nodes at
# the floor levels and uses those values to calculate story displacements
# assuming rigid diaphragm action. In addition this script defines a
# variable that contains individual story heights, which are used to
# calculated interstory drift ratios in other scripts.
 
## Get displacements at top and bottom of each story
scan [nodeResponse 39 1 1] "%s" dB1
scan [nodeResponse 44 1 1] "%s" dB2
scan [nodeResponse 49 1 1] "%s" dB3
scan [nodeResponse 44 1 1] "%s" dT1
scan [nodeResponse 49 1 1] "%s" dT2
scan [nodeResponse 54 1 1] "%s" dT3
 
## Define lists of displacements at top and bottom of each story
set dBs [list $dB1 $dB2 $dB3]
set dTs [list $dT1 $dT2 $dT3]
 
## Define list of story heights (inches)
set hSs [list 180.0 180.0 180.0]
# =========================================================================
