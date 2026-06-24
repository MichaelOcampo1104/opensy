
# Statistics monitor actor
set MonitorActorStatistics_once_flag 0
proc MonitorActorStatistics {} {
	global STKO_VAR_process_id
	global STKO_VAR_increment
	global STKO_VAR_time_increment
	global STKO_VAR_time
	global STKO_VAR_num_iter
	global STKO_VAR_error_norm
	global STKO_VAR_percentage
	global MonitorActorStatistics_once_flag
	# Statistics
	if {$STKO_VAR_process_id == 0} {
		if {$MonitorActorStatistics_once_flag == 0} {
			set MonitorActorStatistics_once_flag 1
			set STKO_monitor_statistics [open "./STKO_monitor_statistics.stats"  w+]
		} else {
			set STKO_monitor_statistics [open "./STKO_monitor_statistics.stats"  a+]
		}
		puts $STKO_monitor_statistics "$STKO_VAR_increment $STKO_VAR_time_increment $STKO_VAR_time $STKO_VAR_num_iter $STKO_VAR_error_norm $STKO_VAR_percentage"
		close $STKO_monitor_statistics
	}
}
lappend STKO_VAR_MonitorFunctions "MonitorActorStatistics"

# Timing monitor actor
set monitor_actor_time_0 [clock seconds]
proc MonitorActorTiming {} {
	global monitor_actor_time_0
	global STKO_VAR_process_id
	if {$STKO_VAR_process_id == 0} {
		set STKO_time [open "./STKO_time_monitor.tim" w+]
		set current_time [clock seconds]
		puts $STKO_time $monitor_actor_time_0
		puts $STKO_time $current_time
		close $STKO_time
	}
}
lappend STKO_VAR_MonitorFunctions "MonitorActorTiming"

#TCL script: parameter declaration
# Note: in OpenSeesMP the processor ID is in the range [0, N[

# declare the current parameter ID
set param_id [getPID]

# declare the parametrized recorder file name
set mpco_fname "Results_$param_id"

# this is a trick... when STKO writes the mpco recorder command, it also writes
# a support *.mpco.cdata file with the same name of the recorder. However in STKO the 
# recorder name has a suffix = $param_id, that will be evaluated by TCL when creating the
# *.mpco file, but not at the time STKO writes the *.mpco.cdata file. So we can
# simply copy the one created by STKO and rename it accordingly.
# this is the name STKO gave it... make sure to use the escape character before the $ char!!
set STKO_file_name "\$mpco_fname.mpco.cdata"
# this is the new name, DON'T use the escape character, to the param_id will be eval by TCL!
set current_file_name "$mpco_fname.mpco.cdata"
file copy -force $STKO_file_name $current_file_name

# directories for ground motion files
# read their content, split every line, skip empty lines
set gmotion_dt [lsearch -all -inline -not -exact [split [read [open "GroundMotionInfo/GMTimeSteps.txt" r]] "\n"] {}]
set gmotion_nsteps [lsearch -all -inline -not -exact [split [read [open "GroundMotionInfo/GMNumPoints.txt" r]] "\n"] {}]
set gmotion_names [lsearch -all -inline -not -exact [split [read [open "GroundMotionInfo/GMFileNames.txt" r]] "\n"] {}]

# make sure they have the same length
set num_dt [llength $gmotion_dt]
set num_nsteps [llength $gmotion_nsteps]
set num_names [llength $gmotion_names]
if {$num_dt != $num_nsteps || $num_dt != $num_names} {
	puts $num_dt
	puts $num_nsteps
	puts $num_names
	error "The GroundMotionInfo files must have the same length"
}

# make sure the user input a correct number of processors
set num_proc [getNP]
set num_param [expr int($num_dt/2)]
if {$num_proc != $num_param} {
	error "The number of processors ($num_proc) must be equal to the number of parameters ($num_param)"
}

# ground motion come in contiguous pairs, here we get their line (0 based)
set gmotion_x_line [expr $param_id*2]
set gmotion_y_line [expr $param_id*2 + 1]

# ground motion x data
set gmotion_x_dt [lindex $gmotion_dt $gmotion_x_line]
set gmotion_x_nsteps [lindex $gmotion_nsteps $gmotion_x_line]
set gmotion_x_file "histories/[lindex $gmotion_names $gmotion_x_line].txt"

# ground motion y data
set gmotion_y_dt [lindex $gmotion_dt $gmotion_y_line]
set gmotion_y_nsteps [lindex $gmotion_nsteps $gmotion_y_line]
set gmotion_y_file "histories/[lindex $gmotion_names $gmotion_y_line].txt"

# since these 2 ground motion are applied in the same analysis,
# we need to make sure the dt and total duration are compatible
set gmotion_x_duration [expr $gmotion_x_dt * $gmotion_x_nsteps]
set gmotion_y_duration [expr $gmotion_y_dt * $gmotion_y_nsteps]
set gmotion_duration [expr max($gmotion_x_duration, $gmotion_y_duration)]
set gmotion_dt [expr min($gmotion_x_dt, $gmotion_y_dt)]
set gmotion_num_steps [expr max(1, int($gmotion_duration / $gmotion_dt))]
set gmotion_dt [expr $gmotion_duration/$gmotion_num_steps]

# print some info... wait 1 second just to make sure every proc reached this point
# this piece of code is not necessary, just to print some info in a clear way
barrier
after 1000 set end 1
vwait end
puts "\nProcessor: $param_id:\n\
   GMX: '$gmotion_x_file' - dt: $gmotion_x_dt - #steps: $gmotion_x_nsteps\n\
   GMY: '$gmotion_y_file' - dt: $gmotion_y_dt - #steps: $gmotion_y_nsteps"
barrier
after 1000 set end 1
vwait end

recorder mpco "$mpco_fname.mpco" \
-N "displacement" "rotation" "velocity" "acceleration" "reactionForce" "reactionMoment" \
-T nsteps 50 \
-E "force" "deformation" "section.force" "section.deformation" "material.stress" "material.strain" "material.damage" "section.fiber.stress" "section.fiber.strain" "section.fiber.damage"

# Constraints.sp fix
	fix 128 1 1 1 1 1 1
	fix 129 1 1 1 1 1 1
	fix 132 1 1 1 1 1 1
	fix 133 1 1 1 1 1 1
	fix 134 1 1 1 1 1 1
	fix 7 1 1 1 1 1 1
	fix 135 1 1 1 1 1 1
	fix 136 1 1 1 1 1 1
	fix 137 1 1 1 1 1 1
	fix 138 1 1 1 1 1 1
	fix 139 1 1 1 1 1 1
	fix 140 1 1 1 1 1 1
	fix 141 1 1 1 1 1 1
	fix 142 1 1 1 1 1 1
	fix 143 1 1 1 1 1 1
	fix 144 1 1 1 1 1 1
	fix 39 1 1 1 1 1 1
	fix 40 1 1 1 1 1 1
	fix 41 1 1 1 1 1 1
	fix 42 1 1 1 1 1 1
	fix 43 1 1 1 1 1 1
	fix 44 1 1 1 1 1 1
	fix 45 1 1 1 1 1 1
	fix 127 1 1 1 1 1 1
	fix 1 0 0 1 1 1 0
	fix 2 0 0 1 1 1 0
	fix 3 0 0 1 1 1 0
	fix 4 0 0 1 1 1 0
	fix 5 0 0 1 1 1 0

# Constraints.mp rigidDiaphragm
rigidDiaphragm 3 1 6
rigidDiaphragm 3 1 8
rigidDiaphragm 3 1 9
rigidDiaphragm 3 2 10
rigidDiaphragm 3 2 11
rigidDiaphragm 3 2 12
rigidDiaphragm 3 3 13
rigidDiaphragm 3 3 14
rigidDiaphragm 3 4 15
rigidDiaphragm 3 2 16
rigidDiaphragm 3 2 17
rigidDiaphragm 3 2 18
rigidDiaphragm 3 2 19
rigidDiaphragm 3 2 20
rigidDiaphragm 3 2 21
rigidDiaphragm 3 2 22
rigidDiaphragm 3 5 23
rigidDiaphragm 3 3 24
rigidDiaphragm 3 1 25
rigidDiaphragm 3 4 26
rigidDiaphragm 3 3 27
rigidDiaphragm 3 3 28
rigidDiaphragm 3 1 29
rigidDiaphragm 3 1 30
rigidDiaphragm 3 1 31
rigidDiaphragm 3 1 32
rigidDiaphragm 3 1 33
rigidDiaphragm 3 1 34
rigidDiaphragm 3 4 35
rigidDiaphragm 3 4 36
rigidDiaphragm 3 5 37
rigidDiaphragm 3 5 38
rigidDiaphragm 3 3 46
rigidDiaphragm 3 3 47
rigidDiaphragm 3 3 48
rigidDiaphragm 3 4 49
rigidDiaphragm 3 4 50
rigidDiaphragm 3 5 51
rigidDiaphragm 3 4 52
rigidDiaphragm 3 4 53
rigidDiaphragm 3 4 54
rigidDiaphragm 3 5 55
rigidDiaphragm 3 5 56
rigidDiaphragm 3 3 57
rigidDiaphragm 3 2 58
rigidDiaphragm 3 1 59
rigidDiaphragm 3 5 60
rigidDiaphragm 3 4 61
rigidDiaphragm 3 4 62
rigidDiaphragm 3 3 63
rigidDiaphragm 3 4 64
rigidDiaphragm 3 3 65
rigidDiaphragm 3 1 66
rigidDiaphragm 3 2 67
rigidDiaphragm 3 3 68
rigidDiaphragm 3 1 69
rigidDiaphragm 3 5 70
rigidDiaphragm 3 5 71
rigidDiaphragm 3 2 72
rigidDiaphragm 3 3 73
rigidDiaphragm 3 2 74
rigidDiaphragm 3 5 75
rigidDiaphragm 3 5 76
rigidDiaphragm 3 4 77
rigidDiaphragm 3 5 78
rigidDiaphragm 3 5 79
rigidDiaphragm 3 4 80
rigidDiaphragm 3 5 81
rigidDiaphragm 3 1 82
rigidDiaphragm 3 5 83
rigidDiaphragm 3 1 84
rigidDiaphragm 3 1 85
rigidDiaphragm 3 3 86
rigidDiaphragm 3 3 87
rigidDiaphragm 3 3 88
rigidDiaphragm 3 2 89
rigidDiaphragm 3 3 90
rigidDiaphragm 3 2 91
rigidDiaphragm 3 2 92
rigidDiaphragm 3 4 93
rigidDiaphragm 3 4 94
rigidDiaphragm 3 2 95
rigidDiaphragm 3 1 96
rigidDiaphragm 3 3 97
rigidDiaphragm 3 4 98
rigidDiaphragm 3 5 99
rigidDiaphragm 3 3 100
rigidDiaphragm 3 4 101
rigidDiaphragm 3 3 102
rigidDiaphragm 3 3 103
rigidDiaphragm 3 4 104
rigidDiaphragm 3 2 105
rigidDiaphragm 3 2 106
rigidDiaphragm 3 1 107
rigidDiaphragm 3 1 108
rigidDiaphragm 3 2 109
rigidDiaphragm 3 5 110
rigidDiaphragm 3 1 111
rigidDiaphragm 3 3 112
rigidDiaphragm 3 2 113
rigidDiaphragm 3 1 114
rigidDiaphragm 3 5 115
rigidDiaphragm 3 4 116
rigidDiaphragm 3 4 117
rigidDiaphragm 3 5 118
rigidDiaphragm 3 4 119
rigidDiaphragm 3 5 120
rigidDiaphragm 3 5 121
rigidDiaphragm 3 3 122
rigidDiaphragm 3 2 123
rigidDiaphragm 3 1 124
rigidDiaphragm 3 5 125
rigidDiaphragm 3 5 126
rigidDiaphragm 3 1 130
rigidDiaphragm 3 1 131
rigidDiaphragm 3 3 145
rigidDiaphragm 3 2 146
rigidDiaphragm 3 4 147
rigidDiaphragm 3 4 148
rigidDiaphragm 3 5 149

# Patterns.addPattern loadPattern
pattern Plain 11 1 {

# Loads.eleLoad eleLoad_beamUniform
eleLoad -ele 4 7 8 9 10 18 19 20 21 24 38 41 42 43 44 45 46 47 48 49 50 51 52 53 54 386 387 388 397 398 400 401 409 410 415 416 423 427 428 429 430 431 432 435 445 446 449 450 451 455 456 457 458 459 460 461 462 463 464 465 466 467 468 469 488 489 490 491 492 496 514 515 516 529 533 534 535 536 537 538 546 547 548 550 551 559 560 561 562 563 564 565 566 567 568 570 573 574 575 576 577 578 579 580 581 586 588 590 592 596 598 599 600 601 602 603 608 615 616 617 -type -beamUniform 0.0 0.0 -5.0625
eleLoad -ele 5 11 25 29 32 402 405 406 408 417 421 422 433 440 444 475 476 477 483 494 508 528 532 542 543 544 545 549 558 569 582 584 595 597 604 606 607 618 619 620 -type -beamUniform 0.0 -22.166
eleLoad -ele 16 22 35 55 60 404 425 453 482 503 513 531 555 557 605 613 -type -beamUniform 0.0 -23.617
eleLoad -ele 478 485 518 591 593 594 623 627 629 630 -type -beamUniform 0.0 -9.88
eleLoad -ele 62 486 524 610 -type -beamUniform 0.0 -11.27
eleLoad -ele 526 611 -type -beamUniform 0.0 -9.23
eleLoad -ele 61 479 520 530 587 589 626 631 -type -beamUniform 0.0 -18.54
eleLoad -ele 521 522 609 625 -type -beamUniform 0.0 -14.46
eleLoad -ele 39 40 484 519 523 527 552 612 624 628 -type -beamUniform 0.0 -15.68
eleLoad -ele 3 6 17 23 28 57 382 392 394 395 396 399 418 439 441 443 448 493 495 497 502 504 505 507 509 517 525 553 571 583 585 622 -type -beamUniform 0.0 -25.235
eleLoad -ele 15 30 56 59 452 487 554 614 -type -beamUniform 0.0 -21.48
eleLoad -ele 14 31 58 384 389 393 403 414 426 434 471 473 480 501 506 621 -type -beamUniform 0.0 -20.96
eleLoad -ele 12 13 26 27 33 34 36 37 383 385 390 391 407 411 412 413 419 420 424 436 437 438 442 447 454 470 472 474 481 498 499 500 510 511 512 539 540 541 556 572 -type -beamUniform 0.0 -22.16
}

# analyses command
domainChange
constraints Penalty 10000000000000.0 10000000000000.0
numberer RCM
system UmfPack
test NormDispIncr 0.001 10  
algorithm Newton
integrator LoadControl 0.0
analysis Static
# ======================================================================================
# NON-ADAPTIVE LOAD CONTROL ANALYSIS
# ======================================================================================

# ======================================================================================
# USER INPUT DATA 
# ======================================================================================

# duration and initial time step
set total_duration 1.0
set initial_num_incr 10

set STKO_VAR_time 0.0
set STKO_VAR_time_increment [expr $total_duration / $initial_num_incr]
set STKO_VAR_initial_time_increment $STKO_VAR_time_increment
integrator LoadControl $STKO_VAR_time_increment 
for {set STKO_VAR_increment 1} {$STKO_VAR_increment <= $initial_num_incr} {incr STKO_VAR_increment} {
	
	# before analyze
	STKO_CALL_OnBeforeAnalyze
	
	# perform this step
	set STKO_VAR_analyze_done [analyze 1 ]
	
	# update common variables
	if {$STKO_VAR_analyze_done == 0} {
		set STKO_VAR_num_iter [testIter]
		set STKO_VAR_time [expr $STKO_VAR_time + $STKO_VAR_time_increment]
		set STKO_VAR_percentage [expr $STKO_VAR_time/$total_duration]
		set norms [testNorms]
		if {$STKO_VAR_num_iter > 0} {set STKO_VAR_error_norm [lindex $norms [expr $STKO_VAR_num_iter-1]]} else {set STKO_VAR_error_norm 0.0}
	}
	
	# after analyze
	set STKO_VAR_afterAnalyze_done 0
	STKO_CALL_OnAfterAnalyze
	
	# check convergence
	if {$STKO_VAR_analyze_done == 0} {
		# print statistics
		if {$STKO_VAR_process_id == 0} {
			puts [format "Increment: %6d | Iterations: %4d | Norm: %8.3e | Progress: %7.3f %%" $STKO_VAR_increment $STKO_VAR_num_iter  $STKO_VAR_error_norm [expr $STKO_VAR_percentage*100.0]]
		}
	} else {
		# stop analysis
		error "ERROR: the analysis did not converge"
	}
	
}

# done
if {$STKO_VAR_process_id == 0} {
	puts "Target time has been reached. Current time = $STKO_VAR_time"
	puts "SUCCESS."
}

loadConst -time 0.0

wipeAnalysis

#TCL script: excitation x & y (parametrized)
# note: start time series tag at 2, because 1 is used for the Linear time series
set gmotion_x_ts 2
set gmotion_y_ts 3

timeSeries Path $gmotion_x_ts -dt $gmotion_dt -filePath $gmotion_x_file -factor 9810.0
timeSeries Path $gmotion_y_ts -dt $gmotion_dt -filePath $gmotion_y_file -factor 9810.0

pattern UniformExcitation 1 1 -accel $gmotion_x_ts
pattern UniformExcitation 2 2 -accel $gmotion_y_ts

# Misc_commands rayleigh
rayleigh 1.399200014548205 0.0 0.0013034802874029102 0.0

# Monitor Actor [15]
set nodes_Y_15 {5}
set MonitorActor15_once_flag 0
set last_step_id_previous_stage_X_15 0
set previous_step_id_X_15 1
set previous_monitor_value_X_15 1
proc MonitorActor15 {} {
	global MonitorActor15_once_flag
	global STKO_VAR_process_id
	global STKO_VAR_increment
	if {$MonitorActor15_once_flag == 0} {
		set MonitorActor15_once_flag 1
		set STKO_plot_00 [open "./monitor_[getPID].plt" w+]
		puts $STKO_plot_00 "Time Step ID 	Displacement (X) "
	} else {
		set STKO_plot_00 [open "./monitor_[getPID].plt" a+]
	}
	global last_step_id_previous_stage_X_15
	global previous_step_id_X_15
	global previous_monitor_value_X_15
	if {$STKO_VAR_increment < $previous_step_id_X_15} {
		# It means a new stage has started
		set last_step_id_previous_stage_X_15 $previous_monitor_value_X_15
	}
	set monitor_value_X [expr $STKO_VAR_increment + $last_step_id_previous_stage_X_15]
	set previous_step_id_X_15 $STKO_VAR_increment
	set previous_monitor_value_X_15 $monitor_value_X
	set monitor_value_Y 0.0
	global nodes_Y_15
	foreach node_id $nodes_Y_15 {
		# get node value
		set node_value [nodeDisp $node_id 1]
		set monitor_value_Y [expr $monitor_value_Y + $node_value]
	}
	set monitor_value_Y [expr 1.0 * $monitor_value_Y + 0.0]
	puts $STKO_plot_00 "$monitor_value_X	$monitor_value_Y"
	close $STKO_plot_00
}
lappend STKO_VAR_MonitorFunctions "MonitorActor15"

#TCL script: Drift Recorder (parametrized)
 recorder Drift -file "DriftX_$param_id.txt" -precision 3 \
 -iNode 144 29 21 48 50 \
 -jNode 29 21 48 50 51 \
 -dof 1 -perpDirn 3
 recorder Drift -file "DriftY_$param_id.txt" -precision 3 \
 -iNode 144 29 21 48 50 \
 -jNode 29 21 48 50 51 \
 -dof 2 -perpDirn 3

#TCL script: Recorder
 recorder Node -file "DISPX_$param_id.txt" -precision 3 \
 -time -node 1 2 3 4 5 \
 -dof 1 disp
 recorder Node -file "DISPY_$param_id.txt" -precision 3 \
 -time -node 1 2 3 4 5 \
 -dof 2 disp
  recorder Node -file "VelX_$param_id.txt" -precision 3 \
 -time -node 1 2 3 4 5 \
 -dof 1 vel
 recorder Node -file "VelY_$param_id.txt" -precision 3 \
 -time -node 1 2 3 4 5 \
 -dof 2 vel

#TCL script: Acceleration Relative
 recorder Node -file "ACCRX_$param_id.txt" -precision 3 \
 -time -node 1 2 3 4 5 \
 -dof 1 accel
 recorder Node -file "ACCRY_$param_id.txt" -precision 3 \
 -time -node 1 2 3 4 5 \
 -dof 2 accel

#TCL script: Acceleration absolute
 recorder Node -file "ACCX_$param_id.txt" -precision 3 \
 -timeSeries $gmotion_x_ts  -time -node 1 2 3 4 5 \
 -dof 1 accel
 recorder Node -file "ACCY_$param_id.txt" -precision 3 \
 -timeSeries $gmotion_y_ts  -time -node 1 2 3 4 5 \
 -dof 2 accel

#TCL script: Acceleration Relative-Copy
 recorder Node -file "ACCRX_$param_id.txt" -precision 3 \
 -time -node 1 2 3 4 5 \
 -dof 1 accel
 recorder Node -file "ACCRY_$param_id.txt" -precision 3 \
 -time -node 1 2 3 4 5 \
 -dof 2 accel

# analyses command
domainChange
constraints Penalty 10000000000000.0 10000000000000.0
numberer RCM
system UmfPack
test NormDispIncr 0.001 100  
algorithm KrylovNewton
integrator Newmark 0.5 0.25
analysis Transient
# Analysis skipped: duration(0.0) * increments(0) = 0


#TCL script: Analysis run (parameterized)
# ======================================================================================
# ADAPTIVE TRANSIENT ANALYSIS
# ======================================================================================

# ======================================================================================
# USER INPUT DATA 
# ======================================================================================

# duration and initial time step
set total_time $gmotion_duration
set initial_num_incr $gmotion_num_steps

# parameters for adaptive time step
set max_factor 1.0
set min_factor 1e-06
set max_factor_increment 1.5
set min_factor_increment 1e-06
set max_iter 200
set desired_iter 100

set increment_counter 0
set factor 1.0
set old_factor $factor
set time 0.0
set initial_time_increment [expr $total_time / $initial_num_incr]
set time_tolerance [expr abs($initial_time_increment) * 1.0e-8]

while 1 {
	
	incr increment_counter
	if {[expr abs($time)] >= [expr abs($total_time)]} {
		if {$STKO_VAR_process_id == 0} {
			puts "Target time has been reached. Current time = $time"
			puts "SUCCESS."
		}
		break
	}
	
	set time_increment [expr $initial_time_increment * $factor]
	if {[expr abs($time + $time_increment)] > [expr abs($total_time) - $time_tolerance]} {
		set time_increment [expr $total_time - $time]
	}
	if {$STKO_VAR_process_id == 0} {
		puts "Increment: $increment_counter. time_increment = $time_increment. Current time = $time"
	}
	
	set ok [analyze 1 $time_increment]
	#barrier
	
	if {$ok == 0} {
		set num_iter [testIter]
		set factor_increment [expr min($max_factor_increment, [expr double($desired_iter) / double($num_iter)])]
		set factor [expr $factor * $factor_increment]
		if {$factor > $max_factor} {
			set factor $max_factor
		}
		if {$STKO_VAR_process_id == 0} {
			if {$factor > $old_factor} {
				puts "Increasing increment factor due to faster convergence. Factor = $factor"
			}
		}
		set old_factor $factor
		set time [expr $time + $time_increment]
		
		# print statistics
		set norms [testNorms]
		if {$num_iter > 0} {set last_norm [lindex $norms [expr $num_iter-1]]} else {set last_norm 0.0}
		if {$STKO_VAR_process_id == 0} {
			puts "Increment: $increment_counter - Iterations: $num_iter - Norm: $last_norm ( [expr $time/$total_time*100.0] % )"
		}
		
		# Call Custom Functions
		set perc [expr $time/$total_time]
		#CustomFunctionCaller $increment_counter $time_increment $time $num_iter $last_norm $perc $STKO_VAR_process_id $is_parallel
		STKO_CALL_OnAfterAnalyze
	} else {
		set num_iter $max_iter
		set factor_increment [expr max($min_factor_increment, [expr double($desired_iter) / double($num_iter)])]
		set factor [expr $factor * $factor_increment]
		if {$STKO_VAR_process_id == 0} {
			puts "Reducing increment factor due to non convergece. Factor = $factor"
		}
		if {$factor < $min_factor} {
			if {$STKO_VAR_process_id == 0} {
				puts "ERROR: current factor is less then the minimum allowed ($factor < $min_factor)"
				puts "Giving up"
			}
			error "ERROR: the analysis did not converge"
		}
	}
	
}

# Done!
puts "ANALYSIS SUCCESSFULLY FINISHED"

# Done!
puts "ANALYSIS SUCCESSFULLY FINISHED"
