# this code generates the elements in the bridge deck

puts $fileID "#======================================================================================"
puts $fileID "#              GIRDER PROPERTIES"
puts $fileID "#======================================================================================"
puts $fileID "#                  TAG   Xv  Yv  Zv"

# setting section properties for the girders
puts $fileID "set Ag       $Ag   ; # Cross-sectional Area in^2"
puts $fileID "set Izg      $Izg   ; # Moment of Inertia in^4"
puts $fileID "set Iyg      $Iyg   ; # Moment of Inertia in^4" 
set Eg     [expr 185000*pow($fcg*1000,3.0/8.0)/1000.0]; # Elastic modulus of concrete in girders         
puts $fileID "set Eg     $Eg         ; # Elastic Modulus  ksi"
set Gg [expr $Eg/(2*(1+0.15))]; # shear modulus
puts $fileID "set Gg $Gg"; # shear modulus
puts $fileID {set Jg    [expr $Iyg+$Izg]} ; # Polar Moment of Inertia in^4"

puts $fileID "#======================================================================================"
puts $fileID "#              LONGITUDINAL DECK ELEMENTS"
puts $fileID "#======================================================================================"
# elements in the bridge girders - each girder in each span is didived in to 6 elements  (i.e. n_div = 6)
puts $fileID "#                  TAG   Xv  Yv  Zv"
puts $fileID "geomTransf Corotational     1    0   1   0\n"


set n 100000
set m 0
for {set i 0} {$i < $spans} {incr i 1} {


	puts $fileID "#\n#       DECK NUMBER [expr $i+1]"
	puts $fileID "#                          Tag     iN    jN     A      E      G     J      Iz     Iy    Transf" 

       
    for {set k 0} {$k < $gd} {incr k 1} {
    
    set n [expr $n+1]
    set m [expr 12000+2*$i*$gd+$k+1]
    
    set p [expr 10000+ $i*($n_trans*($div($i)-1))+$k*(($n_trans-1)/($gd-1))+1]   ; # initial start # + # of nodes from previous deck + # of nodes to skip to reach the next girder
    set long_ele_list($n,1) $m
    set long_ele_list($n,2) $p 
    # element at the beginnign of the girder 
    puts $fileID "element elasticBeamColumn $n $m $p \$Ag \$Eg \$Gg \$Jg \$Izg \$Iyg 1" ;# the bridge deck elements are modeled as elastic elements           
    
    
		  for {set j 0} {$j < [expr $div($i)-2]} {incr j 1} {
			  set n [expr $n+1]
			  set m [expr $p]
			  set p [expr $m+$n_trans] ;# adding number of nodes that will give the node# of the next node in the longitudinal direction
              set long_ele_list($n,1) $m
              set long_ele_list($n,2) $p 
              # interior girder elements 
			  puts $fileID "element elasticBeamColumn $n $m $p \$Ag \$Eg \$Gg \$Jg \$Izg \$Iyg 1"
        
		  }
    
      set n [expr $n+1]
	  set m [expr $p]
      set p [expr 12000+(2*$i+1)*$gd+$k+1]
      set long_ele_list($n,1) $m
      set long_ele_list($n,2) $p
            # element at the end of the girder 
      puts $fileID "element elasticBeamColumn $n $m $p \$Ag \$Eg \$Gg \$Jg \$Izg \$Iyg 1"
      
      
    }
    
}

# transverse deck elements - to model the deck slab
puts $fileID "#======================================================================================"
puts $fileID "#              TRANSVERSE DECK ELEMENTS"
puts $fileID "#======================================================================================"
puts $fileID "#                  TAG   Xv  Yv  Zv"

puts $fileID "geomTransf Corotational    2    0   1   0\n#"

# the following properties are for rigid elements (if necessary)
puts $fileID "set Atd     1e8        ; # Cross-sectional Area in^2"
puts $fileID "set Itd     1e9         ; # Moment of Inertia in^4"
puts $fileID "set Etd     1e8         ; # Elastic Modulus  ksi"
puts $fileID "set Gtd     1e8         ; # Modulus of Rigidity ksi"
puts $fileID "set Jtd     1e9         ; # Polar MOI  in^4 \n#"
puts $fileID "uniaxialMaterial Elastic 1000 9e9"


puts $fileID "set E_t $Ec" ; # same as that of concrete in columns and bent
puts $fileID "set A_t     $A_t        ; # Cross-sectional Area in^2"
puts $fileID "set Iz_t    $Iz_t        ; # Moment of Inertia in^4"
puts $fileID "set Iy_t    $Iy_t         ; # Moment of Inertia in^4"


puts $fileID {set J_t    [expr $Iy_t+$Iz_t]}         ; # Moment of Inertia in^4"
puts $fileID {set G_t [expr $E_t/(2*(1+0.15))]}




set n1 12000
set m1 12000

set n 120000
set m 10000

for {set i 0} {$i < $spans} {incr i 1} {
	puts $fileID "#\n#       DECK NUMBER [expr $i+1]"
	puts $fileID "#                          Tag     iN    jN     A      E      G     J      Iz     Iy    Transf" 
  
    puts $fileID "#      Left End"
    for {set j 0} {$j < [expr $gd-1]} {incr j 1} {
		   
			set n1 [expr $n1+1]
			set m1 [expr $m1+1]
			set p1 [expr $m1+1]
      set trans_ele_list($n1,1) $m1
      set trans_ele_list($n1,2) $p1
			puts $fileID "element elasticBeamColumn $n1 $m1 $p1 \$A_t \$E_t \$G_t \$J_t \$Iz_t \$Iy_t 2"; # transverse elements at the left end of the deck
	 }
   
   
  
    puts $fileID "#      Grillage members"
    for {set j 0} {$j < [expr $div($i)-1]} {incr j 1} {
      for {set k 0} {$k < [expr $n_trans-1]} {incr k 1} {
      
			  set n [expr $n+1]
			  set m [expr $m+1]
			  set p [expr $m+1]
        set trans_ele_list($n,1) $m
        set trans_ele_list($n,2) $p
			  puts $fileID "element elasticBeamColumn $n $m $p \$A_t \$E_t \$G_t \$J_t \$Iz_t \$Iy_t 2" ; # internal transverse deck elements
        }
        set m [expr $m+1]
		  }
  
	
		set m1 [expr $m1+1]
		puts $fileID "#      Right End"
		for {set j 0} {$j < [expr $gd-1]} {incr j 1} {
		  set n1 [expr $n1+1]
			set m1 [expr $m1+1]
			set p1 [expr $m1+1]
      set trans_ele_list($n1,1) $m1
      set trans_ele_list($n1,2) $p1
			puts $fileID "element elasticBeamColumn $n1 $m1 $p1 \$A_t \$E_t \$G_t \$J_t \$Iz_t \$Iy_t 2"  ; # transverse elements at the right end of the deck
		}
    set m1 [expr $m1+1]
		
} 
