# Total stress site response analysis of a layered soil column

Ref: [Site Response Analysis of a Layered Soil Column (Total Stress Analysis)](https://opensees.berkeley.edu/wiki/index.php/Site_Response_Analysis_of_a_Layered_Soil_Column_(Total_Stress_Analysis))

Authors: Christopher McGann and Pedro Arduino, University of Washington

I am just going create a Python version of the anslysis and rest of the files. The original analysis including the soil profile generation was done in Tcl. Matlab was used to generate plots and to integrate acceleration time history to velocity time history and to create spectral acceleration plots. Please read the original solution page referenced above for details. The original authors of the analysis were as shown above.

This is work in progress. I will add files as and when I complete them. When I think this tutorial is complete I will check off all the items in the todo list below.

## Things to do:
- [x] function to generate nodes for four node quad elements
- [x] function to create 4nodequad elements from the nodes
- [x] script to convert PEER database groundmotions from acceleration to velocity
- [x] script to plot PEER ground motion
- [x] check to see if the acceleration to velocity conversion is the same as that from the origin MATLAB script
- [x] script to compute spectral accelerations, velocities and displacements using frequency domain analysis
- [ ] script to compute spectral values using time domain (Nigam and Jennings 1969) integration, this does not work, the velocity spectrum is incorrect. The [eqsig](https://pypi.org/project/eqsig/) package can be used to compute spectral values using time domain analysis, the package uses the Nigam and Jennings (1969) time integration method. Please refer to the example in the linked page to compute response spectra. You may refer to the package [documentation](https://eqsig.readthedocs.io/en/latest/index.html) for installation instructions
- [ ] get the main analysis script to run without error with 'Newton' method.  The python version looks the same as the Tcl example version but the ``.py`` cannot converge during dynamic analysis. With the help from [otaithleigh](https://github.com/otaithleigh), I was able to solve the issue by modifying the two following lines: ``ops.test("NormDispIncr", 1.0e-5, 50, 5)  ops.algorithm("KrylovNewton")``. The question remains why ``.tcl`` version works with  ``ops.test("NormDispIncr", 1.0e-3, 15, 5)  ops.algorithm("Newton")`` and the ``.py`` model does not, even when they are (I think) the exact same model.

## Branches
- master
- ts_sitereponse (deleted after merge)

## Git notes
This is my way of learning ``git``. But, I keep forgetting what I learn, so this is just notes to myself. I have created a branch ``ts_sitereponse`` so make sure that branch is checked out and push changes to that branch and when the analysis is complete push changes to ``master``.

Root of the git directory
``openseespy_examples``

Create a branch
``git branch ts_siteresponse``

Checkout a branch
``git checkout ts_siteresponse``

or both in one command
``git checkout -b ts_siteresponse``

See all the branches, the current checked out branch will have ``*`` in front of it
``git branch -a``

To push the branch to the remote repository for the first time. This ensures tracking connections between local and remote are established.
``git push -u origin ts_siteresponse``
