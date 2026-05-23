########################################################################################################
# ConstructPanel_Rectangle
#
# SubRoutine to construct nodes and rigid elements for the panel zone parallelogram model
#                                                      
##################################################################################################################
#
# Input Arguments:
#------------------
# Axis      	Axis  number ID
# Floor     	Floor number ID
# E         	Young's modulus
# A_Panel   	Area of rigid link that creates the panel zone
# I_Panel   	Moment of inertia of rigid link that creates the panel zone
# d_Col     	Column section depth
# d_Beam    	Beam section depth
# transfTag 	Geometric transformation ID
#
# Written by: Dr. Ahmed Elkady, University of Southampton, UK
#
##################################################################################################################

import openseespy.opensees as ops
def construct_panel_rectangle(
    axis: int,
    floor: int,
    x_axis: float,
    y_floor: float,
    E: float,
    A_panel: float,
    I_panel: float,
    d_col: float,
    d_beam: float,
    transf_tag: int
) -> None:
    """
    Construct nodes and rigid elements for the panel zone parallelogram model.

    Args:
        axis: Axis number ID
        floor: Floor number ID
        x_axis: X coordinate of the panel center (mm)
        y_floor: Y coordinate of the panel center (mm)
        E: Young's modulus (MPa)
        A_panel: Area of rigid link that creates the panel zone (mm^2)
        I_panel: Moment of inertia of rigid link that creates the panel zone (mm^4)
        d_col: Column section depth (mm)
        d_beam: Beam section depth (mm)
        transf_tag: Geometric transformation ID
    """

    # Construct Panel Node Notation
    node_cl = 400000 + floor * 1000 + axis * 100
    node_xy01 = node_cl + 1
    node_xy02 = node_cl + 2
    node_xy03 = node_cl + 3
    node_xy04 = node_cl + 4
    node_xy05 = node_cl + 5
    node_xy06 = node_cl + 6
    node_xy07 = node_cl + 7
    node_xy08 = node_cl + 8
    node_xy09 = node_cl + 9
    node_xy10 = node_cl + 10
    node_xy11 = node_cl + 88
    node_xy12 = node_cl + 99

    # Construct Panel Element Notation
    p_elm_100xy00 = 7000000 + floor * 1000 + axis * 100
    p_elm_100xy01 = p_elm_100xy00 + 1
    p_elm_100xy02 = p_elm_100xy00 + 2
    p_elm_100xy03 = p_elm_100xy00 + 3
    p_elm_100xy04 = p_elm_100xy00 + 4
    p_elm_100xy05 = p_elm_100xy00 + 5
    p_elm_100xy06 = p_elm_100xy00 + 6
    p_elm_100xy07 = p_elm_100xy00 + 7
    p_elm_100xy08 = p_elm_100xy00 + 8

    # Construct Panel Node Coordinates
    ops.node(node_xy01, x_axis,                y_floor - d_beam / 2.0)
    ops.node(node_xy02, x_axis - d_col / 2.0,  y_floor)
    ops.node(node_xy03, x_axis,                y_floor + d_beam / 2.0)
    ops.node(node_xy04, x_axis + d_col / 2.0,  y_floor)
    ops.node(node_xy05, x_axis - d_col / 2.0,  y_floor - d_beam / 2.0)
    ops.node(node_xy06, x_axis - d_col / 2.0,  y_floor - d_beam / 2.0)
    ops.node(node_xy07, x_axis - d_col / 2.0,  y_floor + d_beam / 2.0)
    ops.node(node_xy08, x_axis - d_col / 2.0,  y_floor + d_beam / 2.0)
    ops.node(node_xy09, x_axis + d_col / 2.0,  y_floor + d_beam / 2.0)
    ops.node(node_xy10, x_axis + d_col / 2.0,  y_floor + d_beam / 2.0)
    ops.node(node_xy11, x_axis + d_col / 2.0,  y_floor - d_beam / 2.0)
    ops.node(node_xy12, x_axis + d_col / 2.0,  y_floor - d_beam / 2.0)

    # Construct Panel Element Property
    ops.element('elasticBeamColumn', p_elm_100xy01, node_xy01, node_xy05, A_panel, E, I_panel, transf_tag)
    ops.element('elasticBeamColumn', p_elm_100xy02, node_xy06, node_xy02, A_panel, E, I_panel, transf_tag)
    ops.element('elasticBeamColumn', p_elm_100xy03, node_xy02, node_xy07, A_panel, E, I_panel, transf_tag)
    ops.element('elasticBeamColumn', p_elm_100xy04, node_xy08, node_xy03, A_panel, E, I_panel, transf_tag)
    ops.element('elasticBeamColumn', p_elm_100xy05, node_xy03, node_xy09, A_panel, E, I_panel, transf_tag)
    ops.element('elasticBeamColumn', p_elm_100xy06, node_xy10, node_xy04, A_panel, E, I_panel, transf_tag)
    ops.element('elasticBeamColumn', p_elm_100xy07, node_xy04, node_xy11, A_panel, E, I_panel, transf_tag)
    ops.element('elasticBeamColumn', p_elm_100xy08, node_xy12, node_xy01, A_panel, E, I_panel, transf_tag)

    # Restrain DOFs At Panel Corners
    ops.equalDOF(node_xy05, node_xy06, 1, 2)
    ops.equalDOF(node_xy07, node_xy08, 1, 2)
    ops.equalDOF(node_xy09, node_xy10, 1, 2)
    ops.equalDOF(node_xy11, node_xy12, 1, 2)
