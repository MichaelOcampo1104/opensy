# PT strands material------------------------------------------------------
ops.uniaxialMaterial('ElasticPP',201,8.7799e10,0.0120,-0.0158,-0.0038)
ops.uniaxialMaterial('ElasticPP',202,9.0201e10,0.0089,-0.0127,-0.0038)
ops.uniaxialMaterial('Parallel',203,201,202)

# Frame base connection material--------------------------------------------
ops.uniaxialMaterial('ENT',301,1.0e9); # stiffness for vertical reaction

# Fuse model----------------------------------------------------------------
ops.uniaxialMaterial('SelfCentering',401,Kf1A,0.0,Kf1A*0.0005,0.0,0.0,0.0005,1.0e6); #Gap for bolt connection, fuse A

# for Fuse A-------------------
ops.uniaxialMaterial('Steel01', 414, Fuse_Yield, 373038000.0, 0.04, 0.06, 1.0, 0.0, 1.0)

# print("Materials created!")