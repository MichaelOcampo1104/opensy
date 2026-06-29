
puts $fileID "#======================================================================================"
puts $fileID "#              NODAL MASSES"
puts $fileID "#======================================================================================"


# weight of deck alone = 0.508 k/ft for 75" wide section


# mass of deck slababd girder
	set wt1 [expr $slab_wt + $gd_wt] ; # k/in  -- weight
	set dm1	[expr $ms*$wt1/386.4]; # mass



# a bridge may have un-equal span lengths for end and middle spans; so the loop covers both cases
for {set i 0} {$i < 2} {incr i 1} {

    set dm($i) [expr $dm1*$dl($i)]
		set R($i)	[expr $dm1*$sp($i)/2.*386.4] ;  # calculate the reaction at each girder
		set brg($i)	1 

}



for {set i 0} {$i < 2} {incr i 1} {
set r($i) 0
set z [expr -$width/2.0]

	for {set j 0} {$j < $gd} {incr j 1} {
    set r($i) [expr $r($i)+$z*$z]; # calculating moment arm for girders' rotational mass moment of inertia calculation			
		set z [expr $z+$gd_spc]
	}
}





puts $fileID "#======================================================================================"
puts $fileID "#              DECK MASSES"
puts $fileID "#======================================================================================"

# the mass moment of inertia is only updated in x direction (along traffic) as rotation of the deck is expected mainly about x axis

# for the shorter spans
puts $fileID "set dms $dm(0); # Type $brg(0) Girder"
puts $fileID {set dms2 [expr $dms/2.]} ; # half values for nodes at the end of girders
# for longer spans
puts $fileID "set dml $dm(1); # Type $brg(1) Girder"
puts $fileID {set dml2 [expr $dml/2.]} ; # half values for nodes at the end of girders
set n1 12000
set n2 10000

for {set i 0} {$i < $spans} {incr i 1} {
	puts $fileID "#\n#          Deck No. [expr $i+1]"
	puts $fileID "#       node X-mass   Y-mass   Z-mass   MX-mass  MY-mass  MZ-mass"
  
  
	if {$i == 0 | $i == [expr $spans-1]} {
  
    puts $fileID "#      Left End"
    for {set j 0} {$j < [expr $gd]} {incr j 1} {
		   
      set n1 [expr $n1+1]
			puts $fileID [format "%-8s %3d %-8s %-8s %-8s %-8s %-8s %-8s" mass $n1 \$dms2 \$dms2 \$dms2 \$dms2 \$dms2 \$dms2]
	 }
		
    
		for {set j 1} {$j < $div($i)} {incr j 1} {
    
      for {set k 0} {$k < [expr $gd]} {incr k 1} {
      
        if {$k==0} {
            set n2 [expr $n2 +1]
        } else {
            set n2 [expr $n2+($n_trans-1)/($gd-1)]            
        }
			  
			  puts $fileID [format "%-8s %3d %-8s %-8s %-8s %-8s %-8s %-8s" mass $n2 \$dms \$dms \$dms \$dms \$dms \$dms]
      }
			
		}
    
    
		puts $fileID "#      Right End"
    for {set j 0} {$j < [expr $gd]} {incr j 1} {
		   
			set n1 [expr $n1+1]
			puts $fileID [format "%-8s %3d %-8s %-8s %-8s %-8s %-8s %-8s" mass $n1 \$dms2 \$dms2 \$dms2 \$dms2 \$dms2 \$dms2]
	 }
    
    
	} else {
		puts $fileID "#      Left End"
    for {set j 0} {$j < [expr $gd]} {incr j 1} {
		   
			set n1 [expr $n1+1]
			puts $fileID [format "%-8s %3d %-8s %-8s %-8s %-8s %-8s %-8s" mass $n1 \$dml2 \$dml2 \$dml2 \$dml2 \$dml2 \$dml2]
	 }
		
    
		for {set j 1} {$j < $div($i)} {incr j 1} {
    
      for {set k 0} {$k < [expr $gd]} {incr k 1} {
      
			  if {$k==0} {
            set n2 [expr $n2 +1]
        } else {
            set n2 [expr $n2+($n_trans-1)/($gd-1)]            
        }
			  puts $fileID [format "%-8s %3d %-8s %-8s %-8s %-8s %-8s %-8s" mass $n2 \$dml \$dml \$dml \$dml \$dml \$dml]
      }
			
		}
    
    
		puts $fileID "#      Right End"
    for {set j 0} {$j < [expr $gd]} {incr j 1} {
		   
			set n1 [expr $n1+1]
			puts $fileID [format "%-8s %3d %-8s %-8s %-8s %-8s %-8s %-8s" mass $n1 \$dml2 \$dml2 \$dml2 \$dml2 \$dml2 \$dml2]
	 }
    
	}
}



puts $fileID "#======================================================================================"
puts $fileID "#              BENT CAP MASSES"
puts $fileID "#======================================================================================"
# The total mass of the bent cap is 3.5' x 4.0 ' and has a mass of 0.0004529 k-s^2/in per inch
# and a mass of 0.03397 k-s^2/in per 75" section.
# the mass assigned to bent nodes is scaled according the the spacing between the girders (gd_spc) and the cross section area of the bridge bent (bWidth*bDepth)

puts $fileID "set gd_spc $gd_spc"
puts $fileID "set  bcm   \[expr ($gd_spc/75.)*(\$bWidth*\$bDepth)*0.03397/(3.5*4.0*144)]  ; # bent cap mass for 75 inch section (k-s^2/in)" ; # scaling for girder spacing and cross section area
puts $fileID {set  bcm2   [expr $bcm/2.] ; # nodes at the edge are assigned half the weight 
set n [expr 500 + 3*$gd]

puts $fileID {set bmiz [expr $bcm*($bDepth*$bDepth+$bWidth*$bWidth)/12]}; # mass moment of inertia in z direction
puts $fileID {set bmix [expr $bcm*($bDepth*$bDepth+$gd_spc*$gd_spc)/12]}; # mass moment of inertia in x direction - scaled for girder spacing (which govern the node spacing on the bent)
puts $fileID {set bmiy [expr $bcm*($bWidth*$bWidth+$gd_spc*$gd_spc)/12]}; # mass moment of inertia in y direction - scaled for girder spacing (which govern the node spacing on the bent)

puts $fileID {set bmiz2 [expr $bcm2*($bDepth*$bDepth+$bWidth*$bWidth)/12]}; # mass moment of inertia in z direction
puts $fileID {set bmix2 [expr $bcm2*($bDepth*$bDepth+$gd_spc*$gd_spc/4.)/12+$bcm2*$gd_spc*$gd_spc/16.]}; # mass moment of inertia in x direction for end section (modified using parallel axis theorem)
puts $fileID {set bmiy2 [expr $bcm2*($bWidth*$bWidth+$gd_spc*$gd_spc/4.)/12+$bcm2*$gd_spc*$gd_spc/16.]}; # mass moment of inertia in y direction for end section (modified using parallel axis theorem)

# assigning masses to the nodes
for {set i 1} {$i < $spans} {incr i 1} {
	puts $fileID "#\n#          Bent No. [expr $i+1]"
	puts $fileID "#       node X-mass   Y-mass   Z-mass   MX-mass  MY-mass  MZ-mass"

	set n [expr $n+1]
	puts $fileID [format "%-8s %3d %-8s %-8s %-8s %-8s %-8s %-8s" mass $n \$bcm2 \$bcm2  \$bcm2  \$bmix2  \$bmiy2  \$bmiz2]
#   puts $fileID [format "%-8s %3d %-8s %-8s %-8s %-8s %-8s %-8s" mass $n \$bcm2 \$bcm2  \$bcm2  \$bcm2 \$bcm2  \$bcm2]
	for {set j 1} {$j < [expr $gd-1]} {incr j 1} {
		set n [expr $n+1]
		puts $fileID [format "%-8s %3d %-8s %-8s %-8s %-8s %-8s %-8s" mass $n \$bcm \$bcm  \$bcm  \$bmix  \$bmiy  \$bmiz]
#   puts $fileID [format "%-8s %3d %-8s %-8s %-8s %-8s %-8s %-8s" mass $n \$bcm \$bcm  \$bcm  \$bcm \$bcm  \$bcm]
	}
	set n [expr $n+1]
	puts $fileID [format "%-8s %3d %-8s %-8s %-8s %-8s %-8s %-8s" mass $n \$bcm2 \$bcm2  \$bcm2  \$bmix2  \$bmiy2  \$bmiz2]
#   puts $fileID [format "%-8s %3d %-8s %-8s %-8s %-8s %-8s %-8s" mass $n \$bcm2 \$bcm2  \$bcm2  \$bcm2 \$bcm2  \$bcm2]
	set n [expr $n + $gd]
}

puts $fileID "#======================================================================================"
puts $fileID "#              COLUMN MASSES"
puts $fileID "#======================================================================================"
#  A 36" diameter column has a mass of 0.000229 k-s^2/in per inch
# Mass for a column with different diameter is scaled arrording to the ratio of cross-section area 
puts $fileID "set  colm   [expr ($D*$D/(36.*36.))*0.000229*$ch/3.]  ; "  ; # scaling the mass of the column according to the cross section and the length of the column element
puts $fileID {set  colm2   [expr $colm/2.] ; # column mass for [expr $ch/6.] inch section (k-s^2/in)}  -- used for elements that are half the length of the regular column elements
set n [expr 1050]
set q 0
#

puts $fileID "set ch $ch"
puts $fileID {set cmix [expr $colm*(3*$D*$D+$ch*$ch/9)/12]}; # mass moment of inertia in y direction for ch/3 inch section
puts $fileID {set cmix2 [expr $colm2*(3*$D*$D+$ch*$ch/36)/12+ $colm2*$ch*$ch/144]}; # mass moment of inertia in y direction for ch/6 inch section (useing parallel axis theorem)

puts $fileID {set cmiz [expr $colm*(3*$D*$D+$ch*$ch/9)/12]}; # mass moment of inertia in z direction for ch/3 inch section
puts $fileID {set cmiz2 [expr $colm2*(3*$D*$D+$ch*$ch/36)/12+ $colm2*$ch*$ch/144]}; # mass moment of inertia in z direction for ch/6 inch section (useing parallel axis theorem)

puts $fileID {set cmiy [expr $colm*($D*$D)/2]}; # mass moment of inertia in y direction for ch/3 inch section
puts $fileID {set cmiy2 [expr $colm2*($D*$D)/2]}; # mass moment of inertia in y direction for ch/6 inch section


# assigning masses to the nodes
for {set i 1} {$i < $spans} {incr i 1} {
	for {set j 0} {$j < $bn} {incr j 1} {
	puts $fileID "#\n#    Bent No. $i, Column No. [expr $j+1]"
	puts $fileID "#       node X-mass   Y-mass   Z-mass   MX-mass  MY-mass  MZ-mass"
	set n [expr $n+1]
	puts $fileID [format "%-8s %3d %-8s %-8s %-8s %-8s %-8s %-8s" mass $n \$colm2 \$colm2  \$colm2  \$cmix2  \$cmiy2  \$cmiz2]
	set n [expr $n+1]
	puts $fileID [format "%-8s %3d %-8s %-8s %-8s %-8s %-8s %-8s" mass $n \$colm \$colm  \$colm  \$cmix  \$cmiy  \$cmiz]
	set n [expr $n+1]
	puts $fileID [format "%-8s %3d %-8s %-8s %-8s %-8s %-8s %-8s" mass $n \$colm \$colm  \$colm  \$cmix  \$cmiy  \$cmiz]
	set n [expr $n+5]
	puts $fileID [format "%-8s %3d %-8s %-8s %-8s %-8s %-8s %-8s" mass $n \$colm2 \$colm2  \$colm2  \$cmix2  \$cmiy2  \$cmiz2]
	puts $fileID "#==================================================================="
	set q [expr $q+1]
	set n [expr 1050 + $q*50]
	}
}
puts $fileID "#======================================================================================"
puts $fileID "#              FOUNDATION MASSES"
puts $fileID "#======================================================================================"
# Mass per pile cap is 0.02317 k-s^2/in
puts $fileID "set  fndm   [expr 0.02317]  ; # (k-s^2/in)"

puts $fileID {set fmiz [expr $fndm*((96*96)+43*43)/12]}; # mass moment of inertia in z direction
puts $fileID {set fmix [expr $fndm*(96*96+43*43)/12]}; # mass moment of inertia in x direction for 75" wide section
puts $fileID {set fmiy [expr $fndm*(96*96+96*96)/12]}; # mass moment of inertia in y direction for 75" wide section

set n 8000

for {set i 1} {$i < $spans} {incr i 1} {
	puts $fileID "#\n#    Bent No. $i"
	puts $fileID "#       node X-mass   Y-mass   Z-mass   MX-mass  MY-mass  MZ-mass"
	for {set j 0} {$j < $bn} {incr j 1} {
		set n [expr $n+1]
		puts $fileID [format "%-8s %3d %-8s %-8s %-8s %-8s %-8s %-8s" mass $n \$fndm \$fndm  \$fndm  \$fmix  \$fmiy  \$fmiz]
	}
	puts $fileID "#==================================================================="
}
