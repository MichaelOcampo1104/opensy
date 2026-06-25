set pid [getPID]
set numP [getNP]
logFile CHKc5.0Res0.2RS1RC1/log.txt
set count 0
cd CHKc5.0Res0.2RS1RC1/
foreach nInt {9} {
     if {[expr $count % $numP] == $pid}  {
     model BasicBuilder -ndm 2 -ndf 3;
     set outName [format "nInt%s" $nInt]
     file mkdir $outName;
     set geomName [format "staticFiles/modelGeometry%i.tcl" $nInt];
     set matName [format "staticFiles/modelMaterial%i.tcl" $nInt];
     source $matName;
     source $geomName;
     element zeroLength 197 1 2 -mat 99 -dir 6;
     element zeroLength 198 1 2 -mat 99 -dir 2;
     element zeroLength 199 1 2 -mat 99 -dir 1;
     set nElem 2;
     set nTop [expr $nElem + 2];
     recorder Node -file $outName/RBase.out -node 1 -dof 1 2 3 reaction;
     recorder Node -file $outName/Dtop.out -node $nTop -dof 1 2 3 disp;
     recorder Element -file $outName/Elem1.out -ele 1 section forceAndDeformation;
     recorder Element -file $outName/Elem2.out -ele 2 section forceAndDeformation;
     recorder Element -file $outName/Elem3.out -ele 3 section forceAndDeformation;
     recorder Element -file $outName/Elem4.out -ele 4 section forceAndDeformation;
     recorder Element -file $outName/baseStrainUnc11.out   -ele 1 section 1 fiber [expr -44.291] 0 1 stressStrain
     recorder Element -file $outName/baseStrainConf11.out  -ele 1 section 1 fiber [expr -44.291]  0 11 stressStrain
     recorder Element -file $outName/baseStrainUnc12.out   -ele 1 section 1 fiber [expr 44.291] 0 1 stressStrain
     recorder Element -file $outName/baseStrainConf12.out  -ele 1 section 1 fiber [expr 44.291]  0 11 stressStrain
     recorder Element -file $outName/baseStrainUnc21.out   -ele 1 section 2 fiber [expr -44.291] 0 2 stressStrain
     recorder Element -file $outName/baseStrainConf21.out  -ele 1 section 2 fiber [expr -44.291]  0 12 stressStrain
     recorder Element -file $outName/baseStrainUnc22.out   -ele 1 section 2 fiber [expr 44.291] 0 2 stressStrain
     recorder Element -file $outName/baseStrainConf22.out  -ele 1 section 2 fiber [expr 44.291]  0 12 stressStrain
     recorder Element -file $outName/baseStrainUnc31.out   -ele 1 section 3 fiber [expr -44.291] 0 3 stressStrain
     recorder Element -file $outName/baseStrainConf31.out  -ele 1 section 3 fiber [expr -44.291]  0 13 stressStrain
     recorder Element -file $outName/baseStrainUnc32.out   -ele 1 section 3 fiber [expr 44.291] 0 3 stressStrain
     recorder Element -file $outName/baseStrainConf32.out  -ele 1 section 3 fiber [expr 44.291]  0 13 stressStrain
     recorder Element -file $outName/baseStrainSteel11.out -ele 1 section 1 fiber [expr -44.291]  0 51 stressStrain
     recorder Element -file $outName/baseStrainSteel12.out -ele 1 section 1 fiber [expr 44.291]  0 51 stressStrain
     recorder Element -file $outName/baseStrainSteel21.out -ele 1 section 2 fiber [expr -44.291]  0 52 stressStrain
     recorder Element -file $outName/baseStrainSteel22.out -ele 1 section 2 fiber [expr 44.291]  0 52 stressStrain
     recorder Element -file $outName/baseStrainSteel31.out -ele 1 section 3 fiber [expr -44.291]  0 53 stressStrain
     recorder Element -file $outName/baseStrainSteel32.out -ele 1 section 3 fiber [expr 44.291]  0 53 stressStrain
     recorder Element -file $outName/SectionCurvature11.out -time -ele 1 section 1 deformation
     recorder Element -file $outName/SectionMoment11.out    -time -ele 1 section 1 force
     recorder Element -file $outName/SectionCurvature12.out -time -ele 1 section 2 deformation
     recorder Element -file $outName/SectionMoment12.out    -time -ele 1 section 2 force
     recorder Element -file $outName/SectionCurvature13.out -time -ele 1 section 3 deformation
     recorder Element -file $outName/SectionMoment13.out    -time -ele 1 section 3 force
     recorder Element -file $outName/SectionCurvature14.out -time -ele 1 section 4 deformation
     recorder Element -file $outName/SectionMoment14.out    -time -ele 1 section 4 force
     recorder Element -file $outName/SectionCurvature15.out -time -ele 1 section 5 deformation
     recorder Element -file $outName/SectionMoment15.out    -time -ele 1 section 5 force
     recorder Element -file $outName/SectionCurvature16.out -time -ele 1 section 6 deformation
     recorder Element -file $outName/SectionMoment16.out    -time -ele 1 section 6 force
     recorder Element -file $outName/SectionCurvature17.out -time -ele 1 section 7 deformation
     recorder Element -file $outName/SectionMoment17.out    -time -ele 1 section 7 force
     recorder Element -file $outName/SectionCurvature18.out -time -ele 1 section 8 deformation
     recorder Element -file $outName/SectionMoment18.out    -time -ele 1 section 8 force
     recorder Element -file $outName/SectionCurvature19.out -time -ele 1 section 9 deformation
     recorder Element -file $outName/SectionMoment19.out    -time -ele 1 section 9 force
     pattern Plain 1 Linear {load $nTop 0.0 -326.496 0.0};
     constraints Plain;
     numberer Plain;
     system BandGeneral;
     test NormUnbalance 1e-6 75; 
     algorithm Newton;
     integrator LoadControl 0.1;
     analysis Static;
     analyze 10;
     loadConst -time 0.0;
     pattern Plain 200 Linear {load $nTop 1.0 0.0 -279.1339};
     set nodeTag $nTop;set dofTag 1;set Dtot 0;set stepCount 1;
     set Peak [list 0.1167 -0.1170 0.1199 -0.1168 0.2868 -0.2891 0.2936 -0.2909 0.6769 -0.6438 0.6612 -0.6362 0.9963 -0.9543 0.9996 -0.9550 1.3435 -1.2877 1.2971 -1.2879 1.9855 -1.9407 1.9736 -1.9414 2.6525 -2.5879 2.6720 -2.6030 4.0491 -3.7536];
     source ../../CyclicSolutionAlgorithm.tcl;
     wipeAnalysis;
     wipe;
}
incr count 1
};
