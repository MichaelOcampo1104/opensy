set dataDir1 DGC/GM[lindex $matGMid $idgmi-1]
file mkdir $dataDir1

puts "Create post-gravity recorders"

if {$process_id == 0} {
set soilnodes {1163 1180 1201 1222 1229 1292 }
eval "recorder Node -file $dataDir1/soil_acc13_idCf48_GM[lindex $matGMid $idgmi-1]-part0.out -time -node $soilnodes -dof 1 3 accel"
eval "recorder Node -file $dataDir1/soil_pwp_idCf48_GM[lindex $matGMid $idgmi-1]-part0.out -time -node $soilnodes -dof 4 vel"
} elseif {$process_id == 1} {
set soilnodes {7421 7442 7449 7512 8509 8530 8537 8600 }
eval "recorder Node -file $dataDir1/soil_acc13_idCf48_GM[lindex $matGMid $idgmi-1]-part1.out -time -node $soilnodes -dof 1 3 accel"
eval "recorder Node -file $dataDir1/soil_pwp_idCf48_GM[lindex $matGMid $idgmi-1]-part1.out -time -node $soilnodes -dof 4 vel"
} elseif {$process_id == 2} {
set soilnodes {9573 9594 9601 9664 }
eval "recorder Node -file $dataDir1/soil_acc13_idCf48_GM[lindex $matGMid $idgmi-1]-part2.out -time -node $soilnodes -dof 1 3 accel"
eval "recorder Node -file $dataDir1/soil_pwp_idCf48_GM[lindex $matGMid $idgmi-1]-part2.out -time -node $soilnodes -dof 4 vel"
} elseif {$process_id == 3} {
set soilnodes {15764 15781 15802 15823 15830 15893}
eval "recorder Node -file $dataDir1/soil_acc13_idCf48_GM[lindex $matGMid $idgmi-1]-part3.out -time -node $soilnodes -dof 1 3 accel"
eval "recorder Node -file $dataDir1/soil_pwp_idCf48_GM[lindex $matGMid $idgmi-1]-part3.out -time -node $soilnodes -dof 4 vel"
}

if {$process_id == 0} {
set soilEPInodes {1161 1163 1173 1180 1187 1194 1201 1208 1215 1222 1229 1236 1243 1250 1257 1264 1271 1278 1285 1292 1299 7407 8490 9554 }
eval "recorder Node -file $dataDir1/soilEPI_pwp_idCf48_GM[lindex $matGMid $idgmi-1]-part0.out -time -node $soilEPInodes -dof 4 vel"

} elseif {$process_id == 1} {
set soilEPInodes {7407 7414 7421 7428 7435 7442 7449 7456 7463 7470 7477 7484 7491 7498 7505 7512 7519 8490 8502 8509 8516 8523 8530 8537 8544 8551 8558 8565 8572 8579 8586 8593 8600 8607 }
eval "recorder Node -file $dataDir1/soilEPI_pwp_idCf48_GM[lindex $matGMid $idgmi-1]-part1.out -time -node $soilEPInodes -dof 4 vel"

} elseif {$process_id == 2} {
set soilEPInodes {9554 9566 9573 9580 9587 9594 9601 9608 9615 9622 9629 9636 9643 9650 9657 9664 9671 }
eval "recorder Node -file $dataDir1/soilEPI_pwp_idCf48_GM[lindex $matGMid $idgmi-1]-part2.out -time -node $soilEPInodes -dof 4 vel"

} elseif {$process_id == 3} {
set soilEPInodes {15762 15764 15774 15781 15788 15795 15802 15809 15816 15823 15830 15837 15844 15851 15858 15865 15872 15879 15886 15893 15900}
eval "recorder Node -file $dataDir1/soilEPI_pwp_idCf48_GM[lindex $matGMid $idgmi-1]-part3.out -time -node $soilEPInodes -dof 4 vel"

}

if {$process_id == 0} {
set foundnodes {100006 100073 100435 100475}
eval "recorder Node -file $dataDir1/found_disp13_idCf48_GM[lindex $matGMid $idgmi-1]-part0.out -time -node $foundnodes -dof 1 3 disp"

set foundaccnode {100212}
eval "recorder Node -file $dataDir1/foundacc_acc13_idCf48_GM[lindex $matGMid $idgmi-1]-part0.out -time -node $foundaccnode -dof 1 3 accel"

}
if {$process_id == 0} {
set structnodes {3000004 3000001}
eval "recorder Node -file $dataDir1/struct_disp13_idCf48_GM[lindex $matGMid $idgmi-1]-part0.out -time -node $structnodes -dof 1 3 disp"
eval "recorder Node -file $dataDir1/struct_acc13_idCf48_GM[lindex $matGMid $idgmi-1]-part0.out -time -node $structnodes -dof 1 3 accel"

set springele {600001 600003}
eval "recorder Element -file $dataDir1/springforce_idCf48_GM[lindex $matGMid $idgmi-1]-part0.out -time -ele $springele force"
eval "recorder Element -file $dataDir1/springdeform_idCf48_GM[lindex $matGMid $idgmi-1]-part0.out -time -ele $springele deformation"

}
if {$process_id == 0} {
set soilelement {181 183 184 186 187 189 190 191 199 200 241 243 244 246 247 249 250 251 259 260}
   eval "recorder Element -file $dataDir1/soilstrain27_idCf48_GM[lindex $matGMid $idgmi-1]-part0.out -time -ele $soilelement material 27 strain"
   eval "recorder Element -file $dataDir1/soilstress27_idCf48_GM[lindex $matGMid $idgmi-1]-part0.out -time -ele $soilelement material 27 stress"
} elseif {$process_id == 1} {
set soilelement {1386 1387 1389 1390 1391 1399 1400 1443 1444 1446 1447 1448 1456 1457 1596 1597 1599 1600 1601 1609 1610 1647 1648 1650 1651 1652 1660 1661}
   eval "recorder Element -file $dataDir1/soilstrain27_idCf48_GM[lindex $matGMid $idgmi-1]-part1.out -time -ele $soilelement material 27 strain"
   eval "recorder Element -file $dataDir1/soilstress27_idCf48_GM[lindex $matGMid $idgmi-1]-part1.out -time -ele $soilelement material 27 stress"
} elseif {$process_id == 2} {
set soilelement {1800 1801 1803 1804 1805 1813 1814 1854 1855 1857 1858 1859 1867 1868}
   eval "recorder Element -file $dataDir1/soilstrain27_idCf48_GM[lindex $matGMid $idgmi-1]-part2.out -time -ele $soilelement material 27 strain"
   eval "recorder Element -file $dataDir1/soilstress27_idCf48_GM[lindex $matGMid $idgmi-1]-part2.out -time -ele $soilelement material 27 stress"
} elseif {$process_id == 3} {
set soilelement {2989 2991 2992 2994 2995 2997 2998 2999 3007 3008 3049 3051 3052 3054 3055 3057 3058 3059 3067 3068}
   eval "recorder Element -file $dataDir1/soilstrain27_idCf48_GM[lindex $matGMid $idgmi-1]-part3.out -time -ele $soilelement material 27 strain"
   eval "recorder Element -file $dataDir1/soilstress27_idCf48_GM[lindex $matGMid $idgmi-1]-part3.out -time -ele $soilelement material 27 stress"
}

if {$process_id == 0} {
recorder Node -file $dataDir1/Vbase_idCf48_GM[lindex $matGMid $idgmi-1]-part0.out -time -node 5000001 5000002 -dof 1 reaction


}
puts "Created opensees dynamic recorders..."

