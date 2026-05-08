import openseespy.opensees as ops
import random
from pint import UnitRegistry
import time
import numpy as np
import math

ureg = UnitRegistry()

m = 1.0
kN = 1.0
sec = 1.0

# Length
mm = m / 1000.0
cm = m / 100.0
inch = 25.4 * mm
ft = 12.0 * inch

# Force
N = kN / 1000.0
kips = kN * 4.448221615
lb = kips / 1.0e3

# Stress (kN/m2 or kPa)
Pa = N / (m ** 2)
kPa = Pa * 1.0e3
MPa = Pa * 1.0e6
GPa = Pa * 1.0e9
ksi = 6.8947573 * MPa
psi = 1e-3 * ksi

# Mass - Weight
tonne = kN * sec ** 2 / m
kg = N * sec ** 2 / m
lb = psi*inch**2

# Gravitational acceleration
g = 9.81*m/sec**2

# Time
min = 60*sec
hr = 60*min 

#Common Material Steel
Es = 210*GPa
Fy_s355 = 355*MPa
Fy_s275 = 275*MPa

#Common Material Concrete
E_c30 = 31476*MPa


# Earthquake Constatant 
iv0 = 0.005*mm                   # [mm] Initial velocity applied to the node
st_iv0 = 0.0*sec                  # [s] Initial velocity applied starting time
GMfact = 1                    # GMfact = 9810 # standard acceleration of gravity or standard acceleration 
lin_tstag = 1
conts_tstag = 2
path_tstag = 3

def analysisLoopBasic(ok, nn, Size):
    """
    The load control analysis loops.
    """
    
    if ok != 0:
        print("Trying 5 times smaller timestep at load factor", nn)
        ops.integrator("LoadControl", Size/5)
        ok = ops.analyze(1)

    if ok != 0:
        print("Trying 20 times smaller timestep at load factor", nn)
        ops.integrator("LoadControl", Size/20)
        ok = ops.analyze(1)        
        
    if ok != 0:
        print("Trying 80 times smaller timestep at load factor", nn)
        ops.integrator("LoadControl", Size/80)
        ok = ops.analyze(1)       
        
    if ok != 0:
        print("Trying 160 times smaller timestep at load factor", nn)
        ops.integrator("LoadControl", Size/160)
        ok = ops.analyze(1)
        
    if ok != 0:
        print("Trying 200 interations at load factor", nn)
        ops.test('NormDispIncr', 1.*10**-8, 200)
        ok = ops.analyze(1)
        
    if ok != 0:
        print("Trying ModifiedNewton at load factor", nn)
        ops.algorithm("ModifiedNewton")
        ops.test('NormDispIncr', 1.*10**-8, 200)
        ok = ops.analyze(1)

    ops.test('NormDispIncr', 1.*10**-8, 50)
    ops.integrator("LoadControl", Size)
    ops.algorithm("Newton")
    return ok

def analysisLoopDisp(ok, nn, dx, ControlNode, ControlNodeDof):
    """
    The displacement control analysis loops.
    """
    
    if ok != 0:
        print("Trying 5 times smaller timestep at step", nn)
        ops.integrator('DisplacementControl', ControlNode, ControlNodeDof, dx/5)
        ok = ops.analyze(1)

    if ok != 0:
        print("Trying 20 times smaller timestep at step", nn)
        ops.integrator('DisplacementControl', ControlNode, ControlNodeDof, dx/20)
        ok = ops.analyze(1)        
        
    if ok != 0:
        print("Trying 80 times smaller timestep at step", nn)
        ops.integrator('DisplacementControl', ControlNode, ControlNodeDof, dx/80)
        ok = ops.analyze(1)       
        
    if ok != 0:
        print("Trying 160 times smaller timestep at step", nn)
        ops.integrator('DisplacementControl', ControlNode, ControlNodeDof, dx/160)
        ok = ops.analyze(1)

    if ok != 0:
        print("Trying 1000 times smaller timestep at step", nn)
        ops.integrator('DisplacementControl', ControlNode, ControlNodeDof, dx/1000)
        ok = ops.analyze(1)

                
    if ok != 0:
        print("Trying ModifiedNewton at load factor", nn)
        ops.algorithm("ModifiedNewton")
        ops.test('NormDispIncr', 1.*10**-6, 200)
        ok = ops.analyze(1)

    ops.integrator('DisplacementControl', ControlNode, ControlNodeDof, dx)
    ops.algorithm("Newton")
    ops.test('NormDispIncr', 1.*10**-10, 50)
    return ok


def analysisLoopArc(ok, nn, Size):
    scaleF = 0 # the force scale 
    if ok != 0:
        print("Trying 5 times smaller timestep at load factor", nn)
        # ops.integrator('ArcLength', Size/5, scaleF / 5)
        ops.integrator("ArcLength", Size/5, scaleF)
        ok = ops.analyze(1)
        
    if ok != 0:
        print("Trying 20 times smaller timestep at load factor", nn)
        # ops.integrator('ArcLength', Size/20, scaleF / 20)
        ops.integrator('ArcLength', Size/20, scaleF)
        ok = ops.analyze(1)        
        
    if ok != 0:
        print("Trying 80 times smaller timestep at load factor", nn)
        # ops.integrator('ArcLength', Size/80, scaleF / 80)
        ops.integrator('ArcLength', Size/80, scaleF)
        ok = ops.analyze(1)        
        
    if ok != 0:
        print("Trying 160 times smaller timestep at load factor", nn)
        # ops.integrator('ArcLength', Size/160, scaleF / 160)
        ops.integrator('ArcLength', Size/160, scaleF)
        ok = ops.analyze(1)
        
    if ok != 0:
        print("Trying 1000 times smaller timestep at load factor", nn)
        # ops.integrator('ArcLength', Size/1000, scaleF / 1000)
        ops.integrator('ArcLength', Size/1000, scaleF)
        ok = ops.analyze(1)

    if ok != 0:
        print("Trying increasing the number of iterations to 200", nn)
        ops.test('NormDispIncr', 1.*10**-8, 200)
        ok = ops.analyze(1)
        
    if ok != 0:
        print("Trying 5000 times smaller timestep at load factor", nn)
        # ops.integrator('ArcLength', Size/1000, scaleF / 1000)
        ops.integrator('ArcLength', Size/5000, scaleF)
        ok = ops.analyze(1)
        
    if ok != 0:
        print("Trying 20000 times smaller timestep at load factor", nn)
        # ops.integrator('ArcLength', Size/1000, scaleF / 1000)
        ops.integrator('ArcLength', Size/20000, scaleF)
        ok = ops.analyze(1)

        
    if ok != 0:
        print("Trying 500000 times smaller timestep at load factor", nn)
        # ops.integrator('ArcLength', Size/50000, scaleF / 50000)
        ops.integrator('ArcLength', Size/500000, scaleF)
        # ops.integrator('ArcLength', Size/160, scaleF)
        ok = ops.analyze(1)
                
    if ok != 0:
        print("Trying 200 interations at load factor", nn)
        ops.test('NormDispIncr', 1.*10**-8, 200)
        ok = ops.analyze(1)
                    
    # if ok != 0:
    #     print("Trying ModifiedNewton at load factor", nn)
    #     ops.algorithm("ModifiedNewton")
    #     ops.test('NormDispIncr', 1.*10**-8, 200)
    #     ok = ops.analyze(1)
        
    ops.test('NormDispIncr', 1.*10**-12, 50)
    ops.integrator('ArcLength', Size, scaleF)
    ops.algorithm("Newton")
    # ops.algorithm('Broyden')

    return ok


# =============================================================================
# Load Control Analysis Types
# =============================================================================


def PushoverLcF(Nsteps):

    """
    Load control with force - not super useful because it can't get pas the load peak'
    """    

    ControlNode = 4
    ControlNodeDof = 1
    dForce = 1.*kN
    
    # Define time series
    #  timeSeries('Constant', tag, '-factor', factor=1.0)
    ops.timeSeries('Constant',1)
    ops.timeSeries('Linear', 2)
    
    # define loads
    ops.pattern('Plain',1 , 2)
    ops.load(ControlNode, dForce, 0., 0.)
    
    # Define Analysis Options
    # create SOE
    ops.system("BandGeneral")
    # create DOF number
    ops.numberer("Plain")
    # create constraint handler
    ops.constraints("Transformation")
    # create integrator
    ops.integrator("LoadControl", 1.0)
    # create algorithm
    ops.algorithm("Newton")
    # create analysis object
    ops.analysis("Static")

    # Create Test
    ops.test('NormDispIncr', 1.*10**-10, 50)
    
    # Run Analysis
    
    ops.record()
    ok = ops.analyze(Nsteps)


def PushoverLcD(dispMax, du = 0.00001*m):
    
    """
    Load control with displacement - easy to understand but will not preserve the initial load distribution if
    multiple 'sp' constraints are used on the structure.
    """        
    
    ControlNode = 4
    ControlNodeDof = 1
    
    # Define time series
    ops.timeSeries('Constant',1)
    ops.timeSeries('Linear', 2)
    
    # define loads
    ops.pattern('Plain',1 , 2)
    ops.sp(ControlNode, ControlNodeDof, du) # we will linearly increase increase displacement this step size
    
    
    # Define Analysis Options
    # create SOE
    ops.system("BandGeneral")
    # create DOF number
    ops.numberer("Plain")
    # create constraint handler
    ops.constraints("Transformation")
    # create integrator
    ops.integrator("LoadControl", 1)
    # create algorithm
    ops.algorithm("Newton")
    # create analysis object
    ops.analysis("Static")

    # Create Test
    ops.test('NormDispIncr', 1.*10**-8, 50)
    
    # Run Analysis
    ops.record()
    StepSize = .1
    nn = 0
    while(ops.nodeDisp(ControlNode, ControlNodeDof) < dispMax  ):       
    
        ok = ops.analyze(1)
        
        if ok != 0:
            ok = analysisLoopBasic(ok, nn, StepSize)
            
        if ok != 0:
            print("Analysis failed at load factor:", nn)
            break
        nn =+ 1
                
    print()
    print("# Analysis Complete #")
    

def CyclicAnalysisLc(dispMax, fileName = 'protocols/Ganey_small.thf'):
    
    """
    Load control with displacement - easy to understand but will not preserve the initial load distribution if
    multiple 'sp' constraints are used on the structure.
    """             
    
    ControlNode = 4
    ControlNodeDof = 1
    du = 1.0*m
    
    # Define time series
    #  timeSeries('Constant', tag, '-factor', factor=1.0)
    ops.timeSeries('Constant',1)
    ops.timeSeries('Linear', 2)
    ops.timeSeries('Path',3,  '-dt', 1.0, '-filePath', fileName ,  '-factor',  1.,  '-prependZero')
    
    # define loads
    ops.pattern('Plain',1 , 3)
    ops.sp(ControlNode, ControlNodeDof, du)
    
    
    StepSize = .1
    
    # Define Analysis Options
    # create SOE
    ops.system("BandGeneral")
    # create DOF number
    ops.numberer("Plain")
    # create constraint handler
    ops.constraints("Transformation")
    # create integrator
    ops.integrator("LoadControl", StepSize, 1, StepSize, StepSize*100)
    # create algorithm
    ops.algorithm("Newton")
    # create analysis object
    ops.analysis("Static")
    # Create Test
    ops.test('NormDispIncr', 1.*10**-8, 50)
    
    # Run Analysis
    ops.record()
    print('start')
    nn = 0
    times = []
    LF = []
    while(ops.nodeDisp(ControlNode, ControlNodeDof) < dispMax  ):       
    
        ok = ops.analyze(1.)
        # print(ops.getTime())
        if ok != 0:
            ok = analysisLoopBasic(ok, nn, StepSize)
            
        if ok != 0:
            print("Analysis failed at load factor:", nn)
            break
        
        nn += 1
        times.append(ops.getTime())
        LF.append(ops.getLoadFactor(1))   
        
    print()
    print("# Analysis Complete #")
    return times, LF



# =============================================================================
# Displacement Control Analyses
# =============================================================================

def PushoverDcF(dispMax, du = 0.0002*m):
    
    """
    Displacement control with force. More finicky that force control but will handle most situations thrown at it.
    """            
    
    ControlNode = 4
    ControlNodeDof = 1
    dForce = 1*kN
    
    # Define time series
    #  timeSeries('Constant', tag, '-factor', factor=1.0)
    ops.timeSeries('Constant',1)
    # ops.timeSeries('Linear', 2)
    
    # define loads
    ops.pattern('Plain',1 , 1)
    ops.load(ControlNode, dForce, 0., 0.)
    # ops.sp(ControlNode, ControlNodeDof, du)

    # Define Analysis Options
    # create SOE
    ops.system("BandGeneral")
    # create DOF number
    ops.numberer("Plain")
    # create constraint handler
    ops.constraints("Transformation")
    # create integrator
    # ops.integrator("DisplacementControl", ControlNode, ControlNodeDof, du, 10, du/10000)
    ops.integrator('DisplacementControl', ControlNode, ControlNodeDof, du, 10, du/100, du*10)    
    
    # create algorithm
    ops.algorithm("Newton")
    # create analysis object
    ops.analysis("Static")
    # Create Test
    ops.test('NormDispIncr', 1.*10**-8, 50)
    
    # Run Analysis
    ops.record()   
    nn = 0
    times = []
    LF = []    
    
    while(ops.nodeDisp(ControlNode, ControlNodeDof) < dispMax  ):       
    
        ok = ops.analyze(1)
        
        # nn+=1
        if ok != 0:
            ok = analysisLoopDisp(ok, nn, du, ControlNode, ControlNodeDof)
        
        
        if ok != 0:
            print("Analysis failed at load factor:", nn)
            break            
            
        nn += 1
        times.append(ops.getTime())
        LF.append(ops.getLoadFactor(1))


def PushoverDcD(dispMax, du = 0.0001*m):
    
    """
    Displacement control with displacement. More finicky that force controll but will handle most situations thrown at it.
    Can capture load deterioration.
    """        
   
    ControlNode = 4
    ControlNodeDof = 1
    dForce = 1*kN
    
    # Define time series
    #  timeSeries('Constant', tag, '-factor', factor=1.0)
    ops.timeSeries('Constant',1)
    
    # define loads
    ops.pattern('Plain',1 , 1)
    # ops.load(ControlNode, dForce, 0., 0.)
    ops.sp(ControlNode, ControlNodeDof, 1.0)

    # Define Analysis Options
    # create SOE
    ops.system("BandGeneral")
    # create DOF number
    ops.numberer("Plain")
    # create constraint handler
    ops.constraints("Transformation")
    # create integrator
    ops.integrator("DisplacementControl", ControlNode, ControlNodeDof, du, 10, du/10000)
    # create algorithm
    ops.algorithm("Newton")
    # create analysis object
    ops.analysis("Static")

    # Create Test
    ops.test('NormDispIncr', 1.*10**-8, 50)
    
    # Run Analysis
    ops.record()   
    nn = 0
    times = []
    LF = []    
    
    while(ops.nodeDisp(ControlNode, ControlNodeDof) < dispMax  ):       
    
        ok = ops.analyze(1)
            
        if ok != 0:
            print("Analysis failed at load factor:", nn)
            break            
            
        nn += 1
        times.append(ops.getTime())
        LF.append(ops.getLoadFactor(1))




def CyclicAnalysisDcL(loadProtocol = [0.02,0.05], Nrepeat = [2,2], dx = 0.0001*m):
    
    """
    Displacement control with displacement. More finicky that force controll but will handle most situations thrown at it.
    Can capture load deterioration.
    Figures out what change in force is needed to get a specific input
    """      
    
    ControlNode = 4
    ControlNodeDof = 1
    dForce = 1*kN # the reference load
    
    # Define time series
    ops.timeSeries('Constant',1)

    # define loads
    ops.pattern('Plain',1 , 1)
    ops.load(ControlNode, dForce, 0., 0.)    
    
    # Define Analysis Options
    # create SOE
    ops.system("BandGeneral")
    # create DOF number
    ops.numberer("Plain")
    # create constraint handler
    ops.constraints("Transformation")
    # create algorithm
    ops.algorithm("Newton")
    # create analysis object
    ops.analysis("Static")
    # Create Test
    ops.test('NormDispIncr', 1.*10**-10, 50)
    
    # Run Analysis
    ops.record()
    print('start')
    nn = 0
    for x, Ncycle in zip(loadProtocol, Nrepeat):
        
        # If the load protocol uses, then upate this term with 
        for ii in range(Ncycle):            
            ops.integrator('DisplacementControl', ControlNode, ControlNodeDof, dx, 10, dx/1000, dx*10)
            while (ops.nodeDisp(ControlNode, ControlNodeDof) < x):
                ok = ops.analyze(1)
                nn+=1
                if ok != 0:
                    ok = analysisLoopDisp(ok, nn, dx, ControlNode, ControlNodeDof)
                if ok != 0:
                    print('Ending analysis')
                    ops.wipe()
                    return
                
            # The negative cycle.
            ops.integrator('DisplacementControl', ControlNode, ControlNodeDof, -dx, 10, -dx*10, -dx/1000)
            while (ops.nodeDisp(ControlNode, ControlNodeDof) > -x):
                ok = ops.analyze(1)
                nn+=1
                if ok != 0:
                    ok = analysisLoopDisp(ok, nn, -dx, ControlNode, ControlNodeDof)                
                
                if ok != 0:
                    print('Ending analysis')
                    
                    ops.wipe()
                    return 
            print(x)
    print()
    print("# Analysis Complete #")

# =============================================================================
# Archlength
# =============================================================================
        
def PushoverArc(dispMax, darc= 0.001*m):
    
    ControlNode = 4
    ControlNodeDof = 1
    # dForce = 1*kN
    dForce = 1000
    
    # Define time series
    ops.timeSeries('Constant',1)
    ops.timeSeries('Linear', 2)
    
    # define loads
    ops.pattern('Plain',1 , 2)
    ops.sp(ControlNode, ControlNodeDof, darc)
    # ops.sp(ControlNode, ControlNodeDof, dForce)

    # Define Analysis Options
    # create SOE
    ops.system("BandGeneral")
    # create DOF number
    ops.numberer("Plain")
    # create constraint handler
    ops.constraints("Transformation")
    # create integrator
    ops.integrator('ArcLength', darc,  0.)
    # create algorithm
    ops.algorithm("Newton")
    # create analysis object
    ops.analysis("Static")

    # Create Test
    ops.test('NormDispIncr', 1.*10**-8, 50)
    # Run Analysis
    ops.record()
    nn = 0
    times = []
    LF = []    
    while(ops.nodeDisp(ControlNode, ControlNodeDof) < dispMax  ):       
    
        ok = ops.analyze(1)
        print(ops.nodeDisp(ControlNode, ControlNodeDof))
    
        if ok != 0:
            ok = analysisLoopArc(ok, nn, darc)
    
        if ok != 0:
            print("Analysis failed at load factor:", nn)
            break            
            
        nn += 1
        times.append(ops.getTime())
        LF.append(ops.getLoadFactor(1))
        




def CyclicAnalysisArc(dispMax, darc=0.00001*m, fileName = 'protocols/Ganey_smaller.thf'):
    
    ControlNode = 4
    ControlNodeDof = 1
    du = 1.0*m
    
    # Define time series
    ops.timeSeries('Constant',1)
    ops.timeSeries('Linear', 2)
    ops.timeSeries('Path', 3, '-dt', 1.0, '-filePath',  fileName,  '-factor',  1.0,  '-prependZero')
    
    # define loads
    ops.pattern('Plain',1 , 3)
    ops.sp(ControlNode, ControlNodeDof, du)
    
    # Define Analysis Options
    # create SOE
    ops.system("BandGeneral")
    # create DOF number
    ops.numberer("Plain")
    # create constraint handler
    ops.constraints("Transformation")
    # create integrator
    ops.integrator('ArcLength', darc, 0.)
    # ops.integrator('ArcLength', darc, 1)
    # create algorithm
    ops.algorithm("Newton")
    # ops.algorithm("ModifiedNewton")
    # create analysis object
    ops.analysis("Static")
    # Create Test
    ops.test('NormDispIncr', 1.*10**-12, 50)
    # ops.test('NormUnbalance ', 1.*10**-10, 50)
    
    # Run Analysis
    ops.record()
    print('start')
    nn = 0
    times = []
    LF = []
    changed =False
    while(ops.nodeDisp(ControlNode, ControlNodeDof) < dispMax  ):       
    
        ok = ops.analyze(1)
        
        if ok != 0:
            ok = analysisLoopArc(ok, nn, darc)
            
        if ok != 0:
            print("Analysis failed at load factor:", nn)
            break
        
        nn += 1
        times.append(ops.getTime())
        LF.append(ops.getLoadFactor(1))   
        
    print()
    print("# Analysis Complete #")
    return times, LF

# =============================================================================
# Static Analysis
# =============================================================================

def SimpleTruss_analysis_static():
    
    #time series type, ts tag
    ops.timeSeries('Linear', lin_tstag)
    #pattern type, patterntag, 
    ops.pattern('Plain', 1, lin_tstag)
    #Apply loading
    ops.load(4, 100.0, -50.0)

    # Define analysis parameters
    ops.constraints('Transformation')
    ops.numberer('RCM')
    ops.system('BandSPD')
    ops.test('NormDispIncr', 1.0e-6, 6, 2)
    ops.algorithm('Newton')
    ops.integrator('LoadControl', 0.1)
    ops.analysis('Static')
    ops.analyze(10)

def analysis_static():
    
    #time series type, ts tag
    ops.timeSeries('Linear', lin_tstag)
    #pattern type, patterntag, 
    ops.pattern('Plain', 1, lin_tstag)
    #Apply loading
    ops.load(2, 0.0, -1.0e5, 0.0)
    ops.load(3, 0.0, -1.0e5, 0.0)

    # Define analysis parameters
    ops.constraints('Plain')
    ops.numberer('Plain')
    ops.system('BandSPD')
    ops.test('NormDispIncr', 1.0e-6, 6, 2)
    ops.algorithm('Newton')
    ops.integrator('LoadControl', 0.1)
    ops.analysis('Static')
    ops.analyze(10)

def inelastic_2d_rcframe_static():

    Wy = -20.5 
    ops.timeSeries('Linear', lin_tstag)
    #pattern type, patterntag, 
    ops.pattern('Plain', 1, lin_tstag)

    # eleLoad('-ele', *eleTags, '-range', eleTag1, eleTag2, '-type', '-beamUniform', Wy, <Wz>, Wx=0.0, '-beamPoint', Py, <Pz>, xL, Px=0.0, '-beamThermal', *tempPts)
    ops.eleLoad('-ele', 3, '-type', '-beamUniform', Wy)

    # Define analysis parameters
    ops.constraints('Plain')
    ops.numberer('Plain')
    ops.system('BandSPD')
    ops.test('NormDispIncr', 1.0e-6, 6, 2)
    ops.algorithm('Newton')
    ops.integrator('LoadControl', 0.1)
    ops.analysis('Static')
    ops.analyze(10)

# =============================================================================
# Transient Analysis
# =============================================================================

def SimpleTruss_analysis_transient():
    # Wipe analysis and set loads constant
    ops.wipeAnalysis()
    ops.loadConst('-time', 0.0)

    # Define mass
    ops.mass(4, 100.0, 100.0)

    # Define time series for input motion (Acceleration time history)
    # ops.timeSeries('Path', 11, '-dt', 0.01, '-filePath', 'elcentro.txt', '-factor', GMfact, '-startTime', st_iv0) # SEISMIC-X
    # ops.timeSeries('Path', 2, '-fact', 3., '-filePath', 'elcentro.txt','-dt', 0.01) # SEISMIC-X
    # ops.timeSeries('Path', 22, '-dt', 0.01, '-filePath', 'OPENSEES_SPRING_SEISMIC_02.txt', '-factor', GMfact) # SEISMIC-Y

    # Define load patterns
    # pattern UniformExcitation $patternTag $dof -accel $tsTag <-vel0 $vel0> <-fact $cFact>
    # ops.pattern('UniformExcitation', 2, 11, '-accel', 1, '-vel0', iv0, '-fact', 3.) # SEISMIC-X
    ops.pattern('UniformExcitation', 2, lin_tstag, '-accel',1, 'Series', '-factor', 1., '-filePath', 'elcentro.txt', '-dt', 0.01) # SEISMIC-X
    # ops.pattern('UniformExcitation', 2, 2, '-accel',1) # SEISMIC-X
    # ops.pattern('UniformExcitation', 3, 22, '-accel', 2)                             # SEISMIC-Y
    

    # Define transient analysis parameters
    ops.constraints('Transformation')
    ops.numberer('RCM')
    ops.system('BandSPD')
    ops.test('NormDispIncr', 1.0e-6, 6, 4)
    ops.algorithm('Newton')
    ops.integrator('Newmark', 0.5, 0.25)
    ops.analysis('Transient')
    ops.analyze(2000, 0.01)
    
def analysis_transient():
    # Wipe analysis and set loads constant
    ops.wipeAnalysis()
    ops.loadConst('-time', 0.0)

    Node_A = 3
    Node_B = 4
    Weight_Node = 80*kg
    
    # Define Masses
    ops.mass(Node_A, Weight_Node, 0, 0)
    ops.mass(Node_B, Weight_Node, 0, 0)

    # Load constant
    ops.loadConst('-time', 0.0)

    # Define Ground Motion
    ops.timeSeries('Path', path_tstag, '-dt', 0.02, '-filePath', 'tabas.txt', '-factor', 9.8)
    ops.pattern('UniformExcitation', 2, path_tstag, '-accel', 1)

    # Compute Eigenvalues and Rayleigh Damping
    # A = 93.1*cm**2
    # I_z = 3908*cm**4
    # L = 1.8288*m
    w1s = ops.eigen('-standard','-symmBandLapack',1)[0]

    #w1s = ops.eigen('-fullGenLapack',10)[0]
    w1 = w1s ** 0.5
    ksi = 0.02
    a0 = 0
    a1 = ksi * 2.0 / w1
    ops.rayleigh(a0, 0.0, a1, 0.0)
    print('Computed eigenvalues:',w1s)
    # print('Expected eigenvalues:',2*Es*I_z/L,6*Es*I_z/L)
    # ops.eigen('-standard','-symmBandLapack',10)

    # Define transient analysis parameters
    ops.wipeAnalysis()
    ops.constraints('Plain')
    ops.numberer('Plain')
    ops.system('BandGeneral')
    ops.test('NormDispIncr', 1.0e-8, 10, 2)
    ops.algorithm('Newton')
    ops.integrator('Newmark', 0.5, 0.25)
    ops.analysis('Transient')
    ops.analyze(1000, 0.02)
    
    
def run_sensitivity_analysis(ctrlNode, dof, baseNode, SensParam, steps=500, IOflag=False):
    """
    Run load-control sensitivity analysis
    """
    ops.wipeAnalysis()
    start_time = time.time()

    # title("Running Load-Control Sensitivity Analysis ...")

    ops.system("BandGeneral")
    ops.numberer("RCM")
    ops.constraints("Transformation")
    ops.test("NormDispIncr", 1.0E-12, 10, 3)
    ops.algorithm("Newton")  # KrylovNewton
    ops.integrator("LoadControl", 1/steps)
    ops.analysis("Static")
    ops.sensitivityAlgorithm("-computeAtEachStep")  # automatically compute sensitivity at the end of each step

    outputs = {"time": np.array([]),
               "disp": np.array([]),
               "force": np.array([]),
               }

    for sens in SensParam:
        outputs[f"sensDisp_{sens}"] = np.array([]),

    for i in range(steps):
        ops.reactions()
        if IOflag:
            print(
                f"Single Cycle Response: Step #{i}, Node #{ctrlNode}: {ops.nodeDisp(ctrlNode, dof):.3f} {LunitTXT} / {-ops.nodeReaction(baseNode, dof):.2f} {FunitTXT}.")
        ops.analyze(1)
        tCurrent = ops.getTime()

        outputs["time"] = np.append(outputs["time"], tCurrent)
        outputs["disp"] = np.append(outputs["disp"], ops.nodeDisp(ctrlNode, dof))
        outputs["force"] = np.append(outputs["force"], -ops.nodeReaction(baseNode, dof))

        for sens in SensParam:
            # sensDisp(patternTag, paramTag)
            outputs[f"sensDisp_{sens}"] = np.append(outputs[f"sensDisp_{sens}"], ops.sensNodeDisp(ctrlNode, dof, sens))

    # title("Sensitvity Analysis Completed!")
    print(f"Analysis elapsed time is {(time.time() - start_time):.3f} seconds.\n")

    return outputs



##########################################################
#                                                         #
# Procedure to compute ultimate lateral resistance, p_u,  #
#  and displacement at 50% of lateral capacity, y50, for  #
#  p-y springs representing cohesionless soil.            #
#   Converted to openseespy by: Pavan Chigullapally       #
#                               University of Auckland    # 
#                                                         #
#   Created by:   Hyung-suk Shin                          #
#                 University of Washington                #
#   Modified by:  Chris McGann                            #
#                 Pedro Arduino                           #
#                 Peter Mackenzie-Helnwein                #
#                 University of Washington                #
#                                                         #
###########################################################

# references
#  American Petroleum Institute (API) (1987). Recommended Practice for Planning, Designing and
#   Constructing Fixed Offshore Platforms. API Recommended Practice 2A(RP-2A), Washington D.C,
#   17th edition.
#
# Brinch Hansen, J. (1961). "The ultimate resistance of rigid piles against transversal forces."
#  Bulletin No. 12, Geoteknisk Institute, Copenhagen, 59.
#
#  Boulanger, R. W., Kutter, B. L., Brandenberg, S. J., Singh, P., and Chang, D. (2003). Pile 
#   Foundations in liquefied and laterally spreading ground during earthquakes: Centrifuge experiments
#   and analyses. Center for Geotechnical Modeling, University of California at Davis, Davis, CA.
#   Rep. UCD/CGM-03/01.
#
#  Reese, L.C. and Van Impe, W.F. (2001), Single Piles and Pile Groups Under Lateral Loading.
#    A.A. Balkema, Rotterdam, Netherlands.


def get_pyParam ( pyDepth, gamma, phiDegree, b, pEleLength, puSwitch, kSwitch, gwtSwitch):
    
    #----------------------------------------------------------
    #  define ultimate lateral resistance, pult 
    #----------------------------------------------------------
    
    # pult is defined per API recommendations (Reese and Van Impe, 2001 or API, 1987) for puSwitch = 1
    #  OR per the method of Brinch Hansen (1961) for puSwitch = 2
    
    pi = 3.14159265358979
    phi = phiDegree * (pi/180)
    zbRatio = pyDepth / b
    
    #-------API recommended method-------
    
    if puSwitch == 1:
    
      # obtain loading-type coefficient A for given depth-to-diameter ratio zb
      #  ---> values are obtained from a figure and are therefore approximate
        zb = []
        dataNum = 41
        for i in range(dataNum):
            b1 = i * 0.125
            zb.append(b1)
        As = [2.8460, 2.7105, 2.6242, 2.5257, 2.4271, 2.3409, 2.2546, 2.1437, 2.0575, 1.9589, 1.8973, 1.8111, 1.7372, 1.6632, 1.5893, 1.5277, 1.4415, 1.3799, 1.3368, 1.2690, 1.2074, 1.1581, 
            1.1211, 1.0780, 1.0349, 1.0164, 0.9979, 0.9733, 0.9610, 0.9487, 0.9363, 0.9117, 0.8994, 0.8994, 0.8871, 0.8871, 0.8809, 0.8809, 0.8809, 0.8809, 0.8809] 
      
      # linear interpolation to define A for intermediate values of depth:diameter ratio
        for i in range(dataNum):
            if zbRatio >= 5.0:
                A = 0.88
            elif zb[i] <= zbRatio and zbRatio <= zb[i+1]:
                A = (As[i+1] - As[i])/(zb[i+1] - zb[i]) * (zbRatio-zb[i]) + As[i]
                
      # define common terms
        alpha = phi / 2
        beta = pi / 4 + phi / 2
        K0 = 0.4
        
        tan_1 = math.tan(pi / 4 - phi / 2)        
        Ka = math.pow(tan_1 , 2) 
    
      # terms for Equation (3.44), Reese and Van Impe (2001)
        tan_2 = math.tan(phi)
        tan_3 = math.tan(beta - phi)
        sin_1 = math.sin(beta)
        cos_1 = math.cos(alpha)
        c1 = K0 * tan_2 * sin_1 / (tan_3*cos_1)
        
        tan_4 = math.tan(beta)
        tan_5 = math.tan(alpha)
        c2 = (tan_4/tan_3)*tan_4 * tan_5
        
        c3 = K0 * tan_4 * (tan_2 * sin_1 - tan_5)
        
        c4 = tan_4 / tan_3 - Ka
    
        # terms for Equation (3.45), Reese and Van Impe (2001)
        pow_1 = math.pow(tan_4,8)
        pow_2 = math.pow(tan_4,4)
        c5 = Ka * (pow_1-1)
        c6 = K0 * tan_2 * pow_2
    
      # Equation (3.44), Reese and Van Impe (2001)
        pst = gamma * pyDepth * (pyDepth * (c1 + c2 + c3) + b * c4)
    
      # Equation (3.45), Reese and Van Impe (2001)
        psd = b * gamma * pyDepth * (c5 + c6)
    
      # pult is the lesser of pst and psd. At surface, an arbitrary value is defined
        if pst <=psd:
            if pyDepth == 0:
                pu = 0.01
              
            else:
                pu = A * pst
              
        else:
            pu = A * psd
          
      # PySimple1 material formulated with pult as a force, not force/length, multiply by trib. length
        pult = pu * pEleLength
    
    #-------Brinch Hansen method-------
    elif puSwitch == 2:
      # pressure at ground surface
        cos_2 = math.cos(phi)
        
        tan_6 = math.tan(pi/4+phi/2) 
        
        sin_2 = math.sin(phi)
        sin_3 = math.sin(pi/4 + phi/2)
        
        exp_1 = math.exp((pi/2+phi)*tan_2)
        exp_2 = math.exp(-(pi/2-phi) * tan_2)
        
        Kqo = exp_1 * cos_2 * tan_6 - exp_2 * cos_2 * tan_1
        Kco = (1/tan_2) * (exp_1 * cos_2 * tan_6 - 1)
    
      # pressure at great depth
        exp_3 = math.exp(pi * tan_2)
        pow_3 = math.pow(tan_2,4)
        pow_4 = math.pow(tan_6,2)
        dcinf = 1.58 + 4.09 * (pow_3)
        Nc = (1/tan_2)*(exp_3)*(pow_4 - 1)
        Ko = 1 - sin_2
        Kcinf = Nc * dcinf
        Kqinf = Kcinf * Ko * tan_2
    
      # pressure at an arbitrary depth
        aq = (Kqo/(Kqinf - Kqo))*(Ko*sin_2/sin_3)
        KqD = (Kqo + Kqinf * aq * zbRatio)/(1 + aq * zbRatio)
    
      # ultimate lateral resistance
        if pyDepth == 0:
            pu = 0.01
        else:
            pu = gamma * pyDepth * KqD * b
               
      # PySimple1 material formulated with pult as a force, not force/length, multiply by trib. length
        pult  = pu * pEleLength
        
    #----------------------------------------------------------
    #  define displacement at 50% lateral capacity, y50
    #----------------------------------------------------------
    
    # values of y50 depend of the coefficent of subgrade reaction, k, which can be defined in several ways.
    #  for gwtSwitch = 1, k reflects soil above the groundwater table
    #  for gwtSwitch = 2, k reflects soil below the groundwater table
    #  a linear variation of k with depth is defined for kSwitch = 1 after API (1987)
    #  a parabolic variation of k with depth is defined for kSwitch = 2 after Boulanger et al. (2003)
    
    # API (1987) recommended subgrade modulus for given friction angle, values obtained from figure (approximate)
    
    ph = [28.8, 29.5, 30.0, 31.0, 32.0, 33.0, 34.0, 35.0, 36.0, 37.0, 38.0, 39.0, 40.0]    
   
    # subgrade modulus above the water table
    if gwtSwitch == 1:
        k = [10, 23, 45, 61, 80, 100, 120, 140, 160, 182, 215, 250, 275]
        
    else:
        k = [10, 20, 33, 42, 50, 60, 70, 85, 95, 107, 122, 141, 155]
    
    dataNum = 13  
    for i in range(dataNum):
        if ph[i] <= phiDegree and phiDegree <= ph[i+1]:
            khat = (k[i+1]-k[i])/(ph[i+1]-ph[i])*(phiDegree - ph[i]) + k[i]            
            
    # change units from (lb/in^3) to (kN/m^3)
    k_SIunits = khat * 271.45
    
    # define parabolic distribution of k with depth if desired (i.e. lin_par switch == 2)
    sigV = pyDepth * gamma
    
    if sigV == 0:
         sigV = 0.01
         
    if kSwitch == 2:
       # Equation (5-16), Boulanger et al. (2003)
        cSigma = math.pow(50 / sigV , 0.5)
       # Equation (5-15), Boulanger et al. (2003)
        k_SIunits = cSigma * k_SIunits
    
    # define y50 based on pult and subgrade modulus k
    
    # based on API (1987) recommendations, p-y curves are described using tanh functions.
    #  tcl does not have the atanh function, so must define this specifically
    
    #  i.e.  atanh(x) = 1/2*ln((1+x)/(1-x)), |x| < 1
    
    # when half of full resistance has been mobilized, p(y50)/pult = 0.5
    x = 0.5
    log_1 = math.log((1+x)/(1-x))
    atanh_value = 0.5 * log_1
    
    # need to be careful at ground surface (don't want to divide by zero)
    if pyDepth == 0.0:
        pyDepth = 0.01

    y50 = 0.5 * (pu/ A)/(k_SIunits * pyDepth) * atanh_value
    # return pult and y50 parameters
    outResult = []
    outResult.append(pult)
    outResult.append(y50)
    
    return outResult

#########################################################################################################################################################################

#########################################################################################################################################################################

###########################################################
#                                                         #
# Procedure to compute ultimate tip resistance, qult, and #
#  displacement at 50% mobilization of qult, z50, for     #
#  use in q-z curves for cohesionless soil.               #
#   Converted to openseespy by: Pavan Chigullapally       #  
#                               University of Auckland    #
#   Created by:  Chris McGann                             #
#                Pedro Arduino                            #
#                University of Washington                 #
#                                                         #
###########################################################

# references
#  Meyerhof G.G. (1976). "Bearing capacity and settlement of pile foundations." 
#   J. Geotech. Eng. Div., ASCE, 102(3), 195-228.
#
#  Vijayvergiya, V.N. (1977). "Load-movement characteristics of piles."
#   Proc., Ports 77 Conf., ASCE, New York.
#
#  Kulhawy, F.H. ad Mayne, P.W. (1990). Manual on Estimating Soil Properties for 
#   Foundation Design. Electrical Power Research Institute. EPRI EL-6800, 
#   Project 1493-6 Final Report.

def get_qzParam (phiDegree, b, sigV, G):
    
    # define required constants; pi, atmospheric pressure (kPa), pa, and coeff. of lat earth pressure, Ko
    pi = 3.14159265358979
    pa = 101
    sin_4 = math.sin(phiDegree * (pi/180))
    Ko = 1 - sin_4

  # ultimate tip pressure can be computed by qult = Nq*sigV after Meyerhof (1976)
  #  where Nq is a bearing capacity factor, phi is friction angle, and sigV is eff. overburden
  #  stress at the pile tip.
    phi = phiDegree * (pi/180)

  # rigidity index
    tan_7 = math.tan(phi)
    Ir = G/(sigV * tan_7)
  # bearing capacity factor
    tan_8 = math.tan(pi/4+phi/2)
    sin_5 = math.sin(phi)
    pow_4 = math.pow(tan_8,2)
    pow_5 = math.pow(Ir,(4*sin_5)/(3*(1+sin_5)))
    exp_4 = math.exp(pi/2-phi)
    
    Nq = (1+2*Ko)*(1/(3-sin_5))*exp_4*(pow_4)*(pow_5)  
  # tip resistance
    qu = Nq * sigV
  # QzSimple1 material formulated with qult as force, not stress, multiply by area of pile tip
    pow_6 = math.pow(b, 2)  
    qult = qu * pi*pow_6/4

  # the q-z curve of Vijayvergiya (1977) has the form, q(z) = qult*(z/zc)^(1/3)
  #  where zc is critical tip deflection given as ranging from 3-9% of the
  #  pile diameter at the tip.  

  # assume zc is 5% of pile diameter
    zc = 0.05 * b

  # based on Vijayvergiya (1977) curve, z50 = 0.125*zc
    z50 = 0.125 * zc

  # return values of qult and z50 for use in q-z material
    outResult = []
    outResult.append(qult)
    outResult.append(z50)
    
    return outResult

#########################################################################################################################################################################

#########################################################################################################################################################################
##########################################################
#                                                         #
# Procedure to compute ultimate resistance, tult, and     #
#  displacement at 50% mobilization of tult, z50, for     #
#  use in t-z curves for cohesionless soil.               #
#   Converted to openseespy by: Pavan Chigullapally       #
#                               University of Auckland    #
#   Created by:  Chris McGann                             #
#                University of Washington                 #
#                                                         #
###########################################################

def get_tzParam ( phi, b, sigV, pEleLength):

# references
#  Mosher, R.L. (1984). "Load transfer criteria for numerical analysis of
#   axial loaded piles in sand." U.S. Army Engineering and Waterways
#   Experimental Station, Automatic Data Processing Center, Vicksburg, Miss.
#
#  Kulhawy, F.H. (1991). "Drilled shaft foundations." Foundation engineering
#   handbook, 2nd Ed., Chap 14, H.-Y. Fang ed., Van Nostrand Reinhold, New York

    pi = 3.14159265358979
    
  # Compute tult based on tult = Ko*sigV*pi*dia*tan(delta), where
  #   Ko    is coeff. of lateral earth pressure at rest, 
  #         taken as Ko = 0.4
  #   delta is interface friction between soil and pile,
  #         taken as delta = 0.8*phi to be representative of a 
  #         smooth precast concrete pile after Kulhawy (1991)
  
    delta = 0.8 * phi * pi/180

  # if z = 0 (ground surface) need to specify a small non-zero value of sigV
  
    if sigV == 0.0:
        sigV = 0.01
    
    tan_9 = math.tan(delta)
    tu = 0.4 * sigV * pi * b * tan_9
    
  # TzSimple1 material formulated with tult as force, not stress, multiply by tributary length of pile
    tult = tu * pEleLength

  # Mosher (1984) provides recommended initial tangents based on friction angle
	# values are in units of psf/in
    kf = [6000, 10000, 10000, 14000, 14000, 18000]
    fric = [28, 31, 32, 34, 35, 38]

    dataNum = len(fric)
    
    
	# determine kf for input value of phi, linear interpolation for intermediate values
    if phi < fric[0]:
        k = kf[0]
    elif phi > fric[5]:
        k = kf[5]
    else:
        for i in range(dataNum):
            if fric[i] <= phi and phi <= fric[i+1]:
                k = ((kf[i+1] - kf[i])/(fric[i+1] - fric[i])) * (phi - fric[i]) + kf[i]
        

  # need to convert kf to units of kN/m^3
    kSIunits =  k * 1.885

  # based on a t-z curve of the shape recommended by Mosher (1984), z50 = tult/kf
    z50 = tult / kSIunits

  # return values of tult and z50 for use in t-z material
    outResult = []
    outResult.append(tult)
    outResult.append(z50)

    return outResult