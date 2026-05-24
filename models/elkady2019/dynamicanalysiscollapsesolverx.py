import openseespy.opensees as ops
import opstool as opst
from sdrlimittester import sdr_limit_tester
from pathlib import Path
import time
def dynamic_analysis_collapse_solver(
    dt: float,
    dt_anal_step: float,
    gm_time: float,
    num_stories: int,
    drift_limit: float,
    mf_floor_nodes: list[int],
    egf_floor_nodes: list[int],
    h1: float,
    htyp: float,
    trace_gf_drift: bool,
    max_run_time: float,
    odb: "opst.post.CreateODB",
    output_dir: Path
) -> None:
    """
    Transient solver loop for collapse 'hunting' using opstool's SmartAnalyze.
    Checks story drifts after each converged step.

    Args:
        dt: Ground Motion step (not directly used as step size, we use dt_anal_step)
        dt_anal_step: Analysis time step
        gm_time: Ground Motion Total Time
        num_stories: Total number of stories
        drift_limit: Story drift ratio limit
        mf_floor_nodes: List of node tags for the Moment Frame floors
        egf_floor_nodes: List of node tags for the Gravity Frame floors
        h1: First story height (mm)
        htyp: Typical story height (mm)
        trace_gf_drift: True to also check gravity frame drift
        max_run_time: Maximum allowable clock time for the analysis (seconds)
        odb: Active CreateODB instance for response collection
        output_dir: Output directory path
    """
    # System and Integrator must be set BEFORE instantiating SmartAnalyze
    ops.constraints("Plain")
    ops.numberer("RCM")
    ops.system("UmfPack")
    ops.integrator("Newmark", 0.50, 0.25)

    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Transient",
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30, 50],
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
        relaxation=0.5,
        minStep=1.0e-6,
    )

    npts = int(round((gm_time + 0.0) / dt_anal_step))
    segs = analysis.transient_split(npts)

    start_time = time.time()

    for _ in segs:
        # Run single transient step with smart convergence handling
        status = analysis.TransientAnalyze(dt_anal_step)

        if status != 0:
            print("Analysis did not converge... Collapse or instability.")
            break

        # Collect responses at this converged step (MANDATORY per Section 3d)
        odb.fetch_response_step()

        # Check Max Drifts for Collapse
        # Note: Assumes sdr_limit_tester is imported/available in scope
        collapse_flag = sdr_limit_tester(
            num_stories, drift_limit, mf_floor_nodes, egf_floor_nodes,
            h1, htyp, trace_gf_drift, output_dir
        )

        run_time = time.time() - start_time
        if collapse_flag or run_time > max_run_time:
            print("----> Collapse Occurred or Max Run Time Reached")
            break

    # Always close the analysis loop (MANDATORY per Section 3c)
    analysis.close()
