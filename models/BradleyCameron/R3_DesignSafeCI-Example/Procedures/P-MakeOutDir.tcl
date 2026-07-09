# =========================================================================
# This procedure creates a directory on the path specified by input "dir", 
# overwriting the directory if it already exists. In addition, this proc.
# writes the analysis start time as 1) formatted date and 2) the number of 
# seconds since the epoch as the first two lines of a log file in "dir".

proc MakeOutDir {dir} {;#                           # begin procedure
   if {[file exist "$dir/"]==1} {;                  # if directory exists
   file delete -force -- "$dir/"};                  # delete it
   file mkdir $dir;                                 # make the directory
   set systemTime [clock seconds];                  # get the current time
   set fmt "%D-%H:%M:%S";                           # date format
   set D [clock format $systemTime -format $fmt];   # formatted date
   set startTime "Analysis Start Date: $D";         # start date and time
   WriteToLog $dir $startTime;                      # write to log file
   set sSec "Analysis Start Sec.: [clock seconds]"; # seconds since epoch
   WriteToLog $dir $sSec;                           # write to log file
};                                                  # end procedure
# =========================================================================