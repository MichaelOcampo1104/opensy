set num_story 12
set node_tag1 {}
set node_tag2 {}

# peak story drift ratio
for {set i 1} {$i < [expr $num_story+1]} {incr i} {
    lappend node_tag1 $i
    lappend node_tag2 [expr $i+1]
}
for {set i 1} {$i < [expr $num_story+1]} {incr i} {
    recorder EnvelopeDrift -file max_story_drift_[expr $i]_1.out -iNode [lindex $node_tag1 $i-1] -jNode [lindex $node_tag2 $i-1] -dof 1 -perpDirn 3
    recorder EnvelopeDrift -file max_story_drift_[expr $i]_2.out -iNode [lindex $node_tag1 $i-1] -jNode [lindex $node_tag2 $i-1] -dof 2 -perpDirn 3
}

# story drift history for residual drift
for {set i 1} {$i < [expr $num_story+1]} {incr i} {
    recorder Drift -file story_drift_[expr $i]_1.out -iNode [lindex $node_tag1 $i-1] -jNode [lindex $node_tag2 $i-1] -dof 1 -perpDirn 3
    recorder Drift -file story_drift_[expr $i]_2.out -iNode [lindex $node_tag1 $i-1] -jNode [lindex $node_tag2 $i-1] -dof 2 -perpDirn 3
}

# max abs floor acceleration
lappend node_tag1 [expr $i]
for {set i 1} {$i < [expr $num_story+2]} {incr i} {
    recorder EnvelopeNode -file max_abs_acceleration_[expr $i-1]_1.out -timeSeries 101 -node [lindex $node_tag1 $i-1] -dof 1 accel
    recorder EnvelopeNode -file max_abs_acceleration_[expr $i-1]_2.out -timeSeries 101 -node [lindex $node_tag1 $i-1] -dof 2 accel
}

# max floor displacement
for {set i 1} {$i < [expr $num_story+1]} {incr i} {
    recorder EnvelopeNode -file max_floor_disp_[expr $i]_1.out -node [lindex $node_tag2 $i-1] -dof 1 disp
    recorder EnvelopeNode -file max_floor_disp_[expr $i]_2.out -node [lindex $node_tag2 $i-1] -dof 2 disp
}

# roof drift ratio
recorder EnvelopeDrift -file max_roof_drift_1.out -iNode [lindex $node_tag1 0] -jNode [lindex $node_tag1 $num_story] -dof 1 -perpDirn 3
recorder EnvelopeDrift -file max_roof_drift_2.out -iNode [lindex $node_tag1 0] -jNode [lindex $node_tag1 $num_story] -dof 2 -perpDirn 3