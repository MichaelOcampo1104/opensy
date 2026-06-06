# Define beam hinge force-deformation recorders


cd	$baseDir/$dataDir/BeamHingeMoment

# X-Direction beam hinge element force recorders
recorder	Element	-file	BeamHingeForcesLevel2.out	-time	-ele	7121115	7220913	7221115	7320913	7321115	7420913	force;
recorder	Element	-file	BeamHingeForcesLevel3.out	-time	-ele	7131115	7230913	7231115	7330913	7331115	7430913	force;
recorder	Element	-file	BeamHingeForcesLevel4.out	-time	-ele	7141115	7240913	7241115	7340913	7341115	7440913	force;
recorder	Element	-file	BeamHingeForcesLevel5.out	-time	-ele	7151115	7250913	7251115	7350913	7351115	7450913	force;
recorder	Element	-file	BeamHingeForcesLevel6.out	-time	-ele	7161115	7260913	7261115	7360913	7361115	7460913	force;
recorder	Element	-file	BeamHingeForcesLevel7.out	-time	-ele	7171115	7270913	7271115	7370913	7371115	7470913	force;
recorder	Element	-file	BeamHingeForcesLevel8.out	-time	-ele	7181115	7280913	7281115	7380913	7381115	7480913	force;
recorder	Element	-file	BeamHingeForcesLevel9.out	-time	-ele	7191115	7290913	7291115	7390913	7391115	7490913	force;
recorder	Element	-file	BeamHingeForcesLevel10.out	-time	-ele	71101115	72100913	72101115	73100913	73101115	74100913	force;

cd	$baseDir/$dataDir/BeamHingeDeformations

# X-Direction beam hinge deformation recorders
recorder	Element	-file	BeamHingeForcesLevel2.out	-time	-ele	7121115	7220913	7221115	7320913	7321115	7420913	deformation;
recorder	Element	-file	BeamHingeForcesLevel3.out	-time	-ele	7131115	7230913	7231115	7330913	7331115	7430913	deformation;
recorder	Element	-file	BeamHingeForcesLevel4.out	-time	-ele	7141115	7240913	7241115	7340913	7341115	7440913	deformation;
recorder	Element	-file	BeamHingeForcesLevel5.out	-time	-ele	7151115	7250913	7251115	7350913	7351115	7450913	deformation;
recorder	Element	-file	BeamHingeForcesLevel6.out	-time	-ele	7161115	7260913	7261115	7360913	7361115	7460913	deformation;
recorder	Element	-file	BeamHingeForcesLevel7.out	-time	-ele	7171115	7270913	7271115	7370913	7371115	7470913	deformation;
recorder	Element	-file	BeamHingeForcesLevel8.out	-time	-ele	7181115	7280913	7281115	7380913	7381115	7480913	deformation;
recorder	Element	-file	BeamHingeForcesLevel9.out	-time	-ele	7191115	7290913	7291115	7390913	7391115	7490913	deformation;
recorder	Element	-file	BeamHingeForcesLevel10.out	-time	-ele	71101115	72100913	72101115	73100913	73101115	74100913	deformation;

