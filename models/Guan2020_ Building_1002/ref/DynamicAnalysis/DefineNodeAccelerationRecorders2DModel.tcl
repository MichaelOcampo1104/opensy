# Define node acceleration recorders


cd $baseDir/$dataDir/EQ_$eqNumber/Scale_$scale/NodeAccelerations

recorder	Node	-file	NodeAccLevel1.out	-timeSeries	2	-time	-node	1110	2110	3110	4110	-dof	1	accel;
recorder	Node	-file	NodeAccLevel2.out	-timeSeries	2	-time	-node	1211	2211	3211	4211	-dof	1	accel;
recorder	Node	-file	NodeAccLevel3.out	-timeSeries	2	-time	-node	1311	2311	3311	4311	-dof	1	accel;
recorder	Node	-file	NodeAccLevel4.out	-timeSeries	2	-time	-node	1411	2411	3411	4411	-dof	1	accel;
recorder	Node	-file	NodeAccLevel5.out	-timeSeries	2	-time	-node	1511	2511	3511	4511	-dof	1	accel;
recorder	Node	-file	NodeAccLevel6.out	-timeSeries	2	-time	-node	1611	2611	3611	4611	-dof	1	accel;
recorder	Node	-file	NodeAccLevel7.out	-timeSeries	2	-time	-node	1711	2711	3711	4711	-dof	1	accel;
recorder	Node	-file	NodeAccLevel8.out	-timeSeries	2	-time	-node	1811	2811	3811	4811	-dof	1	accel;
recorder	Node	-file	NodeAccLevel9.out	-timeSeries	2	-time	-node	1911	2911	3911	4911	-dof	1	accel;
recorder	Node	-file	NodeAccLevel10.out	-timeSeries	2	-time	-node	11011	21011	31011	41011	-dof	1	accel;
