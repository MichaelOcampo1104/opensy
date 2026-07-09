# local response
set local_res_flag 1

# build model
source UCSDFrameWall.tcl

# define base motion inputs (level-1 acceleration history)
#set motion_id {"BI-7-ICA140" "FB-1-CNP100"}
set motion_id {"BI-1-CNP100" "BI-2-LAC100" "BI-3-LAC100" "BI-4-SP100" "BI-5-ICA50" "BI-6-ICA100" "BI-7-ICA140" \
               "FB-1-CNP100" "FB-2-LAC100" "FB-3-ICA50" "FB-4-ICA100" "FB-5-DEN67" "FB-6-DEN100"}
#set motion_id {"FB-5-DEN67" "FB-6-DEN100"}
#set motion_id {"BI-7-ICA140" "FB-1-CNP100" "FB-2-LAC100" "FB-3-ICA50" "FB-4-ICA100" "FB-5-DEN67" "FB-6-DEN100"}
set num_motions [llength $motion_id]

# define the recorder directory
set indir "./base_motions"
set resultdir "./analysis_results"

# motion sampling rate
set dt 0.005

# loop over all motions
for {set serial 0} {$serial < $num_motions} {incr serial} {
  # define the ground motion time series
  # X direction
  set filenameX "[lindex $motion_id $serial]-X.txt"
  timeSeries Path [expr 1000+$serial] -dt $dt -filePath $indir/$filenameX -factor [expr $g]
  set eq_load_patternX [expr 1000+$serial]
  pattern UniformExcitation $eq_load_patternX 1 -accel [expr 1000+$serial]
  ## disp (in inch)
  set filenameXd "[lindex $motion_id $serial]-disp-X.txt"
  timeSeries Path [expr 10000+$serial] -dt $dt -filePath $indir/$filenameXd -factor 1.0
  # Y direction
  set filenameY "[lindex $motion_id $serial]-Y.txt"
  timeSeries Path [expr 2000+$serial] -dt $dt -filePath $indir/$filenameY -factor [expr $g]
  set eq_load_patternY [expr 2000+$serial]
  pattern UniformExcitation $eq_load_patternY 2 -accel [expr 2000+$serial]
  ## disp (in inch)
  set filenameYd "[lindex $motion_id $serial]-disp-Y.txt"
  timeSeries Path [expr 20000+$serial] -dt $dt -filePath $indir/$filenameYd -factor 1.0
  # Z direction
  set filenameZ "[lindex $motion_id $serial]-Z.txt"
  timeSeries Path [expr 3000+$serial] -dt $dt -filePath $indir/$filenameZ -factor [expr $g]
  set eq_load_patternZ [expr 3000+$serial]
  pattern UniformExcitation $eq_load_patternZ 3 -accel [expr 3000+$serial]
  ## disp (in inch)
  set filenameZd "[lindex $motion_id $serial]-disp-Z.txt"
  timeSeries Path [expr 30000+$serial] -dt $dt -filePath $indir/$filenameZd -factor 1.0
  # RX direction
  timeSeries Path [expr 4000+$serial] -dt $dt -filePath $indir/$filenameX -factor 0.0
  # RY direction
  timeSeries Path [expr 5000+$serial] -dt $dt -filePath $indir/$filenameY -factor 0.0
  # RZ direction
  timeSeries Path [expr 6000+$serial] -dt $dt -filePath $indir/$filenameZ -factor 0.0
  # number of points
  set numpts 0
  set motion_file [open $indir/$filenameX r]
  while {[gets $motion_file line] >= 0} {
    incr numpts
  }

  # define drift and acceleration recorders for all stories
  set recorderdir "$resultdir/[lindex $motion_id $serial]"
  
  file mkdir $recorderdir
  # disp
  recorder Node -file $recorderdir/story_disp_rel.out -time -dT $dt -node 300 1300 2300 3300 4300 5300 -dof 1 2 3 disp
  recorder Node -file $recorderdir/story_disp.out -time -timeSeries [expr 10000+$serial] [expr 20000+$serial] [expr 30000+$serial] -dT $dt -node 300 1300 2300 3300 4300 5300 -dof 1 2 3 disp
  recorder Node -file $recorderdir/story_acc.out -timeSeries [expr 1000+$serial] [expr 2000+$serial] [expr 3000+$serial] -dT $dt -node 300 1300 2300 3300 4300 5300 -dof 1 2 3 accel
  recorder EnvelopeDrift -file $recorderdir/story_drift_env.out -iNode 300 1300 2300 3300 4300 -jNode 1300 2300 3300 4300 5300 -dof 1 2 -perpDirn 3
  recorder EnvelopeNode -file $recorderdir/story_acc_env.out -timeSeries [expr 1000+$serial] [expr 2000+$serial] -node 300 1300 2300 3300 4300 5300 -dof 1 2 accel
  for {set nid 1} {$nid <= [llength $all_nodes]} {incr nid} {
    recorder Node -file $recorderdir/node_disp_[lindex $all_nodes $nid-1].out -timeSeries [expr 10000+$serial] [expr 20000+$serial] [expr 30000+$serial] [expr 4000+$serial] [expr 5000+$serial] [expr 6000+$serial] -dT $dt -node [lindex $all_nodes $nid-1] -dof 1 2 3 4 5 6 disp
  }
  # story column forces
  #for {set tagele 1} {$tagele <= [llength $col_tags_recorded]} {incr tagele} {
  #  recorder EnvelopeElement -file $recorderdir/column_force_[lindex $col_tags_recorded \
  #    [expr {$tagele-1}]]_env.out -ele [lindex $col_tags_recorded [expr {$tagele-1}]] globalForce
  #}
  # wall bar stress strain response
  if {$local_res_flag} {
    for {set ip_id 1} {$ip_id < $numIntgrPts+1} {incr ip_id} {
      #  recorder Element -file $recorderdir/wall_bar_sst_ip$ip_id.out -dT $dt -ele 500 510 1500 1510 2500 2510 3500 3510 4500 4510 section $ip_id fiber [expr $wall_length/2.0-$c_concrete-0.5] 0.0 stressStrain
      #  recorder Element -file $recorderdir/wall_bar_ssb_ip$ip_id.out -dT $dt -ele 500 510 1500 1510 2500 2510 3500 3510 4500 4510 section $ip_id fiber [expr -$wall_length/2.0+$c_concrete+0.5] 0.0 stressStrain
      recorder Element -file $recorderdir/wall_bar_sst_ip$ip_id.out -dT $dt -ele 1500 1510 section $ip_id fiber [expr $wall_length/2.0-$c_concrete-0.5] 0.0 stressStrain
      recorder Element -file $recorderdir/wall_bar_ssb_ip$ip_id.out -dT $dt -ele 1500 1510 section $ip_id fiber [expr -$wall_length/2.0+$c_concrete+0.5] 0.0 stressStrain
    }
    # beam bar stress strain response
    for {set ip_id 1} {$ip_id < $numIntgrPts+1} {incr ip_id} {
      #  recorder Element -file $recorderdir/beam_bar_sst_ip$ip_id.out -dT $dt -ele 210 410 1210 1410 2210 2410 3210 3410 4210 4410 section $ip_id fiber [expr [lindex $h_beam 0]/2.0-$c_concrete-0.4] [expr [lindex $b_beam 0]/2.0-$c_concrete-0.4] stressStrain
      #  recorder Element -file $recorderdir/beam_bar_ssb_ip$ip_id.out -dT $dt -ele 210 410 1210 1410 2210 2410 3210 3410 4210 4410 section $ip_id fiber [expr -[lindex $h_beam 0]/2.0+$c_concrete+0.4] [expr [lindex $b_beam 0]/2.0-$c_concrete-0.4] stressStrain
      recorder Element -file $recorderdir/beam_bar_sst_ip$ip_id.out -dT $dt -ele 1210 1410 section $ip_id fiber [expr [lindex $h_beam 0]/2.0-$c_concrete-0.4] [expr [lindex $b_beam 0]/2.0-$c_concrete-0.4] stressStrain
      recorder Element -file $recorderdir/beam_bar_ssb_ip$ip_id.out -dT $dt -ele 1210 1410 section $ip_id fiber [expr -[lindex $h_beam 0]/2.0+$c_concrete+0.4] [expr [lindex $b_beam 0]/2.0-$c_concrete-0.4] stressStrain
    }
    # column bar stress strain response
    for {set tagele 7} {$tagele <= 12} {incr tagele} {
      for {set ip_id 1} {$ip_id < $numIntgrPts+1} {incr ip_id} {
        #  recorder Element -file $recorderdir/column_bar_sst_[lindex $col_tags_recorded [expr {$tagele-1}]]_ip$ip_id.out -dT $dt -ele [lindex $col_tags_recorded [expr {$tagele-1}]] section $ip_id fiber [expr [lindex $h_col 0]/2.0-$c_concrete-0.5] [expr [lindex $b_col 0]/2.0-$c_concrete-0.5] stressStrain
        #  recorder Element -file $recorderdir/column_bar_ssb_[lindex $col_tags_recorded [expr {$tagele-1}]]_ip$ip_id.out -dT $dt -ele [lindex $col_tags_recorded [expr {$tagele-1}]] section $ip_id fiber [expr -[lindex $h_col 0]/2.0+$c_concrete+0.5] [expr [lindex $b_col 0]/2.0-$c_concrete-0.5] stressStrain
        recorder Element -file $recorderdir/column_bar_sst_[lindex $col_tags_recorded [expr {$tagele-1}]]_ip$ip_id.out -dT $dt -ele [lindex $col_tags_recorded [expr {$tagele-1}]] section $ip_id fiber [expr [lindex $h_col 0]/2.0-$c_concrete-0.5] [expr [lindex $b_col 0]/2.0-$c_concrete-0.5] stressStrain
        recorder Element -file $recorderdir/column_bar_ssb_[lindex $col_tags_recorded [expr {$tagele-1}]]_ip$ip_id.out -dT $dt -ele [lindex $col_tags_recorded [expr {$tagele-1}]] section $ip_id fiber [expr -[lindex $h_col 0]/2.0+$c_concrete+0.5] [expr [lindex $b_col 0]/2.0-$c_concrete-0.5] stressStrain
      }
    }
    # column curvature response
    for {set tagele 7} {$tagele <= 12} {incr tagele} {
      for {set ip_id 1} {$ip_id < $numIntgrPts+1} {incr ip_id} {
        #  recorder Element -file $recorderdir/column_curvature_[lindex $col_tags_recorded \
        #    [expr {$tagele-1}]]_ip$ip_id.out -dT $dt -ele [lindex $col_tags_recorded [expr {$tagele-1}]] \
        #    section $ip_id deformation
        recorder Element -file $recorderdir/curvature_[lindex $col_tags_recorded \
          [expr {$tagele-1}]]_ip$ip_id.out -dT $dt -ele [lindex $col_tags_recorded [expr {$tagele-1}]] \
          section $ip_id deformation
      }
    }
    # beam curvature response
    for {set ip_id 1} {$ip_id < $numIntgrPts+1} {incr ip_id} {
      #  recorder Element -file $recorderdir/beam_curvature_ip$ip_id.out -dT $dt -ele 210 410 1210 1410 2210 2410 3210 3410 4210 4410 section $ip_id deformation
      recorder Element -file $recorderdir/curvature_1210_ip$ip_id.out -dT $dt -ele 1210 section $ip_id deformation
      recorder Element -file $recorderdir/curvature_1410_ip$ip_id.out -dT $dt -ele 1410 section $ip_id deformation
      recorder Element -file $recorderdir/curvature_1200_ip$ip_id.out -dT $dt -ele 1200 section $ip_id deformation
      recorder Element -file $recorderdir/curvature_1400_ip$ip_id.out -dT $dt -ele 1400 section $ip_id deformation
    }
    # wall curvature response
    for {set ip_id 1} {$ip_id < $numIntgrPts+1} {incr ip_id} {
      #  recorder Element -file $recorderdir/wall_curvature_ip$ip_id.out -dT $dt -ele 500 510 1500 1510 2500 2510 3500 3510 4500 4510 section $ip_id deformation
      recorder Element -file $recorderdir/curvature_1500_ip$ip_id.out -dT $dt -ele 1500 section $ip_id deformation
      recorder Element -file $recorderdir/curvature_1510_ip$ip_id.out -dT $dt -ele 1510 section $ip_id deformation
    }
    # beam forces
    for {set ip_id 1} {$ip_id < $numIntgrPts+1} {incr ip_id} {
      recorder Element -file $recorderdir/force_1210_ip$ip_id.out -dT $dt -ele 1210 section $ip_id force
      recorder Element -file $recorderdir/force_1410_ip$ip_id.out -dT $dt -ele 1410 section $ip_id force
      recorder Element -file $recorderdir/force_1200_ip$ip_id.out -dT $dt -ele 1200 section $ip_id force
      recorder Element -file $recorderdir/force_1400_ip$ip_id.out -dT $dt -ele 1400 section $ip_id force
    }
    # column forces
    for {set tagele 7} {$tagele <= 12} {incr tagele} {
      for {set ip_id 1} {$ip_id < $numIntgrPts+1} {incr ip_id} {
        recorder Element -file $recorderdir/force_[lindex $col_tags_recorded \
          [expr {$tagele-1}]]_ip$ip_id.out -dT $dt -ele [lindex $col_tags_recorded [expr {$tagele-1}]] section $ip_id force
      }
    }
    # wall forces
    for {set ip_id 1} {$ip_id < $numIntgrPts+1} {incr ip_id} {
      recorder Element -file $recorderdir/force_1500_ip$ip_id.out -dT $dt -ele 1500 $ip_id force
      recorder Element -file $recorderdir/force_1510_ip$ip_id.out -dT $dt -ele 1510 $ip_id force
    }
  }
  # beam fracture index
  #recorder Element -file $recorderdir/beam_bar_fit1.out -dT $dt -ele 210 410 1210 1410 2210 2410 3210 3410 4210 4410 section 1 fiber [expr [lindex $h_beam 0]/2.0-$c_concrete-0.4] [expr [lindex $b_beam 0]/2.0-$c_concrete-0.4] damage
  #recorder Element -file $recorderdir/beam_bar_fib1.out -dT $dt -ele 210 410 1210 1410 2210 2410 3210 3410 4210 4410 section 1 fiber [expr -[lindex $h_beam 0]/2.0+$c_concrete+0.4] [expr [lindex $b_beam 0]/2.0-$c_concrete-0.4] damage
  #recorder Element -file $recorderdir/beam_bar_fit2.out -dT $dt -ele 210 410 1210 1410 2210 2410 3210 3410 4210 4410 section $numIntgrPts fiber [expr [lindex $h_beam 0]/2.0-$c_concrete-0.4] [expr [lindex $b_beam 0]/2.0-$c_concrete-0.4] damage
  #recorder Element -file $recorderdir/beam_bar_fib2.out -dT $dt -ele 210 410 1210 1410 2210 2410 3210 3410 4210 4410 section $numIntgrPts fiber [expr -[lindex $h_beam 0]/2.0+$c_concrete+0.4] [expr [lindex $b_beam 0]/2.0-$c_concrete-0.4] damage

  #column fracture index
  #recorder Element -file $recorderdir/column_2_bar_fit1.out -dT $dt -ele 100 110 120 300 310 320 section 1 fiber [expr [lindex $h_col 0]/2.0-$c_concrete-0.5] [expr [lindex $b_col 0]/2.0-$c_concrete-0.5] damage
  #recorder Element -file $recorderdir/column_2_bar_fib1.out -dT $dt -ele 100 110 120 300 310 320 section 1 fiber [expr -[lindex $h_col 0]/2.0+$c_concrete+0.5] [expr [lindex $b_col 0]/2.0-$c_concrete-0.5] damage
  #recorder Element -file $recorderdir/column_2_bar_fit2.out -dT $dt -ele 100 110 120 300 310 320 section $numIntgrPts fiber [expr [lindex $h_col 0]/2.0-$c_concrete-0.5] [expr [lindex $b_col 0]/2.0-$c_concrete-0.5] damage
  #recorder Element -file $recorderdir/column_2_bar_fib2.out -dT $dt -ele 100 110 120 300 310 320 section $numIntgrPts fiber [expr -[lindex $h_col 0]/2.0+$c_concrete+0.5] [expr [lindex $b_col 0]/2.0-$c_concrete-0.5] damage

  # conduct analysis
  puts "Analyzing the structural response under #[expr $serial+1] motion: [lindex $motion_id $serial]."
  source SolverNewmark.tcl

  # Remove current recorders

  remove recorders
  wipeAnalysis
  loadConst -time 0.0
  puts "Analysis completed for #[expr $serial+1] motion."
}

