####################################################################################################
# DefineConcreteMaterial: Defines a procedure which create the user-defined concrete material
#
# Authoer: Kuanshi Zhong
# Date: 11/2016
#
# Formal arguments
# fc: the conpressive strength (negative, ksi)
# nl: the number of longitudinal bars restrained by corners of hoops or legs of crossties
# s: the lateral steel spacing
# b: the column width
# rou: the lateral reinforcement ratio Ash/(b*s) in the loading direction
# fyt: the yield strength of lateral steel
#
# Notes
# Wall
# All materials defined below are regularized following Pugh et al. (2015)

# Define an unconfined concrete material
proc DefineRegularizedUnconfinedConcreteMaterial {type matTag fc LIP} {
# Define unit converters
set mm_in 25.4;
set mpa_ksi 6.895;
# Concrete 01 Material: Zero Tensile Strength
if {$type == "Concrete01"} {
	set fpc	$fc;
	set epsc0	-0.002;
	set fpcu	[expr 0.2*$fpc];
	set Gfc	[expr 2.0*(-$fc)*$mpa_ksi];
	set Ec_temp	[expr 57*sqrt(-$fc*1000)*$mpa_ksi];
	set epsU	[expr -($Gfc/0.6/(-$fc)/($LIP*$mm_in)-0.8*(-$fc)/$Ec_temp+(-$epsc0))];
	uniaxialMaterial Concrete01 $matTag $fpc $epsc0 $fpcu $epsU;
}
# Concrete 02 Material: Linear Tension Softening
if {$type == "Concrete02"} {
	set fpc	$fc;
	set epsc0	-0.002;
	set fpcu	[expr 0.2*$fpc];
	set Ec	[expr 57*sqrt(-$fc*1000)];
	set Gfc	[expr 2*(-$fc)*$mpa_ksi];
	set Ec_temp	[expr 57*sqrt(-$fc*1000)*$mpa_ksi];
	set epsU	[expr -($Gfc/0.6/(-$fc)/($LIP*$mm_in)-0.8*(-$fc)/$Ec_temp+(-$epsc0))];
	set lambda	0.1;
	set ft	[expr 0.004*sqrt(-$fc*1000)];
	set Ets	[expr $Ec*0.05];
	uniaxialMaterial Concrete02 $matTag $fpc $epsc0 $fpcu $epsU $lambda $ft $Ets;
}
# Concrete04 Material: Popovics Concrete Material
if {$type == "Concrete04"} {
	set fpc	$fc;
	set epsc0	-0.002;
	set Gfc	[expr 2*(-$fc)*$mpa_ksi];
	set Ec_temp	[expr 57*sqrt(-$fc*1000)*$mpa_ksi];
	set epsU	[expr -($Gfc/0.6/(-$fc)/($LIP*$mm_in)-0.8*(-$fc)/$Ec_temp+(-$epsc0))];
	set Ec	[expr 57*sqrt(-$fc*1000)];
	set ft	[expr 0.0074*sqrt(-$fc*1000)];
	set et	0.002;
	set beta	0.0; # the residual stress ratio
	uniaxialMaterial Concrete04 $matTag $fpc $epsc0 $epsU $Ec $ft $et $beta;
}
#puts "Unconfined Concrete Material Defined"
#puts "fpc is $fpc";
#puts "epsc0 is $epsc0";
#puts "epsU is $epsU";
}

# Define a confined concrete material
proc DefineRegularizedConfinedConcreteMaterial {type matTag fc nl s b d db rou fyt LIP} {
# Define unit converters
set mm_in	25.4;
set mpa_ksi	6.895;
set n		[expr $nl/2.];
set wi	[expr ($b-$n*$db)/($n-1)];
set ke1	[expr 1-$n*$wi**2/6/$b/$d];
set ke2	[expr 1-0.5*$s/$b];
set ke3	[expr 1-0.5*$s/$d];
set rou_cc	[expr $n*0.25*3.14*$db**2/$b/$d];
set ke	[expr $ke1*$ke2*$ke3/(1-$rou_cc)];

# Concrete 01 Material: Zero Tensile Strength
if {$type == "Concrete01"} {
#	set ke	[expr ($nl-2.)/$nl*(1-$s/$b)];
	set fl	[expr $ke*$rou*$fyt];
	set Kfc 	[expr -1.254+2.254*sqrt(1.0+7.94*$fl/(-$fc))-2*$fl/(-$fc)];
	set fpc	[expr $Kfc*$fc];
	set Keps	[expr 1+5*($Kfc-1)];
	set epsc0	[expr $Keps*(-0.002)];
	set fpcu	[expr 0.2*$fpc];
	set Gfc	[expr 1.7*2*(-$fc)*$mpa_ksi];
	set Ec_temp	[expr 57*sqrt(-$fc*1000)*$mpa_ksi];
	set epsU	[expr -($Gfc/0.6/(-$fpc)/($LIP*$mm_in)-0.8*(-$fpc)/$Ec_temp+(-$epsc0))];
	uniaxialMaterial Concrete01 $matTag $fpc $epsc0 $fpcu $epsU;
}
# Concrete 02 Material: Linear Tension Softening
if {$type == "Concrete02"} {
#	set ke	[expr ($nl-2.)/$nl*(1-$s/$b)];
	set fl	[expr $ke*$rou*$fyt];
	set Kfc 	[expr -1.254+2.254*sqrt(1+7.94*$fl/(-$fc))-2*$fl/(-$fc)];
	set fpc	[expr $Kfc*$fc];
	set Keps	[expr 1+5*($Kfc-1)];
	set epsc0	[expr $Keps*(-0.002)];
	set fpcu	[expr 0.2*$fpc];
	set Ec	[expr 57*sqrt(-$fc*1000)];
	set Gfc	[expr 1.7*2*(-$fc)*$mpa_ksi];
	set Ec_temp	[expr 57*sqrt(-$fc*1000)*$mpa_ksi];
	set epsU	[expr -($Gfc/0.6/(-$fpc)/($LIP*$mm_in)-0.8*(-$fpc)/$Ec_temp+(-$epsc0))];
	set lambda	0.1;
	set ft	[expr 0.004*sqrt(-$fc*1000)];
	set Ets	[expr $Ec*0.05];
	uniaxialMaterial Concrete02 $matTag $fpc $epsc0 $fpcu $epsU $lambda $ft $Ets;
}
# Concrete04 Material: Popovics Concrete Material
if {$type == "Concrete04"} {
#	set ke	[expr ($nl-2.)/$nl*(1-$s/$b)];
	set fl	[expr $ke*$rou*$fyt];
	set Kfc 	[expr -1.254+2.254*sqrt(1+7.94*$fl/(-$fc))-2*$fl/(-$fc)];
	set fpc	[expr $Kfc*$fc];
	set Keps	[expr 1+5*($Kfc-1)];
	set epsc0	[expr $Keps*(-0.002)];
	set Gfc	[expr 1.7*2*(-$fc)*$mpa_ksi];
	set Ec_temp	[expr 57*sqrt(-$fc*1000)*$mpa_ksi];
	set epsU	[expr -($Gfc/0.6/(-$fpc)/($LIP*$mm_in)-0.8*(-$fpc)/$Ec_temp+(-$epsc0))];
	set Ec	[expr 57*sqrt(-$fc*1000)];
	set ft	[expr 0.0074*sqrt(-$fc*1000)];
	set et	0.002;
	set beta	0.0; # the residual tensile stress ratio
	uniaxialMaterial Concrete04 $matTag $fpc $epsc0 $epsU $Ec $ft $et $beta;
}
#puts "Confined Concrete Material Defined"
#puts "nl is $nl"
#puts "s is $s"
#puts "b is $b"
#puts "ke is $ke"
#puts "fl is $fl"
#puts "Kfc is $Kfc"
#puts "Keps is $Keps"
#puts "fpc is $fpc";
#puts "epsc0 is $epsc0";
#puts "epsU is $epsU";
}