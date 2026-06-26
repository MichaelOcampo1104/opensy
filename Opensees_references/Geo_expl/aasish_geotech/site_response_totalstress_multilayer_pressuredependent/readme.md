# Total stress site response analysis of a layered soil column with pressure dependent soil properties

Ref: [Site Response Analysis of a Layered Soil Column (Total Stress Analysis)](https://opensees.berkeley.edu/wiki/index.php/Site_Response_Analysis_of_a_Layered_Soil_Column_(Total_Stress_Analysis))

Original authors: Christopher McGann and Pedro Arduino, University of Washington

I am just going create a Python version of the analysis and rest of the files. The original analysis including the soil profile generation was done in Tcl. MATLAB was used to generate plots, to integrate acceleration time history to velocity time history, and to create spectral acceleration plots. Please read the original solution page referenced above for details. The original authors of the analysis were as shown above. This is not a line by line conversion from ``.tcl`` to ``.py``. Some of the programming here may be more verbose and inefficient.

This is a work in progress. I will add files as and when I complete them. When I think this tutorial is complete I will check off all the items in the todo list below.

Corresponding Tcl file: freeFieldIndepend.tcl

# Steps
In general, the script files are in the project root directory, all input and output data are in the ``.\data`` and all the plots are in ``.\plt``. The examples files that were directly downloaded from the above website are in ``.\original_solution\downloaded\``. The example ``.tcl`` files and their outputs are in ``.\original_solution``. I may have modified the original ``.tcl`` analysis files by peppering it with print statements for comparison purpose.

This information is only for using ``.py`` script
1. Start by creating a ``ndmat_autogen_multiyield_pressuredependent_layers.csv`` file. This has layer information for all the layers.
2. If the directory structure has not been changed then running ``ex_g_02_siteresponse_totalstress_multilayer_pressuredependent.py`` should produce the output files.
3. To plot the ground motions at the top of the soil layer, run ``plt_output_groundmotion.py``. Currently this file also reads the output from the original analysis to compare the results.

## Things to do:
- [x] for multilayer soil profile create a spreadsheet with layer properties, saved as .cvs file.
- [x] function to generate nodes for four node quad elements given the layer thickness and the maximum element size
- [x] the code is working, however there are some remnants from the single layer code that is providing some values, see if this can be made layer dependent too, for example while creating soil elements the wgt_y can be made layer dependent for layers with different densities
- [x] visualize the response ground motion by plotting acceleration, velocity and displacement time histories
- [x] plot acceleration, velocity and displacement response spectra
- [x] plot acceleration, velocity and displacement along depth for the timestep when maximum acceleration occurs on the surface
- [x] plot acceleration, velocity and displacement spectrum for a column of nodes at all timesteps
- [ ] find out if the same analysis can be performed using Deepsoil and compare the results
- [ ] clean up of code, remove unnecessary parts from single layer example


# Git branch
Branch from master to refine the multi-layer total stress site response analysis.
1. ``git branch mltssra``
2. ``git checkout mltssra``
Once in the branch ``add`` and ``commit`` as usual to the branch
3. ``git add file``
4. ``git commit -m 'message'``
To merge a branch to the master, first checkout master and then merge
5. ``git checkout master``
6. ``git merge mltssra``
The branch can be deleted
7. ``git branch -d mltssra``
