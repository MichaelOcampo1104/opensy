import openseespy.opensees as ops
import opstool as opst
from pathlib import Path
import time

def _transient_smart_analyze(
    odb: "opst.post.CreateODB",
    dt_anal: float,
    gm_time: float,
    max_run_time: float = 1800.0,
) -> None:
    """
    Inner transient loop using opstool SmartAnalyze.
    Constraints, numberer, system and integrator must be set before calling.
    """
    analysis = opst.anlys.SmartAnalyze(
        analysis_type="Transient",
        tryAlterAlgoTypes=True,
        algoTypes=[40, 10, 20, 30, 50],   # KrylovNewton, Newton, ModNewton, NewtonLS, Broyden
        tryAddTestTimes=True,
        testIterTimesMore=[50, 100],
        relaxation=0.5,
        minStep=1.0e-6,
    )
    npts = int(round(gm_time / dt_anal))
    segs = analysis.transient_split(npts)
    start_time = time.time()

    for _ in segs:
        status = analysis.TransientAnalyze(dt_anal)
        if status != 0:
            print("SmartAnalyze: did not converge — stopping dynamic analysis.")
            break
        odb.fetch_response_step()
        if time.time() - start_time > max_run_time:
            print(f"SmartAnalyze: max run time ({max_run_time}s) reached — stopping.")
            break

    analysis.close()

