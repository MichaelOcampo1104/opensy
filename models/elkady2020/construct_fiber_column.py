############################################################################################
# ConstructFiberColumn.py
#
# This procedure will produce a 2D column element between the 2 given points in a 2D/3D system (Z coordinates were set to 0).
# P-Delta Transformation is used by default
#
# Command Syntax ConstructBrace eleID Node1 Node2 secID numSeg Initial_GI nInt Trans_tag
#
# Command Arguments
# L 			Overall Length of Bracing
# Initial_GI	Required Maximum Initial Imperfection ratio at Middle of Bracing
# numSeg		Number of required Segment along Bracing Length
# nInt 			Number of integration point per segment.
# Node1 		Node ID Brace Element Start Point
# Node2			Node ID Brace Element End Point
# Splice_status 0 --> Column wtih No Splice
#				1 --> Column with Splice (lower part)
#				2 --> Column with Splice (upper part)
############################################################################################
import openseespy.opensees as ops
import math

def construct_fiber_column(eleID, Node1, Node2, secID, numSeg, Initial_GI, nInt, Trans_tag, Splice_status):
    """
    SubRoutine to produce a 2D column element between 2 given points.
    
    Splice_status: 
        0 --> Column with No Splice
        1 --> Column with Splice (lower part)
        2 --> Column with Splice (upper part)
    """
    
    # 1. Define Beam Integration
    # We use eleID as a unique integration tag to avoid conflicts across routine calls
    integrationTag = eleID
    ops.beamIntegration('Lobatto', integrationTag, secID, nInt)
    
    # 2. Get Coordinates of the Column End Points
    X1 = ops.nodeCoord(Node1, 1)
    Y1 = ops.nodeCoord(Node1, 2)
    X2 = ops.nodeCoord(Node2, 1)
    Y2 = ops.nodeCoord(Node2, 2)
    
    # Deduce the Length of the Column
    L = math.sqrt((X2 - X1)**2 + (Y2 - Y1)**2)
    
    # 3. Process Based on Splice Status
    # --- NO SPLICE ---
    if Splice_status == 0:
        base_nodeID = 100000 + Node1
        
        # Generate intermediate nodes
        for i in range(1, numSeg):
            nodeid = base_nodeID + i
            xGlobal = X1 + math.sin(math.pi * i / numSeg) * Initial_GI * L
            yGlobal = Y1 + (L / numSeg) * i
            ops.node(nodeid, xGlobal, yGlobal)
            
        ElementID = eleID
        if numSeg > 1:
            # Define first element
            ops.element('dispBeamColumn', ElementID, Node1, base_nodeID + 1, Trans_tag, integrationTag)
            
            # Define internal elements
            for i in range(1, numSeg - 1):
                ElementID += 1
                iNode = i + base_nodeID
                jNode = i + base_nodeID + 1
                ops.element('dispBeamColumn', ElementID, iNode, jNode, Trans_tag, integrationTag)
                
            # Define last element
            ops.element('dispBeamColumn', ElementID + 1, base_nodeID + numSeg - 1, Node2, Trans_tag, integrationTag)
        else:
            ops.element('dispBeamColumn', ElementID, Node1, Node2, Trans_tag, integrationTag)

    # --- LOWER PART SPLICE ---
    elif Splice_status == 1:
        base_nodeID = 100000 + Node1 + 3
        
        # Generate intermediate nodes
        for i in range(1, numSeg):
            nodeid = base_nodeID + i
            xGlobal = X1 + math.sin(math.pi * i / numSeg) * Initial_GI * L
            yGlobal = Y1 + (L / numSeg) * i
            ops.node(nodeid, xGlobal, yGlobal)
            
        ElementID = eleID + 3
        if numSeg > 1:
            # Define first element (uses explicit eleID per original logic)
            ops.element('dispBeamColumn', eleID, Node1, base_nodeID + 1, Trans_tag, integrationTag)
            
            # Define internal elements
            for i in range(1, numSeg - 1):
                ElementID += 1
                iNode = i + base_nodeID
                jNode = i + base_nodeID + 1
                ops.element('dispBeamColumn', ElementID, iNode, jNode, Trans_tag, integrationTag)
                
            # Define last element
            ops.element('dispBeamColumn', ElementID + 1, base_nodeID + numSeg - 1, Node2, Trans_tag, integrationTag)
        else:
            ops.element('dispBeamColumn', eleID, Node1, Node2, Trans_tag, integrationTag)

    # --- UPPER PART SPLICE ---
    elif Splice_status == 2:
        base_nodeID = 100000 + Node2 + 10
        
        # Generate intermediate nodes (Note: orientation uses X2/Y2 references)
        for i in range(1, numSeg):
            nodeid = base_nodeID + i
            xGlobal = X2 + math.sin(math.pi * i / numSeg) * Initial_GI * L
            yGlobal = Y2 - (L / numSeg) * i
            ops.node(nodeid, xGlobal, yGlobal)
            
        ElementID = eleID + 10
        if numSeg > 1:
            # Define first element (uses explicit eleID per original logic)
            ops.element('dispBeamColumn', eleID, Node1, base_nodeID + 1, Trans_tag, integrationTag)
            
            # Define internal elements
            for i in range(1, numSeg - 1):
                ElementID += 1
                iNode = i + base_nodeID
                jNode = i + base_nodeID + 1
                ops.element('dispBeamColumn', ElementID, iNode, jNode, Trans_tag, integrationTag)
                
            # Define last element
            ops.element('dispBeamColumn', ElementID + 1, base_nodeID + numSeg - 1, Node2, Trans_tag, integrationTag)
        else:
            ops.element('dispBeamColumn', eleID, Node1, Node2, Trans_tag, integrationTag)
            
    else:
        raise ValueError(f"Invalid Splice_status: {Splice_status}. Must be 0, 1, or 2.")
