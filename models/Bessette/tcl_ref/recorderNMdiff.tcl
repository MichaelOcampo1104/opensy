set dataDir1 NM/GM[lindex $matGMid $idgmi-1]
file mkdir $dataDir1

puts "Create post-gravity recorders"

set recDT 1

if {$process_id == 0} {
set soilEPInodes {850 852 862 869 876 883 890 897 904 911 918 925 932 939 946 953 960 967 974 981 988 4980 5767 6547 }
eval "recorder Node -file $dataDir1/soilEPI_pwp_diff_idCf48_GM[lindex $matGMid $idgmi-1]-part0.out -time -dT $recDT -node $soilEPInodes -dof 4 vel"

} elseif {$process_id == 1} {
set soilEPInodes {4980 4987 4994 5001 5008 5015 5022 5029 5036 5043 5050 5057 5064 5071 5078 5085 5092 5767 5779 5786 5793 5800 5807 5814 5821 5828 5835 5842 5849 5856 5863 5870 5877 5884 6547 6559 6566 6573 6580 6587 6594 6601 6608 6615 6622 6629 6636 6643 6650 6657 6664 }
eval "recorder Node -file $dataDir1/soilEPI_pwp_diff_idCf48_GM[lindex $matGMid $idgmi-1]-part1.out -time -dT $recDT -node $soilEPInodes -dof 4 vel"

} elseif {$process_id == 2} {
set soilEPInodes {10642 10644 10654 10661 10668 10675 10682 10689 10696 10703 10710 10717 10724 10731 10738 10745 10752 10759 10766 10773 10780}
eval "recorder Node -file $dataDir1/soilEPI_pwp_diff_idCf48_GM[lindex $matGMid $idgmi-1]-part2.out -time -dT $recDT -node $soilEPInodes -dof 4 vel"

}
