# Define design properties for the Gr 60 steel reinforced column
# size
set	L	288.0; # inch
set	D	48.0; # inch
set	c	2.0; # inch
# material
# concrete
set	fc	-6.1; # ksi
set	ft	[expr 7.4*sqrt(-$fc*1000.0)/1000.0]; # ksi
set	Ec	3320.0; # ksi
#set	Ec	[expr 57.0*sqrt(-$fc*1000.0)];
set	Et	[expr $ft/0.002]; # ksi
# longitudinal reinforcement
set	nsl	18;
set	dbl	1.41; # in
set	Asl	1.56; # in^2
set	fyl	75.2; # ksi
set	ful	102.4; # ksi
set	esy	0.0026; # in/in
set	esh	0.0110; # in/in
set	esu	0.1220; # in/in
set	esf	0.1982; # in/in
set	Esl	28400.0; # ksi
#set	Esl	[expr $fyl/$esy];
set	b	[expr ($ful-$fyl)/($esu-$esy)/$Esl];
set	Esh	[expr $b*2.0*$Esl]; # ksi
# lateral reinforcement
set	dbt	0.625; # in
set	Ast	0.62; # in^2
set	fyt	54.8; # ksi
set	fut	85.9; # ksi
set	Est	29000.0; # ksi;
set	s	6.0; # in

