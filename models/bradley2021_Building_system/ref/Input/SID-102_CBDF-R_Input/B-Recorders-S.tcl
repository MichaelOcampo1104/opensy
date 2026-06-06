# ===================================================================================================================================================================================
# This script defines a set of recorders to produce desired output for various elements and nodes.
set recDrift [ recorder Drift -file "$out/Drift.txt" -time -iNode 39 44 49 39 55 60 65 55 -jNode 44 49 54 54 60 65 70 70 -dof 1 -perpDirn 2 ];# Drift.txt
set recNodalReactions [ recorder Node -file "$out/NodalReactions.txt" -time -node 1 25 39 55 71 85 109 133 157 171 185 209 233 247 261 285 309 323 -dof 1 2 reaction ];# NodalReactions.txt
# ===================================================================================================================================================================================
