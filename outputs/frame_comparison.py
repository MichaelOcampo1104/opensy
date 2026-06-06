import openseespy.opensees as ops # type : ignnore
import numpy as np
import opstool as opst


def build_frame(support_type="fixed", save_prefix="fixed"):
    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 3)

    # Parameters
    width = 20.0
    height = 30.0
    bays = 2
    stories = 10
    L_bay = width / bays
    H_story = height / stories

    # Materials / Sections (Simplified Elastic)
    E = 3.0e7  # kPa
    A_col = 0.5 * 0.5
    I_col = (0.5**4) / 12
    A_beam = 0.4 * 0.6
    I_beam = (0.4 * 0.6**3) / 12

    # Nodes
    node_tag = 1
    for i in range(stories + 1):
        y = i * H_story
        for j in range(bays + 1):
            x = j * L_bay
            ops.node(node_tag, x, y)
            node_tag += 1

    # Supports
    if support_type == "fixed":
        for j in range(bays + 1):
            ops.fix(j + 1, 1, 1, 1)
    else:
        # Soil Springs (Winkler)
        kv = 1.0e5
        kh = 5.0e4
        kr = 1.0e6

        ops.uniaxialMaterial("Elastic", 101, kh)
        ops.uniaxialMaterial("Elastic", 102, kv)
        ops.uniaxialMaterial("Elastic", 103, kr)

        for j in range(bays + 1):
            support_node = j + 1
            spring_node = 1000 + j + 1
            ops.node(spring_node, (j * L_bay), 0.0)
            ops.fix(spring_node, 1, 1, 1)
            ops.element(
                "zeroLength",
                500 + j,
                spring_node,
                support_node,
                "-mat",
                101,
                102,
                103,
                "-dir",
                1,
                2,
                3,
            )

    # Elements
    ops.geomTransf("Linear", 1)
    ele_tag = 1
    for j in range(bays + 1):
        for i in range(stories):
            n1 = i * (bays + 1) + j + 1
            n2 = (i + 1) * (bays + 1) + j + 1
            ops.element("elasticBeamColumn", ele_tag, n1, n2, A_col, E, I_col, 1)
            ele_tag += 1
    for i in range(1, stories + 1):
        for j in range(bays):
            n1 = i * (bays + 1) + j + 1
            n2 = i * (bays + 1) + j + 2
            ops.element("elasticBeamColumn", ele_tag, n1, n2, A_beam, E, I_beam, 1)
            ele_tag += 1

    # Loading
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    top_nodes = [(stories * (bays + 1)) + j + 1 for j in range(bays + 1)]
    for node in top_nodes:
        ops.load(node, 100.0, 0.0, 0.0)

    # opstool ODB
    odb = opst.post.CreateODB(save_prefix)

    # Analysis
    ops.system("BandSPD")
    ops.numberer("RCM")
    ops.constraints("Plain")
    ops.integrator("LoadControl", 1.0)
    ops.algorithm("Linear")
    ops.analysis("Static")
    ops.analyze(1)

    # Fetch and save response
    odb.fetch_response_step()
    odb.save_response()
    odb.save_model_data()

    # opstool visualization
    # Save model and deflection plots as HTML
    fig_model = opst.vis.po.plot_model(odb_tag=save_prefix)
    fig_model.write_html(f"{save_prefix}_model.html")

    fig_defo = opst.vis.po.plot_nodal_responses(odb_tag=save_prefix, defo_scale=50)
    fig_defo.write_html(f"{save_prefix}_deflection.html")

    return ops.nodeDisp(top_nodes[0], 1)


# Run and compare
disp_fixed = build_frame("fixed", "fixed")
disp_spring = build_frame("spring", "spring")

print(f"--- Results for 20m x 30m Frame ---")
print(f"Top Displacement (Fixed Base):  {disp_fixed:.4f} m")
print(f"Top Displacement (Soil Spring): {disp_spring:.4f} m")
print(f"Difference: {((disp_spring / disp_fixed) - 1) * 100:.2f}%")
print(f"\nVisualization files created:")
print(f"- fixed_model.html / fixed_deflection.html")
print(f"- spring_model.html / spring_deflection.html")
