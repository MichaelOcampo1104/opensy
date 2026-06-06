# =========================================================================   
# This script is used to analyze the response of building models to various
# loading types, including gravity, pushover, and groundmotion. The model 
# and analysis framework is based on the work by Sizemore (2017); 
# however, a number of changes and modifications have been implemented.    

## Define relevant system paths
set root [pwd];                                     # root directory
set gmdir "$root/GroundMotions";                    # ground motions dir.
set bld "B";                                        # building model prefix
set bldPath "$root/BuildingAnalysis/$bld";          # analysis files dir.
set prc "$root/Procedures/";                        # procedure directory
foreach f [glob -dir "$prc" *.tcl] {source $f};     # source procedures

## Set analysis variables based on user input
set sN       "1-R3";                                # system name
set dampType "Rayleigh";                            # "Rayleigh" or "Modal"
set recType  "S";                                   # "All" or "Select"
set itr      20;                                    # number of iterations
set Lszfs    "5_10_20";                             # list of step factors
set Ltols    "1e-08_1e-07_1e-06_1e-05";             # list of tolerances
set SOE      "UmfPack";                             # SOE solver
set aType    "groundmotion";                        # analysis type

## Define paths and switch to current directory
set input "OpenSees/Input";                         # OpenSees input dir.
set recFile "$bld-Recorders-$recType.tcl";          # recorder file
set in "$root";                                     # working directory
cd $in; source "$bld-SystemParameters.tcl";         # system parameters  

## Run the analysis
switch $aType \
  "gravity" {
   source "$bldPath-GravityAnalysis.tcl";           # run the analysis
} "pushover" {
   set pType "monotonic";                           # drift protocol type
   source "$bldPath-PushoverAnalysis.tcl";          # run the analysis
} "groundmotion" {
   set gmmin 1;                                     # first ground motion
   set gmmax 1;                                     # last ground motion
   set sfmin 0.2;                                   # first scale factor
   set sfinc 0.2;                                   # scale factor incr.
   set sfmax 0.2;                                   # last scale factor
   source "$bldPath-GroundmotionAnalysis.tcl";      # run the analysis
};                                                  # end switch
# =========================================================================