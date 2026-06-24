
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
	fix 136 1 1 1 1 1 1
	fix 137 1 1 1 1 1 1
	fix 138 1 1 1 1 1 1
	fix 139 1 1 1 1 1 1
	fix 140 1 1 1 1 1 1
	fix 142 1 1 1 1 1 1
	fix 143 1 1 1 1 1 1
	fix 144 1 1 1 1 1 1
	fix 145 1 1 1 1 1 1
	fix 146 1 1 1 1 1 1
	fix 147 1 1 1 1 1 1
	fix 148 1 1 1 1 1 1
	fix 149 1 1 1 1 1 1
	fix 35 1 1 1 1 1 1
	fix 36 1 1 1 1 1 1
	fix 73 1 1 1 1 1 1
	fix 74 1 1 1 1 1 1
	fix 75 1 1 1 1 1 1
	fix 76 1 1 1 1 1 1
	fix 77 1 1 1 1 1 1
	fix 78 1 1 1 1 1 1
	fix 79 1 1 1 1 1 1
	fix 80 1 1 1 1 1 1
	fix 81 1 1 1 1 1 1
	fix 1 0 0 1 1 1 0
	fix 2 0 0 1 1 1 0
	fix 3 0 0 1 1 1 0
	fix 4 0 0 1 1 1 0
	fix 5 0 0 1 1 1 0

# Constraints.mp rigidDiaphragm
rigidDiaphragm 3 5 6
rigidDiaphragm 3 4 7
rigidDiaphragm 3 5 8
rigidDiaphragm 3 5 9
rigidDiaphragm 3 3 10
rigidDiaphragm 3 3 11
rigidDiaphragm 3 4 12
rigidDiaphragm 3 3 13
rigidDiaphragm 3 4 14
rigidDiaphragm 3 2 15
rigidDiaphragm 3 2 16
rigidDiaphragm 3 2 17
rigidDiaphragm 3 1 18
rigidDiaphragm 3 1 19
rigidDiaphragm 3 1 20
rigidDiaphragm 3 1 21
rigidDiaphragm 3 1 22
rigidDiaphragm 3 1 23
rigidDiaphragm 3 2 24
rigidDiaphragm 3 2 25
rigidDiaphragm 3 2 26
rigidDiaphragm 3 2 27
rigidDiaphragm 3 2 28
rigidDiaphragm 3 2 29
rigidDiaphragm 3 2 30
rigidDiaphragm 3 2 31
rigidDiaphragm 3 4 32
rigidDiaphragm 3 3 33
rigidDiaphragm 3 3 34
rigidDiaphragm 3 1 37
rigidDiaphragm 3 1 38
rigidDiaphragm 3 1 39
rigidDiaphragm 3 1 40
rigidDiaphragm 3 1 41
rigidDiaphragm 3 1 42
rigidDiaphragm 3 2 43
rigidDiaphragm 3 3 44
rigidDiaphragm 3 3 45
rigidDiaphragm 3 3 46
rigidDiaphragm 3 2 47
rigidDiaphragm 3 2 48
rigidDiaphragm 3 2 49
rigidDiaphragm 3 2 50
rigidDiaphragm 3 2 51
rigidDiaphragm 3 1 52
rigidDiaphragm 3 1 53
rigidDiaphragm 3 3 54
rigidDiaphragm 3 3 55
rigidDiaphragm 3 3 56
rigidDiaphragm 3 3 57
rigidDiaphragm 3 3 58
rigidDiaphragm 3 3 59
rigidDiaphragm 3 3 60
rigidDiaphragm 3 3 61
rigidDiaphragm 3 3 62
rigidDiaphragm 3 4 63
rigidDiaphragm 3 4 64
rigidDiaphragm 3 4 65
rigidDiaphragm 3 3 66
rigidDiaphragm 3 4 67
rigidDiaphragm 3 4 68
rigidDiaphragm 3 1 69
rigidDiaphragm 3 5 70
rigidDiaphragm 3 4 71
rigidDiaphragm 3 4 72
rigidDiaphragm 3 1 82
rigidDiaphragm 3 4 83
rigidDiaphragm 3 3 84
rigidDiaphragm 3 4 85
rigidDiaphragm 3 5 86
rigidDiaphragm 3 5 87
rigidDiaphragm 3 4 88
rigidDiaphragm 3 5 89
rigidDiaphragm 3 5 90
rigidDiaphragm 3 3 91
rigidDiaphragm 3 1 92
rigidDiaphragm 3 1 93
rigidDiaphragm 3 1 94
rigidDiaphragm 3 1 95
rigidDiaphragm 3 4 96
rigidDiaphragm 3 3 97
rigidDiaphragm 3 4 98
rigidDiaphragm 3 4 99
rigidDiaphragm 3 4 100
rigidDiaphragm 3 2 101
rigidDiaphragm 3 4 102
rigidDiaphragm 3 5 103
rigidDiaphragm 3 5 104
rigidDiaphragm 3 5 105
rigidDiaphragm 3 5 106
rigidDiaphragm 3 5 107
rigidDiaphragm 3 5 108
rigidDiaphragm 3 2 109
rigidDiaphragm 3 5 110
rigidDiaphragm 3 2 111
rigidDiaphragm 3 2 112
rigidDiaphragm 3 5 113
rigidDiaphragm 3 2 114
rigidDiaphragm 3 2 115
rigidDiaphragm 3 1 116
rigidDiaphragm 3 4 117
rigidDiaphragm 3 2 118
rigidDiaphragm 3 5 119
rigidDiaphragm 3 5 120
rigidDiaphragm 3 3 121
rigidDiaphragm 3 5 122
rigidDiaphragm 3 5 123
rigidDiaphragm 3 4 124
rigidDiaphragm 3 3 125
rigidDiaphragm 3 3 126
rigidDiaphragm 3 1 127
rigidDiaphragm 3 4 128
rigidDiaphragm 3 5 129
rigidDiaphragm 3 1 130
rigidDiaphragm 3 4 131
rigidDiaphragm 3 4 132
rigidDiaphragm 3 5 133
rigidDiaphragm 3 5 134
rigidDiaphragm 3 1 135
rigidDiaphragm 3 5 141

# Patterns.addPattern loadPattern
pattern Plain 8 1 {

# Loads.eleLoad eleLoad_beamUniform
eleLoad -ele 23 24 25 34 35 37 38 46 47 52 53 60 64 65 66 67 68 69 72 82 83 86 87 88 92 93 94 95 96 97 98 99 100 101 102 103 104 105 106 125 126 127 128 129 133 152 153 154 164 168 174 175 176 177 178 179 180 181 182 183 197 199 200 202 203 211 212 213 214 215 216 217 218 219 220 222 225 226 227 228 229 230 231 232 233 234 235 236 237 242 244 246 248 252 256 257 258 259 260 261 266 273 274 275 276 295 304 305 306 307 308 309 310 311 312 313 314 315 316 317 -type -beamUniform 0.0 0.0 -5.0625
eleLoad -ele 39 42 43 45 54 58 59 70 77 81 112 113 114 120 131 146 167 169 173 184 191 193 194 196 201 210 221 238 240 251 255 262 264 265 277 281 284 287 288 289 -type -beamUniform 0.0 -22.166
eleLoad -ele 41 62 90 119 140 151 172 195 207 209 253 263 271 291 318 324 -type -beamUniform 0.0 -23.617
eleLoad -ele 115 122 156 247 249 250 296 302 320 325 -type -beamUniform 0.0 -9.88
eleLoad -ele 123 162 268 327 -type -beamUniform 0.0 -11.27
eleLoad -ele 165 269 -type -beamUniform 0.0 -9.23
eleLoad -ele 116 158 171 243 245 301 326 328 -type -beamUniform 0.0 -18.54
eleLoad -ele 159 160 267 299 -type -beamUniform 0.0 -14.46
eleLoad -ele 121 157 161 166 204 270 297 298 300 303 -type -beamUniform 0.0 -15.68
eleLoad -ele 19 29 31 32 33 36 55 76 78 80 85 130 132 134 139 141 142 143 145 147 155 163 170 198 205 223 239 241 254 280 293 321 -type -beamUniform 0.0 -25.235
eleLoad -ele 89 124 192 206 272 282 319 323 -type -beamUniform 0.0 -21.48
eleLoad -ele 21 26 30 40 51 63 71 108 110 117 138 144 190 283 290 322 -type -beamUniform 0.0 -20.96
eleLoad -ele 20 22 27 28 44 48 49 50 56 57 61 73 74 75 79 84 91 107 109 111 118 135 136 137 148 149 150 185 186 187 188 189 208 224 278 279 285 286 292 294 -type -beamUniform 0.0 -22.16
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
rayleigh 1.026122700478766 0.0 0.0014846543198870832 0.0

# Monitor Actor [12]
set nodes_Y_12 {5}
set MonitorActor12_once_flag 0
set last_step_id_previous_stage_X_12 0
set previous_step_id_X_12 1
set previous_monitor_value_X_12 1
proc MonitorActor12 {} {
	global MonitorActor12_once_flag
	global STKO_VAR_process_id
	global STKO_VAR_increment
	if {$MonitorActor12_once_flag == 0} {
		set MonitorActor12_once_flag 1
		set STKO_plot_00 [open "./monitor_[getPID].plt" w+]
		puts $STKO_plot_00 "Time Step ID 	Displacement (X) "
	} else {
		set STKO_plot_00 [open "./monitor_[getPID].plt" a+]
	}
	global last_step_id_previous_stage_X_12
	global previous_step_id_X_12
	global previous_monitor_value_X_12
	if {$STKO_VAR_increment < $previous_step_id_X_12} {
		# It means a new stage has started
		set last_step_id_previous_stage_X_12 $previous_monitor_value_X_12
	}
	set monitor_value_X [expr $STKO_VAR_increment + $last_step_id_previous_stage_X_12]
	set previous_step_id_X_12 $STKO_VAR_increment
	set previous_monitor_value_X_12 $monitor_value_X
	set monitor_value_Y 0.0
	global nodes_Y_12
	foreach node_id $nodes_Y_12 {
		# get node value
		set node_value [nodeDisp $node_id 1]
		set monitor_value_Y [expr $monitor_value_Y + $node_value]
	}
	set monitor_value_Y [expr 1.0 * $monitor_value_Y + 0.0]
	puts $STKO_plot_00 "$monitor_value_X	$monitor_value_Y"
	close $STKO_plot_00
}
lappend STKO_VAR_MonitorFunctions "MonitorActor12"

#TCL script: Drift Recorder (parametrized)
 recorder Drift -file "DriftX_$param_id.txt" -precision 3 \
 -iNode 137 92 118 97 100 \
 -jNode 92 118 97 100 134 \
 -dof 1 -perpDirn 3
 recorder Drift -file "DriftY_$param_id.txt" -precision 3 \
 -iNode 137 92 118 97 100 \
 -jNode 92 118 97 100 134 \
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
