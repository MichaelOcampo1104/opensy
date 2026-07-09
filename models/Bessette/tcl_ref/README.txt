Example Numerical Model OpenSees/
│
├── README.txt                             # Main explanation file
├── DGC/									# Results/recorders for analysis with DGCs
├── NM/									# Results/recorders for analysis without mitigation
├── elementsNM.tcl							# OpenSEES MP files
├── id48_NM.png
├── idCf=48_idgm=225_MP_mainNM.tcl
├── idCf=48_idgm=225_MP_mainStructPushoverNM.tcl
├── nodesNM.tcl
├── recorderNM.tcl
├── recorderNMDiff.tcl
├── recorderNMtcl
├── elementsDGC.tcl
├── id48_DGC.png
├── idCf=48_idgm=225_MP_mainDGC.tcl
├── idCf=48_idgm=225_MP_mainStructPushover.tcl
├── nodesDGC.tcl
├── recorderDGC.tcl
├── recorderDGCDiff.tcl
├── recorderDGCtcl
├── OutcropMotions/
│    ├── (acceleration and velocity time histories for all outcrop rock ground motions (GMs))
├── WithinMotions/
│    ├── (acceleration time histories for all within motions obtained from 1D single column site response analysis with elastic half-space)
├── README.txt

### Notes
- 'idCf': Model configurations (e.g., soil properties, structural parameters, mitigation, foundation)
- 'idgm' or 'GM': Ground motions used in the simulations

