import openseespy.opensees as ops
import opstool as opst
import matplotlib.pyplot as plt


# Define units
# ------------------------------------------------------------------------
# Basic Units
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


def create_uniaxial_material(mat_dict):
    """
    Helper function to create a uniaxial material in OpenSees
    using a structured dictionary while ensuring argument order.
    """
    if mat_dict['ID'] == 'Concrete02':
        ops.uniaxialMaterial(mat_dict['ID'], mat_dict['matTag'], mat_dict['fpc'], 
                              mat_dict['epsc0'], mat_dict['fpcu'], mat_dict['epsU'], 
                              mat_dict['lamda'], mat_dict['ft'], mat_dict['Ets'])
    
    elif mat_dict['ID'] == 'Concrete04':
        ops.uniaxialMaterial(mat_dict['ID'], mat_dict['matTag'], mat_dict['fc'], 
                              mat_dict['ec'], mat_dict['ecu'], mat_dict['Ec'], 
                              mat_dict['ft'], mat_dict['et'])
    
    elif mat_dict['ID'] == 'Steel02':
        ops.uniaxialMaterial(mat_dict['ID'], mat_dict['matTag'], mat_dict['Fy'], 
                              mat_dict['E0'], mat_dict['b'], mat_dict['R0'], 
                              mat_dict['cR1'], mat_dict['cR2'])
    
    else:
        raise ValueError(f"Unsupported material ID: {mat_dict['ID']}")


def rect_RC_section_o_two(matTagC, matTagCCore, matTagS, fc1U, 
                                 eps2C, eps2U, fc1C, Fy_reinf, Es_reinf,
                                 beam_breadth,beam_depth,conc_cover,bar_dia_top,bar_dia_bot,gap):
    """
    Defines materials for a rectangular reinforced concrete section 
    in OpenSees using Concrete02, Concrete04, and Steel02 models.
    """
    ops.model("basic", "-ndm", 3, "-ndf", 6)
    # Unconfined concrete (Cover region) - Kent-Scott-Park model
    mat_Concrete02_cover = {
        'ID': 'Concrete02',
        'matTag': matTagC,
        'fpc': fc1U,
        'epsc0': eps2C,
        'fpcu': 0.2 * fc1U,
        'epsU': eps2C,
        'lamda': 0.1,
        'ft': -0.1 * fc1U,
        'Ets': (-0.1 * fc1U) / 0.002
    }
 
    # Confined concrete (Core region) - Kent-Scott-Park model
    mat_Concrete02_core = {
        'ID': 'Concrete02',
        'matTag': matTagCCore,
        'fpc': fc1C,
        'epsc0': eps2U,
        'fpcu': 0.2 * fc1C,
        'epsU': eps2U,
        'lamda': 0.1,
        'ft': -0.1 * fc1C,
        'Ets': (-0.1 * fc1C) / 0.002
    }

    # Steel reinforcement - Giuffré-Menegotto-Pinto model
    mat_rebar = {
        'ID': 'Steel02',
        'matTag': matTagS,
        'Fy': Fy_reinf,
        'E0': Es_reinf,
        'b': 0.005,
        'R0': 20.0,
        'cR1': 0.925,
        'cR2': 0.15
    }

    # Create materials in OpenSees
    create_uniaxial_material(mat_Concrete02_cover)  # Cover concrete
    create_uniaxial_material(mat_Concrete02_core)    # Core concrete
    create_uniaxial_material(mat_rebar)         # Reinforcement steel
    
    outlines = [[0., 0.], [beam_breadth, 0.], [beam_breadth, beam_depth], [0., beam_depth]]
    rebar_top_line = [[conc_cover,conc_cover],[beam_breadth-conc_cover, conc_cover]]
    rebar_bot_line = [[beam_breadth-conc_cover, beam_depth-conc_cover],[conc_cover,  beam_depth-conc_cover]]
    coverlines = opst.pre.section.offset(outlines, d=conc_cover)
    cover = opst.pre.section.create_polygon_patch(outlines, holes=[coverlines])
    
    core = opst.pre.section.create_polygon_patch(coverlines)
    SEC = opst.pre.section.FiberSecMesh()
    SEC.add_patch_group(dict(cover=cover, core=core))
    SEC.set_mesh_size(dict(cover=0.10, core=0.10))
    SEC.set_mesh_color(dict(cover="gray", core="green"))
    SEC.set_ops_mat_tag(dict(cover=matTagC, core=matTagCCore))
    SEC.mesh()
    # add rebars
    
    SEC.add_rebar_line(
        points=rebar_top_line,
        dia=bar_dia_top,
        gap=gap,
        color="red",
        ops_mat_tag=matTagS,
    )

    SEC.add_rebar_line(
        points=rebar_bot_line,
        dia=bar_dia_bot,
        gap=gap,
        color="red",
        ops_mat_tag=matTagS,
    )

    SEC.get_frame_props(display_results=False)
    
    SEC.centring()
    # sec.rotate(45)
    return SEC


def rect_RC_section_o_four(matTagC, matTagCCore, matTagS, Ec, Vc, fc, ec, ecu, ft, et, 
                           fccore, eccore, ecucore, Fy_reinf, Es_reinf, bs):
    """
    Defines materials for a rectangular reinforced concrete section 
    in OpenSees using Concrete04 and Steel01 models.
    """
    ops.model("basic", "-ndm", 3, "-ndf", 6)
    # Compute shear modulus Gc from Vc
    Gc = 0.5 * Ec / (1 + Vc)

    # Concrete04 - Cover material
    mat_Concrete04_cover = {
        'ID': 'Concrete04',
        'matTag': matTagC,
        'fc': fc,
        'ec': ec,
        'ecu': ecu,
        'Ec': Ec,
        'ft': ft,
        'et': et
    }

    # Concrete04 - Core material
    mat_Concrete04_core = {
        'ID': 'Concrete04',
        'matTag': matTagCCore,
        'fc': fccore,
        'ec': eccore,
        'ecu': ecucore,
        'Ec': Ec,
        'ft': ft,
        'et': et
    }

    # Steel01 - Reinforcement material
    mat_rebar = {
        'ID': 'Steel01',
        'matTag': matTagS,
        'Fy': Fy_reinf,
        'E0': Es_reinf,
        'b': bs
    }

    # Create materials in OpenSees
    create_uniaxial_material(mat_Concrete04_cover)  # Cover concrete
    create_uniaxial_material(mat_Concrete04_core)   # Core concrete
    create_uniaxial_material(mat_rebar)          # Reinforcement steel

    outlines = [[0., 0.], [.400, 0.], [.400, .500], [0., .500]]
    rebar_top_line = [[.040,.040],[.360, .040]]
    rebar_bot_line = [[.360, .460],[.040,  .460]]
    coverlines = opst.pre.section.offset(outlines, d=.040)
    cover = opst.pre.section.create_polygon_patch(outlines, holes=[coverlines])
    
    core = opst.pre.section.create_polygon_patch(coverlines)
    SEC = opst.pre.section.FiberSecMesh()
    SEC.add_patch_group(dict(cover=cover, core=core))
    SEC.set_mesh_size(dict(cover=.020, core=.020))
    SEC.set_mesh_color(dict(cover="gray", core="green"))
    SEC.set_ops_mat_tag(dict(cover=matTagC, core=matTagCCore))
    SEC.mesh()
    # add rebars
    
    SEC.add_rebar_line(
        points=rebar_top_line,
        dia=0.010,
        gap=.100,
        color="red",
        ops_mat_tag=matTagS,
    )

    SEC.add_rebar_line(
        points=rebar_bot_line,
        dia=0.010,
        gap=.100,
        color="red",
        ops_mat_tag=matTagS,
    )

    SEC.get_frame_props(display_results=False)
    
    SEC.centring()
    # sec.rotate(45)
    return SEC


def rc_section_fiber_model():
    
    ops.wipe()
    ops.model("basic", "-ndm", 3, "-ndf", 6)
    Ec = 3.45e7
    Es = 2.0e8
    Nus = 0.3
    Nuc = 0.2
    pho_c = 2.55
    pho_s = 7.86
    steel_mat = opst.pre.section.create_material(
        name="steel", elastic_modulus=Es, poissons_ratio=Nus, density=pho_s
    )
    conc_mat = opst.pre.section.create_material(
        name="conc", elastic_modulus=Ec, poissons_ratio=Nuc, density=pho_c
    )

    outlines = [[0, 0], [2, 0], [2, 2], [0, 2]]
    rebar_top_line = [[1.90,1.90],[0.090, 1.91]]
    rebar_bot_line = [[0.09, 0.09],[1.90, 0.091]]
    coverlines = opst.pre.section.offset(outlines, d=0.05)
    cover_geo = opst.pre.section.create_polygon_patch(
        outlines, holes=[coverlines], material=conc_mat
    )
    

    SEC_MESH = opst.pre.section.FiberSecMesh()
    core = opst.pre.section.create_polygon_patch(coverlines)
    SEC_MESH.add_patch_group(dict(cover=cover_geo, core=core))
    SEC_MESH.set_mesh_size(dict(cover=0.1, core=0.2))
    SEC_MESH.set_mesh_color(dict(cover="gray", core="#b84592"))
    SEC_MESH.set_ops_mat_tag(dict(cover=1, core=2))
    SEC_MESH.mesh()

    # add rebars
    # rebar_lines1 = opst.pre.section.offset(outlines, d=0.05 + 0.032 / 2)
    
    SEC_MESH.add_rebar_line(
        points=rebar_top_line, dia=0.032, gap=0.6, color="black", ops_mat_tag=3,
        
    )
    
    SEC_MESH.add_rebar_line(
        points=rebar_bot_line, dia=0.032, gap=0.1, color="black", ops_mat_tag=3,
        
    ) 
      
    props = SEC_MESH.get_sec_props(display_results=True)
    SEC_MESH.centring()
    SEC_MESH.view(fill=True, show_legend=True)
    
    return

def rc_section_fiber_model_tee_sec():
    
    ops.wipe()
    ops.model("basic", "-ndm", 3, "-ndf", 6)
    Ec = 3.45e7
    Es = 2.0e8
    Nus = 0.3
    Nuc = 0.2
    pho_c = 2.55
    pho_s = 7.86
    steel_mat = opst.pre.section.create_material(
        name="steel", elastic_modulus=Es, poissons_ratio=Nus, density=pho_s
    )
    conc_mat = opst.pre.section.create_material(
        name="conc", elastic_modulus=Ec, poissons_ratio=Nuc, density=pho_c
    )

    outlines = [
    [0.6752, 0.0000],
    [1.3872, 0.0000],
    [1.3872, 1.2714],
    [2.0000, 1.2714],
    [2.0000, 2.0000],
    [0.0000, 2.0000],
    [0.0000, 1.2714],
    [0.6752, 1.2714]
]
    rebar_top_line = [[1.90,1.90],[0.090, 1.91]]
    rebar_bot_line = [[0.09, 0.09],[1.90, 0.091]]
    coverlines = opst.pre.section.offset(outlines, d=0.05)
    cover_geo = opst.pre.section.create_polygon_patch(
        outlines, holes=[coverlines], material=conc_mat
    )
    

    SEC_MESH = opst.pre.section.FiberSecMesh()
    core = opst.pre.section.create_polygon_patch(coverlines)
    SEC_MESH.add_patch_group(dict(cover=cover_geo, core=core))
    SEC_MESH.set_mesh_size(dict(cover=0.1, core=0.2))
    SEC_MESH.set_mesh_color(dict(cover="gray", core="#b84592"))
    SEC_MESH.set_ops_mat_tag(dict(cover=1, core=2))
    SEC_MESH.mesh()

    # add rebars
    # rebar_lines1 = opst.pre.section.offset(outlines, d=0.05 + 0.032 / 2)
    
    SEC_MESH.add_rebar_line(
        points=rebar_top_line, dia=0.032, gap=0.6, color="black", ops_mat_tag=3,
        
    )
    
    SEC_MESH.add_rebar_line(
        points=rebar_bot_line, dia=0.032, gap=0.1, color="black", ops_mat_tag=3,
        
    ) 
      
    props = SEC_MESH.get_sec_props(display_results=True)
    SEC_MESH.centring()
    SEC_MESH.view(fill=True, show_legend=True)
    
    return

def rc_section_fiber_model_compo():
    
    ops.wipe()
    ops.model("basic", "-ndm", 3, "-ndf", 6)
    Ec = 3.45e7
    Es = 2.0e8
    Nus = 0.3
    Nuc = 0.2
    pho_c = 2.55
    pho_s = 7.86
    steel_mat = opst.pre.section.create_material(
        name="steel", elastic_modulus=Es, poissons_ratio=Nus, density=pho_s
    )
    conc_mat = opst.pre.section.create_material(
        name="conc", elastic_modulus=Ec, poissons_ratio=Nuc, density=pho_c
    )

    outlines = [[0, 0], [2, 0], [2, 2], [0, 2]]
    rebar_top_line = [[1.90,1.90],[0.090, 1.91]]
    rebar_bot_line = [[0.09, 0.09],[1.90, 0.091]]
    coverlines = opst.pre.section.offset(outlines, d=0.05)
    cover_geo = opst.pre.section.create_polygon_patch(
        outlines, holes=[coverlines], material=conc_mat
    )
    bonelines = [
        [0.5, 0.5],
        [1.5, 0.5],
        [1.5, 0.7],
        [1.1, 0.7],
        [1.1, 1.3],
        [1.5, 1.3],
        [1.5, 1.5],
        [0.5, 1.5],
        [0.5, 1.3],
        [0.9, 1.3],
        [0.9, 0.7],
        [0.5, 0.7],
        [0.5, 0.5],
    ]

    core_geo = opst.pre.section.create_polygon_patch(
        coverlines, holes=[bonelines], material=conc_mat
    )

    bone_geo = opst.pre.section.create_polygon_patch(bonelines, material=steel_mat)

    SEC_MESH = opst.pre.section.FiberSecMesh()
    SEC_MESH.add_patch_group(dict(cover=cover_geo, core=core_geo, bone=bone_geo))
    SEC_MESH.set_mesh_size(dict(cover=0.1, core=0.2, bone=0.1))
    SEC_MESH.set_mesh_color(dict(cover="gray", core="#b84592", bone="#ffc168"))
    SEC_MESH.set_ops_mat_tag(dict(cover=1, core=2, bone=4))
    SEC_MESH.mesh()

    # add rebars
    # rebar_lines1 = opst.pre.section.offset(outlines, d=0.05 + 0.032 / 2)
    
    SEC_MESH.add_rebar_line(
        points=rebar_top_line, dia=0.032, gap=0.6, color="black", ops_mat_tag=3,
        
    )
    
    SEC_MESH.add_rebar_line(
        points=rebar_bot_line, dia=0.032, gap=0.1, color="black", ops_mat_tag=3,
        
    ) 
      
    props = SEC_MESH.get_sec_props(display_results=True)
    SEC_MESH.centring()
    SEC_MESH.view(fill=True, show_legend=True)
    
    return

def create_rec__RC_ofour_sec():
    # ops.wipe()
    # ops.model("basic", "-ndm", 3, "-ndf", 6)
    # materials
    Ec = 3.55e7
    Vc = 0.2
    Gc = 0.5 * Ec / (1 + Vc)
    fc = -32.4e3
    ec = -2000.0e-6
    ecu = 2.1 * ec
    ft = 2.64e3
    et = 107e-6
    fccore = -40.6e3
    eccore = -4079e-6
    ecucore = -0.0144
    Fys = 300.0e3
    Es = 2.0e8
    bs = 0.01
    matTagC = 101
    matTagCCore = 201
    matTagS = 301
    # for cover
    ops.uniaxialMaterial("Concrete04", matTagC, fc, ec, ecu, Ec, ft, et)
    # for core
    ops.uniaxialMaterial("Concrete04", matTagCCore, fccore, eccore, ecucore, Ec, ft, et)
    ops.uniaxialMaterial(
        "Steel01",
        matTagS,
        Fys,
        Es,
        bs,
    )
    outlines = [[0, 0], [1, 0], [1, 1], [0, 1]]
    coverlines = opst.pre.section.offset(outlines, d=0.075)
    cover = opst.pre.section.create_polygon_patch(outlines, holes=[coverlines])
    #holelines = [[0.5, 0.5], [1.5, 0.5], [1.5, 1.5], [0.5, 1.5]]
    core = opst.pre.section.create_polygon_patch(coverlines,) #holes=[holelines] to make hollow
    SEC = opst.pre.section.FiberSecMesh()
    SEC.add_patch_group(dict(cover=cover, core=core))
    SEC.set_mesh_size(dict(cover=0.1, core=0.1))
    SEC.set_mesh_color(dict(cover="gray", core="green"))
    SEC.set_ops_mat_tag(dict(cover=matTagC, core=matTagCCore))
    SEC.mesh()
    # add rebars
    # rebar_lines = opst.pre.section.offset(outlines, d=0.075 + 0.032 / 2) for columns
    rebar_top_line = [[0.075,0.925],[0.925, 0.925]]
    rebar_bot_line = [[0.075, 0.075],[0.95, 0.075]]

    SEC.add_rebar_line(
        points=rebar_top_line,
        dia=0.04,
        gap=0.15,
        color="red",
        ops_mat_tag=matTagS,
    )

    SEC.add_rebar_line(
        points=rebar_bot_line,
        dia=0.04,
        gap=0.15,
        color="red",
        ops_mat_tag=matTagS,
    )

    SEC.get_frame_props(display_results=False)
    SEC.centring()
    # sec.rotate(45)
    return SEC