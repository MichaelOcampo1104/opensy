# =========================================================================   
# This script is used to analyze the response of building models to various
# loading types, including gravity, pushover, and groundmotion. The model 
# and analysis framework is based on the work by Sizemore 2017; 
# however, a number of changes and modifications have been implemented.    

## Define relevant system paths
regsub {(.*)/Buildings.+} [pwd] {\1} root;          # root directory
set gmdir "$root/Buildings/GroundMotions";          # ground motions dir.
set bld "B";                                        # building model prefix
set bldPath "$root/Buildings/OpenSees/$bld";        # analysis files dir.
set prc "$root/SharedFiles/OpenSees/Procedures/";   # procedure directory
foreach f [glob -dir "$prc" *.tcl] {source $f};     # source procedures

## Set analysis variables based on user input
set sN       [lindex $argv 0];                      # system name
set dampType [lindex $argv 1];                      # "Rayleigh" or "Modal"
set recType  [lindex $argv 2];                      # "All" or "Select"
set itr      [lindex $argv 3];                      # number of iterations
set Lszfs    [lindex $argv 4];                      # list of step factors
set Ltols    [lindex $argv 5];                      # list of tolerances
set SOE      [lindex $argv 6];                      # SOE solver
set aType    [lindex $argv 7];                      # analysis type

## Define paths and switch to current directory
set input "OpenSees/Input";                         # OpenSees input dir.
set recFile "$bld-Recorders-$recType.tcl";          # recorder file
set in "$root/Buildings/Systems/$sN/$input";        # working directory
cd $in; source "$bld-SystemParameters.tcl";         # system parameters  

## Run the analysis
switch $aType \
  "gravity" {
   source "$bldPath-GravityAnalysis.tcl";           # run the analysis
} "pushover" {
   set pType [lindex $argv 8];                      # drift protocol type
   source "$bldPath-PushoverAnalysis.tcl";          # run the analysis
} "groundmotion" {
   set gmmin [lindex $argv 8];                      # first ground motion
   set gmmax [lindex $argv 9];                      # last ground motion
   set sfmin [lindex $argv 10];                     # first scale factor
   set sfinc [lindex $argv 11];                     # scale factor incr.
   set sfmax [lindex $argv 12];                     # last scale factor
   source "$bldPath-GroundmotionAnalysis.tcl";      # run the analysis
};                                                  # end switch
# =========================================================================