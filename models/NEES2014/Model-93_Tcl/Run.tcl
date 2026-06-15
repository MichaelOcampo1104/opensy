# READ EQ INFORMATION FILE 

set path "InputExcitations"
set fid [open $path/inf.txt r];
set j 1

foreach line [split [read $fid] \n] {
	set EQ_NAME($j)  [lindex $line 0];
	set EQ_DT($j)    [lindex $line 1];
	set EQ_NPT($j)   [lindex $line 2];
	set EQ_SF($j)    [lindex $line 3];

 	incr j 1;
}
close $fid; unset j;

# RUNNING

set gACC 386;
set nStory 4; 
# EQ 1-44
for {set EQ 1} {$EQ <= 10} {incr EQ 1} {

	set out_dir "UnprocessedOutput/[expr $EQ]";
	file mkdir $out_dir;	file mkdir "$out_dir";	
	set fid_DA [open $out_dir/Analysis_Check.txt w];
	
	
	# -- Sounding EQ Properties --
	set EQ_Record "$path/SortedEQFile_$EQ_NAME($EQ).txt"
	set dt 	$EQ_DT($EQ);
	set NPT	$EQ_NPT($EQ);
	set PGA	$EQ_SF($EQ);

	set		step	1
	source	ModelComponents/Model.tcl; 
	set		GMfact		$gACC;
	set		Scale	[expr $PGA];
	source	ModelComponents/Analysis_Dynamic.tcl
	puts $fid_DA [list "Ground_Motion" $EQ "Done" ];

	
	close $fid_DA
	wipe;
};
	
