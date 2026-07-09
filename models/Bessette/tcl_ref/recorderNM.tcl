set dataDir1 NM/GM[lindex $matGMid $idgmi-1]
file mkdir $dataDir1

puts "Create post-gravity recorders"

if {$process_id == 0} {
set soilnodes {852 869 890 911 918 981 }
eval "recorder Node -file $dataDir1/soil_acc13_idCf48_GM[lindex $matGMid $idgmi-1]-part0.out -time -node $soilnodes -dof 1 3 accel"
eval "recorder Node -file $dataDir1/soil_pwp_idCf48_GM[lindex $matGMid $idgmi-1]-part0.out -time -node $soilnodes -dof 4 vel"
} elseif {$process_id == 1} {
set soilnodes {4994 5015 5022 5085 5786 5807 5814 5877 6566 6587 6594 6657 }
eval "recorder Node -file $dataDir1/soil_acc13_idCf48_GM[lindex $matGMid $idgmi-1]-part1.out -time -node $soilnodes -dof 1 3 accel"
eval "recorder Node -file $dataDir1/soil_pwp_idCf48_GM[lindex $matGMid $idgmi-1]-part1.out -time -node $soilnodes -dof 4 vel"
} elseif {$process_id == 2} {
set soilnodes {10644 10661 10682 10703 10710 10773}
eval "recorder Node -file $dataDir1/soil_acc13_idCf48_GM[lindex $matGMid $idgmi-1]-part2.out -time -node $soilnodes -dof 1 3 accel"
eval "recorder Node -file $dataDir1/soil_pwp_idCf48_GM[lindex $matGMid $idgmi-1]-part2.out -time -node $soilnodes -dof 4 vel"
}

if {$process_id == 0} {
set soilEPInodes {850 852 862 869 876 883 890 897 904 911 918 925 932 939 946 953 960 967 974 981 988 4980 5767 6547 }
eval "recorder Node -file $dataDir1/soilEPI_pwp_idCf48_GM[lindex $matGMid $idgmi-1]-part0.out -time -node $soilEPInodes -dof 4 vel"

} elseif {$process_id == 1} {
set soilEPInodes {4980 4987 4994 5001 5008 5015 5022 5029 5036 5043 5050 5057 5064 5071 5078 5085 5092 5767 5779 5786 5793 5800 5807 5814 5821 5828 5835 5842 5849 5856 5863 5870 5877 5884 6547 6559 6566 6573 6580 6587 6594 6601 6608 6615 6622 6629 6636 6643 6650 6657 6664 }
eval "recorder Node -file $dataDir1/soilEPI_pwp_idCf48_GM[lindex $matGMid $idgmi-1]-part1.out -time -node $soilEPInodes -dof 4 vel"

} elseif {$process_id == 2} {
set soilEPInodes {10642 10644 10654 10661 10668 10675 10682 10689 10696 10703 10710 10717 10724 10731 10738 10745 10752 10759 10766 10773 10780}
eval "recorder Node -file $dataDir1/soilEPI_pwp_idCf48_GM[lindex $matGMid $idgmi-1]-part2.out -time -node $soilEPInodes -dof 4 vel"

}

if {$process_id == 0} {
set foundnodes {100006 100047 100319 100344}
eval "recorder Node -file $dataDir1/found_disp13_idCf48_GM[lindex $matGMid $idgmi-1]-part0.out -time -node $foundnodes -dof 1 3 disp"

set foundaccnode {100156}
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
set soilelement {121 123 124 126 127 129 130 131 139 140 161 163 164 166 167 169 170 171 179 180}
   eval "recorder Element -file $dataDir1/soilstrain27_idCf48_GM[lindex $matGMid $idgmi-1]-part0.out -time -ele $soilelement material 27 strain"
   eval "recorder Element -file $dataDir1/soilstress27_idCf48_GM[lindex $matGMid $idgmi-1]-part0.out -time -ele $soilelement material 27 stress"
} elseif {$process_id == 1} {
set soilelement {846 847 849 850 851 859 860 883 884 886 887 888 896 897 985 986 988 989 990 998 999 1019 1020 1022 1023 1024 1032 1033 1121 1122 1124 1125 1126 1134 1135 1158 1159 1161 1162 1163 1171 1172}
   eval "recorder Element -file $dataDir1/soilstrain27_idCf48_GM[lindex $matGMid $idgmi-1]-part1.out -time -ele $soilelement material 27 strain"
   eval "recorder Element -file $dataDir1/soilstress27_idCf48_GM[lindex $matGMid $idgmi-1]-part1.out -time -ele $soilelement material 27 stress"
} elseif {$process_id == 2} {
set soilelement {1833 1835 1836 1838 1839 1841 1842 1843 1851 1852 1873 1875 1876 1878 1879 1881 1882 1883 1891 1892}
   eval "recorder Element -file $dataDir1/soilstrain27_idCf48_GM[lindex $matGMid $idgmi-1]-part2.out -time -ele $soilelement material 27 strain"
   eval "recorder Element -file $dataDir1/soilstress27_idCf48_GM[lindex $matGMid $idgmi-1]-part2.out -time -ele $soilelement material 27 stress"
}

if {$process_id == 0} {
recorder Node -file $dataDir1/Vbase_idCf48_GM[lindex $matGMid $idgmi-1]-part0.out -time -node 5000001 5000002 -dof 1 reaction


}
puts "Created opensees dynamic recorders..."

