set dataDir1 DGC/GM[lindex $matGMid $idgmi-1]
file mkdir $dataDir1

puts "Create post-gravity recorders"

set recDT 1

if {$process_id == 0} {
set soilEPInodes {1161 1163 1173 1180 1187 1194 1201 1208 1215 1222 1229 1236 1243 1250 1257 1264 1271 1278 1285 1292 1299 7407 8490 9554 }
eval "recorder Node -file $dataDir1/soilEPI_pwp_diff_idCf48_GM[lindex $matGMid $idgmi-1]-part0.out -time -dT $recDT -node $soilEPInodes -dof 4 vel"

} elseif {$process_id == 1} {
set soilEPInodes {7407 7414 7421 7428 7435 7442 7449 7456 7463 7470 7477 7484 7491 7498 7505 7512 7519 8490 8502 8509 8516 8523 8530 8537 8544 8551 8558 8565 8572 8579 8586 8593 8600 8607 }
eval "recorder Node -file $dataDir1/soilEPI_pwp_diff_idCf48_GM[lindex $matGMid $idgmi-1]-part1.out -time -dT $recDT -node $soilEPInodes -dof 4 vel"

} elseif {$process_id == 2} {
set soilEPInodes {9554 9566 9573 9580 9587 9594 9601 9608 9615 9622 9629 9636 9643 9650 9657 9664 9671 }
eval "recorder Node -file $dataDir1/soilEPI_pwp_diff_idCf48_GM[lindex $matGMid $idgmi-1]-part2.out -time -dT $recDT -node $soilEPInodes -dof 4 vel"

} elseif {$process_id == 3} {
set soilEPInodes {15762 15764 15774 15781 15788 15795 15802 15809 15816 15823 15830 15837 15844 15851 15858 15865 15872 15879 15886 15893 15900}
eval "recorder Node -file $dataDir1/soilEPI_pwp_diff_idCf48_GM[lindex $matGMid $idgmi-1]-part3.out -time -dT $recDT -node $soilEPInodes -dof 4 vel"

}
