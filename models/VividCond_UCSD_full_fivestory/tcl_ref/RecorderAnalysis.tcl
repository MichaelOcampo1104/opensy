# define the recorder directory
set recorderdir $outdir

# define the ground motion time series
timeSeries Path [expr 1000+$serial] -dt $dt -filePath $indir/$filenameX -factor [expr $g*$scalor]
set eq_load_patternX 3
pattern UniformExcitation $eq_load_patternX 1 -accel [expr 1000 + $serial]
timeSeries Path [expr 2000+$serial] -dt $dt -filePath $indir/$filenameY -factor [expr $g*$scalor]
set eq_load_patternY 4
pattern UniformExcitation $eq_load_patternY 2 -accel [expr 2000 + $serial]

# define drift and acceleration recorders for all stories
for {set storytag 1} {$storytag <= $num_stories} {incr storytag} {
	recorder Drift -file $recorderdir/story${storytag}_drift_X.out -time -iNode [lindex $ctrl_nodes \
            [expr $storytag-1]] -jNode [lindex $ctrl_nodes $storytag] -dof 1 -perpDirn 3
    recorder EnvelopeDrift -file $recorderdir/story${storytag}_drift_env_X.out -iNode [lindex $ctrl_nodes \
            [expr $storytag-1]] -jNode [lindex $ctrl_nodes $storytag] -dof 1 -perpDirn 3
    recorder EnvelopeDrift -file $recorderdir/story${storytag}_drift_env_Y.out -iNode [lindex $ctrl_nodes \
            [expr $storytag-1]] -jNode [lindex $ctrl_nodes $storytag] -dof 2 -perpDirn 3
	recorder EnvelopeNode -file $recorderdir/story${storytag}_acc_env_X.out -timeSeries [expr 1000+$serial] \
        -node [lindex $ctrl_nodes $storytag] -dof 1 accel
	recorder EnvelopeNode -file $recorderdir/story${storytag}_acc_env_Y.out -timeSeries [expr 2000+$serial] \
        -node [lindex $ctrl_nodes $storytag] -dof 2 accel
}

# story column forces
for {set tagele 1} {$tagele <= [llength $col_tags_recorded]} {incr tagele} {
    recorder EnvelopeElement -file $recorderdir/column_force_[lindex $col_tags_recorded \
        [expr {$tagele-1}]]_env.out -ele [lindex $col_tags_recorded [expr {$tagele-1}]] globalForce
}

# conduct analysis
source SolverNewmark.tcl

# review data and determin collapse
set collapse_flag false
if {$ok != 0} {
	puts [format "Model failed (time = %1.3e)" $tCurrent]
	set max_drift [max_drift_model $ctrl_nodes]
	if {$max_drift < 0.1} {
		set max_drift 0.1;
	}
	#if {$DFTag == 1} {
	#	set max_fi [max_fi_outfile $recorderdir $nsl]
	#}
	puts [format "Maximum drift ratio = " $max_drift]
	if {$max_drift >= $col_drift} {
		set collapse_flag true
	}
} else {
	puts [format "\nResponse-history analysis completed"]
	set max_drift [max_drift_outfile $recorderdir $num_stories]
	#if {$DFTag == 1} {
	#	set max_fi [max_fi_outfile $recorderdir $nsl]
	#}
	puts [format "Maximum drift ratio = " $max_drift]
	if {$max_drift >= $col_drift} {
		set collapse_flag true
	}
}

# Write the analysis results to the stripe text file
if {$collapse_flag} {
    puts $stripe_file "[format "%.5f" $col_drift]"
} else {
    puts $stripe_file "[format "%.5f" $max_drift]"
}
