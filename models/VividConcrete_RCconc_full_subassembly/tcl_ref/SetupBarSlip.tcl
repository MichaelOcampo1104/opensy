set BarslipBEStemBSMatTag	100001;
set BarslipBEStemTSMatTag	100002;
set BarslipBEFlangeLSMatTag	100003;
set BarslipBEFlangeRSMatTag	100004;
set BarslipWebStemSMatTag	100005;
set BarslipWebFlangeLSMatTag	100006;
set BarslipWebFlangeRSMatTag	100007;
set BarslipBEStemBCMatTag	100008;
set BarslipBEStemTCMatTag	100009;
set BarslipBEFlangeLCMatTag	100010;
set BarslipBEFlangeRCMatTag	100011;
set BarslipUCCMatTag		100012;

set BarslipAlpha	0.4;
set Barslipb	0.3;
set BarslipR	0.5;
set Su_Sy		50;

set BarslipBEStemBSfyl		[lindex $BEStemBSfyl 0];
set BarslipBEStemTSfyl		[lindex $BEStemTSfyl 0];
set BarslipBEFlangeLSfyl	[lindex $BEFlangeLSfyl 0];
set BarslipBEFlangeRSfyl	[lindex $BEFlangeRSfyl 0];
set BarslipWebStemSfyl		[lindex $WebStemSfyl 0];
set BarslipWebFlangeLSfyl	[lindex $WebFlangeLSfyl 0];
set BarslipWebFlangeRSfyl	[lindex $WebFlangeRSfyl 0];
set BarslipBEStemBSful		[expr $BarslipBEStemBSfyl*[lindex $BEStemBSTYl 0]];
set BarslipBEStemTSful		[expr $BarslipBEStemTSfyl*[lindex $BEStemTSTYl 0]];
set BarslipBEFlangeLSful	[expr $BarslipBEFlangeLSfyl*[lindex $BEFlangeLSTYl 0]];
set BarslipBEFlangeRSful	[expr $BarslipBEFlangeRSfyl*[lindex $BEFlangeRSTYl 0]];
set BarslipWebStemSful		[expr $BarslipWebStemSfyl*[lindex $WebStemSTYl 0]];
set BarslipWebFlangeLSful	[expr $BarslipWebFlangeLSfyl*[lindex $WebFlangeLSTYl 0]];
set BarslipWebFlangeRSful	[expr $BarslipWebFlangeRSfyl*[lindex $WebFlangeRSTYl 0]];
if {$BEStemBconfigi == 1} {
	set dbBEStemBS		[lindex [dict get [dict get $BEStemBSC 1] db] 0];
	set SyBEStemBS		[expr 0.013+0.1*((2*$BarslipAlpha+1)*$BarslipBEStemBSfyl*1000.0/sqrt(-[lindex $fc 0]*1000)*$dbBEStemBS/4000.0)];
	uniaxialMaterial Bond_SP01 $BarslipBEStemBSMatTag $BarslipBEStemBSfyl $SyBEStemBS $BarslipBEStemBSful \
		[expr $Su_Sy*$SyBEStemBS] $Barslipb $BarslipR;
}
if {$BEStemTconfigi == 1} {
	set dbBEStemTS		[lindex [dict get [dict get $BEStemTSC 1] db] 0];
	set SyBEStemTS		[expr 0.013+0.1*((2*$BarslipAlpha+1)*$BarslipBEStemTSfyl*1000.0/sqrt(-[lindex $fc 0]*1000)*$dbBEStemTS/4000.0)];
	uniaxialMaterial Bond_SP01 $BarslipBEStemTSMatTag $BarslipBEStemTSfyl $SyBEStemTS $BarslipBEStemTSful \
		[expr $Su_Sy*$SyBEStemTS] $Barslipb $BarslipR;
}
if {$BEFlangeLconfigi == 1} {
	set dbBEFlangeLS		[lindex [dict get [dict get $BEFlangeLSC 1] db] 0];
	set SyBEFlangeLS		[expr 0.013+0.1*((2*$BarslipAlpha+1)*$BarslipBEFlangeLSfyl*1000.0/sqrt(-[lindex $fc 0]*1000)*$dbBEFlangeLS/4000.0)];
	uniaxialMaterial Bond_SP01 $BarslipBEFlangeLSMatTag $BarslipBEFlangeLSfyl $SyBEFlangeLS $BarslipBEFlangeLSful \
		[expr $Su_Sy*$SyBEFlangeLS] $Barslipb $BarslipR;
}
if {$BEFlangeRconfigi == 1} {
	set dbBEFlangeRS		[lindex [dict get [dict get $BEFlangeRSC 1] db] 0];
	set SyBEFlangeRS		[expr 0.013+0.1*((2*$BarslipAlpha+1)*$BarslipBEFlangeRSfyl*1000.0/sqrt(-[lindex $fc 0]*1000)*$dbBEFlangeRS/4000.0)];
	uniaxialMaterial Bond_SP01 $BarslipBEFlangeRSMatTag $BarslipBEFlangeRSfyl $SyBEFlangeRS $BarslipBEFlangeRSful \
		[expr $Su_Sy*$SyBEFlangeRS] $Barslipb $BarslipR;
}
set dbWebStemS		[lindex [dict get [dict get $WebStemSC 1] db] 0];
set SyWebStemS		[expr 0.013+0.1*((2*$BarslipAlpha+1)*$BarslipWebStemSfyl*1000.0/sqrt(-[lindex $fc 0]*1000)*$dbWebStemS/4000.0)];
set dbWebFlangeLS		[lindex [dict get [dict get $WebFlangeLSC 1] db] 0];
set SyWebFlangeLS		[expr 0.013+0.1*((2*$BarslipAlpha+1)*$BarslipWebFlangeLSfyl*1000.0/sqrt(-[lindex $fc 0]*1000)*$dbWebFlangeLS/4000.0)];
set dbWebFlangeRS		[lindex [dict get [dict get $WebFlangeRSC 1] db] 0];
set SyWebFlangeRS		[expr 0.013+0.1*((2*$BarslipAlpha+1)*$BarslipWebFlangeRSfyl*1000.0/sqrt(-[lindex $fc 0]*1000)*$dbWebFlangeRS/4000.0)];

uniaxialMaterial Bond_SP01 $BarslipWebStemSMatTag $BarslipWebStemSfyl $SyWebStemS $BarslipWebStemSful \
	[expr $Su_Sy*$SyWebStemS] $Barslipb $BarslipR;
uniaxialMaterial Bond_SP01 $BarslipWebFlangeLSMatTag $BarslipWebFlangeLSfyl $SyWebFlangeLS $BarslipWebFlangeLSful \
	[expr $Su_Sy*$SyWebFlangeLS] $Barslipb $BarslipR;
uniaxialMaterial Bond_SP01 $BarslipWebFlangeRSMatTag $BarslipWebFlangeRSfyl $SyWebFlangeRS $BarslipWebFlangeRSful \
	[expr $Su_Sy*$SyWebFlangeRS] $Barslipb $BarslipR;

DefineRegularizedUnconfinedConcreteMaterial "Concrete02" 1 $BarslipUCCMatTag $fci [lindex $LIP $IPTag-1];
puts "Unconfined concrete: fc = $fci";
if {$BEStemBconfigi == 1} {
	DefineRegularizedConfinedConcreteMaterial "Concrete02" 1 $BarslipBEStemBCMatTag $fci $BEStemBnumbt $BEStemBSsi [expr [lindex $BEStemBdist 1]-[lindex $BEStemBdist 0]] \
		[expr ($bwi-2*$ci)/[lindex $BEStemBnumb 0]] $bwi [expr $lbesbi+2*$ci] $BEStemBroutx $BEStemBrouty $BEStemBSfyti 0;
}
if {$BEStemTconfigi == 1} {
	DefineRegularizedConfinedConcreteMaterial "Concrete02" 1 $BarslipBEStemTCMatTag $fci $BEStemTnumbt $BEStemTSsi [expr [lindex $BEStemTdist 1]-[lindex $BEStemTdist 0]] \
		[expr ($bwi-2*$ci)/[lindex $BEStemTnumb 0]] $bwi [expr $lbesti+2*$ci] $BEStemTroutx $BEStemTrouty $BEStemTSfyti 0;
}
if {$BEFlangeLconfigi == 1} {
	DefineRegularizedConfinedConcreteMaterial "Concrete02" 1 $BarslipBEFlangeLCMatTag $fci $BEFlangeLnumbt $BEFlangeLSsi [expr [lindex $BEFlangeLdist 1]-[lindex $BEFlangeLdist 0]] \
		[expr ($tfli-2*$ci)/[lindex $BEFlangeLnumb 0]] $tfli [expr $lbefli+2*$ci] $BEFlangeLroutx $BEFlangeLrouty $BEFlangeLSfyti 0;
}
if {$BEFlangeRconfigi == 1} {
	DefineRegularizedConfinedConcreteMaterial "Concrete02" 1 $BarslipBEFlangeRCMatTag $fci $BEFlangeRnumbt $BEFlangeRSsi [expr [lindex $BEFlangeRdist 1]-[lindex $BEFlangeRdist 0]] \
		[expr ($tfri-2*$ci)/[lindex $BEFlangeRnumb 0]] $tfri [expr $lbefri+2*$ci] $BEFlangeRroutx $BEFlangeRrouty $BEFlangeLSfyti 0;
}


set WallMatID "";
set WallMatID		[lappend WallMatID $BarslipBEStemBCMatTag $BarslipBEStemTCMatTag $BarslipBEFlangeLCMatTag $BarslipBEFlangeRCMatTag $BarslipUCCMatTag \
					$BarslipBEStemBSMatTag $BarslipBEStemTSMatTag $BarslipBEFlangeLSMatTag $BarslipBEFlangeRSMatTag \
					$BarslipWebStemSMatTag $BarslipWebFlangeLSMatTag $BarslipWebFlangeRSMatTag];

CreateTWallSection 100001 $WallConfig $WallGeom $WallMatID $WallBarLayer $WallFibLayer $WallShear \
					$BEStemBdist $BEStemTdist $BEFlangeLdist $BEFlangeRdist $WebStemdist $WebFlangeLdist $WebFlangeRdist \
					$BEStemBnumb $BEStemTnumb $BEFlangeLnumb $BEFlangeRnumb $WebStemnumb $WebFlangeLnumb $WebFlangeRnumb \
					$BEStemBdb $BEStemTdb $BEFlangeLdb $BEFlangeRdb $WebStemdb $WebFlangeLdb $WebFlangeRdb;
