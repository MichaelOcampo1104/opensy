proc MSSS-Concrete_Box_3-D {fc fys cof_ep st_ep dwl_str dwl_gap st_abp st_aba rot_fnd trns_fnd ms dr gap1 gap2 gap3 gap4 spans ln bn ch  D rho_l rho_t cover gd gd_spc spacing  A_t Ag fcg Iz_t Iy_t Izg Iyg  load_dir EQ  gd_wt slab_wt bear_pad_area bear_pad_d d_dec G_fac dowel_dec number} {
#                        1  2   3       4       5      6       7      8     9        10    11 12  13   14   15   16   17   18 19 20 21   22    23    24  25   26      27    28  29 30   31  32   33  34      35    36   37     38         39          40       41    42      43       44

#####################################################################################################
#  Input parameter descriptions
# ------------------------------
#	1. fc -- concrete strength (ksi)
#	2. fys	--	steel strength (ksi)
# 3. cof_ep -- coefficient of friction between the concrete and elastomeric bearing pad
# 4. st_ep --  initial stiffness of elastomeric bearing pad (ksi)
# 5. dwl_str -- strength of dowel in the elastomeric bearing
# 6. dwl_gap -- gap between dowel and elastomeric expansion bearing (in.) 
# 7. st_abp -- passive soil stiffness of abutment (k/in/in) (for abutments)
# 8. st_aba -- lateral stiffness of abutment piles (k/in/pile)
# 9.	rot_fnd -- vertical stiffness of foundation piles (k/in/pile)
#	10. trns_fnd -- 	lateral stiffness of foundation piles (k/in/pile)
#	11. ms --	multiplication factor for deck mass (percentage)
#	12. dr --		damping ratio                   
#	13. gap1 --	gaps for impact elements
#	14. gap2 --	gaps for impact elements
#	15. gap3 --	gaps for impact elements
#	16. gap4 --	gaps for impact elements
#	17. spans -- number of spans
#	18. ln --	max span length (in.)
#	19. bn --	number of columns per bent (deck width)
#	20. ch -- column height	(in.)
# 21. D -- column diameter (in)
# 22. rho_l -- longitudinal reinforcement ratio
# 23. rho_t -- transverse reinforcement ratio
# 24. cover -- concrete cover (in.)
# 25. gd -- number of girders
# 26. gd_spc -- girder spacing
# 27. spacing -- column spacing (in transverse direction)
# 28. A_t -- area of transverse deck elements (in.^2) (slab depth*distance b/w transerse elements)
# 29. Ag --  Cross-section area of a girder (in.^2) (concrete area + area of steel rebars transformed to quivalent concrete area)
# 30. fcg -- compressive strength of concrete in the girder
# 31. Iz_t -- Area moment of intertia of transverse elements along z direction (transverse direction) (in.^4) 
# 32. Iy_t -- Area moment of intertia of transverse elements along y direction (vertical direction) (in.^4)
# 33. Izg -- Area moment of intertia of girder elements along z direction (transverse direction) (in.^4)
# 34. Iyg -- Area moment of intertia of girder elements along y direction (vertical direction) (in.^4)
# 35. load_dir -- 	direction of loading in degrees
# 36. EQ -- earthquake number
# 37. gd_wt -- girder weight (kip/in)
# 38. slab_wt -- weight of slab for 'gd_spc' wide section (kip/in)
# 39. bear_pad_area -- area of the elastomeric bearing pad (in.^2) 
# 40. bear_pad_d -- thickness of the elastomeric bearing pad (in.) 
# 41. d_dec -- expeceted decrease in the diameter of the longitudinal r/f bars (in.) 
# 42. G_fac -- modification factor to acount for stiffening of bearing pads due to oxidation that occurs in time
# 43. dowel_dec -- expeceted decrease in the diameter of dowel bars elastomeric bearing pads (in.) 
#	44. number --	simulation number
#####################################################################################################
# this code creates a finite element model for the combination of parameters described above
# for each set of parameter combinations a folder is created where all the
# generated finite element model and the necessary files are stored

#

set name [concat MSSS-Concrete_Box_$number]
file mkdir $name
set fileID [open [concat $name/$name.tcl] w]
source rectify_gm.tcl
file copy "modal.tcl" $name/


puts $fileID "#########################################################"
puts $fileID "#                                                       #"
puts $fileID "# Generated Automatically for the sake of a parametric  #"
puts $fileID "# response and fragility modeling study.                #"
puts $fileID "# Multi-Span Simply Supported Concrete Box Girder Bridge#"
puts $fileID "# with eastomeric bearings                              #"
puts $fileID "#                                                       #"
puts $fileID "# Number of Spans:         $spans                       #"
puts $fileID "# Longest Span Length:     $ln in.                      #"
puts $fileID "# Column Height:           $ch in.                      #"
puts $fileID "# Number of Columns:       $bn                          #"
puts $fileID "#                                                       #"
puts $fileID "# Units: in and kips                                    #"
puts $fileID "# Originaly created by: Bryant Nielson                  #"
puts $fileID "# Improved for parametrization and inculsion of aging   #"
puts $fileID "# by Sabarethinam Kameshwar and Navya Vishnu            #"
puts $fileID "# Auto Created: [clock format [clock seconds] -format %D___%H:%M:%S] (time)              #"
puts $fileID "#                                                       #"
puts $fileID "#      Simulation Number $number                           #"
puts $fileID "#########################################################"
puts $fileID "#"
puts $fileID {set begin [clock clicks -milliseconds]}
puts $fileID "#\n source modal.tcl"
puts $fileID "#\n#                 number of dimensions"
puts $fileID "model BasicBuilder -ndm 3 -ndf 6"
puts $fileID "#\n#"

# the following generates the nodes in the bridge model
puts $fileID "#\n#=========================================================================="
puts $fileID "#                       NODE GENERATION"
puts $fileID "#==========================================================================\n#"
puts $fileID "#\n# NODES FOR DECK\n#"  

set ndiv1 6.; # the deck grillage has 6 divisions in the longitudinal direction; in the transverse direction it is governed by the number of girders 
set ndiv2 6 ; # same as ndiv1 but as an integer
for {set i 0} {$i < $spans} {incr i 1} {
	if {$spans < 2 | $spans > 9} {
		puts "Valid Number of spans is from 2 to 9, PLEASE TRY AGAIN!!"
		break
	} elseif {$spans == 2} {
		set sp($i) $ln
		set dl($i) [expr $sp($i)/$ndiv1]
		set div($i) $ndiv2
	} elseif {$spans > 2} {
		
			set sp($i) $ln
			set dl($i) [expr $sp($i)/$ndiv1]
			set div($i) $ndiv2
		
	}
}


set width [expr ($gd-1)*$gd_spc] ; # deck width
set trans_spc $gd_spc; # spacing b/w girders
set n_trans $gd  ; # specifying the number of elemets in the transverse elements for the grillage, i.e. the number of girders 

# creating nodes for the deck grillege
# the following loop does not include nodes at the left and right ends (w.r.t. longitudinal direction) of each deck


set n 10000  ; # herein, and in the remainder of this code, particular node numbers are assigned to different components such as columns, bearing etc so that each component gets a unique set of easily identifiable nodes. 
set x $dl(0)
for {set i 0} {$i < $spans} {incr i 1} {
	puts $fileID "#\n#         ID         X         Y         Z" 
	puts $fileID "#       DECK NUMBER [expr $i+1]"
	for {set j 0} {$j < [expr $div($i)-1]} {incr j 1} {
    set z [expr -$width/2.0]
    
    for {set k 0} {$k < $n_trans} {incr k 1} {
		  set n [expr $n+1]
		  set coord($n,0) $n
		  set coord($n,1) $x
		  set coord($n,2) 0.0
		  set coord($n,3) $z
		  puts $fileID [format "%-8s %3d %9.1f %9.1f %9.1f" node $coord($n,0) $coord($n,1) $coord($n,2) $coord($n,3)]
      set z [expr $z+$trans_spc]
    }
    set x [expr $x+$dl($i)]
	}
	set x [expr ($i+1)*$sp($i)+$dl($i)]          ;# because dl is same for all the spans
  
}



puts $fileID "#======================================================================================"
puts $fileID "#              NODES RIGID LINKS AT DECKS (TRANSVERSE BEAMS)"
puts $fileID "#======================================================================================"
# the following loop creates the nodes at the left and right ends (w.r.t. longitudinal direction) of each deck

	
set n 12000
set x 0

for {set i 0} {$i < $spans} {incr i 1} {
set z [expr -$width/2.0]

	puts $fileID "#       DECK NUMBER [expr $i+1] (Left End)"
	for {set j 0} {$j < $gd} {incr j 1} {
		set n [expr $n+1]
		set coord($n,0) $n
		set coord($n,1) $x
		set coord($n,2) 0.0
		set coord($n,3) $z
		puts $fileID [format "%-8s %3d %9.1f %9.1f %9.1f" node $coord($n,0) $coord($n,1) $coord($n,2) $coord($n,3)]
		set z [expr $z+$gd_spc]
	}
set z [expr -$width/2.0]
set x [expr $x+$sp($i)]
	puts $fileID "#       DECK NUMBER [expr $i+1] (Right End)"
	for {set j 0} {$j < $gd} {incr j 1} {
		set n [expr $n+1]
		set coord($n,0) $n
		set coord($n,1) $x
		set coord($n,2) 0.0
		set coord($n,3) $z
		puts $fileID [format "%-8s %3d %9.1f %9.1f %9.1f" node $coord($n,0) $coord($n,1) $coord($n,2) $coord($n,3)]
		set z [expr $z+$gd_spc]
	}

}

# the following generates nodes for the abutment and bent caps
puts $fileID "#======================================================================================"
puts $fileID "#              ABUTMENT AND BENT CAP NODES"
puts $fileID "#======================================================================================"
set m 500
set n [expr $n+1]

puts $fileID "# NODES FOR LEFT ABUTMENT\n#         ID         X         Y         Z"  
	set z [expr -$width/2.0]
	for {set j 0} {$j < $gd} {incr j 1} {
		set m [expr $m+1]
    set n $m
		set coord($n,0) $m
		set coord($n,1) 0.0
		set coord($n,2) 0.0
		set coord($n,3) $z
		puts $fileID [format "%-8s %3d %9.1f %9.1f %9.1f" node $coord($n,0) $coord($n,1) $coord($n,2) $coord($n,3)]
		set z [expr $z+$gd_spc]
	}
puts $fileID "# NODES FOR DECK #1 LEFT BEARING"
	set z [expr -$width/2.0]
	for {set j 0} {$j < $gd} {incr j 1} {
		set m [expr $m+1]
    set n $m
		set coord($n,0) $m
		set coord($n,1) 0.0
		set coord($n,2) 0.0
		set coord($n,3) $z
		puts $fileID [format "%-8s %3d %9.1f %9.1f %9.1f" node $coord($n,0) $coord($n,1) $coord($n,2) $coord($n,3)]
		set z [expr $z+$gd_spc]
	}
#==========================================================================================
#                            BENT CAP NODES
#==========================================================================================
set cover 1.5; # cover for the bents
set bWidth [expr $D+2*$cover]
set bDepth [expr $bWidth+2*$cover]

set x $sp(0)
for {set i 0} {$i < [expr $spans-1]} {incr i 1} {
	set z [expr -$width/2.0]

	puts $fileID "#       BENT NUMBER [expr $i+1] (Top)"
	for {set j 0} {$j < $gd} {incr j 1} {
		set m [expr $m+1]
    set n $m
		set coord($n,0) $m
		set coord($n,1) $x
		set coord($n,2) 0.0
		set coord($n,3) $z
		puts $fileID [format "%-8s %3d %9.1f %9.1f %9.1f" node $coord($n,0) $coord($n,1) $coord($n,2) $coord($n,3)]
		set z [expr $z+$gd_spc]
	}
set z [expr -$width/2.0]
	puts $fileID "#       BENT NUMBER [expr $i+1] (Bottom)"
	for {set j 0} {$j < $gd} {incr j 1} {
		set m [expr $m+1]
    set n $m
		set coord($n,0) $m
		set coord($n,1) $x
		set coord($n,2) [expr -$bDepth/2]
		set coord($n,3) $z
		puts $fileID [format "%-8s %3d %9.1f %9.1f %9.1f" node $coord($n,0) $coord($n,1) $coord($n,2) $coord($n,3)]
		set z [expr $z+$gd_spc]
	}
	set x [expr $x+$sp([expr $i+1])]
}


#==========================================================================================
#                            RIGHT ABUTMENT NODES
#==========================================================================================
#
puts $fileID "# NODES FOR DECK #$spans RIGHT BEARING\n#         ID         X         Y         Z"  
	set z [expr -$width/2.0]
	for {set j 0} {$j < $gd} {incr j 1} {
		set m [expr $m+1]
    set n $m
		set coord($n,0) $m
		set coord($n,1) $x
		set coord($n,2) 0.0
		set coord($n,3) $z
		puts $fileID [format "%-8s %3d %9.1f %9.1f %9.1f" node $coord($n,0) $coord($n,1) $coord($n,2) $coord($n,3)]
		set z [expr $z+$gd_spc]
	}
puts $fileID "# NODES FOR RIGHT ABUTMENT" 
	set z [expr -$width/2.0]
	for {set j 0} {$j < $gd} {incr j 1} {
		set m [expr $m+1]
    set n $m
		set coord($n,0) $m
		set coord($n,1) $x
		set coord($n,2) 0.0
		set coord($n,3) $z
		puts $fileID [format "%-8s %3d %9.1f %9.1f %9.1f" node $coord($n,0) $coord($n,1) $coord($n,2) $coord($n,3)]
		set z [expr $z+$gd_spc]
	}
  
  
  
# additional nodes for points where the bent and the columns meet
puts $fileID "\n#Additional nodes for points where the bent and the columns meet"
set n 26000
set k 1
set l 1

set x $sp(0)

for {set i 0} {$i < [expr $spans-1]} {incr i 1} {

set m [expr 500 + 2*$gd + $gd + $i*2*$gd]
set temp 1.
set z [expr -($bn-1)*$spacing/2.0]
set z2 [expr -$width/2.0]

# set count 0

for {set j 0} {$j < $bn} {incr j 1} {

  while {[expr round($z2*100)/100.<round($z*100)/100.]} {
#     set count [expr $count + 1]
    set m [expr $m+1]
    set bent_list($k) $m    
    set k [expr $k+1]
    set z2 [expr $z2+$gd_spc]
#     puts "z2 = $z2"
    }
    
    if {[expr round($z2*100)/100.==round($z*100)/100.]} {
      set eqdof_list($l) [expr $m+1]
      set l [expr $l+1]
      puts "case 1; i=$i"
    } elseif {[expr round($z2*100)/100.>round($z*100)/100.]} {
      set n [expr $n+1]
      set coord($n,0) $n
		  set coord($n,1) $x
		  set coord($n,2) [expr -$bDepth/2]
		  set coord($n,3) $z
      puts $fileID [format "%-8s %3d %9.1f %9.1f %9.1f" node $coord($n,0) $coord($n,1) $coord($n,2) $coord($n,3)]
    
      set bent_list($k) $n    
      set k [expr $k+1]
    
      set eqdof_list($l) [expr $n]
      set l [expr $l+1]
      puts "case 2; i=$i"
    }
    
  set z [expr $z+$spacing]
  
#   puts "temp = $temp"
}

  while {[expr round($z2*100)/100.<=round($width*100/2)/100.]} {
    set m [expr $m+1]
    set bent_list($k) $m    
    set k [expr $k+1]
    set z2 [expr $z2+$gd_spc]
    }
    

set x [expr $x+$sp([expr $i+1])]
}
  

puts "length of bentlist = [array size bent_list]"

  
  
#
#==========================================================================================
#                            FOUNDATION NODES
#==========================================================================================
#
puts $fileID "#======================================================================================"
puts $fileID "#              FOUNDATION NODES"
puts $fileID "#======================================================================================"
#
set m 8000	
set y [expr -$ch-48-$bDepth/2]
set x 0

for {set i 1} {$i < $spans} {incr i 1} {
	set x [expr $x+$sp([expr $i-1])]	
	set z [expr -($spacing*($bn-1))/2.0]
puts $fileID "# NODES FOR FOUNDATION - BENT #$i \n#         ID         X         Y         Z"  
	for {set j 0} {$j < $bn} {incr j 1} {
		set m [expr $m + 1]
		set coord($n,0) $m
		set coord($n,1) $x
		set coord($n,2) $y
		set coord($n,3) $z
		puts $fileID [format "%-8s %3d %9.1f %9.1f %9.1f" node $coord($n,0) $coord($n,1) $coord($n,2) $coord($n,3)]
		set m [expr $m + 1]
		set coord($n,0) $m
		puts $fileID [format "%-8s %3d %9.1f %9.1f %9.1f" node $coord($n,0) $coord($n,1) $coord($n,2) $coord($n,3)]
		set z [expr $z+$spacing]
	}
}
#
#==========================================================================================
#                            COLUMN NODES
#==========================================================================================
#
puts $fileID "#======================================================================================"
puts $fileID "#              COLUMN NODES"
puts $fileID "#======================================================================================"
#	
set m 1000
set n 1
set x 0
set q 0



for {set i 0} {$i < [expr $spans-1]} {incr i 1} {
	set x [expr $x+$sp($i)]	
	set z [expr -($spacing*($bn-1))/2.0]
	puts $fileID "#\n#============BENT NUMBER [expr $i +1]========================"
	for {set j 0} {$j < $bn} {incr j 1} {
		puts $fileID "#   COLUMN NUMBER [expr $j+1]\n#         ID         X         Y         Z"
		set q [expr $q + 1]
		set nn [expr $m + $q*50]
		set coord($n,0) $nn
		set coord($n,1) $x
		set coord($n,2) [expr -$bDepth/2]
		set coord($n,3) $z
		puts $fileID [format "%-8s %3d %9.1f %9.1f %9.1f" node $coord($n,0) $coord($n,1) $coord($n,2) $coord($n,3)]
	
		set nn [expr $nn+1]
		set coord($n,0) $nn
		set coord($n,1) $x
		set coord($n,2) [expr -$bDepth]
		set coord($n,3) $z
		puts $fileID [format "%-8s %3d %9.1f %9.1f %9.1f" node $coord($n,0) $coord($n,1) $coord($n,2) $coord($n,3)]

		set nn [expr $nn+1]
		set coord($n,0) $nn
		set coord($n,1) $x
		set coord($n,2) [expr -$bDepth-$ch/3.]
		set coord($n,3) $z
		puts $fileID [format "%-8s %3d %9.1f %9.1f %9.1f" node $coord($n,0) $coord($n,1) $coord($n,2) $coord($n,3)]

		set nn [expr $nn+1]
		set coord($n,0) $nn
		set coord($n,1) $x
		set coord($n,2) [expr -$bDepth-2*$ch/3.]
		set coord($n,3) $z
		puts $fileID [format "%-8s %3d %9.1f %9.1f %9.1f" node $coord($n,0) $coord($n,1) $coord($n,2) $coord($n,3)]

		for {set k 0} {$k < 5} {incr k 1} {
			set nn [expr $nn+1]
			set coord($n,0) $nn
			set coord($n,1) $x
			set coord($n,2) [expr -$bDepth-2*$ch/3.-$ch/15.*($k+1)]
			set coord($n,3) $z
			puts $fileID [format "%-8s %3d %9.1f %9.1f %9.1f" node $coord($n,0) $coord($n,1) $coord($n,2) $coord($n,3)]
		}
		set z [expr $z + $spacing]
	}
}


#
#==========================================================================================
#                            NODE CONSTRAINTS
#==========================================================================================
#
puts $fileID "#======================================================================================"
puts $fileID "#              NODE CONSTRAINTS"
puts $fileID "#======================================================================================"
#
puts $fileID "#\n#    Abutments - Left"
puts $fileID "#        TAG   X   Y   Z  MX  MY  MZ"
	set num 500
	for {set i 0} {$i < $gd} {incr i 1} {
		set num [expr $num + 1]
		puts $fileID [format "%-8s %3d %3d %3d %3d %3d %3d %3d" fix $num 1 1 1 1 1 1]
	}

puts $fileID "#\n#    Abutments - Right"
puts $fileID "#        TAG   X   Y   Z  MX  MY  MZ"
	set num [expr 500 + (2*$spans + 1)*$gd]
	for {set i 0} {$i < $gd} {incr i 1} {
		set num [expr $num + 1]
		puts $fileID [format "%-8s %3d %3d %3d %3d %3d %3d %3d" fix $num 1 1 1 1 1 1]
	}


puts $fileID "#\n#    Left Abutment - Bearing"
puts $fileID "#        TAG   X   Y   Z  MX  MY  MZ"
	set num [expr 500 + $gd]
	for {set i 0} {$i < $gd} {incr i 1} {
		set num [expr $num + 1]
		puts $fileID [format "%-8s %3d %3d %3d %3d %3d %3d %3d" fix $num 0 1 0 1 1 1]
	}

puts $fileID "#\n#    Right Abutment - Bearing"
puts $fileID "#        TAG   X   Y   Z  MX  MY  MZ"
	set num [expr 500 + (2*$spans)*$gd]
	for {set i 0} {$i < $gd} {incr i 1} {
		set num [expr $num + 1]
		puts $fileID [format "%-8s %3d %3d %3d %3d %3d %3d %3d" fix $num 0 1 0 1 1 1]
	}



for {set i 0} {$i < [expr $spans-1]} {incr i 1} {
	puts $fileID "#\n#    Foundation - Bent # [expr $i+1]"
	puts $fileID "#        TAG   X   Y   Z  MX  MY  MZ"
	set num [expr 7999+$i*$bn*2]
	for {set j 0} {$j < $bn} {incr j 1} {
		set num [expr $num + 2]
		puts $fileID [format "%-8s %3d %3d %3d %3d %3d %3d %3d" fix $num 0 1 0 0 1 0]
	}
}

for {set i 0} {$i < [expr $spans-1]} {incr i 1} {
	puts $fileID "#\n#    Foundation - Fixed Base - Bent # [expr $i+1]"
	puts $fileID "#        TAG   X   Y   Z  MX  MY  MZ"
	set num [expr 8000+$i*$bn*2]
	for {set j 0} {$j < $bn} {incr j 1} {
		set num [expr $num + 2]
		puts $fileID [format "%-8s %3d %3d %3d %3d %3d %3d %3d" fix $num 1 1 1 1 1 1]
	}
}



source MSSS-Concrete_Box_3-D_bent2_circ_col.tcl ; # to generate columns and bent elements
#
source MSSS-Concrete_Box_3-D_masses.tcl ; # to assign masses to node
#
source MSSS-Concrete_Box_3-D_deck.tcl ; # to generate deck grillage elements                               
# 
source MSSS-Concrete_Box_3-D_rigid.tcl ; # to generate rigis elements
#
source MSSS-Concrete_Box_3-D_bearings.tcl ; # to generate bearing elements
#
source MSSS-Concrete_Box_3-D_impact.tcl ; # to generate impact elements
#
source MSSS-Concrete_Box_3-D_abutments.tcl ; # to generate abutment elements
#
source MSSS-Concrete_Box_3-D_foundations.tcl ; # to generate foundation springs
#




puts $fileID "#\n#\n#=========================================================================="
puts $fileID "#                       END OF MODEL GENERATION"
puts $fileID "#==========================================================================\n#"
puts $fileID "logFile [concat $name/$name.log]"  ;# this log file is different from the log file specified in the main.tcl file. This log file will only record the screen output for this particular run.


puts $fileID "#\n#=========================================================================="
puts $fileID "#             DEFINE RECORDERS"
puts $fileID "#==========================================================================\n#"

set rng " "
set rng_b_n " "
set n 1007
for {set i 0} {$i < [expr ($spans-1)*$bn]} { incr i 1} {
	set n [expr $n + 50]
	set rng [concat $rng "$n"]
  set rng_b_n [concat $rng_b_n "[expr $n]"]
}

set rng_top " "
set n 1001
for {set i 0} {$i < [expr ($spans-1)*$bn]} { incr i 1} {
	set n [expr $n + 50]
	set rng_top [concat $rng_top "$n"]
}


puts $fileID "	recorder EnvelopeElement -file [concat $name/col_base.frc] -ele $rng section $\int force"; # forces at the base of the column 
puts $fileID "	recorder EnvelopeElement -file [concat $name/col_base.def] -ele $rng section $\int deformation\n#\n#" ; # deformation at the base of the column
puts $fileID "	recorder EnvelopeElement -file [concat $name/col_top.frc]  -ele $rng_top section 1 force" ; # forces at the top of the column
puts $fileID "	recorder EnvelopeElement -file [concat $name/col_top.def]  -ele $rng_top section 1 deformation\n#\n#"; # deformation at the base of the column  

puts $fileID "	recorder EnvelopeElement -file    [concat $name/abut.frc] -eleRange 7001 [expr 7000 + 2*$gd]  force"; # forces in abutment elements
puts $fileID "	recorder EnvelopeElement -file    [concat $name/abut.def] -eleRange 7001 [expr 7000 + 2*$gd]  deformation"; # deformations in abutment elements

puts $fileID "	recorder EnvelopeElement -file  [concat $name/fxdbrg.frc] -eleRange  501 [expr 500 + ($spans) *$gd]  force" ; # forces in fixed bearings
puts $fileID "	recorder EnvelopeElement -file  [concat $name/fxdbrg.def] -eleRange  501 [expr 500 + ($spans) *$gd]  deformation" ; # deformations in fixed bearings
puts $fileID "	recorder EnvelopeElement -file  [concat $name/expbrg.frc] -eleRange  701 [expr 700 + ($spans) *$gd]  force" ; # forces in expansion bearings
puts $fileID "	recorder EnvelopeElement -file  [concat $name/expbrg.def] -eleRange  701 [expr 700 + ($spans) *$gd]  deformation"; # deformations in expansion bearings

puts $fileID "  recorder EnvelopeNode -file [concat $name/inode.out] -node $rng_b_n -dof 1 3 disp" ; #nodal displacement at the base of the columns
puts $fileID "  recorder EnvelopeNode -file [concat $name/jnode.out] -node $rng_top -dof 1 3 disp" ; #nodal displacement at the top of the columns

puts $fileID "recorder EnvelopeDrift -file [concat $name/col_drift_l.out] -iNode $rng_b_n -jNode $rng_top -dof 1 -perpDirn 2" ; # column drift in the longitudinal direction
puts $fileID "recorder EnvelopeDrift -file [concat $name/col_drift_t.out] -iNode $rng_b_n -jNode $rng_top -dof 3 -perpDirn 2" ; # column drift in the tansverse direction


puts $fileID "	recorder EnvelopeElement -file    [concat $name/girder.frc] -eleRange 100001 [expr 100000 + $spans*$gd*$ndiv2]  force" ; # forces in the girders in the deck
puts $fileID "	recorder EnvelopeElement -file    [concat $name/transverse.frc] -eleRange 120001 [expr 120000 + $spans*($gd-1)*($ndiv2-1)]  force" ; # forces in the transverse deck elements (slab)
puts $fileID "	recorder EnvelopeNode -file    [concat $name/girder.out] -nodeRange 10001 [expr 10000 + $spans*$gd*$ndiv2] -dof 1 2 3 4 5 6 disp" ; # displacement at deck nodes

puts $fileID "	recorder EnvelopeElement -file  [concat $name/impact.frc] -eleRange 14001 [expr 14000 + ($spans + 1)*$gd]  force";# forces in the impact elements
puts $fileID "	recorder EnvelopeElement -file  [concat $name/impact.def] -eleRange 14001 [expr 14000 + ($spans + 1)*$gd]  deformation" ; # deformations in the impact elements



# displaying the bridge and the deformations
set mode_num 1

puts $fileID {recorder display "longitudinal view" 10 10 750 600 -wipe}
  puts $fileID "prp 0 0 0;"
  puts $fileID "vup  0  1 0"
  puts $fileID "vpn  1  0 0;"
  puts $fileID "viewWindow [expr -$width/2.-100] [expr $width/2.+100] [expr -900] [expr 700]"
  puts $fileID "display $mode_num 2 40" 
  puts $fileID "port -1 1 -1 1 # area of window that will be drawn into"
  puts $fileID "fill 1 # fill mode"
  
  
puts $fileID {recorder display "Displacement view 2" 770 10 750 600 -wipe}
  puts $fileID "prp [expr $spans*$ln/2.] 0. [expr $width/2.];" 
   puts $fileID "vup  0  1  0"
   puts $fileID "vpn  0  0  1"
  puts $fileID "viewWindow [expr -$spans*$ln/2.-200] [expr $spans*$ln/2.+200] [expr -900] [expr 700]"
  puts $fileID "display $mode_num 2 40" 
  puts $fileID "port -1 1 -1 1 # area of window that will be drawn into"
  puts $fileID "fill 1 # fill mode" 
  
  puts $fileID {recorder display "Displacement view 3" 1650 10 1500 600 -wipe}
  puts $fileID "prp [expr $spans*$ln/2.] $ch 0;" 
   puts $fileID "vup  0  0  1"
   puts $fileID "vpn  0  1  0"
  puts $fileID "viewWindow [expr -$spans*$ln/2.-100] [expr $spans*$ln/2.+100] [expr -$width/2.-200] [expr $width/2.+200]"
  puts $fileID "display $mode_num 2 40" 
  puts $fileID "port -1 1 -1 1 # area of window that will be drawn into"
  puts $fileID "fill 1 # fill mode"  
# puts $fileID "1111"              


puts $fileID "#\n#=========================================================================="
puts $fileID "#                       DEFINE GRAVITY LOADS"
puts $fileID "#==========================================================================\n#"
source gravity.tcl



# puts $fileID "#\n#=========================================================================="
# puts $fileID "#             PERFORM EIGEN ANALYSIS"
# puts $fileID "#==========================================================================\n#"
# 
puts $fileID "set N  10"
puts $fileID {ModalAnalysis $N      $name}
puts $fileID {puts "here" }
puts $fileID "#\nloadConst -time 0.0\n#"

# perform dynamic analysis
source t_analysis_eq2.tcl


close $fileID

}

