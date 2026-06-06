# =========================================================================
# This procedure write the string defined by "txt" to the output file "f"
# located in the directory "dir". The string "txt" will also be printed to
# the console by default, but this behavior can be suppressed by setting 
# the "print" input to 0. 

proc WriteToLog {dir txt {f "Logfile"} {print 1}} {;# begin procedure
   set checkgrav [string first "gravity" "$dir"];   # check if gravity file
   if {$checkgrav != -1} {;                         # if not gravity dir.
      set done [file exists "$dir-DONE/"];          # check analysis done
   } else {;                                        # if gravity dir.
      set done 0;                                   # analysis not done
   };                                               # end if
   if {$done == 0} {;                               # if analysis not done
      file mkdir $dir;                              # make output dir.
      set outFilename "$dir/$f.txt";                # output file
      set outFileID [open $outFilename "a"];        # open file (append)
      puts $outFileID $txt;                         # append to file
      close $outFileID;                             # close file
      if {$print != 0} {;                           # if print is not 0
         puts stdout $txt;                          # print to console
      };                                            # end if
   };                                               # end if
};                                                  # end procedure
# =========================================================================