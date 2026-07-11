#set SpecID 1
set LoadStage 0
for {set Stage 0} {$Stage <= $LoadStage} {incr Stage} {
    puts "Analyzing Stage $Stage..."
    source $dir_loading/LoadingParameterCB33D-S$Stage.tcl   
    RunStaticLoading [expr $Stage+200] 4 2 $LoadType $LoadHistory $Dincr $numIter $Tol $ControlMethod
    puts "Stage $Stage done"
}
