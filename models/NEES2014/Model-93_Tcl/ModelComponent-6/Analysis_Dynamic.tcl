# This file needs  	dt  NPT  EQ_Record  GMfact
# outputs are		STATE  &  MAX_DR_R


## Applying E.Q. Load
set Gaccel "Series -dt $dt -filePath $EQ_Record -factor $GMfact";
pattern UniformExcitation [expr 9002 + $step] 1 -accel $Gaccel;    


#............................
constraints Transformation
numberer RCM
system UmfPack
#---------
set testType NormDispIncr
set testTol 1.0e-8;	
set testIter 200;	
test $testType $testTol $testIter 
#---------
set algoType KrylovNewton
algorithm  $algoType
#---------
integrator Newmark 0.5 0.25
analysis Transient

set STATE "successful"
set  Allowable_Drift_R  0.8;	#Maximum Allowable Drift Ratio
set  MAX_DR_R 0; 				#MAX DRIFT RATIO
set  MAX_T_D 0; 				#MAX TOP DISP


# iii index for each instance of record data
# jj index for moving along height of frame to calculate max. drift 

for {set iii 1} {$iii <= $NPT+4000} {incr iii} {

	set ok [analyze 1  $dt];
	set DR_Cu $MAX_DR_R
	
	#####################################################################
	## Convergence Script ###############################################
	
	if {$ok != 0} {
		# set ti [expr $iii * $dt];
		# puts $fid_conv "Error at $ti"
		
		if {$ok != 0} {
			puts "............................. Check With Newron"
	  		algorithm Newton
			set ok [analyze 1  $dt]; 
			algorithm $algoType
			#if {$ok == 0} {puts $fid_conv "Newton solved"}
		}
		if {$ok != 0} {
			puts "............................. Check With Newron -initialCurrent"
	  		algorithm Newton -initialCurrent
			set ok [analyze 1  $dt]; 
			algorithm $algoType
			#if {$ok == 0} {puts $fid_conv "Newton w/ iniCurrent solved"}
		}
		if {$ok != 0} {
			puts "......................................................"
			set tt 1
			while {$tt <= 40} {
	      		set ok [analyze 1  [expr $dt/40]]
				incr tt 1
				if {$ok != 0} {set tt 200}
			}
			# if {$ok == 0} {puts $fid_conv "time decreasing solved"}
		# }
				
		if {$ok == 0} {
			puts "************************************************ "
			puts "+++++++++++++++++++++++ Pedram, You are done !!! :D"
			puts "************************************************ "
		}
	}
	
	#####################################################################
	## Max. Drift & Collapse Check ######################################
	
	if {$ok == 0} {
	
		for {set jj 1} {$jj <= $nStory-1} {incr jj} {
		
			set nodeI [expr 10*$jj + 1];	#puts $nodeI ########################################## should be changed; set nodeI [expr 10+$jj]     #######
			set nodeJ [expr $nodeI + 10];	#puts $nodeJ ########################################## should be changed; set nodeJ [expr $nodeI + 1]  #######

			set D1 [nodeDisp $nodeI 1];		#puts "D1 = $D1"
			set D2 [nodeDisp $nodeJ 1];		#puts "D2 = $D2"
			
			set y_Cord1	[lindex [nodeCoord $nodeI] 1];	#puts $y_Cord1
			set y_Cord2	[lindex [nodeCoord $nodeJ] 1];	#puts $y_Cord2
						
			set Cu_DR_R [expr abs($D2 - $D1) / ($y_Cord2 - $y_Cord1)];
			# puts "$Cu_DR_R  ----------------- $iii"
			
			if {$Cu_DR_R  >= $Allowable_Drift_R} {
				puts "########################################"
				puts "#######  COLLAPSED!!!! at $iii  ########" 
				puts "########################################"

				set STATE "COLLAPSED"
				set MAX_DR_R  $Allowable_Drift_R
				set iii [expr $NPT + 10000];
				set jj [expr $nStory + 10000];

			} elseif {$MAX_DR_R < $Cu_DR_R } {
				set MAX_DR_R $Cu_DR_R 
			}
			
		}
		
		set top_node [expr $nStory*10 + 1];         ######################################### should be changed; set top_node [expr $nStory+10]; #############
		set Cu_T_D [nodeDisp $top_node  1];
		if {abs($Cu_T_D) > $MAX_T_D} {set MAX_T_D [expr abs($Cu_T_D)]};
		
	} elseif {$ok != 0} {
	
		puts "##########################################"
		puts "##########################################"
		puts "###########  NON-Convergence  ############"
		puts "###########  had error at $iii  ############"
		puts "##########################################"
		puts "##########################################"
		set STATE "NOT Converged"
		
		set iii [expr $NPT+10000];
	
	}; # end of loop for determination of max. drift

}; # end of loop for dynamic analysis
