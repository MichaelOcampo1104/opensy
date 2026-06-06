# =========================================================================
# This script is used to define the model nodes, elements, materials, etc. 

## Define basic model parameters
wipe;                                               # clear past model
model BasicBuilder -ndm 2 -ndf 3;                   # 2-D, 3 DOF (1,2,6)
geomTransf PDelta 1;                                # beams and columns
geomTransf Corotational 2;                          # braces

## Source files to define the model
set filenames [list "Nodes" "Constraints" \
   "Materials" "Sections" "Elements"];              # define files list
foreach filename $filenames {;                      # for each file
   if {[file exists "$bld-$filename.tcl"] == 1} {;  # if file exists
      source "$bld-$filename.tcl";                  # source the file
   };                                               # end if
};                                                  # end foreach
# =========================================================================