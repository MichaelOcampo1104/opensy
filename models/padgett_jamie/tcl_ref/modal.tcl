# Procedure to calculate the periods and eigen vectors of a bridge
#
proc ModalAnalysis { nModes name } {

   #Wipe the analysis
   wipeAnalysis

   #Perform Eigen Value analysis
   set eigenvalues [eigen $nModes]
   puts $eigenvalues

   #Create .eig file
   set _fID [open $name/$name.eig w]
   
   #Open the temp files
   for {set jjj 0} {$jjj < $nModes} {incr jjj 1} {
       
       set tempPeriod [expr 2*3.1416/sqrt([lindex $eigenvalues $jjj])] ; # calculating the period in seconds
       puts "here1"
       puts $_fID "$tempPeriod"
  }

   #Close the .eig File
   close $_fID   
   
}


