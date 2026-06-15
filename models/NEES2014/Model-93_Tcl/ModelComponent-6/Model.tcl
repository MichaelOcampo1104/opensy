# 3-story MRF of SAC/FEMA steel project, pre-Northridge L.A. structure
# Ref: FEMA-355-C, Appedndix B [or FEMA-440 Appendix-F].
# By: Pedram Khajehhesameddin
# Purdue University
# June 2014
# ===============================================================

wipe
model BasicBuilder -ndm 2 -ndf 3

# NODES =================
node	11	0		0
node	12	360		0
node	13	720		0
node	14	1080	0


set small_mass 1e-5;
			
node	21	0		156
node	22	360		156
node	23	720		156
node	24	1080	156

			
node	31	0		312
node	32	360		312
node	33	720		312
node	34	1080	312

			
node	41	0		468
node	42	360		468
node	43	720		468
node	44	1080	468

# constrain beam-column joints in a floor to have the same lateral displacement using the "equalDOF" command
	# command: equalDOF $MasterNodeID $SlaveNodeID $dof1 $dof2...
	set dof1 1;	# constrain movement in dof 1 (x-direction)
	
	equalDOF 21 22 $dof1;	# Floor 2:  Pier 1 to Pier 2
	equalDOF 21 23 $dof1;	# Floor 2:  Pier 1 to Pier 3
	equalDOF 21 24 $dof1;	# Floor 2:  Pier 1 to Pier 4

	
	equalDOF 31 32 $dof1;	# Floor 3:  Pier 1 to Pier 2
	equalDOF 31 33 $dof1;	# Floor 3:  Pier 1 to Pier 3
	equalDOF 31 34 $dof1;	# Floor 3:  Pier 1 to Pier 4

	
	equalDOF 41 42 $dof1;	# Floor 4:  Pier 1 to Pier 2
	equalDOF 41 43 $dof1;	# Floor 4:  Pier 1 to Pier 3
	equalDOF 41 44 $dof1;	# Floor 4:  Pier 1 to Pier 4

	
	

	mass	21	0.683	$small_mass	$small_mass
	mass	22	0.683	$small_mass	$small_mass
	mass	23	0.683	$small_mass	$small_mass
	mass	24	0.683	$small_mass	$small_mass

				
	mass	31	0.683	$small_mass	$small_mass
	mass	32	0.683	$small_mass	$small_mass
	mass	33	0.683	$small_mass	$small_mass
	mass	34	0.683	$small_mass	$small_mass

				
	mass	41	0.74	$small_mass	$small_mass
	mass	42	0.74	$small_mass	$small_mass
	mass	43	0.74	$small_mass	$small_mass
	mass	44	0.74	$small_mass	$small_mass



fix 11 1 1 1;
fix 12 1 1 1;
fix 13 1 1 1;
fix 14 1 1 1;




# MATERIAL ============================================
set matID_Be 301
set matID_Co 501

uniaxialMaterial Steel02 $matID_Be 36 29000 3e-3 18 0.925 0.15;	#for beams
uniaxialMaterial Steel02 $matID_Co 54 29000 3e-3 18 0.925 0.15;	#for columns



# SECTION =============================================
									# 0   1     2    3    4    5     6    7     8    9    10 
source ModelComponents/getWSection_CSI.tcl;	# d	  bf	tf	 tw	  A	   Ixx	 Iyy  Sxx	Syy	 Zxx  Zyy
source ModelComponents/Wsection_S.tcl; 

set nfdw 6;			# number of fibers along dw
set nftw 2;			# number of fibers along tw
set nfbf 4;			# number of fibers along bf
set nftf 2;			# number of fibers along tf


# W14x257
set secTag 14257;
set Wprop [getWSection_CSI W14X257];
set d  [lindex $Wprop 0];
set bf [lindex $Wprop 1];
set tf [lindex $Wprop 2];
set tw [lindex $Wprop 3];
Wsection_S  $secTag $matID_Co $d $bf $tf $tw $nfdw $nftw $nfbf $nftf


# W14x311
set secTag 14311;
set Wprop [getWSection_CSI W14X311];
set d  [lindex $Wprop 0];
set bf [lindex $Wprop 1];
set tf [lindex $Wprop 2];
set tw [lindex $Wprop 3];
Wsection_S  $secTag $matID_Co $d $bf $tf $tw $nfdw $nftw $nfbf $nftf


# W33x118
set secTag 33118;
set Wprop [getWSection_CSI W33X118];
set d  [lindex $Wprop 0];
set bf [lindex $Wprop 1];
set tf [lindex $Wprop 2];
set tw [lindex $Wprop 3];
Wsection_S  $secTag $matID_Be $d $bf $tf $tw $nfdw $nftw $nfbf $nftf



# W30x116
set secTag 30116;
set Wprop [getWSection_CSI W30X116];
set d  [lindex $Wprop 0];
set bf [lindex $Wprop 1];
set tf [lindex $Wprop 2];
set tw [lindex $Wprop 3];
Wsection_S  $secTag $matID_Be $d $bf $tf $tw $nfdw $nftw $nfbf $nftf



# W24x68
set secTag 2468;
set Wprop [getWSection_CSI W24X68];
set d  [lindex $Wprop 0];
set bf [lindex $Wprop 1];
set tf [lindex $Wprop 2];
set tw [lindex $Wprop 3];
Wsection_S  $secTag $matID_Be $d $bf $tf $tw $nfdw $nftw $nfbf $nftf



# =====================================================================
set numIntgrPts 3


geomTransf Linear 1
geomTransf PDelta 2
geomTransf Corotational 3

set COtranID 2;
set BEtranID 2;


element nonlinearBeamColumn	5011	11	21	$numIntgrPts	14257	$COtranID;		#1st Col.
element nonlinearBeamColumn	5021	21	31	$numIntgrPts	14257	$COtranID;		#1st Col.
element nonlinearBeamColumn	5031	31	41	$numIntgrPts	14257	$COtranID;		#1st Col.
								
element nonlinearBeamColumn	5012	12	22	$numIntgrPts	14311	$COtranID;		#2nd Col.
element nonlinearBeamColumn	5022	22	32	$numIntgrPts	14311	$COtranID;		#2nd Col.
element nonlinearBeamColumn	5032	32	42	$numIntgrPts	14311	$COtranID;		#2nd Col.
								
element nonlinearBeamColumn	5013	13	23	$numIntgrPts	14311	$COtranID;		#3rd Col.
element nonlinearBeamColumn	5023	23	33	$numIntgrPts	14311	$COtranID;		#3rd Col.
element nonlinearBeamColumn	5033	33	43	$numIntgrPts	14311	$COtranID;		#3rd Col.
								
element nonlinearBeamColumn	5014	14	24	$numIntgrPts	14257	$COtranID;		#4th Col.
element nonlinearBeamColumn	5024	24	34	$numIntgrPts	14257	$COtranID;		#4th Col.
element nonlinearBeamColumn	5034	34	44	$numIntgrPts	14257	$COtranID;		#4th Col.
								
								
element nonlinearBeamColumn	3021	21	22	$numIntgrPts	33118	$BEtranID;		# 1~2 Beam.
element nonlinearBeamColumn	3022	22	23	$numIntgrPts	33118	$BEtranID;		# 1~2 Beam.
element nonlinearBeamColumn	3023	23	24	$numIntgrPts	33118	$BEtranID;		# 1~2 Beam.
								
element nonlinearBeamColumn	3031	31	32	$numIntgrPts	30116	$BEtranID;		#2~3 Beam.
element nonlinearBeamColumn	3032	32	33	$numIntgrPts	30116	$BEtranID;		#2~3 Beam.
element nonlinearBeamColumn	3033	33	34	$numIntgrPts	30116	$BEtranID;		#2~3 Beam.
								
element nonlinearBeamColumn	3041	41	42	$numIntgrPts	2468	$BEtranID;		# 3~4 Beam.
element nonlinearBeamColumn	3042	42	43	$numIntgrPts	2468	$BEtranID;		# 3~4 Beam.
element nonlinearBeamColumn	3043	43	44	$numIntgrPts	2468	$BEtranID;		# 3~4 Beam.



pattern Plain 500 Linear {

	load	21	0	-13.6	0
	load	22	0	-27.2	0
	load	23	0	-27.2	0
	load	24	0	-13.6	0
				
	load	31	0	-13.6	0
	load	32	0	-27.2	0
	load	33	0	-27.2	0
	load	34	0	-13.6	0
				
	load	41	0	-12.1	0
	load	42	0	-24.2	0
	load	43	0	-24.2	0
	load	44	0	-12.1	0

}


constraints Transformation
numberer RCM
system BandGeneral
test NormDispIncr 1.0e-9 100
algorithm KrylovNewton
integrator LoadControl 0.1
analysis Static
analyze 10
loadConst -time 0.0


#--------------
#source DisplayModel2D.tcl
#source DisplayPlane.tcl
#set ViewScale 5;
#DisplayModel2D DeformedShape $ViewScale
#---------------


# This records the base shear forces	
recorder Node    -file $out_dir/Base_Shear.txt -node 11 12 13 14 -dof 1 reaction

# This records the roof dynamic displacements	
recorder Node -file $out_dir/Top_Disp.txt -time -node 41 -dof 1 disp

##Damping
set xDamp 0.05;						# damping ratio
set MpropSwitch 1.0;
set KcurrSwitch 0.0;
set KcommSwitch 0.0;
set KinitSwitch 1.0;
set nEigenI 1;						# mode 1
set nEigenJ 3;						# mode 3

set lambdaN [eigen [expr $nEigenJ]];				# eigenvalue analysis for nEigenJ modes
set lambdaI [lindex $lambdaN [expr $nEigenI-1]]; 	# eigenvalue mode i
set lambdaJ [lindex $lambdaN [expr $nEigenJ-1]]; 	# eigenvalue mode j
set omegaI [expr pow($lambdaI,0.5)];				# omega of mode i
set omegaJ [expr pow($lambdaJ,0.5)];				# omega of mode i

set alphaM    [expr $MpropSwitch*$xDamp*(2*$omegaI*$omegaJ)/($omegaI+$omegaJ)];	# M-prop. damping; D = alphaM*M
set betaKcurr [expr $KcurrSwitch*2.*$xDamp/($omegaI+$omegaJ)];					# current-K;      +beatKcurr*KCurrent
set betaKcomm [expr $KcommSwitch*2.*$xDamp/($omegaI+$omegaJ)];					# last-committed K;   +betaKcomm*KlastCommitt
set betaKinit [expr $KinitSwitch*2.*$xDamp/($omegaI+$omegaJ)];					# initial-K;     +beatKinit*Kini

rayleigh $alphaM $betaKcurr $betaKinit $betaKcomm; 	# RAYLEIGH damping



