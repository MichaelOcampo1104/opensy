# Total stress site response analysis of a layered soil column

Ref: [Site Response Analysis of a Layered Soil Column (Total Stress Analysis)](https://opensees.berkeley.edu/wiki/index.php/Site_Response_Analysis_of_a_Layered_Soil_Column_(Total_Stress_Analysis))

Authors: Christopher McGann and Pedro Arduino, University of Washington

I am just going create a Python version of the analysis and rest of the files. The original analysis including the soil profile generation was done in Tcl. MATLAB was used to generate plots, to integrate acceleration time history to velocity time history, and to create spectral acceleration plots. Please read the original solution page referenced above for details. The original authors of the analysis were as shown above. This is not a line to line conversion from ``.tcl`` to ``.py``. Some of the programming here may be more verbose or inefficient.

This is work in progress. I will add files as and when I complete them. When I think this tutorial is complete I will check off all the items in the todo list below. This is the multilayer soil profile with pressure independent material.

Corresponding Tcl file: freeFieldIndepend.tcl

# Steps
In general, the script file are in the project root directory, all input and output data are in the ``.\data`` and all the plots are in ``.\plt``. The examples files that were directly downloaded from the above website are in ``.\original_solution\downloaded\``. The example ``.tcl`` file and their outputs are in ``.\original_solution``. I may have modified the ``.tcl`` analysis file found in this folder by peppering it with print statements for comparison purpose.

This information is only for using ``.py`` script
1. Start by creating a ``ndmat_multiyield_pressureindependent_layers.csv`` file. This has layer information for all the layers.
2. The shear modulus reduction curve is specified by user, pairs of shear strain and modulus reduction ratio is given in the script.
3. Run the script ``ex_g_02_siteresponse_totalstress_multilayer_pressureindependent.py`` for analysis.
4. Use ``response_spectra.py``, ``depth_profiles.py``, and ``depth_spectrum.py`` to create data files for respective plots. Use the plotting scripts for generating the plots.

## Things to do:
- [x] for multilayer soil profile create a spreadsheet with layer properties, this file can be saved as .xls file. Also save a .csv version to be read by the Python script
- [x] function to generate nodes for four node quad elements given the layer thickness and the maximum element size
- [ ] the code is working, however there are some remnants from the single layer code that is providing some values, see if this can be made layer dependent too, for example while creating soil elements the wgt_y can be made layer dependent for layers with different densities
- [x] visualize the response ground motion by plotting acceleration, velocity and displacement time histories
- [x] plot acceleration, velocity and displacement response spectra
- [ ] my version of Nigam and Jennings does not work, needs work so do not use that. Use the *EQSIG* version.
- [x] plot acceleration, velocity and displacement along depth for the timestep when maximum acceleration occurs on the surface
- [x] plot acceleration, velocity and displacement spectrum for a column of nodes at all timesteps, colormap.
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
