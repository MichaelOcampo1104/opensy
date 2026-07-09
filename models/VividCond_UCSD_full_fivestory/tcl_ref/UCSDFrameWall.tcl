# clear memory of all past model definitions
wipe

# source files
source GetGaussLobattoIP.tcl
source CreateConcreteMaterial.tcl
source BuildRCrectSection3D.tcl
source CreateRCWallSection.tcl

# Define the model builder, ndm=#dimension, ndf=#dofs
model BasicBuilder -ndm 3 -ndf 6

# fracture tag
set frac_tag 1
set phi_col 0.01
set phi_beam 0.25
set phi_wall 0.01

# bar slip tag
set barslip_tag 0

# ft unit in inch
set ft 12.0
# 
set PI [expr 2*asin(1.0)]
# story number
set num_stories 5
# story height (in)
set h_story [expr 12.0*$ft]
# floor center
set flr_ctr_x [expr 17.0*$ft]
set flr_ctr_y [expr 10.0*$ft]
# lateral frame bay numbers
set num_bays_x 2
set num_bays_y 1
# bay width (in)
set bay_x [expr 17.0*$ft]
set bay_y [expr 20.0*$ft]
# wall dimensions (in)
set wall_length [expr 9.0*$ft]
set wall_thickness 7.5
set wall_ctr_x {25.5 138.6}
set wall_ctr_y {180.0 180.0}
set num_walls 2
# slab dimensions (in)
set slab_thickness 8.0
set slab_width_eff 90.0
set slab_A [expr $slab_thickness*$slab_width_eff]
set slab_Iy [expr 1.0/12.0*$slab_thickness*$slab_width_eff**3]
set slab_Iz [expr 1.0/12.0*$slab_width_eff*$slab_thickness**3]
set slab_J 1.0e9
set slab_db_1 0.625
set slab_db_2 0.5
set slab_n1 [expr round($slab_width_eff/8.0)]
set slab_n2 [expr round($slab_width_eff/16.0)]
set slab_c 1.0
# beam dimensions by story
set b_beam {12.0 12.0 12.0 12.0 12.0}
set h_beam {28.0 28.0 28.0 28.0 28.0}
# exterior dimensions by story
set h_col {26.0 26.0 26.0 26.0 26.0}
set b_col {18.0 18.0 18.0 18.0 18.0}
# reinforcement (beam)
set rt_beam {0.008 0.008 0.008 0.008 0.016}
set s_beam {4.0 4.0 4.0 4.0 4.0}
set db_beam {0.875 0.875 0.875 0.875 0.875}
set nl_beam {4 4 4 4 8}
set fyl_beam {130.0 130.0 125.0 125.0 73.5}
set ful_beam {160.0 160.0 160.0 160.0 97.0}
set esu_beam {0.05 0.05 0.05 0.05 0.15}
set fyt_beam {69.0 69.0 69.0 69.0 69.0}
# reinforcement (column)
set rt_col {0.008 0.008 0.008 0.008 0.008}
set s_col {4.0 4.0 4.0 4.0 4.0}
set db_col_1 {1.128 1.128 1.128 1.128 1.128}
set nl_col_1 {4 4 4 4 4}
set fyl_col_1 {79.5 79.5 79.5 79.5 79.5}
set ful_col_1 {119.3 119.3 119.3 119.3 119.3}
set esu_col_1 {0.12 0.12 0.12 0.12 0.12}
set db_col_2 {0.75 0.75 0.75 0.75 0.75}
set nl_col_2 {6 6 6 6 6}
set fyl_col_2 {84.5 84.5 84.5 84.5 84.5}
set ful_col_2 {118.8 118.8 118.8 118.8 118.8}
set esu_col_2 {0.12 0.12 0.12 0.12 0.12}
set fyt_col {80.0 80.0 80.0 80.0 80.0}
# reinforcement (wall)
set rt_wall {0.0025 0.0025 0.0025 0.0025 0.0025 0.0025}
set s_wall {6.0 6.0 6.0 6.0 6.0}
set db_wall_1 {1.128 1.128 1.128 1.128 1.128}
set nl_wall_1 {4 4 4 4 4}
set fyl_wall_1 {79.5 79.5 79.5 79.5 79.5}
set ful_wall_1 {119.3 119.3 119.3 119.3 119.3}
set esu_wall_1 {0.12 0.12 0.12 0.12 0.12}
set db_wall_2 {0.375 0.375 0.375 0.375 0.375}
set nl_wall_2 {15 15 15 15 15}
set fyl_wall_2 {80.0 80.0 80.0 80.0 80.0}
set ful_wall_2 {106.0 106.0 106.0 106.0 106.0}
set esu_wall_2 {0.12 0.12 0.12 0.12 0.12}
set fyt_wall {80.0 80.0 80.0 80.0 80.0}
# mass and weight
set g 386.4
set w_story {166.1 168.2 228.4 226.3 134.8}
set story_mass {}
foreach w $w_story {
  set story_mass [lappend story_mass $w/$g]
}
#set pr_1 [expr 1.0/4.0]
#set pr_2 [expr 1.0/6.0]
#set pr_3 [expr 1.0/8.0]
#set pr_4 [expr 1.0/12.0]
#set pr_5 [expr 1.0/14.0]
set pr_1 [expr 0.18]
set pr_2 [expr 0.12]
set pr_3 [expr 0.12]
set pr_4 [expr 0.12]
set pr_5 [expr 0.12]
set p1 {}
set p2 {}
set p3 {}
set p4 {}
set p5 {}
foreach w $w_story {
  set p1 [lappend p1 $w*$pr_1]
  set p2 [lappend p2 $w*$pr_2]
  set p3 [lappend p3 $w*$pr_3]
  set p4 [lappend p4 $w*$pr_4]
  set p5 [lappend p5 $w*$pr_5]
}

# small mass
set mass_small 1e-6
set mass_small_2 1e-3

# number of integration points / story
set	numIntgrPts 6
set	LIP_col_wall	""
set	LIPR_col_wall	""
set	XIP_col_wall	""
set	LIP_beam	""
set	LIPR_beam	""
set	XIP_beam	""
set	IntegrationTag	"GaussLobattol"
if {$IntegrationTag == "NewtonCotes"} {
	for {set IPTag 1} {$IPTag <= $numIntgrPts} {incr IPTag} {
		set LIP_col_wall [lappend LIP_col_wall [expr $h_story/$numIntgrPts]]
	}
} else {
	set tempIP [GetGaussLobattolLIP $numIntgrPts]
	set tempXIP [lindex $tempIP 0] 
	set tempLIP [lindex $tempIP 1]
	for {set IPTag 1} {$IPTag <= $numIntgrPts} {incr IPTag} {
		set LIPR_col_wall [lappend LIPR_col_wall [expr 0.5*[lindex $tempLIP $IPTag-1]]]
		set LIP_col_wall [lappend LIP_col_wall [expr 0.5*[lindex $tempLIP $IPTag-1]*$h_story]]
		set XIP_col_wall [lappend XIP_col_wall [expr 0.5*[lindex $tempXIP $IPTag-1]+0.5]]
	}
}
if {$IntegrationTag == "NewtonCotes"} {
	for {set IPTag 1} {$IPTag <= $numIntgrPts} {incr IPTag} {
		set LIP_beam [lappend LIP_beam [expr $bay_x/$numIntgrPts]]
	}
} else {
	set tempIP [GetGaussLobattolLIP $numIntgrPts]
	set tempXIP [lindex $tempIP 0] 
	set tempLIP [lindex $tempIP 1]
	for {set IPTag 1} {$IPTag <= $numIntgrPts} {incr IPTag} {
		set LIPR_beam [lappend LIPR_beam [expr 0.5*[lindex $tempLIP $IPTag-1]]]
		set LIP_beam [lappend LIP_beam [expr 0.5*[lindex $tempLIP $IPTag-1]*$bay_x]]
		set XIP_beam [lappend XIP_beam [expr 0.5*[lindex $tempXIP $IPTag-1]+0.5]]
	}
}

# shear tag
set shear_tag "NonLinear"

# loop over stories
set joint_ele_id 0
set ctrl_nodes {}
set all_nodes {}
for {set floor_id 0} {$floor_id < $num_stories+1} {incr floor_id} {
  puts "Creating nodes for floor #$floor_id..."
  # current story height level
  set cur_z [expr $floor_id*$h_story]
  # south lateral frame
  set cur_y 0.0
  for {set col_id 0} {$col_id < $num_bays_x+1} {incr col_id} {
    set cur_x [expr 18.0*$ft+$col_id*$bay_x]
    set node_id [expr $floor_id*1000+100+$col_id*10]
    node $node_id $cur_x $cur_y $cur_z -mass $mass_small $mass_small $mass_small $mass_small_2 $mass_small_2 $mass_small_2
    lappend all_nodes $node_id
    if {$floor_id == 0} {
      fix $node_id 1 1 1 1 1 1
    }
  }
  # north later frame
  set cur_y [expr 120.0*$ft]
  for {set col_id 0} {$col_id < $num_bays_x+1} {incr col_id} {
    set cur_x [expr 18.0*$ft+$col_id*$bay_x]
    set node_id [expr $floor_id*1000+200+$col_id*10]
    node $node_id $cur_x $cur_y $cur_z -mass $mass_small $mass_small $mass_small $mass_small_2 $mass_small_2 $mass_small_2
    lappend all_nodes $node_id
    if {$floor_id == 0} {
      fix $node_id 1 1 1 1 1 1
    }
  }
  # wall
  for {set wall_id 0} {$wall_id < $num_walls} {incr wall_id} {
    set node_id [expr $floor_id*1000+500+$wall_id*10]
    node $node_id [lindex $wall_ctr_x $wall_id] [lindex $wall_ctr_y $wall_id] $cur_z -mass $mass_small $mass_small $mass_small $mass_small_2 $mass_small_2 $mass_small_2
    lappend all_nodes $node_id
    if {$floor_id == 0} {
      fix $node_id 1 1 1 1 1 1
    }
  }
  # rigid diaphram node
  set node_id [expr $floor_id*1000+300]
  lappend ctrl_nodes $node_id
  lappend all_nodes $node_id
  if {$floor_id > 0} {
    node $node_id $flr_ctr_x $flr_ctr_y $cur_z \
         -mass [expr [lindex $story_mass $floor_id-1]] [expr [lindex $story_mass $floor_id-1]] [expr [lindex $story_mass $floor_id-1]] $mass_small_2 $mass_small_2 $mass_small_2
    fix $node_id 0 0 1 1 1 0
  } else {
    node $node_id $flr_ctr_x $flr_ctr_y $cur_z
    fix $node_id 1 1 1 1 1 1
  }
}
puts "All nodes created."

# steel Young's module
set Es 29000.0
# concrete material
set fc0_col_wall -8.3
set fc0_beam -7.5
for {set story_id 0} {$story_id < $num_stories} {incr story_id} {
  set cur_nl_beam [lindex $nl_beam $story_id]
  set cur_db_beam [lindex $db_beam $story_id]
  set cur_b_beam [lindex $b_beam $story_id]
  set cur_h_beam [lindex $h_beam $story_id]
  set cur_rt_beam [lindex $rt_beam $story_id]
  set cur_fyt_beam [lindex $fyt_beam $story_id]
  set cur_s_beam [lindex $s_beam $story_id]
  set cur_nl_col [expr [lindex $nl_col_1 $story_id]+[lindex $nl_col_2 $story_id]]
  set cur_db_col_1 [lindex $db_col_1 $story_id]
  set cur_db_col_2 [lindex $db_col_2 $story_id]
  set cur_db_wall_1 [lindex $db_col_1 $story_id]
  set cur_db_wall_2 [lindex $db_col_2 $story_id]
  set cur_b_col [lindex $b_col $story_id]
  set cur_h_col [lindex $h_col $story_id]
  set cur_rt_col [lindex $rt_col $story_id]
  set cur_fyt_col [lindex $fyt_col $story_id]
  set cur_s_col [lindex $s_col $story_id]
  set cur_s_wall [lindex $s_wall $story_id]
  for {set ip_id 0} {$ip_id < $numIntgrPts} {incr ip_id} {
    set curLIP1 [lindex $LIP_col_wall $ip_id]
    set curLIP2 [lindex $LIP_beam $ip_id]
    # cover concrete
    DefineRegularizedUnconfinedConcreteMaterial "Concrete02" [expr $story_id*1000+$ip_id*10+1] $fc0_col_wall $curLIP1
    DefineRegularizedUnconfinedConcreteMaterial "Concrete02" [expr $story_id*1000+$ip_id*10+2] $fc0_beam $curLIP2
    # core concrete
    DefineRegularizedConfinedConcreteMaterial "Concrete02" [expr $story_id*1000+$ip_id*10+4] $fc0_col_wall $cur_nl_col $cur_s_col $cur_b_col \
                                                          [expr 0.9*$cur_h_col] $cur_db_col_1 $cur_rt_col $cur_fyt_col $curLIP1
    DefineRegularizedConfinedConcreteMaterial "Concrete02" [expr $story_id*1000+$ip_id*10+5] $fc0_beam $cur_nl_beam $cur_s_beam $cur_b_beam \
                                                          [expr 0.9*$cur_h_beam] $cur_db_beam $cur_rt_beam $cur_fyt_beam $curLIP2
  }
  # steel
  set cur_fyl_beam [lindex $fyl_beam $story_id]
  set cur_ful_beam [lindex $ful_beam $story_id]
  set cur_esu_beam [lindex $esu_beam $story_id]
  set cur_fyl_col_1 [lindex $fyl_col_1 $story_id]
  set cur_ful_col_1 [lindex $ful_col_1 $story_id]
  set cur_esu_col_1 [lindex $esu_col_1 $story_id]
  set cur_fyl_col_2 [lindex $fyl_col_2 $story_id]
  set cur_ful_col_2 [lindex $ful_col_2 $story_id]
  set cur_esu_col_2 [lindex $esu_col_2 $story_id]
  set cur_fyl_wall_1 [lindex $fyl_wall_1 $story_id]
  set cur_ful_wall_1 [lindex $ful_wall_1 $story_id]
  set cur_esu_wall_1 [lindex $esu_wall_1 $story_id]
  set cur_fyl_wall_2 [lindex $fyl_wall_2 $story_id]
  set cur_ful_wall_2 [lindex $ful_wall_2 $story_id]
  set cur_esu_wall_2 [lindex $esu_wall_2 $story_id]
  uniaxialMaterial Steel02 [expr $story_id*1000+101] $cur_fyl_beam $Es [expr ($cur_ful_beam-$cur_fyl_beam)/($cur_esu_beam-$cur_fyl_beam/$Es)/$Es] 18 0.925 0.15
  uniaxialMaterial Steel02 [expr $story_id*1000+102] $cur_fyl_col_1 $Es [expr ($cur_ful_col_1-$cur_fyl_col_1)/($cur_esu_col_1-$cur_fyl_col_1/$Es)/$Es] 18 0.925 0.15
  uniaxialMaterial Steel02 [expr $story_id*1000+103] $cur_fyl_col_2 $Es [expr ($cur_ful_col_2-$cur_fyl_col_2)/($cur_esu_col_2-$cur_fyl_col_2/$Es)/$Es] 18 0.925 0.15
  uniaxialMaterial Steel02 [expr $story_id*1000+104] $cur_fyl_wall_1 $Es [expr ($cur_ful_wall_1-$cur_fyl_wall_1)/($cur_esu_wall_1-$cur_fyl_wall_1/$Es)/$Es] 18 0.925 0.15
  uniaxialMaterial Steel02 [expr $story_id*1000+105] $cur_fyl_wall_2 $Es [expr ($cur_ful_wall_2-$cur_fyl_wall_2)/($cur_esu_wall_2-$cur_fyl_wall_2/$Es)/$Es] 18 0.925 0.15
  # steel fracture
  uniaxialMaterial DuctileFracture [expr $story_id*1000+201] [expr $story_id*1000+101] -c_mono [expr exp(-3.96-1.85*log($cur_esu_beam)+0.2*log($cur_db_beam/8.0))] \
                                                           -c_cycl [expr exp(5.90+1.53*log($cur_fyl_beam/60.0)+2.32*log($cur_esu_beam)+1.11*log($cur_db_beam/8.0))] \
                                                           -c_symm 1.05 -E_s $Es -esu $cur_esu_beam \
                                                           -k1 [expr exp(2.21-0.32*log($cur_ful_beam/$cur_fyl_beam)-0.66*log($cur_db_beam/8.0))] \
                                                           -k2 [expr exp(1.29+0.64*log($cur_fyl_beam/60.0)-0.46*log($cur_db_beam/8.0))] \
                                                           -db $cur_db_beam \
                                                           -b1 [expr exp(-2.53-1.90*log($cur_ful_beam/$cur_fyl_beam)-1.36*log($cur_db_beam/8.0))] \
                                                           -b2 [expr exp(-3.29-0.49*log($cur_esu_beam)-0.7*log($phi_beam*$cur_s_beam/$cur_db_beam))]
  uniaxialMaterial DuctileFracture [expr $story_id*1000+202] [expr $story_id*1000+102] -c_mono [expr exp(-3.96-1.85*log($cur_esu_col_1)+0.2*log($cur_db_col_1/8.0))] \
                                                           -c_cycl [expr exp(5.90+1.53*log($cur_fyl_col_1/60.0)+2.32*log($cur_esu_col_1)+1.11*log($cur_db_col_1/8.0))] \
                                                           -c_symm 1.05 -E_s $Es -esu $cur_esu_col_1 \
                                                           -k1 [expr exp(2.21-0.32*log($cur_ful_col_1/$cur_fyl_col_1)-0.66*log($cur_db_col_1/8.0))] \
                                                           -k2 [expr exp(1.29+0.64*log($cur_fyl_col_1/60.0)-0.46*log($cur_db_col_1/8.0))] \
                                                           -db $cur_db_col_1 \
                                                           -b1 [expr exp(-2.53-1.90*log($cur_ful_col_1/$cur_fyl_col_1)-1.36*log($cur_db_col_1/8.0))] \
                                                           -b2 [expr exp(-3.29-0.49*log($cur_esu_col_1)-0.7*log($phi_col*$cur_s_col/$cur_db_col_1))]
  uniaxialMaterial DuctileFracture [expr $story_id*1000+203] [expr $story_id*1000+103] -c_mono [expr exp(-3.96-1.85*log($cur_esu_col_2)+0.2*log($cur_db_col_2/8.0))] \
                                                           -c_cycl [expr exp(5.90+1.53*log($cur_fyl_col_2/60.0)+2.32*log($cur_esu_col_2)+1.11*log($cur_db_col_2/8.0))] \
                                                           -c_symm 1.05 -E_s $Es -esu $cur_esu_col_2 \
                                                           -k1 [expr exp(2.21-0.32*log($cur_ful_col_2/$cur_fyl_col_2)-0.66*log($cur_db_col_2/8.0))] \
                                                           -k2 [expr exp(1.29+0.64*log($cur_fyl_col_2/60.0)-0.46*log($cur_db_col_2/8.0))] \
                                                           -db $cur_db_col_2 \
                                                           -b1 [expr exp(-2.53-1.90*log($cur_ful_col_2/$cur_fyl_col_2)-1.36*log($cur_db_col_2/8.0))] \
                                                           -b2 [expr exp(-3.29-0.49*log($cur_esu_col_2)-0.7*log($phi_col*$cur_s_col/$cur_db_col_2))]
  uniaxialMaterial DuctileFracture [expr $story_id*1000+204] [expr $story_id*1000+104] -c_mono [expr exp(-3.96-1.85*log($cur_esu_wall_1)+0.2*log($cur_db_wall_1/8.0))] \
                                                           -c_cycl [expr exp(5.90+1.53*log($cur_fyl_wall_1/60.0)+2.32*log($cur_esu_wall_1)+1.11*log($cur_db_wall_1/8.0))] \
                                                           -c_symm 1.05 -E_s $Es -esu $cur_esu_wall_1 \
                                                           -k1 [expr exp(2.21-0.32*log($cur_ful_wall_1/$cur_fyl_wall_1)-0.66*log($cur_db_wall_1/8.0))] \
                                                           -k2 [expr exp(1.29+0.64*log($cur_fyl_wall_1/60.0)-0.46*log($cur_db_wall_1/8.0))] \
                                                           -db $cur_db_wall_1 \
                                                           -b1 [expr exp(-2.53-1.90*log($cur_ful_wall_1/$cur_fyl_wall_1)-1.36*log($cur_db_wall_1/8.0))] \
                                                           -b2 [expr exp(-3.29-0.49*log($cur_esu_wall_1)-0.7*log($phi_wall*$cur_s_wall/$cur_db_wall_1))]
  uniaxialMaterial DuctileFracture [expr $story_id*1000+205] [expr $story_id*1000+105] -c_mono [expr exp(-3.96-1.85*log($cur_esu_wall_2)+0.2*log($cur_db_wall_2/8.0))] \
                                                           -c_cycl [expr exp(5.90+1.53*log($cur_fyl_wall_2/60.0)+2.32*log($cur_esu_wall_2)+1.11*log($cur_db_wall_2/8.0))] \
                                                           -c_symm 1.05 -E_s $Es -esu $cur_esu_wall_2 \
                                                           -k1 [expr exp(2.21-0.32*log($cur_ful_wall_2/$cur_fyl_wall_2)-0.66*log($cur_db_wall_2/8.0))] \
                                                           -k2 [expr exp(1.29+0.64*log($cur_fyl_wall_2/60.0)-0.46*log($cur_db_wall_2/8.0))] \
                                                           -db $cur_db_wall_2 \
                                                           -b1 [expr exp(-2.53-1.90*log($cur_ful_wall_2/$cur_fyl_wall_2)-1.36*log($cur_db_wall_2/8.0))] \
                                                           -b2 [expr exp(-3.29-0.49*log($cur_esu_wall_2)-0.7*log($phi_beam*$cur_s_wall/$cur_db_wall_2))]
  # bar slip
  set curLIP1 [lindex $LIP_col_wall 0]
  set curLIP2 [lindex $LIP_beam 0]
  set cur_sy [expr (0.013+0.1*pow($cur_db_beam/4000.0*$cur_fyl_beam/sqrt(abs($fc0_beam*1000))*(2.0*0.4+1),2.5))/$curLIP2]
  set cur_su [expr 40.0*$cur_sy]
  uniaxialMaterial Bond_SP01 [expr $story_id*1000+301] $cur_fyl_beam $cur_sy $cur_ful_beam $cur_su 0.3 0.5
  set cur_sy [expr (0.013+0.1*pow($cur_db_col_1/4000.0*$cur_fyl_col_1/sqrt(abs($fc0_col_wall*1000))*(2.0*0.4+1),2.5))/$curLIP1]
  set cur_su [expr 40.0*$cur_sy]
  uniaxialMaterial Bond_SP01 [expr $story_id*1000+302] $cur_fyl_col_1 $cur_sy $cur_ful_col_1 $cur_su 0.3 1.0
  set cur_sy [expr (0.013+0.1*pow($cur_db_col_2/4000.0*$cur_fyl_col_2/sqrt(abs($fc0_col_wall*1000))*(2.0*0.4+1),2.5))/$curLIP1]
  set cur_su [expr 40.0*$cur_sy]
  uniaxialMaterial Bond_SP01 [expr $story_id*1000+303] $cur_fyl_col_2 $cur_sy $cur_ful_col_2 $cur_su 0.3 1.0
  set cur_sy [expr (0.013+0.1*pow($cur_db_wall_1/4000.0*$cur_fyl_wall_1/sqrt(abs($fc0_col_wall*1000))*(2.0*0.4+1),2.5))/$curLIP1]
  set cur_su [expr 40.0*$cur_sy]
  uniaxialMaterial Bond_SP01 [expr $story_id*1000+304] $cur_fyl_wall_1 $cur_sy $cur_ful_wall_1 $cur_su 0.3 1.0
  set cur_sy [expr (0.013+0.1*pow($cur_db_wall_2/4000.0*$cur_fyl_wall_2/sqrt(abs($fc0_col_wall*1000))*(2.0*0.4+1),2.5))/$curLIP1]
  set cur_su [expr 40.0*$cur_sy]
  uniaxialMaterial Bond_SP01 [expr $story_id*1000+305] $cur_fyl_wall_2 $cur_sy $cur_ful_wall_2 $cur_su 0.3 1.0
}
puts "Concrete and steel material models created."

# sections
set c_concrete 1.375
set nfCoreY 10
set nfCoreZ 10
set nfCoverY 2
set nfCoverZ 2
for {set story_id 0} {$story_id < $num_stories} {incr story_id} {
  for {set ip_id 0} {$ip_id < $numIntgrPts} {incr ip_id} {
    if {$ip_id == 0 || $ip_id == $numIntgrPts-1} {
      if {$barslip_tag == 1} {
        set steel_tag_b [expr $story_id*1000+301]
        set steel_tag_c1 [expr $story_id*1000+302]
        set steel_tag_c2 [expr $story_id*1000+303]
        set steel_tag_w1 [expr $story_id*1000+304]
        set steel_tag_w2 [expr $story_id*1000+305]
      } else {
        set steel_tag_b [expr $story_id*1000+101+$frac_tag*100]
        set steel_tag_c1 [expr $story_id*1000+102+$frac_tag*100]
        set steel_tag_c2 [expr $story_id*1000+103+$frac_tag*100]
        set steel_tag_w1 [expr $story_id*1000+104+$frac_tag*100]
        set steel_tag_w2 [expr $story_id*1000+105+$frac_tag*100]
      }
    } else {
      set steel_tag_b [expr $story_id*1000+101+$frac_tag*100]
      set steel_tag_c1 [expr $story_id*1000+102+$frac_tag*100]
      set steel_tag_c2 [expr $story_id*1000+103+$frac_tag*100]
      set steel_tag_w1 [expr $story_id*1000+104+$frac_tag*100]
      set steel_tag_w2 [expr $story_id*1000+105+$frac_tag*100]
    }
    # beam section
    set sec_id [expr $story_id*1000+100+$ip_id]
    BuildRCrectSection $sec_id [lindex $h_beam $story_id] [lindex $b_beam $story_id] $c_concrete $c_concrete \
                      [expr $story_id*1000+$ip_id*10+5] [expr $story_id*1000+$ip_id*10+2] $steel_tag_b \
                      [expr [lindex $nl_beam $story_id]/2] [expr 0.25*3.14*[lindex $db_beam $story_id]**2] \
                      [expr [lindex $nl_beam $story_id]/2] [expr 0.25*3.14*[lindex $db_beam $story_id]**2] \
                      0 0 [expr 57.0*sqrt(abs($fc0_beam)*1000)/2.0/(1+0.3)*[lindex $h_beam $story_id]*[lindex $b_beam $story_id]*([lindex $h_beam $story_id]**2+[lindex $b_beam $story_id]**2)/12.0] \
                      [expr 57.0*sqrt(abs($fc0_beam)*1000)/2.0/(1+0.3)*[lindex $h_beam $story_id]*[lindex $b_beam $story_id]] \
                      $nfCoreY $nfCoreZ $nfCoverY $nfCoverZ
    # column section
    set sec_id [expr $story_id*1000+200+$ip_id]
    BuildRCrectSection $sec_id [lindex $h_col $story_id] [lindex $b_col $story_id] $c_concrete $c_concrete \
                      [expr $story_id*1000+$ip_id*10+4] [expr $story_id*1000+$ip_id*10+1] $steel_tag_c1 \
                      3 [expr (0.25*3.14*[lindex $db_col_1 $story_id]**2*2+0.25*3.14*[lindex $db_col_2 $story_id]**2)/3.0] \
                      3 [expr (0.25*3.14*[lindex $db_col_1 $story_id]**2*2+0.25*3.14*[lindex $db_col_2 $story_id]**2)/3.0] \
                      2 [expr 0.25*3.14*[lindex $db_col_2 $story_id]**2] \
                      [expr 57.0*sqrt(abs($fc0_col_wall)*1000)/2.0/(1+0.3)*[lindex $h_col $story_id]*[lindex $b_col $story_id]*([lindex $h_col $story_id]**2+[lindex $b_col $story_id]**2)/12.0] \
                      [expr 57.0*sqrt(abs($fc0_col_wall)*1000)/2.0/(1+0.3)*[lindex $h_col $story_id]*[lindex $b_col $story_id]] \
                      $nfCoreY $nfCoreZ $nfCoverY $nfCoverZ
    # wall section 
    set sec_id [expr $story_id*1000+300+$ip_id]
    CreatePlanarWallSection $sec_id [expr $wall_length] [expr $wall_thickness] $c_concrete 18.0 18.0 \
                      [expr $story_id*1000+$ip_id*10+1] [expr $story_id*1000+$ip_id*10+1] [expr $story_id*1000+$ip_id*10+1] [expr $story_id*1000+$ip_id*10+1] \
                      $steel_tag_w1 $steel_tag_w1 $steel_tag_w2 \
                      [lindex $db_wall_1 $story_id] [expr 0.25*3.14*[lindex $db_wall_1 $story_id]**2] 1 1 0 0 \
                      [lindex $db_wall_1 $story_id] [expr 0.25*3.14*[lindex $db_wall_1 $story_id]**2] 1 1 0 0 \
                      [lindex $db_wall_2 $story_id] [expr 0.25*3.14*[lindex $db_wall_2 $story_id]**2] [lindex $nl_wall_2 $story_id] \
                      $nfCoreY $nfCoreZ $nfCoverY $nfCoverZ [expr 5*$nfCoreY] \
                      $fc0_col_wall 2.0 [lindex $rt_wall $story_id] [lindex $fyt_wall $story_id] $shear_tag
    # slab section
    set sec_id [expr $story_id*1000+400+$ip_id]
    BuildRCrectSection $sec_id $slab_thickness $slab_width_eff $slab_c $slab_c \
                      [expr $story_id*1000+$ip_id*10+2] [expr $story_id*1000+$ip_id*10+2] [expr $story_id*1000+102] \
                      $slab_n2 [expr 0.25*3.14*$slab_db_2**2] \
                      $slab_n1 [expr 0.25*3.14*$slab_db_1**2] \
                      0 0 [expr 57.0*sqrt(abs($fc0_beam)*1000)/2.0/(1+0.3)*$slab_thickness*$slab_width_eff*($slab_thickness**2+$slab_width_eff**2)/12.0] \
                      [expr 57.0*sqrt(abs($fc0_beam)*1000)/2.0/(1+0.3)*$slab_thickness*$slab_width_eff] \
                      $nfCoreY $nfCoreZ $nfCoverY $nfCoverZ
  }
}

# lateral system elements
set col_tags_recorded {}
set beam_tags_recorded {}
set wall_tags_recorded {}
for {set story_id 0} {$story_id < $num_stories} {incr story_id} {
  puts "Creating lateral system elements for story #[expr $story_id+1]..."
  # south lateral frame
  # columns
  for {set col_id 0} {$col_id < $num_bays_x+1} {incr col_id} {
    set node1_id [expr $story_id*1000+100+$col_id*10]
    set node2_id [expr ($story_id+1)*1000+100+$col_id*10]
    set secTags ""
    for {set ip_id 0} {$ip_id < $numIntgrPts} {incr ip_id} {
      set	secTags	[lappend secTags [expr $story_id*1000+200+$ip_id]]
    }
    set	integration	"UserDefined $numIntgrPts $secTags $XIP_col_wall $LIPR_col_wall";
    set dXi 0.0
    set dYi 0.0
    if {$story_id == 0} {
      set dZi 0.0
    } else {
      set dZi [expr 0.5*[lindex $h_beam $story_id-1]]
    }
    set dXj 0.0
    set dYj 0.0
    set dZj [expr -0.5*[lindex $h_beam $story_id]]
    geomTransf PDelta [expr 100000+$story_id*100+$col_id] 0 -1 0 -jntOffset $dXi $dYi $dZi $dXj $dYj $dZj
    element forceBeamColumn [expr $story_id*1000+100+$col_id*10] $node1_id $node2_id [expr 100000+$story_id*100+$col_id] $integration
    set col_tags_recorded [lappend col_tags_recorded [expr $story_id*1000+100+$col_id*10]]
  }
  # beams
  for {set beam_id 0} {$beam_id < $num_bays_x} {incr beam_id} {
    set node1_id [expr ($story_id+1)*1000+100+$beam_id*10]
    set node2_id [expr ($story_id+1)*1000+100+($beam_id+1)*10]
    if {$beam_id > 0} {
      set secTags ""
      for {set ip_id 0} {$ip_id < $numIntgrPts} {incr ip_id} {
        set	secTags	[lappend secTags [expr $story_id*1000+100+$ip_id]]
      }
      set	integration	"UserDefined $numIntgrPts $secTags $XIP_beam $LIPR_beam";
      if {$beam_id == 0} {
        set dXi [expr 0.5*[lindex $h_col $story_id]]
      } else {
        set dXi [expr 0.5*[lindex $h_col $story_id]]
      }
      set dYi 0.0
      set dZi 0.0
      if {$beam_id == $num_bays_x-1} {
        set dXj [expr -0.5*[lindex $h_col $story_id]]
      } else {
        set dXj [expr -0.5*[lindex $h_col $story_id]]
      }
      set dYj 0.0
      set dZj 0.0
      geomTransf PDelta [expr 100000+$story_id*100+$beam_id*10+9] 0 -1 0 -jntOffset $dXi $dYi $dZi $dXj $dYj $dZj
      element forceBeamColumn [expr $story_id*1000+200+$beam_id*10] $node1_id $node2_id [expr 100000+$story_id*100+$beam_id*10+9] $integration
      set beam_tags_recorded [lappend beam_tags_recorded [expr $story_id*1000+200+$beam_id*10]]
    } else {
      set secTags ""
      for {set ip_id 0} {$ip_id < $numIntgrPts} {incr ip_id} {
        set	secTags	[lappend secTags [expr $story_id*1000+400+$ip_id]]
      }
      set	integration	"UserDefined $numIntgrPts $secTags $XIP_beam $LIPR_beam";
      if {$beam_id == 0} {
        set dXi [expr 0.5*[lindex $h_col $story_id]]
      } else {
        set dXi [expr 0.5*[lindex $h_col $story_id]]
      }
      set dYi 0.0
      set dZi 0.0
      if {$beam_id == $num_bays_x-1} {
        set dXj [expr -0.5*[lindex $h_col $story_id]]
      } else {
        set dXj [expr -0.5*[lindex $h_col $story_id]]
      }
      set dYj 0.0
      set dZj 0.0
      geomTransf PDelta [expr 100000+$story_id*100+$beam_id*10+9] 0 -1 0 -jntOffset $dXi $dYi $dZi $dXj $dYj $dZj
      element forceBeamColumn [expr $story_id*1000+200+$beam_id*10] $node1_id $node2_id [expr 100000+$story_id*100+$beam_id*10+9] $integration
      #element elasticBeamColumn [expr $story_id*1000+200+$beam_id*10] $node1_id $node2_id $slab_A [expr 57.0*sqrt(abs($fc0_beam*1000.0))] [expr 57.0*sqrt(abs($fc0_beam*1000.0))/2.6] $slab_J $slab_Iy $slab_Iz [expr 100000+$story_id*100+$beam_id*10+9]
    }
  }
  # north lateral frame
  # columns
  for {set col_id 0} {$col_id < $num_bays_x+1} {incr col_id} {
    set node1_id [expr $story_id*1000+200+$col_id*10]
    set node2_id [expr ($story_id+1)*1000+200+$col_id*10]
    set secTags ""
    for {set ip_id 0} {$ip_id < $numIntgrPts} {incr ip_id} {
      set	secTags	[lappend secTags [expr $story_id*1000+200+$ip_id]]
    }
    set	integration	"UserDefined $numIntgrPts $secTags $XIP_col_wall $LIPR_col_wall";
    set dXi 0.0
    set dYi 0.0
    if {$story_id == 0} {
      set dZi 0.0
    } else {
      set dZi [expr 0.5*[lindex $h_beam $story_id-1]]
    }
    set dXj 0.0
    set dYj 0.0
    set dZj [expr -0.5*[lindex $h_beam $story_id]]
    geomTransf PDelta [expr 200000+$story_id*100+$col_id] 0 -1 0 -jntOffset $dXi $dYi $dZi $dXj $dYj $dZj
    element forceBeamColumn [expr $story_id*1000+300+$col_id*10] $node1_id $node2_id [expr 200000+$story_id*100+$col_id] $integration
    set col_tags_recorded [lappend col_tags_recorded [expr $story_id*1000+300+$col_id*10]]
  }
  # beams
  for {set beam_id 0} {$beam_id < $num_bays_x} {incr beam_id} {
    if {$beam_id > 0} {
      set node1_id [expr ($story_id+1)*1000+200+$beam_id*10]
      set node2_id [expr ($story_id+1)*1000+200+($beam_id+1)*10]
      set secTags ""
      for {set ip_id 0} {$ip_id < $numIntgrPts} {incr ip_id} {
        set	secTags	[lappend secTags [expr $story_id*1000+100+$ip_id]]
      }
      set	integration	"UserDefined $numIntgrPts $secTags $XIP_beam $LIPR_beam";
      if {$beam_id == 0} {
        set dXi [expr 0.5*[lindex $h_col $story_id]]
      } else {
        set dXi [expr 0.5*[lindex $h_col $story_id]]
      }
      set dYi 0.0
      set dZi 0.0
      if {$beam_id == $num_bays_x-1} {
        set dXj [expr -0.5*[lindex $h_col $story_id]]
      } else {
        set dXj [expr -0.5*[lindex $h_col $story_id]]
      }
      set dYj 0.0
      set dZj 0.0
      geomTransf PDelta [expr 200000+$story_id*100+$beam_id*10+9] 0 -1 0 -jntOffset $dXi $dYi $dZi $dXj $dYj $dZj
      element forceBeamColumn [expr $story_id*1000+400+$beam_id*10] $node1_id $node2_id [expr 200000+$story_id*100+$beam_id*10+9] $integration
      set beam_tags_recorded [lappend beam_tags_recorded [expr $story_id*1000+400+$beam_id*10]]
    } else {
      set node1_id [expr ($story_id+1)*1000+200+$beam_id*10]
      set node2_id [expr ($story_id+1)*1000+200+($beam_id+1)*10]
      set secTags ""
      for {set ip_id 0} {$ip_id < $numIntgrPts} {incr ip_id} {
        set	secTags	[lappend secTags [expr $story_id*1000+400+$ip_id]]
      }
      set	integration	"UserDefined $numIntgrPts $secTags $XIP_beam $LIPR_beam";
      if {$beam_id == 0} {
        set dXi [expr 0.5*[lindex $h_col $story_id]]
      } else {
        set dXi [expr 0.5*[lindex $h_col $story_id]]
      }
      set dYi 0.0
      set dZi 0.0
      if {$beam_id == $num_bays_x-1} {
        set dXj [expr -0.5*[lindex $h_col $story_id]]
      } else {
        set dXj [expr -0.5*[lindex $h_col $story_id]]
      }
      set dYj 0.0
      set dZj 0.0
      geomTransf PDelta [expr 200000+$story_id*100+$beam_id*10+9] 0 -1 0 -jntOffset $dXi $dYi $dZi $dXj $dYj $dZj
      element forceBeamColumn [expr $story_id*1000+400+$beam_id*10] $node1_id $node2_id [expr 200000+$story_id*100+$beam_id*10+9] $integration
      #element elasticBeamColumn [expr $story_id*1000+400+$beam_id*10] $node1_id $node2_id $slab_A [expr 57.0*sqrt(abs($fc0_beam*1000.0))] [expr 57.0*sqrt(abs($fc0_beam*1000.0))/2.6] $slab_J $slab_Iy $slab_Iz [expr 100000+$story_id*100+$beam_id*10+9]
    }
  }
  # for stories 3, 4 & 5 - Y-direction beam
  if {$story_id > 2} {
    set node1_id [expr ($story_id+1)*1000+100+$num_bays_x*10]
    set node2_id [expr ($story_id+1)*1000+200+$num_bays_x*10]
    set secTags ""
    for {set ip_id 0} {$ip_id < $numIntgrPts} {incr ip_id} {
      set	secTags	[lappend secTags [expr $story_id*1000+100+$ip_id]]
    }
    set	integration	"UserDefined $numIntgrPts $secTags $XIP_beam $LIPR_beam";
    geomTransf PDelta [expr 300000+$story_id*100+9] 1 0 0
    element forceBeamColumn [expr $story_id*1000+900] $node1_id $node2_id [expr 300000+$story_id*100+9] $integration
  }
  # walls
  for {set wall_id 0} {$wall_id < $num_walls} {incr wall_id} {
    set node1_id [expr $story_id*1000+500+$wall_id*10]
    set node2_id [expr ($story_id+1)*1000+500+$wall_id*10]
    set secTags ""
    for {set ip_id 0} {$ip_id < $numIntgrPts} {incr ip_id} {
      set	secTags	[lappend secTags [expr $story_id*1000+300+$ip_id]]
    }
    set	integration	"UserDefined $numIntgrPts $secTags $XIP_col_wall $LIPR_col_wall";
    geomTransf PDelta [expr 300000+$story_id*100+$wall_id] 1 0 0
    element forceBeamColumn [expr $story_id*1000+500+$wall_id*10] $node1_id $node2_id [expr 300000+$story_id*100+$wall_id] $integration
    set wall_tags_recorded [lappend wall_tags_recorded [expr $story_id*1000+500+$wall_id*10]]
  }
}

# diagonal steel brace
uniaxialMaterial ElasticPPGap 999 $Es 68.0 0.0 0.005
for {set story_id 0} {$story_id < $num_stories} {incr story_id} {
  set node1_id [expr $story_id*1000+100+$num_bays_x*10]
  set node2_id [expr ($story_id+1)*1000+200+$num_bays_x*10]
  element corotTruss [expr 9000+$story_id*100+1] $node1_id $node2_id [expr 0.25*3.14*1.25**2] 999
  set node1_id [expr $story_id*1000+200+$num_bays_x*10]
  set node2_id [expr ($story_id+1)*1000+100+$num_bays_x*10]
  element corotTruss [expr 9000+$story_id*100+2] $node1_id $node2_id [expr 0.25*3.14*1.25**2] 999
}
puts "All lateral system elements created."

# diaphragms
for {set story_id 1} {$story_id < $num_stories+1} {incr story_id} {
  rigidDiaphragm 3 [expr $story_id*1000+300] \
                   [expr $story_id*1000+100] [expr $story_id*1000+110] [expr $story_id*1000+120] \
                   [expr $story_id*1000+200] [expr $story_id*1000+210] [expr $story_id*1000+220] \
                   [expr $story_id*1000+500] [expr $story_id*1000+510]
}

# gravity loads
pattern Plain 1 Constant {
  for {set story_id 1} {$story_id < $num_stories+1} {incr story_id} {
    load [expr $story_id*1000+100] 0.0 0.0 [expr -[lindex $p2 $story_id-1]] 0.0 0.0 0.0
    load [expr $story_id*1000+110] 0.0 0.0 [expr -[lindex $p4 $story_id-1]] 0.0 0.0 0.0
    load [expr $story_id*1000+120] 0.0 0.0 [expr -[lindex $p5 $story_id-1]] 0.0 0.0 0.0
    load [expr $story_id*1000+200] 0.0 0.0 [expr -[lindex $p5 $story_id-1]] 0.0 0.0 0.0
    load [expr $story_id*1000+210] 0.0 0.0 [expr -[lindex $p2 $story_id-1]] 0.0 0.0 0.0
    load [expr $story_id*1000+220] 0.0 0.0 [expr -[lindex $p1 $story_id-1]] 0.0 0.0 0.0
    load [expr $story_id*1000+500] 0.0 0.0 [expr -[lindex $p5 $story_id-1]] 0.0 0.0 0.0
    load [expr $story_id*1000+510] 0.0 0.0 [expr -[lindex $p3 $story_id-1]] 0.0 0.0 0.0
  }
}
puts "Gravity loads applied."

# static analysis
wipeAnalysis
constraints Transformation
numberer RCM
system BandGeneral -piv
test EnergyIncr 1e-6 25 3
algorithm Newton
integrator LoadControl 0.1
analysis Static
analyze 10
puts "Gravity analysis completed."
wipeAnalysis
loadConst -time 0.0

# eigen analysis
if {0>1} {
  for {set k 1} {$k <= 6} {incr k} {
    recorder Node -file [format "mode-%i-dof1.out" $k] -node 1000 2000 3000 4000 5000 -dof 1 "eigen $k"
    recorder Node -file [format "mode-%i-dof2.out" $k] -node 1000 2000 3000 4000 5000 -dof 2 "eigen $k"
    recorder Node -file [format "mode-%i-dof3.out" $k] -node 1000 2000 3000 4000 5000 -dof 3 "eigen $k"
    recorder Node -file [format "mode-%i-dof4.out" $k] -node 1000 2000 3000 4000 5000 -dof 4 "eigen $k"
    recorder Node -file [format "mode-%i-dof5.out" $k] -node 1000 2000 3000 4000 5000 -dof 5 "eigen $k"
    recorder Node -file [format "mode-%i-dof6.out" $k] -node 1000 2000 3000 4000 5000 -dof 6 "eigen $k"
  }
}
set a [eigen 6];
set W12 [lindex $a 0];
set W22 [lindex $a 1];
set W32 [lindex $a 2];
set W42 [lindex $a 3];
set W52 [lindex $a 4];
set W62 [lindex $a 5];
set W1 [expr pow($W12,0.5)];
set W2 [expr pow($W22,0.5)];
set W3 [expr pow($W32,0.5)];
set W4 [expr pow($W42,0.5)];
set W5 [expr pow($W52,0.5)];
set W6 [expr pow($W62,0.5)];
set T1 [expr 2.0*$PI/$W1];
set T2 [expr 2.0*$PI/$W2];
set T3 [expr 2.0*$PI/$W3];
set T4 [expr 2.0*$PI/$W4];
set T5 [expr 2.0*$PI/$W5];
set T6 [expr 2.0*$PI/$W6];
puts "Eigen analysis completed."
puts "T1=$T1 sec"
puts "T2=$T2 sec"
puts "T3=$T3 sec"
puts "T4=$T4 sec"
puts "T5=$T5 sec"
puts "T6=$T6 sec"

# damping
set xDamp 0.02; # damping ratio
set alphaM [expr $xDamp*(2*$W1*$W3)/($W1+$W3)]
set betaK [expr 2.*$xDamp/($W1+$W3)]
#KZ
rayleigh $alphaM 0.0 $betaK 0.0
#modalDamping $xDamp $xDamp $xDamp $xDamp $xDamp $xDamp