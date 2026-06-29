# This code creates the elements for the columns and the bent beams
puts $fileID "#\n#\n#=========================================================================="
puts $fileID "#                       COLUMN & BENT CAP MATERIAL"
puts $fileID "#=========================================================================="
#  
puts $fileID "set cover $cover" ; # setting cover depth
set d [expr $D-2*$cover-1]; #  depth of concrete core
puts $fileID "set D $D"; # column diameter
set hoop_dia [expr $D-2*$cover+0.25] ; # diameter of hoops for transverse reinforcement
set Ast [expr 0.31]        ; # area of transverse r/f   (area of #16 bars = 0.31)

puts $fileID "set d $d" ; # depth of concrete core
puts $fileID "set hoop_dia [expr $D-2*$cover+0.25]" ; # diameter of hoops for transverse reinforcement
puts $fileID "set Ast [expr 0.31]"        ; # area of transverse r/f   (area of #16 bars = 0.31)
puts $fileID "set rho_t $rho_t"; # ransverse reinforcement ratio  

puts $fileID "set fyst     $fys; # Reinforcing steel yield strength"
puts $fileID "set fc     -$fc; # Unconfined concrete strength"

# parameters for un-confined concrete (in ksi). variable names and meaning are described in the OpenSees wiki page for Concrete04 material 
set ec [expr -pow($fc*1000, 0.25)/4000.0]
set Ec [expr 185000*pow($fc*1000,3.0/8.0)/1000.0]
set ft [expr 7.5*pow($fc*1000,0.5)/1000.0]
set et [expr 2.0*$ft/$Ec]
set xp 2.0
set xn 2.3
set r_p [expr $fc*1000.0/750.0-1.9]  

# parameters for confined concrete (in ksi) - for detailed description of parameters refer: 
# Mander, J.B., Priestley, M.J. and Park, R., 1988. Theoretical stress-strain 
# model for confined concrete. Journal of structural engineering, 114(8), pp.1804-1826.

set s [expr 4*$Ast/($d*$rho_t)] ; # hoop clear spacing
set A_bar_t [expr $rho_l*3.14*$D*$d/4]; # area of longitudinal steel
set Ast [expr $Ast*(1-$d_dec/0.625)*(1-$d_dec/0.625)] ; # modifying Ast for aging
set rho_t [expr 4*$Ast/($d*$s)]   ; # modifying rho_t for aging
set rho_cc [expr $Ast/(3.14*$d*$d/4)]
set Ke [expr (1-($s-0.25)/(2*$hoop_dia))*(1-($s-0.25)/(2*$hoop_dia))/(1-$rho_cc)]
set fl [expr 0.5*$Ke*$rho_t*66.66]
set xd [expr $fl*2/(2*$fc)]; # because circular column
set q 1.0 ; # because circular column
set a [expr 6.886 -(0.6069+17.275*$q)*exp(-4.989*$q)]
set b [expr 4.5/((5/$a)*(0.9849-0.6036*exp(-3.8939*$q)-0.1))-5.0]
set k1 [expr $a*(0.1+0.9/(1+$b*$xd))]
set k2 [expr 5*$k1]; # for normal strength steel 
set fcon [expr (($fc*(1+$k1*$xd)))]
set eccon [expr $ec*(1+$k2*$xd)]
set n [expr -$Ec*$ec/($fcon)]
set rcon [expr $n/($n-1)]
puts "\nn = $n"
puts "rcon = $rcon"
set xncon 30.
set ftcon [expr 7.5*pow($fcon*1000,0.5)/1000.0]

puts $fileID "set fcon -$fcon" ;# strength of confined concrete
puts $fileID "set Ec $Ec"  ; # elastic modulus of concrete


puts $fileID "set fc     -$fc; # Unconfined concrete strength"

puts $fileID "set fys     $fys; # Reinforcing steel yield strength"
puts $fileID "set Es   29000.0; # Reinforcing steel Modulus of Elasticity"
puts $fileID "# Estimate yield curvature"
puts $fileID "# (Assuming no axial load and only top and bottom steel)"
puts $fileID {set epsy [expr $fys/$Es]	;# steel yield strain}
puts $fileID {set Ky [expr $epsy/(0.7*$d)]; # Yield Curvature}
puts $fileID "#\n# Print estimate to standard output"
puts $fileID {puts "Estimated yield curvature: $Ky"}
puts $fileID "set name $name"
puts $fileID {set file_curve [open [concat $name/$name.crv] w]}; # file where the yeild curature is printed
puts $fileID {puts $file_curve $Ky}
puts $fileID {close $file_curve}

puts $fileID {set ec [expr 0.002]};   # strain at maximum strength 
puts $fileID {set ecu 0.012};   # strain at crushing strength
puts $fileID {set Econ  [expr 57.0*pow(-$fcon*1000,0.5)]}


#
puts $fileID "#\n#\n#  CONCRETE                 tag  f'c              ec0           f'cu     ecu"
puts $fileID "#  Core concrete (confined)"
puts $fileID {uniaxialMaterial Concrete04 1   $fcon   [expr -1.0*$ec]  [expr -1.0*$ecu]    $Econ}


puts $fileID "#\n#  Cover concrete (un-confined)"
puts $fileID {uniaxialMaterial Concrete04 2     $fc       [expr -1.0*0.002]  [expr -1.0*0.004]    $Ec}

puts $fileID "#\n#  REINFORCING STEEL        tag  "
puts $fileID "uniaxialMaterial Steel02   3  \$fys \$Es 0.025 18.0 0.925 0.15"; # Menegotto-Pinto uniaxial steel model (coefficients by Terzic, 2010)
puts $fileID "#\n# Torsion Material"
puts $fileID "uniaxialMaterial Elastic    4    1.0e10" ;# rigid elastic material
puts $fileID "#\n#=========================================================================="
puts $fileID "#                       COLUMN SECTION GENERATION"
puts $fileID "#==========================================================================\n#"


set d_b  1.128; # diameter of r/f bars in the longitudinal direction
puts $fileID "set d_b  $d_b"
set A_bar [expr 3.14*$d_b*$d_b/4] ; # area of the r/f bar
set n_bar [expr $A_bar_t/$A_bar] ; # number of bar in the longitudinal direction
set n_bar [expr round($n_bar)] ; # rounding off to get an integer

if {$n_bar<2} {
set n_bar 2
}

puts "n_bar = $n_bar"
set rho_l [expr $n_bar*$A_bar/(3.14*$D*$d/4)] ; # recalculating longitudinal reinforcement ratio

# printing the revised longitudinal and transverse reinforcement ratio in to a file
puts "$n_bar  $A_bar_t $rho_l"
puts $fileID {set file_rho_tl [open [concat $name/$name.rho_tl] w]}
puts $fileID "puts \$file_rho_tl $rho_l"
puts $fileID "puts \$file_rho_tl $rho_t"
puts $fileID {close $file_rho_tl}

# changing bar area to account for aging
set D_Ar_fac [expr (1-$d_dec/$d_b)*(1-$d_dec/$d_b)] ; # factor to be multiplied with area of dowel bar to consider decrease in area due to aging 
set A_bar [expr $A_bar*$D_Ar_fac]

# Circular fiber section for columns
puts $fileID "section Fiber 1 {                                                                      ;                  #                    angle"
puts $fileID "# Core concrete       tag      div     raddiv       Y-cen    Z-cen     int-rad                    out-rad                     start  end"
puts $fileID "patch circ             1      $n_bar      8          0.0      0.0        0.0                    [expr $D/2.0-$cover+$d_b/2]          0.0   360.0"
puts $fileID "# Cover concrete "
puts $fileID "patch circ             2      $n_bar      2          0.0      0.0       [expr $D/2.0-$cover+$d_b/2]     [expr $D/2.0]                0.0   360.0"
puts $fileID "# Reinforcing Steel"
puts $fileID "layer circ             3      $n_bar    $A_bar   0.0      0.0       [expr $D/2.0-$cover+$d_b/2]                                  0.0   [expr 360.0 - 360.0/$n_bar]"
puts $fileID "}"

puts $fileID "#                   TAG  Mat  Dir    section"
puts $fileID "section Aggregator   2    4    T   -section 1"
puts $fileID "#\n#=========================================================================="
puts $fileID "#                       COLUMN ELEMENTS"
puts $fileID "#==========================================================================\n#"
puts $fileID "geomTransf	PDelta	3    1   0   0\n#\n#"
puts $fileID "set int  6	;# integration point"

set q 0

# creating column elements
for {set i 0} {$i < [expr $spans-1]} {incr i 1} {
	for {set j 0} {$j < $bn} {incr j 1} {
		set q [expr $q+1]
		set n [expr 1000 +$q*50]
		set m [expr 1000 +$q*50]
		puts $fileID "#\n#  Bent No. [expr $i+1] - Column No. [expr $j+1]"
		puts $fileID "#                        TAG    In    Jn  int-pts   Sect   Transf"
		for {set k 0} {$k < 7} {incr k 1} {
			set n [expr $n+1]
			set m [expr $m+1]
			set p [expr $m+1]
			puts $fileID [format "%-7s %-14s %5d %5d %5d %6s %5d %5d " element dispBeamColumn $n $m $p \$int 2 3]
		}
	}
}



puts $fileID "#\n#=========================================================================="
puts $fileID "#                       BENT CAP SECTION GENERATION"
puts $fileID "#==========================================================================\n#"

puts $fileID "set bWidth \[expr $D+2*$cover]\nset bDepth \[expr \$bWidth+2*$cover]\n#"


puts $fileID {set A_steel [expr 1.0767*($bWidth-2*$cover)*($bDepth-2*$cover)/100]}; # 1.067 is the stell r/f ratio
puts $fileID {set factor [expr $A_steel/(15*1+4*0.32)]}
puts $fileID {set As1    [expr $factor*1.00];      }; # area of no. 9 bars
puts $fileID {set As2    [expr $factor*0.32];     }; # area of no. 5 bars

set D_Ar_fac1 [expr (1-$d_dec/1.128)*(1-$d_dec/1.128)] ; # factor to be multiplied with area of dowel bar to consider decrease in area due to aging 
puts $fileID "set As1 \[expr \$As1*$D_Ar_fac1]"
set D_Ar_fac2 [expr (1-$d_dec/0.625)*(1-$d_dec/0.625)] ; # factor to be multiplied with area of dowel bar to consider decrease in area due to aging 
puts $fileID "set As2 \[expr \$As2*$D_Ar_fac2]"


# rectangular bent column section
puts $fileID "# some variables derived from the parameters"
puts $fileID {set y1 [expr $bDepth/2.0]}
puts $fileID {set z1 [expr $bWidth/2.0]}

puts $fileID "#\n#\nsection Fiber 3 {\n#"

puts $fileID "    # Create the concrete core fibers"
puts $fileID {    patch quad 1 10 10 [expr $cover-$y1] [expr $cover-$z1] [expr $y1-$cover] [expr $cover-$z1] [expr $y1-$cover] [expr $z1-$cover] [expr $cover-$y1] [expr $z1-$cover]}

puts $fileID "#\n    # Create the concrete cover fibers (top, bottom, left, right)"
puts $fileID {    patch quad 2 10 2  [expr -$y1] [expr $z1-$cover] $y1 [expr $z1-$cover] $y1 $z1 [expr -$y1] $z1}
puts $fileID {    patch quad 2 10 2  [expr -$y1] [expr -$z1] $y1 [expr -$z1] $y1 [expr $cover-$z1] [expr -$y1] [expr $cover-$z1]}
puts $fileID {    patch quad 2  2 10  [expr -$y1] [expr $cover-$z1] [expr $cover-$y1] [expr $cover-$z1] [expr $cover-$y1] [expr $z1-$cover] [expr -$y1] [expr $z1-$cover]}
puts $fileID {    patch quad 2  2 10  [expr $y1-$cover] [expr $cover-$z1] $y1 [expr $cover-$z1] $y1 [expr $z1-$cover] [expr $y1-$cover] [expr $z1-$cover]}

puts $fileID "#\n    # Create the reinforcing fibers (right, middle, left)"
puts $fileID {    layer straight 3 9 $As1 [expr $y1-$cover] [expr $z1-$cover] [expr $y1-$cover] [expr $cover-$z1]}
puts $fileID {    layer straight 3 2 $As2 -7.0 [expr $z1-$cover] -7.0 [expr $cover-$z1]}
puts $fileID {    layer straight 3 2 $As2 7.0 [expr $z1-$cover] 7.0 [expr $cover-$z1]}
puts $fileID {    layer straight 3 6 $As1 [expr $cover-$y1] [expr $z1-$cover] [expr $cover-$y1] [expr $cover-$z1]}
puts $fileID "}\n#"    

puts $fileID "section Aggregator 4  4   T   -section 3"

puts $fileID "#\n#=========================================================================="
puts $fileID "#                       BENT CAP ELEMENTS"
puts $fileID "#==========================================================================\n#"
puts $fileID "geomTransf	PDelta	4  -1  0  0"

puts $fileID "#\n#\nset int3  4	;# integration point\n#"

set n 5000


set node_per_bent [expr [array size bent_list]/($spans-1)]

puts "node_per_bent = $node_per_bent"


set inode_list " "
set jnode_list " "
# generating bent beam elements
for {set i 0} {$i < [expr $spans-1]} {incr i 1} {


  for {set j 1} {$j < [expr $node_per_bent]} {incr j 1} {

    set n [expr $n+1]
    set m $bent_list([expr $i*$node_per_bent+$j]);# picking start node from the list of nodes on the bent 
    set p $bent_list([expr 1+$i*$node_per_bent+$j]) ;# picking end node from the list of nodes on the bent
    set inode_list [concat $inode_list "$m"] ; # adding to a list that only has start nodes
    set jnode_list [concat $jnode_list "$p"] ; # adding to a list that only has end nodes
    puts $fileID "element dispBeamColumn  $n    $m  $p   \$int3     4      4"

  }
}

set p 1050
for {set i 1} {$i <= [expr $bn*($spans-1)]} {incr i 1} {
  set m $eqdof_list($i)
  puts $fileID "equalDOF $p $m  1 2 3 4 5 6" ;# where the bent and the column meet
  set p [expr $p+50] 
}