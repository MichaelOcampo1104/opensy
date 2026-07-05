OutputAddss = 'Structural Model/Outputs'
os.makedirs(OutputAddss, exist_ok = True)

# Fuse shear deformation
ops.recorder('Node', '-file', OutputAddss+'/disp2011.out','-time','-node',2011,'-dof',1,2,3,'disp')
ops.recorder('Node', '-file', OutputAddss+'/disp2051.out','-time','-node',2051,'-dof',1,2,3,'disp')

# Roof displacement
ops.recorder('Node', '-file', OutputAddss+'/disp604.out','-time','-node',604,'-dof',1,2,3,'disp')

# strand forces
ops.recorder('Element', '-file', OutputAddss+'/Strand1.out','-time','-ele',6011,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Strand2.out','-time','-ele',6051,'localForce')

# Column forces
ops.recorder('Element', '-file', OutputAddss+'/Element1.out','-time','-ele',1001,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element2.out','-time','-ele',1002,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element3.out','-time','-ele',1004,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element4.out','-time','-ele',1021,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element5.out','-time','-ele',1022,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element6.out','-time','-ele',1024,'localForce')

ops.recorder('Element', '-file', OutputAddss+'/Element7.out','-time','-ele',1201,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element8.out','-time','-ele',1202,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element9.out','-time','-ele',1204,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element10.out','-time','-ele',1221,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element11.out','-time','-ele',1222,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element12.out','-time','-ele',1224,'localForce')

ops.recorder('Element', '-file', OutputAddss+'/Element13.out','-time','-ele',1401,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element14.out','-time','-ele',1402,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element15.out','-time','-ele',1404,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element16.out','-time','-ele',1421,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element17.out','-time','-ele',1422,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element18.out','-time','-ele',1424,'localForce')

# Beam forces
ops.recorder('Element', '-file', OutputAddss+'/Element19.out','-time','-ele',3101,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element20.out','-time','-ele',3102,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element21.out','-time','-ele',3104,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element22.out','-time','-ele',3121,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element23.out','-time','-ele',3122,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element24.out','-time','-ele',3124,'localForce')

ops.recorder('Element', '-file', OutputAddss+'/Element25.out','-time','-ele',3301,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element26.out','-time','-ele',3302,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element27.out','-time','-ele',3304,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element28.out','-time','-ele',3321,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element29.out','-time','-ele',3322,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element30.out','-time','-ele',3324,'localForce')

ops.recorder('Element', '-file', OutputAddss+'/Element31.out','-time','-ele',3501,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element32.out','-time','-ele',3502,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element33.out','-time','-ele',3504,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element34.out','-time','-ele',3521,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element35.out','-time','-ele',3522,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element36.out','-time','-ele',3524,'localForce')

# Brace forces
ops.recorder('Element', '-file', OutputAddss+'/Element37.out','-time','-ele',5001,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element38.out','-time','-ele',5021,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element39.out','-time','-ele',5041,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element40.out','-time','-ele',5061,'localForce')

ops.recorder('Element', '-file', OutputAddss+'/Element41.out','-time','-ele',5201,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element42.out','-time','-ele',5221,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element43.out','-time','-ele',5241,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element44.out','-time','-ele',5261,'localForce')

ops.recorder('Element', '-file', OutputAddss+'/Element45.out','-time','-ele',5401,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element46.out','-time','-ele',5421,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element47.out','-time','-ele',5441,'localForce')
ops.recorder('Element', '-file', OutputAddss+'/Element48.out','-time','-ele',5461,'localForce')

# print("Rcorders defined!")