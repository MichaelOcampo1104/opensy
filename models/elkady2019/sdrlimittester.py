# ########################################################################################
# SDRlimitTester 
# Procedure that checks if the Pre-Specified Collapse Drift Limit is reached and Generate 
# a Flag
#
# Developed by Dimitrios G. Lignos, Ph.D
# Modified  by Ahmed Elkady, Ph.D
#
# First Created: 04/20/2010
# Last Modified: 05/05/2020
#
# #######################################################################################

import openseespy.opensees as ops
from pathlib import Path
def sdr_limit_tester(
    num_stories: int,
    sdr_limit: float,
    mf_floor_nodes: list[int],
    egf_floor_nodes: list[int],
    h1: float,
    htyp: float,
    trace_gf_drift: bool,
    output_dir: Path
) -> bool:
    """
    Check if the Pre-Specified Collapse Drift Limit is reached and generate a Flag.
    Args:
        num_stories: Total number of stories
        sdr_limit: Story drift ratio limit
        mf_floor_nodes: List of node tags for the Moment Frame floors
        egf_floor_nodes: List of node tags for the Gravity Frame floors
        h1: First story height (mm)
        htyp: Typical story height (mm)
        trace_gf_drift: True to also check gravity frame drift
        output_dir: Path to the output directory to write collapse state files
    Returns:
        collapse_flag: True if collapse occurred, False otherwise
    """
    collapse_flag = False

    smf_drift = []
    gf_drift = []

    # Read the Floor Node Displacements and Deduce the Story Drift Ratio
    for i in range(num_stories):
        if i == 0:
            node = mf_floor_nodes[i]
            node_disp_i = ops.nodeDisp(node, 1)
            sdr_mf = node_disp_i / h1
            smf_drift.append(sdr_mf)

            if trace_gf_drift:
                node_egf = egf_floor_nodes[i]
                node_disp_egf = ops.nodeDisp(node_egf, 1)
                sdr_egf = node_disp_egf / h1
                gf_drift.append(sdr_egf)

        else:
            node_i = mf_floor_nodes[i]
            node_disp_i = ops.nodeDisp(node_i, 1)
            node_j = mf_floor_nodes[i-1]
            node_disp_j = ops.nodeDisp(node_j, 1)
            sdr_mf = (node_disp_i - node_disp_j) / htyp
            smf_drift.append(sdr_mf)

            if trace_gf_drift:
                node_egf_i = egf_floor_nodes[i]
                node_disp_egf_i = ops.nodeDisp(node_egf_i, 1)
                node_egf_j = egf_floor_nodes[i-1]
                node_disp_egf_j = ops.nodeDisp(node_egf_j, 1)
                sdr_egf = (node_disp_egf_i - node_disp_egf_j) / htyp
                gf_drift.append(sdr_egf)

    # Check if any Story Drift Ratio Exceeded the Drift Limit
    for i in range(num_stories):
        smf_t_drift = abs(smf_drift[i])

        gf_t_drift = 0.0
        if trace_gf_drift:
            gf_t_drift = abs(gf_drift[i])

        # If the Story Drift Ratio at Current Story is Less than the Drift Limit then
        # write a value of "0" for no collapse
        if smf_t_drift < sdr_limit and gf_t_drift < sdr_limit:
            with open(output_dir / "CollapsedFrame.txt", "w") as f:
                f.write("0")

        # If Drift Limit was exceeded in MF
        if smf_t_drift > sdr_limit:
            print("MF Collapse")
            with open(output_dir / "CollapsedFrame.txt", "w") as f:
                f.write("1")

        # If Drift Limit was exceeded in EGF
        if gf_t_drift > sdr_limit:
            print("GF Collapse")
            with open(output_dir / "CollapsedFrame.txt", "w") as f:
                f.write("2")

        # If Drift Limit was exceeded in both MF and EGF
        if smf_t_drift > sdr_limit or gf_t_drift > sdr_limit:
            collapse_flag = True
            print("Collapse")
            with open(output_dir / "CollapseState.txt", "w") as f:
                f.write("1")

    return collapse_flag
