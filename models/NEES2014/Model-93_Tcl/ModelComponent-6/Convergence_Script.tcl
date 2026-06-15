#convenrgence Script



if {$ok != 0} {
	algorithm KrylovNewton
	test $testType_Current $testTol_Current $testIter_Current 0 
	set ok [analyze 1 $dt_Current];
}

if {$ok != 0} {
	algorithm KrylovNewton -initial
	test $testType_Current $testTol_Current $testIter_Current 0 
	set ok [analyze 1 $dt_Current];
}

if {$ok != 0} {
	algorithm KrylovNewton -initialCurrent
	test $testType_Current $testTol_Current $testIter_Current 0 
	set ok [analyze 1 $dt_Current];
}

if {$ok != 0} {
	algorithm Newton
	test $testType_Current $testTol_Current $testIter_Current 0 
	set ok [analyze 1 $dt_Current];
}

if {$ok != 0} {
	algorithm Newton  -initial
	test $testType_Current $testTol_Current $testIter_Current 0 
	set ok [analyze 1 $dt_Current];
}

if {$ok != 0} {
	algorithm Newton -initialCurrent
	test $testType_Current $testTol_Current $testIter_Current 0 
	set ok [analyze 1 $dt_Current];
}


	### Change test & algorithm back to there default #########
	###########################################################
	test $testType $testTol $testIter
	algorithm KrylovNewton 
