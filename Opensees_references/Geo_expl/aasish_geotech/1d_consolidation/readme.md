# 1D Consolidation
Original solution prepared by: Christopher McGann and Pedro Arduino, University of Washington

Please refer to the [original](https://opensees.berkeley.edu/wiki/index.php/One-dimensional_Consolidation) solution before starting with these script files. The original problem was solved using the Tcl scripting language, I have used OpenSeesPy. I have also created a Python script to plot the output as shown the in original solution. The analysis is no different than that presented above apart from node generation and plotting using Python instead of Matlab.

## Drawing the soil profile
The node numbers are not the same as shown in the original solution. Running the ``ex_g_01_create_soillayer.py`` will generate the soil profile showing node numbering. I have included the output of the script which is a ``.svg`` file and a ``.png`` file. One can use [Inkscape](https://inkscape.org/) to view and manipulate ``.svg`` files. I draw the ``.svg`` files using the [svgwrite](https://svgwrite.readthedocs.io/en/master/) package. Please refer to the documentation for installation and tutorials. 

## Scripts
1. ``ex_g_01_create_soillayer.py`` create soil profile
2. ``ex_g_01_1dconsolidation.py`` to solve 1D consolidation problem for single and double drainage. Select the drainage condition and the file path locations. All the file paths are hardcoded in the script. The paths are:
* 1d_consolidation - root folder
    * /data for all output of the scripts

    * /plt for all figures
* *.py - all scripts are under the root folder
