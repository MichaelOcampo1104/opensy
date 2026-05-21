import openseespy.opensees as ops
from pathlib import Path
from model import init_model, define_nodes, define_elements, define_boundary_conditions, define_materials, define_sections, define_gravity_loads, define_lateral_loads, run_gravity

def main():
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    init_model()
    define_nodes()
    define_elements(output_dir)
    define_boundary_conditions()
    define_materials()
    define_sections()
    define_gravity_loads()

    ops.integrator("LoadControl", 0.5)
    ops.analysis("Static")
    for _ in range(2):
        ops.analyze(1)
    ops.loadConst("-time", 0.0)

    define_lateral_loads()

    # Apply displacement control directly
    ops.wipeAnalysis()
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.test("NormDispIncr", 1.0e-5, 1000)
    ops.algorithm("Newton")
    
    ctrl_node = 1113
    ctrl_dof = 1
    
    # We will do 10 steps of 1 mm
    ops.integrator("DisplacementControl", ctrl_node, ctrl_dof, 1.0)
    ops.analysis("Static")
    
    for i in range(10):
        ops.analyze(1)
        # get base shear (sum of x-reactions at ground nodes)
        ops.reactions()
        base_shear = sum([ops.nodeReaction(tag, 1) for tag in [1110, 1210, 1310, 1410]])
        disp = ops.nodeDisp(ctrl_node, ctrl_dof)
        time = ops.getTime()
        print(f"Step {i+1}, Disp: {disp:.3f} mm, Base Shear: {base_shear:.1f} N, Lambda (Time): {time:.3f}")

if __name__ == "__main__":
    main()
