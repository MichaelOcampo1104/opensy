#########################################################################
# Define fiber-type wall section (flexure + shear)				#
# Author: Kuanshi Zhong									#
# Email: kuanhsi@stanford.edu								#
# Date: 02/2017										#	
# Notes: 1. Planar/C-shape wall are currently available			#
# #######################################################################
#
#########################################################################
# Parent:	1. BuildWallModelMainMP.tcl
# Calling:	None
# Input:	None
# Note:	Please see the introduction pdf to evaluate the required
#		arguments
#########################################################################
#

proc CreatePlanarWallSection {id lw bw cover lbe1 lbe2 coreID1 coreID2 coreID3 coverID steelID1 steelID2 steelID3 db1 longBarArea1 numBotBars1 numTopBars1 interBarArea1 numInterLayers1 db2 longBarArea2 numBotBars2 numTopBars2 interBarArea2 numInterLayers2 db3 webBarArea numWebLayers nfCoreY nfCoreZ nfCoverY nfCoverZ nfWebY fc alpha_c rou_t fyt ShearTag} {

   # Do outputs for testing
#   puts "id is $id"
#   puts "h is $h"
#   puts "cover is $cover"
#   puts "coreid is $coreID"
#   puts "coverID is $coverID"
#   puts "steelID is $steelID"
#   puts "longBarArea is $longBarArea"
#   puts "numBotBars is $numBotBars"
#   puts "numTopBars is $numTopBars"
#   puts "interBarArea is $interBarArea"
#   puts "numInterLayers is $numInterLayers"
#   puts "nfCoreY is $nfCoreY"
#   puts "nfCoreZ is $nfCoreZ"
#   puts "nfCoverY is $nfCoverY"
#   puts "nfCoverZ is $nfCoverZ"

   # Set number of intermediate bars per layer
   set numInterBarsPerLayer 2

   # The distance from the section z-axis to the edge of the cover concrete
   # in the positive y direction
   set coverY [expr $lw/2.0]

   # The distance from the section y-axis to the edge of the cover concrete
   # in the positive z direction
   set coverZ [expr $bw/2.0]

   # The distance from the section z-axis to the edge of the web concrete
   # in the positive y direction
   set webY	[expr $lw/2.0-$cover-$lbe1];
   # in the negative y direction
   set nwebY [expr -$lw/2.0+$cover+$lbe2];

   # The negative values of the two above
   set ncoverY [expr -$coverY]
   set ncoverZ [expr -$coverZ]

   # Determine the corresponding values from the respective axes to the
   # edge of the core concrete
   set coreY [expr $coverY-$cover]
   set coreZ [expr $coverZ-$cover]
   set ncoreY [expr -$coreY]
   set ncoreZ [expr -$coreZ]

   # Define the fiber section
   set id_temp [expr $id+10000];
   set GJ [expr 1.0e9]
   section fiberSec $id_temp -GJ $GJ {

	# Define the upper boundary core patch
	# puts "$nfCoreY $nfCoreZ $webY $coreZ $webY $ncoreZ $coreY $ncoreZ $coreY $coreZ";
	patch quadr $coreID1 $nfCoreY $nfCoreZ $webY $coreZ $webY $ncoreZ $coreY $ncoreZ $coreY $coreZ
	# Define the lower boundary core patch
	# puts "$nfCoreY $nfCoreZ $ncoreY $coreZ $ncoreY $ncoreZ $nwebY $ncoreZ $nwebY $coreZ"
	patch quadr $coreID2 $nfCoreY $nfCoreZ $ncoreY $coreZ $ncoreY $ncoreZ $nwebY $ncoreZ $nwebY $coreZ
      
	# Define the four cover patches
	# Side cover
	# puts "$nfCoreY $nfCoverZ $webY $coverZ $webY $coreZ $coreY $coreZ $coverY $coverZ"
	# puts "$nfCoreY $nfCoverZ $webY $ncoreZ $webY $ncoverZ $coverY $ncoverZ $coreY $ncoreZ"
	# puts "$nfCoreY $nfCoverZ $ncoverY $coverZ $ncoreY $coreZ $nwebY $coreZ $nwebY $coverZ"
	# puts "$nfCoreY $nfCoverZ $ncoreY $ncoreZ $ncoverY $ncoverZ $nwebY $ncoverZ $nwebY $ncoreZ"
	patch quadr $coverID $nfCoreY $nfCoverZ $webY $coverZ $webY $coreZ $coreY $coreZ $coverY $coverZ
	patch quadr $coverID $nfCoreY $nfCoverZ $webY $ncoreZ $webY $ncoverZ $coverY $ncoverZ $coreY $ncoreZ
	patch quadr $coverID $nfCoreY $nfCoverZ $ncoverY $coverZ $ncoreY $coreZ $nwebY $coreZ $nwebY $coverZ
	patch quadr $coverID $nfCoreY $nfCoverZ $ncoreY $ncoreZ $ncoverY $ncoverZ $nwebY $ncoverZ $nwebY $ncoreZ
	
	# Top and bottom cover
	# puts "$nfCoverY $nfCoreZ $ncoverY $coverZ $ncoverY $ncoverZ $ncoreY $ncoreZ $ncoreY $coreZ"
	# puts "$nfCoverY $nfCoreZ $coreY $coreZ $coreY $ncoreZ $coverY $ncoverZ $coverY $coverZ"
	patch quadr $coverID $nfCoverY $nfCoreZ $ncoverY $coverZ $ncoverY $ncoverZ $ncoreY $ncoreZ $ncoreY $coreZ
	patch quadr $coverID $nfCoverY $nfCoreZ $coreY $coreZ $coreY $ncoreZ $coverY $ncoverZ $coverY $coverZ

	# Web concrete
	if {$nfWebY > 0} {
		patch quadr $coreID3 $nfWebY $nfCoverZ $nwebY $coverZ $nwebY $coreZ $webY $coreZ $webY $coverZ
		patch quadr $coreID3 $nfWebY $nfCoverZ $nwebY $coreZ $nwebY $ncoreZ $webY $ncoreZ $webY $coreZ
		patch quadr $coreID3 $nfWebY $nfCoverZ $nwebY $ncoreZ $nwebY $ncoverZ $webY $ncoverZ $webY $ncoreZ
	}

	# Define the steel layers in the upper boundary element
	# Top layer
	layer straight $steelID1 $numTopBars1 $longBarArea1 [expr $coreY-0.5*$db1] [expr $coreZ-0.5*$db1] [expr $coreY-0.5*$db1] [expr $ncoreZ+0.5*$db1]; 	
	# Bottom layer
	layer straight $steelID1 $numBotBars1 $longBarArea1 [expr $webY+0.5*$db1] [expr $coreZ-0.5*$db1] [expr $webY+0.5*$db1] [expr $ncoreZ+0.5*$db1]; 

	# Do intermediate layers if they exist
#	puts "Check: Number of intermeddiate layers is $numInterLayers"
   	if {$numInterLayers1 == 0} {
		# Don't make any intermediate layers of bars
   	} else {
		# Compute spacing of intermediate layers (equally spaced)
		set interSpacing1 [expr (($lbe1 - 2*$db1)/[expr $numInterLayers1 + 1])]
		#puts "Inter spacing is $interSpacing"
		
		# Make intermediate layers
		set layerDepth1 [expr ($coreY-0.5*$db1-$interSpacing1)]
		for {set layerNum 1} {$layerNum < [expr $numInterLayers1 + 1]} {incr layerNum 1} {
			layer straight $steelID1 $numInterBarsPerLayer $interBarArea1 $layerDepth1 [expr $coreZ-0.5*$db1] $layerDepth1 [expr $ncoreZ+0.5*$db1]; 
			#puts "Intermediate layer placed at $layerDepth"
			set layerDepth1 [expr $layerDepth1 - $interSpacing1]
		}
   	}

	# Define the steel layers in the lower boundary element
	# Top layer
	layer straight $steelID2 $numTopBars2 $longBarArea2 [expr $ncoreY+0.5*$db2] [expr $coreZ-0.5*$db2] [expr $ncoreY+0.5*$db2] [expr $ncoreZ+0.5*$db2]; 	
	# Bottom layer
	layer straight $steelID2 $numBotBars2 $longBarArea2 [expr $nwebY-0.5*$db2] [expr $coreZ-0.5*$db2] [expr $nwebY-0.5*$db2] [expr $ncoreZ+0.5*$db2]; 

	# Do intermediate layers if they exist
#	puts "Check: Number of intermeddiate layers is $numInterLayers"
   	if {$numInterLayers2 == 0} {
		# Don't make any intermediate layers of bars
   	} else {
		# Compute spacing of intermediate layers (equally spaced)
		set interSpacing2 [expr (($lbe2 - 2*$db2)/[expr $numInterLayers2 + 1])]
		#puts "Inter spacing is $interSpacing"
		
		# Make intermediate layers
		set layerDepth2 [expr ($ncoreY+0.5*$db2+$interSpacing2)]
		for {set layerNum 1} {$layerNum < [expr $numInterLayers2 + 1]} {incr layerNum 1} {
			layer straight $steelID2 $numInterBarsPerLayer $interBarArea2 $layerDepth2 [expr $coreZ-0.5*$db2] $layerDepth2 [expr $ncoreZ+0.5*$db2]; 
			#puts "Intermediate layer placed at $layerDepth"
			set layerDepth2 [expr $layerDepth2 + $interSpacing2]
		}
   	}

	# Define the steel layers in the web
	# Do intermediate layers if they exist
#	puts "Check: Number of web-steel layers is $numWebLayers"
   	if {$numWebLayers == 0} {
		# Don't make any intermediate layers of bars
   	} else {
		# Compute spacing of intermediate layers (equally spaced)
		set interSpacing3 [expr (($webY-$nwebY)/[expr $numWebLayers+1])]
		#puts "Inter spacing is $interSpacing"
		
		# Make intermediate layers
		set layerDepth3 [expr ($nwebY+$interSpacing3)]
		for {set layerNum 1} {$layerNum < [expr $numWebLayers + 1]} {incr layerNum 1} {
			layer straight $steelID3 $numInterBarsPerLayer $webBarArea $layerDepth3 [expr $coreZ-0.5*$db3] $layerDepth3 [expr $ncoreZ+0.5*$db3]; 
			#puts "Intermediate layer placed at $layerDepth"
			set layerDepth3 [expr $layerDepth3 + $interSpacing3]
		}
   	}
	
   }
   
   # Define the shear material
   set Ec [expr 57.0*sqrt(-$fc*1000.0)];
   set Gc [expr $Ec/2.0/(1+0.2)];
   set vn [expr $alpha_c*sqrt(-$fc*1000.0)/1000.0+$rou_t*$fyt];
   if {$vn > [expr 8*sqrt(-$fc*1000.0)/1000.0]} {
		set vn [expr 8*sqrt(-$fc*1000.0)/1000.0];
   }
   set s1p [expr 0.002*sqrt(-$fc*1000.0)*$lw*$bw];
   set e1p [expr $s1p/$Gc/($lw*$bw)];
   set s2p [expr 0.6*$vn*$lw*$bw];
   set e2p [expr $e1p+($s2p-$s1p)/0.4/$Gc/($lw*$bw)];
   set s3p [expr $vn*$lw*$bw];
   set e3p [expr $e2p+0.4*$vn/0.1/$Gc];
   set s1n [expr -$s1p];
   set e1n [expr -$e1p];
   set s2n [expr -$s2p];
   set e2n [expr -$e2p];
   set s3n [expr -$s3p];
   set e3n [expr -$e3p];
   set pinchX 1.0;
   set pinchY 1.0;
   set damage1 0;
   set damage2 0;
   set beta 0;
   if {$ShearTag == "Linear"} {
		uniaxialMaterial Elastic $id_temp [expr $s1p/$e1p];
#		puts "K_shear [expr $s1p/$e1p]";
   } else {
#		puts "$id_temp $s1p $e1p $s2p $e2p $s3p $e3p $s1n $e1n $s2n $e2n $s3n $e3n $pinchX $pinchY $damage1 $damage2 $beta"
   		uniaxialMaterial Hysteretic $id_temp $s1p $e1p $s2p $e2p $s3p $e3p $s1n $e1n $s2n $e2n $s3n $e3n $pinchX $pinchY $damage1 $damage2 $beta;
   }

   # Aggregate the shear material to the flexure section
   section Aggregator $id $id_temp Vy $id_temp Vz -section $id_temp;
}

# 
proc CreateCWallSection {id lw bw bf1 bf2 tf1 tf2 cover lbe1 lbe2 coreIDWT coreIDWB coreIDFT coreIDFB coverID steelIDWT steelIDWB steelIDFT steelIDFB steelIDWM \
				db1 longBarArea1 numWT1 numWT2 db2 longBarArea2 numWB1 numWB2 db3 webBarArea numWM1 numWM2 db4 longBarArea4 numFT1 numFT2 db5 longBarArea5 numFB1 numFB2 \
				nfCoreY nfCoreZ nfCoverY nfCoverZ nfWebY fc alpha_c \
				rou_tWT fytWT rou_tWB fytWB rou_tWM fytWM ShearTag} {
   # Do outputs for testing
#   puts "id is $id"
#   puts "h is $h"
#   puts "cover is $cover"
#   puts "coreid is $coreID"
#   puts "coverID is $coverID"
#   puts "steelID is $steelID"
#   puts "longBarArea is $longBarArea"
#   puts "numBotBars is $numBotBars"
#   puts "numTopBars is $numTopBars"
#   puts "interBarArea is $interBarArea"
#   puts "numInterLayers is $numInterLayers"
#   puts "nfCoreY is $nfCoreY"
#   puts "nfCoreZ is $nfCoreZ"
#   puts "nfCoverY is $nfCoverY"
#   puts "nfCoverZ is $nfCoverZ"

   # Set number of intermediate bars per layer
   set numInterBarsPerLayer 2

   # The distance from the section z-axis to the edge of the cover concrete
   # in the positive y direction
   set coverY [expr $lw/2.0]
   set coverYft [expr $lw/2.0-$tf1];
   set coverYfb [expr -$lw/2.0+$tf2];

   # The distance from the section y-axis to the edge of the cover concrete
   # in the positive z direction
   set coverZ [expr $bw/2.0]
   set coverZft [expr $bf1-$bw/2.0];
   set coverZfb [expr $bf2-$bw/2.0];

   # The distance from the section z-axis to the edge of the web concrete
   # in the positive y direction
   set webY	[expr $lw/2.0-$cover-$lbe1];
   # in the negative y direction
   set nwebY [expr -$lw/2.0+$cover+$lbe2];

   # The negative values of the two above
   set ncoverY [expr -$coverY]
   set ncoverZ [expr -$coverZ]

   # Determine the corresponding values from the respective axes to the
   # edge of the core concrete
   set coreY [expr $coverY-$cover]
   set coreZ [expr $coverZ-$cover]
   set ncoreY [expr -$coreY]
   set ncoreZ [expr -$coreZ]
   set coreYft [expr $coverYft+$cover];
   set coreYfb [expr $coverYfb-$cover];
   set coreZft [expr $coverZft-$cover];
   set coreZfb [expr $coverZfb-$cover];

   # Define the fiber section
   set id_temp [expr $id+10000];
   section fiberSec $id_temp -GJ 1e12 {

	# Define the upper boundary core patch
	# puts "$nfCoreY $nfCoreZ $webY $coreZ $webY $ncoreZ $coreY $ncoreZ $coreY $coreZ";
	patch quadr $coreIDFT [expr int($nfCoreY/2)] $nfCoreZ $coreYft $coreZft $coreYft $coreZ $coreY $coreZ $coreY $coreZft;
	patch quadr $coreIDWT [expr int($nfCoreY/2)] $nfCoreZ $coreYft $coreZ $coreYft $ncoreZ $coreY $ncoreZ $coreYft $coreZ;
	patch quadr $coreIDWT $nfCoreY $nfCoreZ $webY $coreZ $webY $ncoreZ $coreYft $ncoreZ $coreYft $coreZ;
	# Define the lower boundary core patch
	# puts "$nfCoreY $nfCoreZ $ncoreY $coreZ $ncoreY $ncoreZ $nwebY $ncoreZ $nwebY $coreZ"
	patch quadr $coreIDFB [expr int($nfCoreY/2)] $nfCoreZ $ncoreY $coreZfb $ncoreY $coreZ $coreYfb $coreZ $coreYfb $coreZfb;
	patch quadr $coreIDWB [expr int($nfCoreY/2)] $nfCoreZ $ncoreY $coreZ $ncoreY $ncoreZ $coreYfb $ncoreZ $coreYfb $coreZ;
	patch quadr $coreIDWB $nfCoreY $nfCoreZ $coreYfb $coreZ $coreYfb $ncoreZ $nwebY $ncoreZ $nwebY $coreZ;
      
	# Define the four cover patches
	# Side cover
	# puts "$nfCoreY $nfCoverZ $webY $coverZ $webY $coreZ $coreY $coreZ $coverY $coverZ"
	# puts "$nfCoreY $nfCoverZ $webY $ncoreZ $webY $ncoverZ $coverY $ncoverZ $coreY $ncoreZ"
	# puts "$nfCoreY $nfCoverZ $ncoverY $coverZ $ncoreY $coreZ $nwebY $coreZ $nwebY $coverZ"
	# puts "$nfCoreY $nfCoverZ $ncoreY $ncoreZ $ncoverY $ncoverZ $nwebY $ncoverZ $nwebY $ncoreZ"
	patch quadr $coverID $nfCoreY $nfCoverZ $webY $coverZ $webY $coreZ $coreYft $coreZ $coverYft $coverZ
	patch quadr $coverID [expr int($nfCoreY*1.5)] $nfCoverZ $webY $ncoreZ $webY $ncoverZ $coverY $ncoverZ $coreY $ncoreZ
	patch quadr $coverID [expr int($nfCoreY/2)] $nfCoverZ $coverYft $coverZft $coreYft $coreZft $coreY $coreZft $coreY $coverZft;
	patch quadr $coverID $nfCoreY $nfCoverZ $coverYfb $coverZ $coreYfb $coreZ $nwebY $coreZ $nwebY $coverZ
	patch quadr $coverID [expr int($nfCoreY*1.5)] $nfCoverZ $ncoreY $ncoreZ $ncoverY $ncoverZ $nwebY $ncoverZ $nwebY $ncoreZ
	patch quadr $coverID [expr int($nfCoreY/2)] $nfCoverZ $ncoverY $coverZfb $ncoreY $coreZfb $coreYfb $coreZfb $coverYfb $coverZfb;
	
	# Top and bottom cover
	# puts "$nfCoverY $nfCoreZ $ncoverY $coverZ $ncoverY $ncoverZ $ncoreY $ncoreZ $ncoreY $coreZ"
	# puts "$nfCoverY $nfCoreZ $coreY $coreZ $coreY $ncoreZ $coverY $ncoverZ $coverY $coverZ"
	patch quadr $coverID $nfCoverY $nfCoreZ $ncoverY $coverZfb $ncoverY $ncoverZ $ncoreY $ncoreZ $ncoreY $coreZfb;
	patch quadr $coverID $nfCoverY $nfCoreZ $coreYfb $coreZfb $coreYfb $coreZ $coverYfb $coverZ $coverYfb $coverZfb;
	patch quadr $coverID $nfCoverY $nfCoreZ $coreY $coreZft $coreY $ncoreZ $coverY $ncoverZ $coverY $coverZft;
	patch quadr $coverID $nfCoverY $nfCoreZ $coverYft $coverZft $coverYft $coverZ $coreYft $coreZ $coreYft $coreZft;

	# Web concrete
	if {$nfWebY > 0} {
		patch quadr $coverID $nfWebY $nfCoverZ $nwebY $coverZ $nwebY $coreZ $webY $coreZ $webY $coverZ
		patch quadr $coverID $nfWebY $nfCoverZ $nwebY $coreZ $nwebY $ncoreZ $webY $ncoreZ $webY $coreZ
		patch quadr $coverID $nfWebY $nfCoverZ $nwebY $ncoreZ $nwebY $ncoverZ $webY $ncoverZ $webY $ncoreZ
	}
	if {$numWB1 > 0} {
		# Define the steel layers in the upper boundary element
		# Top layer
		layer straight $steelIDWT $numWT1 $longBarArea1 [expr $coreY-0.5*$db1] [expr $coreZ-0.5*$db1] [expr $coreY-0.5*$db1] [expr $ncoreZ+0.5*$db1]; 	
		# Bottom layer
		layer straight $steelIDWT $numWT1 $longBarArea1 [expr $webY+0.5*$db1] [expr $coreZ-0.5*$db1] [expr $webY+0.5*$db1] [expr $ncoreZ+0.5*$db1]; 
	}
	# Do intermediate layers if they exist
   	if {$numWT2 < 3} {
		# Don't make any intermediate layers of bars
   	} else {
		# Compute spacing of intermediate layers (equally spaced)
		set interSpacing1 [expr (($lbe1 - 2*$db1)/[expr $numWT2 - 1])]
		#puts "Inter spacing is $interSpacing"
		
		# Make intermediate layers
		set layerDepth1 [expr ($coreY-0.5*$db1-$interSpacing1)]
		for {set layerNum 1} {$layerNum < [expr $numWT2 - 1]} {incr layerNum 1} {
			layer straight $steelIDWT $numInterBarsPerLayer $longBarArea1 $layerDepth1 [expr $coreZ-0.5*$db1] $layerDepth1 [expr $ncoreZ+0.5*$db1]; 
			#puts "Intermediate layer placed at $layerDepth"
			set layerDepth1 [expr $layerDepth1 - $interSpacing1]
		}
   	}

	# steel in the top intruded flange
#	layer straight $steelID $numTopBars1 $longBarArea1 [expr $coreYft+0.5*$db1] [expr $coreZft-0.5*$db1] [expr $coreY-0.5*$db1] [expr $coreZft-0.5*$db1];
#	set lbef1 [expr $bf1-$bw-$cover];
#	set barnumf1 [expr int($lbef1/$lbe1*$numInterLayers1)-1];
#	puts $barnumf1;
	if {$numFT2 > 0} {
		layer straight $steelIDFT $numFT2 $longBarArea4 [expr $coreYft+0.5*$db4] [expr $coreZft-0.5*$db4] [expr $coreYft+0.5*$db4] [expr $coreZ+0.5*$db4];
		layer straight $steelIDFT $numFT2 $longBarArea4 [expr $coreY-0.5*$db4] [expr $coreZft-0.5*$db4] [expr $coreY-0.5*$db4] [expr $coreZ+0.5*$db4];
	}

	if {$numWB1 > 0} {
		# Define the steel layers in the lower boundary element
		# Top layer
		layer straight $steelIDWB $numWB1 $longBarArea2 [expr $ncoreY+0.5*$db2] [expr $coreZ-0.5*$db2] [expr $ncoreY+0.5*$db2] [expr $ncoreZ+0.5*$db2]; 	
		# Bottom layer
		layer straight $steelIDWB $numWB1 $longBarArea2 [expr $nwebY-0.5*$db2] [expr $coreZ-0.5*$db2] [expr $nwebY-0.5*$db2] [expr $ncoreZ+0.5*$db2]; 
	}	

	# Do intermediate layers if they exist
#	puts "Check: Number of intermeddiate layers is $numInterLayers"
   	if {$numWB2 < 3} {
		# Don't make any intermediate layers of bars
   	} else {
		# Compute spacing of intermediate layers (equally spaced)
		set interSpacing2 [expr (($lbe2 - 2*$db2)/[expr $numWB2 - 1])]
		#puts "Inter spacing is $interSpacing"
		
		# Make intermediate layers
		set layerDepth2 [expr ($ncoreY+0.5*$db2+$interSpacing2)]
		for {set layerNum 1} {$layerNum < [expr $numWB2 - 1]} {incr layerNum 1} {
			layer straight $steelIDWB $numInterBarsPerLayer $longBarArea2 $layerDepth2 [expr $coreZ-0.5*$db2] $layerDepth2 [expr $ncoreZ+0.5*$db2]; 
			#puts "Intermediate layer placed at $layerDepth"
			set layerDepth2 [expr $layerDepth2 + $interSpacing2]
		}
   	}

	# steel in the bottom intruded flange
#	layer straight $steelID $numTopBars2 $longBarArea2 [expr $coreYfb-0.5*$db2] [expr $coreZfb-0.5*$db2] [expr $ncoreY+0.5*$db2] [expr $coreZfb-0.5*$db2];
#	set lbef2 [expr $bf2-$bw-$cover];
#	set barnumf2 [expr int($lbef2/$lbe2*$numInterLayers2)-1];
	if {$numFB2 > 0} {
		layer straight $steelIDFB $numFB2 $longBarArea5 [expr $coreYfb-0.5*$db5] [expr $coreZfb-0.5*$db5] [expr $coreYfb-0.5*$db5] [expr $coreZ+0.5*$db5];
		layer straight $steelIDFB $numFB2 $longBarArea5 [expr $ncoreY+0.5*$db5] [expr $coreZfb-0.5*$db5] [expr $ncoreY+0.5*$db5] [expr $coreZ+0.5*$db5];
	}
	
	# Define the steel layers in the web
	# Do intermediate layers if they exist
#	puts "Check: Number of web-steel layers is $numWebLayers"
   	if {$numWM2 == 0} {
		# Don't make any intermediate layers of bars
   	} else {
		# Compute spacing of intermediate layers (equally spaced)
		set interSpacing3 [expr (($webY-$nwebY)/[expr $numWM2+1])]
		#puts "Inter spacing is $interSpacing"
		
		# Make intermediate layers
		set layerDepth3 [expr ($nwebY+$interSpacing3)]
		for {set layerNum 1} {$layerNum < [expr $numWM2 + 1]} {incr layerNum 1} {
			layer straight $steelIDWM $numInterBarsPerLayer $longBarArea3 $layerDepth3 [expr $coreZ-0.5*$db3] $layerDepth3 [expr $ncoreZ+0.5*$db3]; 
			#puts "Intermediate layer placed at $layerDepth"
			set layerDepth3 [expr $layerDepth3 + $interSpacing3]
		}
   	}
	
   }
   
   # Define the shear material
   set rou_fyt [expr ($lbe1*$rou_tWT*$fytWT+$lbe2*$rou_tWB*$fytWB+($lw-$lbe1-$lbe2)*$rou_tWM*$fytWM)/$lw];
   set Ec [expr 5.7*sqrt(-$fc*1000.0)];
   set Gc [expr $Ec/2.0/(1+0.2)];
   set vn [expr $alpha_c*sqrt(-$fc*1000.0)/1000.0+$rou_fyt];
   if {$vn > [expr 8*sqrt(-$fc*1000.0)/1000.0]} {
		set vn [expr 8*sqrt(-$fc*1000.0)/1000.0];
   }
   set s1p [expr 0.002*sqrt(-$fc*1000.0)*$lw*$bw];
   set e1p [expr $s1p/$Gc/($lw*$bw)];
   set s2p [expr 0.6*$vn*$lw*$bw];
   set e2p [expr $e1p+($s2p-$s1p)/0.4/$Gc/($lw*$bw)];
   set s3p [expr $vn*$lw*$bw];
   set e3p [expr $e2p+0.4*$vn/0.1/$Gc];
   set s1n [expr -$s1p];
   set e1n [expr -$e1p];
   set s2n [expr -$s2p];
   set e2n [expr -$e2p];
   set s3n [expr -$s3p];
   set e3n [expr -$e3p];
   set pinchX 1.0;
   set pinchY 1.0;
   set damage1 0;
   set damage2 0;
   set beta 0;
   if {$ShearTag == "Linear"} {
		uniaxialMaterial Elastic $id_temp [expr $s1p/$e1p];
#		puts "K_shear [expr $s1p/$e1p]";
   } else {
#		puts "$id_temp $s1p $e1p $s2p $e2p $s3p $e3p $s1n $e1n $s2n $e2n $s3n $e3n $pinchX $pinchY $damage1 $damage2 $beta"
   		uniaxialMaterial Hysteretic $id_temp $s1p $e1p $s2p $e2p $s3p $e3p $s1n $e1n $s2n $e2n $s3n $e3n $pinchX $pinchY $damage1 $damage2 $beta;
   }

   # Aggregate the shear material to the flexure section
   section Aggregator $id $id_temp Vy -section $id_temp;
}






####################################################################################################
# Procedure - CreateBeamWithSlabSection: Defines a procedure which generates a rectangular reinforced concrete section
#  with two outer layers of longitudinal bars and multiple intermediate layers of longitudinal bars, evenly 
# spaced between the outer layers.  Note that the "cover" is both used for both the clear cover and 
# the side cover.  For each intermediate layer, two bars are placed at each of the layers.
# The slab is added to the -z side of the section, but it really doesn't matter b/c of the PSRP 
# assumption.  Slab steel is placed at the top and the bottom of the slab section, a distance
# "slab cover" from the top and bototm of the section.  A slab bar is only placed if the slab width
# is >= the slab bar spacing.
#
# If slab width or slab thinkness is < 0, then no slab is created.  
# If slabBarSpacing is > slabWidth, then no slab stell is defined. 
#
# Original file written by: Paul Cordova
# Date: 09/2001
#
# Altered by: Curt Haselton 
# Date: 03/2004
# 
#                       y
#                       |
#                       |	    |<-----------slabWidth----------->|
#                       |    
#             -------------------------------------------------------
#             |			    |o             o             o   
#             |  o o o o o o o o  |
#             |   		    |o_____________o_____________o_____	
#             |  o             o  |			    
#  z ---------|                   |  h		    
#	        |  o 		 o  |				
#		  |			    |			Ex. 	numBotBars = 8
#		  |  o      	 o  |				numTopBars = 8
#             |      	          |				numInterLayers = 3 
#             |  o o o o o o o o  |
#             |                   |
#             ---------------------
#                       b
#
# Formal arguments
#    id - tag for the section that is generated by this procedure
#    h - overall height of the section (see above)
#    b - overall width of the section (see above)
#    cover - thickness of the cover patches (from edge to center of bar) for the beam
#    coreID - material tag for the core patch
#    coverID - material tag for the cover patches
#    slabID - material tag for the slab patches
#    steelID - material tag for the reinforcing steel
#    longBarArea - area of each longitudinal reinforcing bar (same for top/bot bars) 
#    numBotBars - number of tension (bottom) bars
#    numTopBars - number of compression (top) bars
#    interBarArea - area of each intermediate reinforcing bar 
#    numInterLayers - number of intermediate layers of bars (2 bars per intermediate layer)
#    slabWidth - slab width in addition to the beam width
#    slabThick - slab thickness
#    slabBarArea -  area of each slab steel reinforcing bar (same for top/bot bars) 
#    slabBarSpacing - spacing between sets of slab bars - BE SURE THIS IS NOT ZERO BECAUSE OF DIVISION!
#    slabBarCover - cover to center of slab bars - used for both top and bottom bar layers
#    nfCoreY - number of fibers in the core patch in the y direction
#    nfCoreZ - number of fibers in the core patch in the z direction
#    nfCoverY - number of fibers in the cover patches with long sides in the y direction
#    nfCoverZ - number of fibers in the cover patches with long sides in the z direction
#    nfSlabY - number of fibers in the slab with long sides in the y direction
#    nfSlabZ - number of fibers in the slab with long sides in the z direction
#
# Notes
#    The thickness of cover concrete is constant on all sides of the core.
#    The number of bars is the same on any given side of the section.
#    The reinforcing bars are all the same size.
#    The number of fibers in the short direction of the cover patches is set to 1.
# 
proc CreateBeamWithSlabSection {id h b cover coreID coverID slabID steelID longBarArea numBotBars numTopBars interBarArea numInterLayers slabWidth slabThick slabBarArea slabBarSpacing slabBarCover nfCoreY nfCoreZ nfCoverY nfCoverZ nfSlabY nfSlabZ} {

   # Do outputs for testing
#   puts "id is $id"
#   puts "h is $h"
#   puts "cover is $cover"
#   puts "coreid is $coreID"
#   puts "coverID is $coverID"
#   puts "steelID is $steelID"
#   puts "longBarArea is $longBarArea"
#   puts "numBotBars is $numBotBars"
#   puts "numTopBars is $numTopBars"
#   puts "interBarArea is $interBarArea"
#   puts "numInterLayers is $numInterLayers"
#   puts "nfCoreY is $nfCoreY"
#   puts "nfCoreZ is $nfCoreZ"
#   puts "nfCoverY is $nfCoverY"
#   puts "nfCoverZ is $nfCoverZ"

   # Set number of intermediate bars per layer
   set numInterBarsPerLayer 2

   # The distance from the section z-axis to the edge of the cover concrete
   # in the positive y direction
   set coverY [expr $h/2.0]

   # The distance from the section y-axis to the edge of the cover concrete
   # in the positive z direction
   set coverZ [expr $b/2.0]

   # The negative values of the two above
   set ncoverY [expr -$coverY]
   set ncoverZ [expr -$coverZ]

   # Determine the corresponding values from the respective axes to the
   # edge of the core concrete
   set coreY [expr $coverY-$cover]
   set coreZ [expr $coverZ-$cover]
   set ncoreY [expr -$coreY]
   set ncoreZ [expr -$coreZ]

   # Define the fiber section
   section fiberSec $id {

	# Define the core patch - OK - checked on 9-13-04
	patch quadr $coreID $nfCoreZ $nfCoreY $ncoreY $coreZ $ncoreY $ncoreZ $coreY $ncoreZ $coreY $coreZ
      
	# Define the four cover patches  - I changed this on 9-13-04 - The top and bottom covers were discretized wrong.
	# Side cover
	patch quadr $coverID $nfCoverZ $nfCoreY $ncoverY $coverZ $ncoreY $coreZ $coreY $coreZ $coverY $coverZ
	patch quadr $coverID $nfCoverZ $nfCoreY $ncoreY $ncoreZ $ncoverY $ncoverZ $coverY $ncoverZ $coreY $ncoreZ
	# Top and bottom cover
	patch quadr $coverID $nfCoverZ $nfCoverY $ncoverY $coverZ $ncoverY $ncoverZ $ncoreY $ncoreZ $ncoreY $coreZ
	patch quadr $coverID $nfCoverZ $nfCoverY $coreY $coreZ $coreY $ncoreZ $coverY $ncoverZ $coverY $coverZ
	# Left cover patch
#	patch quadr $coverID $nfCoverZ $nfCoverY $ncoreY $coverZ $ncoreY $coreZ $coreY $coreZ $coreY $coverZ
#	# Right cover patch
#	patch quadr $coverID $nfCoverZ $nfCoverY $ncoreY $ncoreZ $ncoreY $ncoverZ $coreY $ncoverZ $coreY $ncoreZ
#	# Bottom cover patch
#	patch quadr $coverID $nfCoverZ $nfCoverY $ncoverY $coverZ $ncoverY $ncoverZ $ncoreY $ncoverZ $ncoreY $coverZ
#	# Top cover patch
#	patch quadr $coverID $nfCoverZ $nfCoverY $coverY $coverZ $coverY $ncoverZ $coverY $ncoverZ $coverY $coverZ
	
	# Define the steel layers
	# Top layer
	layer straight $steelID $numTopBars $longBarArea $coreY $ncoreZ $coreY $coreZ; 	
	# Bottom layer
	layer straight $steelID $numBotBars $longBarArea $ncoreY $ncoreZ $ncoreY $coreZ; 

	# Do intermediate layers if they exist
   	if {$numInterLayers == 0} {
		# Don't make any intermediate layers of bars
   	} else {
		# Compute spacing of intermediate layers (equally spaced)
		set interSpacing [expr (($h - 2*$cover)/[expr $numInterLayers + 1])]
		#puts "Inter spacing is $interSpacing"
		
		# Make intermediate layers
		set layerDepth [expr ($coreY - $interSpacing)]
		for {set layerNum 1} {$layerNum < [expr $numInterLayers + 1]} {incr layerNum 1} {
			layer straight $steelID $numInterBarsPerLayer $interBarArea $layerDepth $coreZ $layerDepth $ncoreZ; 
			#puts "Intermediate layer placed at $layerDepth"
			set layerDepth [expr $layerDepth - $interSpacing]
		}
   	}

	# Define the patch for the slab, if there is a slab -    
	set rightSlabZ [expr $ncoverZ - $slabWidth]
	set botSlabY [expr $coverY - $slabThick]	

	if {$slabWidth > 0 && $slabThick > 0} {
		#     					   bot/left   	   bot/right             top/right           top/left          	              
		# Careful here - need to define quadr in CCW around the patch!!!
		patch quadr $slabID $nfSlabZ $nfSlabY $botSlabY $ncoverZ $botSlabY $rightSlabZ $coverY $rightSlabZ $coverY $ncoverZ  
		#puts "Slab patch defined!"
		#puts "Slab ID is: $slabID"
	}

 	# Define steel layers for the slab
     		# Compute top and bottom slab layer heights
     		set topSlabBarY [expr $coverY - $slabBarCover]
     		set botSlabBarY [expr $botSlabY + $slabBarCover]

		# Compute number of bars to put in layers in slab - this should round to an integer result
     		set numSlabBarsInLayer [expr int($slabWidth/$slabBarSpacing)]

     		# Place layers, if there are bars to place - top then bottom
		if {$numSlabBarsInLayer > 0} {
     			layer straight $steelID $numSlabBarsInLayer $slabBarArea $topSlabBarY $ncoverZ $topSlabBarY $rightSlabZ
     			layer straight $steelID $numSlabBarsInLayer $slabBarArea $botSlabBarY $ncoverZ $botSlabBarY $rightSlabZ
			#puts "Slab layers defined with $numSlabBarsInLayer bars per layer!"
		}
   }
}
####################################################################################################
