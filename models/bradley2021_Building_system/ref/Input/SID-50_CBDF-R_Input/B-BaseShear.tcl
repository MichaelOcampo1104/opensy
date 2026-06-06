# =========================================================================
# This script obtains the reaction forces of nodes at the bottom of all
# columns in the building and then uses those values to calculate the
# current base shear of the system.
 
## Get column base reactions (x-direction)
set node1   [nodeReaction 1   1 0 0]
set node25  [nodeReaction 25  1 0 0]
set node39  [nodeReaction 39  1 0 0]
set node55  [nodeReaction 55  1 0 0]
set node71  [nodeReaction 71  1 0 0]
set node85  [nodeReaction 85  1 0 0]
set node109 [nodeReaction 109 1 0 0]
set node133 [nodeReaction 133 1 0 0]
set node157 [nodeReaction 157 1 0 0]
set node171 [nodeReaction 171 1 0 0]
set node185 [nodeReaction 185 1 0 0]
set node209 [nodeReaction 209 1 0 0]
set node233 [nodeReaction 233 1 0 0]
set node247 [nodeReaction 247 1 0 0]
set node261 [nodeReaction 261 1 0 0]
set node285 [nodeReaction 285 1 0 0]
set node309 [nodeReaction 309 1 0 0]
set node323 [nodeReaction 323 1 0 0]
 
## Calculate base shear
set Vb [expr \
   +$node1   +$node25  +$node39  +$node55  +$node71  +$node85  \
   +$node109 +$node133 +$node157 +$node171 +$node185 +$node209 \
   +$node233 +$node247 +$node261 +$node285 +$node309 +$node323 \
]
# =========================================================================
