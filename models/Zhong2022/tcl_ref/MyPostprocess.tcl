set num_story 12

set sdr_max_1 {}
set sdr_max_2 {}
set pfa_1 {}
set pfa_2 {}
set pfd_1 {}
set pfd_2 {}
set sdr_res_1 {}
set sdr_res_2 {}

# max drift ratio
for {set i 1} {$i < [expr $num_story+1]} {incr i} {
   # dof 1
   set mdrIn [open max_story_drift_[expr $i]_1.out r]
   while { [gets $mdrIn data] >= 0 } {
      set tmp_max $data
   }
   lappend sdr_max_1 $tmp_max
   # dof 2
   set mdrIn [open max_story_drift_[expr $i]_2.out r]
   while { [gets $mdrIn data] >= 0 } {
      set tmp_max $data
   }
   lappend sdr_max_2 $tmp_max
}

# residual drift ratio
for {set i 1} {$i < [expr $num_story+1]} {incr i} {
   # dof 1
   set sdrIn [open story_drift_[expr $i]_1.out r]
   while { [gets $sdrIn data] >= 0 } {
      # reading until the last data point
      set tmp $data
   }
   lappend sdr_res_1 $tmp
   # dof 2
   set sdrIn [open story_drift_[expr $i]_2.out r]
   while { [gets $sdrIn data] >= 0 } {
      # reading until the last data point
      set tmp $data
   }
   lappend sdr_res_2 $tmp
}

# peak floor acceleration
for {set i 1} {$i < [expr $num_story+1]} {incr i} {
   # dof 1
   set pfaIn [open max_abs_acceleration_[expr $i]_1.out r]
   while { [gets $pfaIn data] >= 0 } {
      set tmp_pfa $data
   }
   lappend pfa_1 $tmp_pfa
   # dof 2
   set pfaIn [open max_abs_acceleration_[expr $i]_2.out r]
   while { [gets $pfaIn data] >= 0 } {
      set tmp_pfa $data
   }
   lappend pfa_2 $tmp_pfa
}

# max roof drift
# dof 1
set roofIn [open max_roof_drift_1.out r]
while { [gets $roofIn data] >= 0 } {
   set roof_drift_1 $data
}
# dof 2
set roofIn [open max_roof_drift_2.out r]
while { [gets $roofIn data] >= 0 } {
   set roof_drift_2 $data
}

# max floor displacement
for {set i 1} {$i < [expr $num_story+1]} {incr i} {
   # dof 1
   set mfdIn [open max_floor_disp_[expr $i]_1.out r]
   while { [gets $mfdIn data] >= 0 } {
      set tmp_pfd $data
   }
   lappend pfd_1 $tmp_pfd
   # dof 2
   set mfdIn [open max_floor_disp_[expr $i]_2.out r]
   while { [gets $mfdIn data] >= 0 } {
      set tmp_pfd $data
   }
   lappend pfd_2 $tmp_pfd
}

# create file handler to write results to output & list into which we will put results
set resultFile [open results.out w]
set results []

# for each quanity in list of QoI passed

foreach edp $listQoI {
   puts $edp
   set splitEDP [split $edp "-"]
   set levelIndex [lindex $splitEDP 2]
   set dofIndex [lindex $splitEDP 3]

   # maximum drift ratio
   if {[lindex $splitEDP 1] == "PID"} {
      if {$dofIndex == "1"} {
         set edp_value [lindex $sdr_max_1 [expr $levelIndex-1]]
      } else {
         set edp_value [lindex $sdr_max_2 [expr $levelIndex-1]]
      }
   }

   # residual story drift ratio
   if {[lindex $splitEDP 1] == "RSD"} {
      if {$dofIndex == "1"} {
         set edp_value [lindex $sdr_res_1 [expr $levelIndex-1]]
      } else {
         set edp_value [lindex $sdr_res_2 [expr $levelIndex-1]]
      }
   }

   # pfa
   if {[lindex $splitEDP 1] == "PFA"} {
      if {$dofIndex == "1"} {
         set edp_value [lindex $pfa_1 [expr $levelIndex-1]]
      } else {
         set edp_value [lindex $pfa_2 [expr $levelIndex-1]]
      }
   }

   # pfd
   if {[lindex $splitEDP 1] == "PFD"} {
      if {$dofIndex == "1"} {
         set edp_value [lindex $pfd_1 [expr $levelIndex-1]]
      } else {
         set edp_value [lindex $pfd_2 [expr $levelIndex-1]]
      }
   }

   # roof drift
   if {[lindex $splitEDP 1] == "PRD"} {
      if {$dofIndex == "1"} {
         set edp_value $roof_drift_1
      } else {
         set edp_value $roof_drift_2
      }
   }
  
   lappend results $edp_value
}

# write results into the resultFile
puts $resultFile $results
close $resultFile