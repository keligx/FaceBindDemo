
CONTEXT_TO_OBJECT_MODE = {
    'EDIT_MESH': 'EDIT',
    'EDIT_CURVE': 'EDIT',
    'EDIT_SURFACE': 'EDIT',
    'EDIT_TEXT': 'EDIT',
    'EDIT_ARMATURE': 'EDIT',
    'EDIT_METABALL': 'EDIT',
    'EDIT_LATTICE': 'EDIT',
    'POSE': 'POSE',
    'SCULPT': 'SCULPT',
    'PAINT_WEIGHT': 'WEIGHT_PAINT',
    'PAINT_VERTEX': 'VERTEX_PAINT',
    'PAINT_TEXTURE': 'TEXTURE_PAINT',
    'PARTICLE': 'PARTICLE_EDIT',
    'OBJECT': 'OBJECT',
    'PAINT_GPENCIL': 'PAINT_GPENCIL',
    'EDIT_GPENCIL': 'EDIT_GPENCIL',
    'SCULPT_GPENCIL': 'SCULPT_GPENCIL',
    'WEIGHT_GPENCIL': 'WEIGHT_GPENCIL',
    'VERTEX_GPENCIL': 'VERTEX_GPENCIL',
}

MODIFIER_TYPES = [
    'GENERATOR',
    'FNGENERATOR',
    'ENVELOPE',
    'CYCLES',
    'NOISE',
    'LIMITS',
    'STEPPED',
]

VERTEX_GROUPS = [
    'faceit_right_eyeball',
    'faceit_left_eyeball',
    'faceit_left_eyes_other',
    'faceit_right_eyes_other',
    'faceit_upper_teeth',
    'faceit_lower_teeth',
    'faceit_tongue',
    'faceit_eyelashes',
    'faceit_rigid',
    'faceit_main',
    'faceit_facial_hair',
]

GROUP_COLORS_LIGHT = {
    'faceit_right_eyeball': (1.0, 0.0, 0.0, 1.0),     # Red
    'faceit_left_eyeball': (0.0, 1.0, 0.0, 1.0),     # Green
    'faceit_left_eyes_other': (0.0, 0.0, 1.0, 1.0),     # Blue
    'faceit_right_eyes_other': (1.0, 1.0, 0.0, 1.0),     # Yellow
    'faceit_upper_teeth': (0.5, 0.0, 0.5, 1.0),     # Purple
    'faceit_lower_teeth': (1.0, 0.5, 0.0, 1.0),     # Orange
    'faceit_tongue': (0.0, 1.0, 1.0, 1.0),     # Cyan
    'faceit_eyelashes': (1.0, 0.0, 1.0, 1.0),     # Magenta
    'faceit_rigid': (0.0, 0.5, 0.5, 1.0),     # Teal
    'faceit_main': (1.0, 0.5, 0.5, 1.0),     # Pink
    'faceit_facial_hair': (0.5, 1.0, 0.0, 1.0)      # Lime
}
GROUP_COLORS_DARK = {
    'faceit_right_eyeball': (0.5, 0.0, 0.0, 1.0),     # Dark Red
    'faceit_left_eyeball': (0.0, 0.5, 0.0, 1.0),     # Dark Green
    'faceit_left_eyes_other': (0.0, 0.0, 0.5, 1.0),     # Dark Blue
    'faceit_right_eyes_other': (0.5, 0.5, 0.0, 1.0),     # Dark Yellow
    'faceit_upper_teeth': (0.25, 0.0, 0.25, 1.0),   # Dark Purple
    'faceit_lower_teeth': (0.5, 0.25, 0.0, 1.0),    # Dark Orange
    'faceit_tongue': (0.0, 0.5, 0.5, 1.0),     # Dark Cyan
    'faceit_eyelashes': (0.5, 0.0, 0.5, 1.0),     # Dark Magenta
    'faceit_rigid': (0.0, 0.25, 0.25, 1.0),   # Dark Teal
    'faceit_main': (0.5, 0.25, 0.25, 1.0),   # Dark Pink
    'faceit_facial_hair': (0.25, 0.5, 0.0, 1.0)     # Dark Lime
}


LIVE_MOCAP_DEFAULT_SETTINGS = {
    'FACECAP': {
        'address': '0.0.0.0',
        'port': 9001,
        'rotation_units': 'DEG',
        'can_animate_head_rotation': True,
        'can_animate_head_location': True,
        'can_animate_eye_rotation': True,
    },
    'EPIC': {
        'address': '0.0.0.0',
        'port': 11111,
        'rotation_units': 'RAD',
        'can_animate_head_rotation': True,
        'can_animate_head_location': False,
        'can_animate_eye_rotation': True,
    },
    'TILE': {
        'address': '0.0.0.0',
        'port': 9001,
        'rotation_units': 'DEG',
        'rotation_units_variable': True,
        'can_animate_head_rotation': True,
        'can_animate_head_location': True,
        'can_animate_eye_rotation': True,

    },
    'IFACIALMOCAP': {
        'address': '0.0.0.0',
        'port': 49983,
        'rotation_units': 'DEG',
        'can_animate_head_rotation': True,
        'can_animate_head_location': True,
        'can_animate_eye_rotation': True,
        'head_location_multiplier': 100,
    },
    'A2F': {
        'can_animate_head_rotation': False,
        'can_animate_head_location': False,
        'can_animate_eye_rotation': False,
    },
}


FACE_REGIONS_BASE = {
    'Eyes': [
        'eyeLookDownLeft',
        'eyeLookInLeft',
        'eyeLookOutLeft',
        'eyeLookUpLeft',
        'eyeLookDownRight',
        'eyeLookInRight',
        'eyeLookOutRight',
        'eyeLookUpRight',
        'eyesLookLeft',
        'eyesLookRight',
        'eyesLookUp',
        'eyesLookDown',
    ],
    'Eyelids': [
        'eyeBlinkLeft',
        'eyeBlinkRight',
        'eyeSquintLeft',
        'eyeWideLeft',
        'eyeSquintRight',
        'eyeWideRight',
        'eyesCloseL',
        'eyesCloseR',
        'eyesUpperLidRaiserL',
        'eyesUpperLidRaiserR',
        'squintL',
        'squintR',
    ],
    'Brows': [
        'browDownLeft',
        'browDownRight',
        'browInnerUp',
        'browOuterUpLeft',
        'browOuterUpRight',
        'browLowerL',
        'browLowerR',
        'innerBrowRaiserL',
        'innerBrowRaiserR',
        'outerBrowRaiserL',
        'outerBrowRaiserR',
    ],
    'Cheeks': [
        'cheekPuff',
        'cheekSquintLeft',
        'cheekSquintRight',
        'cheekRaiserL',
        'cheekRaiserR',
        'cheekPuffL',
        'cheekPuffR',
    ],
    'Nose': [
        'noseSneerLeft',
        'noseSneerRight',
        'noseWrinklerL',
        'noseWrinklerR',
    ],
    'Mouth': [
        'jawForward',
        'jawLeft',
        'jawRight',
        'jawOpen',
        'mouthClose',
        'mouthFunnel',
        'mouthPucker',
        'mouthRight',
        'mouthLeft',
        'mouthSmileLeft',
        'mouthSmileRight',
        'mouthFrownRight',
        'mouthFrownLeft',
        'mouthDimpleLeft',
        'mouthDimpleRight',
        'mouthStretchLeft',
        'mouthStretchRight',
        'mouthRollLower',
        'mouthRollUpper',
        'mouthShrugLower',
        'mouthShrugUpper',
        'mouthPressLeft',
        'mouthPressRight',
        'mouthLowerDownLeft',
        'mouthLowerDownRight',
        'mouthUpperUpLeft',
        'mouthUpperUpRight',
        'aa_ah_ax_01',
        'aa_02',
        'ao_03',
        'ey_eh_uh_04',
        'er_05',
        'y_iy_ih_ix_06',
        'w_uw_07',
        'ow_08',
        'aw_09',
        'oy_10',
        'ay_11',
        'h_12',
        'r_13',
        'l_14',
        's_z_15',
        'sh_ch_jh_zh_16',
        'th_dh_17',
        'f_v_18',
        'd_t_n_19',
        'k_g_ng_20',
        'p_b_m_21',
        'jawDrop',
        'jawDropLipTowards',
        'jawThrust',
        'jawSlideLeft',
        'jawSlideRight',
        'mouthSlideLeft',
        'mouthSlideRight',
        'dimplerL',
        'dimplerR',
        'lipCornerPullerL',
        'lipCornerPullerR',
        'lipCornerDepressorL',
        'lipCornerDepressorR',
        'lipStretcherL',
        'lipStretcherR',
        'upperLipRaiserL',
        'upperLipRaiserR',
        'lowerLipDepressorL',
        'lowerLipDepressorR',
        'chinRaiser',
        'lipPressor',
        'pucker',
        'funneler',
        'lipSuck',

    ],
    'Tongue': [
        'tongueOut',
        'tongueBack',
        'tongueTwistLeft',
        'tongueTwistRight',
        'tongueLeft',
        'tongueRight',
        'tongueWide',
        'tongueThin',
        'tongueCurlUp',
        'tongueCurlUp',
        'tongueCurlUp',
        'tongueCurlDown',
    ],
    'Other': [
    ]
}

BONES = [
    'MCH-eyes_parent', 'eyes', 'eye.L', 'eye.R', 'DEF-face', 'DEF-forehead.L', 'DEF-forehead.R', 'DEF-forehead.L.001',
    'DEF-forehead.R.001', 'DEF-forehead.L.002', 'DEF-forehead.R.002', 'DEF-temple.L', 'DEF-temple.R', 'master_eye.L',
    'brow.B.L', 'DEF-brow.B.L', 'brow.B.L.001', 'DEF-brow.B.L.001', 'brow.B.L.002', 'DEF-brow.B.L.002', 'brow.B.L.003',
    'DEF-brow.B.L.003', 'brow.B.L.004', 'lid.B.L', 'lid.B.L.001', 'lid.B.L.002', 'lid.B.L.003', 'lid.T.L',
    'lid.T.L.001', 'lid.T.L.002', 'lid.T.L.003', 'MCH-eye.L', 'DEF_eye.L', 'MCH-eye.L.001', 'MCH-lid.B.L',
    'DEF-lid.B.L', 'MCH-lid.B.L.001', 'DEF-lid.B.L.001', 'MCH-lid.B.L.002', 'DEF-lid.B.L.002', 'MCH-lid.B.L.003',
    'DEF-lid.B.L.003', 'MCH-lid.T.L', 'DEF-lid.T.L', 'MCH-lid.T.L.001', 'DEF-lid.T.L.001', 'MCH-lid.T.L.002',
    'DEF-lid.T.L.002', 'MCH-lid.T.L.003', 'DEF-lid.T.L.003', 'master_eye.R', 'brow.B.R', 'DEF-brow.B.R', 'brow.B.R.001',
    'DEF-brow.B.R.001', 'brow.B.R.002', 'DEF-brow.B.R.002', 'brow.B.R.003', 'DEF-brow.B.R.003', 'brow.B.R.004',
    'lid.B.R', 'lid.B.R.001', 'lid.B.R.002', 'lid.B.R.003', 'lid.T.R', 'lid.T.R.001', 'lid.T.R.002', 'lid.T.R.003',
    'MCH-eye.R', 'DEF_eye.R', 'MCH-eye.R.001', 'MCH-lid.B.R', 'DEF-lid.B.R', 'MCH-lid.B.R.001', 'DEF-lid.B.R.001',
    'MCH-lid.B.R.002', 'DEF-lid.B.R.002', 'MCH-lid.B.R.003', 'DEF-lid.B.R.003', 'MCH-lid.T.R', 'DEF-lid.T.R',
    'MCH-lid.T.R.001', 'DEF-lid.T.R.001', 'MCH-lid.T.R.002', 'DEF-lid.T.R.002', 'MCH-lid.T.R.003', 'DEF-lid.T.R.003',
    'jaw_master', 'chin', 'DEF-chin', 'chin.001', 'DEF-chin.001', 'chin.L', 'DEF-chin.L', 'chin.R', 'DEF-chin.R', 'jaw',
    'DEF-jaw', 'jaw.L.001', 'DEF-jaw.L.001', 'jaw.R.001', 'DEF-jaw.R.001', 'MCH-tongue.001', 'tongue.001',
    'DEF-tongue.001', 'MCH-tongue.002', 'tongue.002', 'DEF-tongue.002', 'tongue_master', 'tongue', 'DEF-tongue',
    'tongue.003', 'teeth.B', 'DEF-teeth.B', 'brow.T.L', 'DEF-cheek.T.L', 'DEF-brow.T.L', 'brow.T.L.001',
    'DEF-brow.T.L.001', 'brow.T.L.002', 'DEF-brow.T.L.002', 'brow.T.L.003', 'DEF-brow.T.L.003', 'brow.T.R',
    'DEF-cheek.T.R', 'DEF-brow.T.R', 'brow.T.R.001', 'DEF-brow.T.R.001', 'brow.T.R.002', 'DEF-brow.T.R.002',
    'brow.T.R.003', 'DEF-brow.T.R.003', 'jaw.L', 'DEF-jaw.L', 'jaw.R', 'DEF-jaw.R', 'nose', 'DEF-nose', 'nose.L',
    'DEF-nose.L', 'nose.R', 'DEF-nose.R', 'MCH-mouth_lock', 'MCH-jaw_master', 'lip.B', 'DEF-lip.B.L', 'DEF-lip.B.R',
    'chin.002', 'MCH-jaw_master.001', 'lip.B.L.001', 'DEF-lip.B.L.001', 'lip.B.R.001', 'DEF-lip.B.R.001',
    'MCH-jaw_master.002', 'cheek.B.L.001', 'DEF-cheek.B.L.001', 'cheek.B.R.001', 'DEF-cheek.B.R.001', 'lips.L',
    'DEF-cheek.B.L', 'lips.R', 'DEF-cheek.B.R', 'MCH-jaw_master.003', 'lip.T.L.001', 'DEF-lip.T.L.001', 'lip.T.R.001',
    'DEF-lip.T.R.001', 'lip.T', 'DEF-lip.T.L', 'DEF-lip.T.R', 'nose.005', 'MCH-jaw_master.004', 'nose_master',
    'nose.002', 'DEF-nose.002', 'nose.003', 'DEF-nose.003', 'nose.001', 'DEF-nose.001', 'nose.004', 'DEF-nose.004',
    'nose.L.001', 'DEF-nose.L.001', 'nose.R.001', 'DEF-nose.R.001', 'cheek.T.L.001', 'DEF-cheek.T.L.001',
    'cheek.T.R.001', 'DEF-cheek.T.R.001', 'DEF_forhead_01.L', 'DEF_forhead_02.L', 'DEF_forhead_03.L',
    'DEF_forhead_04.L', 'DEF_forhead_01.R', 'DEF_forhead_02.R', 'DEF_forhead_03.R', 'DEF_forhead_04.R', 'teeth.T',
    'DEF-teeth.T']

CTRL_BONES = [
    'eyes', 'eye.L', 'eye.R', 'brow.B.L', 'brow.B.L.001', 'brow.B.L.002', 'brow.B.L.003', 'brow.B.L.004', 'lid.B.L',
    'lid.B.L.001', 'lid.B.L.002', 'lid.B.L.003', 'lid.T.L', 'lid.T.L.001', 'lid.T.L.002', 'lid.T.L.003', 'brow.B.R',
    'brow.B.R.001', 'brow.B.R.002', 'brow.B.R.003', 'brow.B.R.004', 'lid.B.R', 'lid.B.R.001', 'lid.B.R.002',
    'lid.B.R.003', 'lid.T.R', 'lid.T.R.001', 'lid.T.R.002', 'lid.T.R.003', 'jaw_master', 'chin', 'chin.001', 'chin.L',
    'chin.R', 'jaw', 'jaw.L.001', 'jaw.R.001', 'tongue.001', 'tongue.002', 'tongue_master', 'tongue', 'tongue.003',
    'teeth.B', 'brow.T.L', 'brow.T.L.001', 'brow.T.L.002', 'brow.T.L.003', 'brow.T.R', 'brow.T.R.001', 'brow.T.R.002',
    'brow.T.R.003', 'jaw.L', 'jaw.R', 'nose', 'nose.L', 'nose.R', 'lip.B', 'chin.002', 'lip.B.L.001', 'lip.B.R.001',
    'cheek.B.L.001', 'cheek.B.R.001', 'lips.L', 'lips.R', 'lip.T.L.001', 'lip.T.R.001', 'lip.T', 'nose.005',
    'nose_master', 'nose.002', 'nose.003', 'nose.001', 'nose.004', 'nose.L.001', 'nose.R.001', 'cheek.T.L.001',
    'cheek.T.R.001', 'teeth.T']

MOD_TYPE_ICON_DICT = {
    'DATA_TRANSFER': 'MOD_DATA_TRANSFER',
    'MESH_CACHE': 'MOD_MESHDEFORM',
    'MESH_SEQUENCE_CACHE': 'MOD_MESHDEFORM',
    'NORMAL_EDIT': 'MOD_NORMALEDIT',
    'WEIGHTED_NORMAL': 'MOD_NORMALEDIT',
    'UV_PROJECT': 'MOD_UVPROJECT',
    'UV_WARP': 'MOD_UVPROJECT',
    'VERTEX_WEIGHT_EDIT': 'MOD_VERTEX_WEIGHT',
    'VERTEX_WEIGHT_MIX': 'MOD_VERTEX_WEIGHT',
    'VERTEX_WEIGHT_PROXIMITY': 'MOD_VERTEX_WEIGHT',
    'ARRAY': 'MOD_ARRAY',
    'BEVEL': 'MOD_BEVEL',
    'BOOLEAN': 'MOD_BOOLEAN',
    'BUILD': 'MOD_BUILD',
    'DECIMATE': 'MOD_DECIM',
    'EDGE_SPLIT': 'MOD_EDGESPLIT',
    'NODES': 'GEOMETRY_NODES',
    'MASK': 'MOD_MASK',
    'MIRROR': 'MOD_MIRROR',
    'MESH_TO_VOLUME': 'VOLUME_DATA',
    'MULTIRES': 'MOD_MULTIRES',
    'REMESH': 'MOD_REMESH',
    'SCREW': 'MOD_SCREW',
    'SKIN': 'MOD_SKIN',
    'SOLIDIFY': 'MOD_SOLIDIFY',
    'SUBSURF': 'MOD_SUBSURF',
    'TRIANGULATE': 'MOD_TRIANGULATE',
    'VOLUME_TO_MESH': 'VOLUME_DATA',
    'WELD': 'AUTOMERGE_OFF',
    'WIREFRAME': 'MOD_WIREFRAME',
    'ARMATURE': 'MOD_ARMATURE',
    'CAST': 'MOD_CAST',
    'CURVE': 'MOD_CURVE',
    'DISPLACE': 'MOD_DISPLACE',
    'HOOK': 'HOOK',
    'LAPLACIANDEFORM': 'MOD_MESHDEFORM',
    'LATTICE': 'MOD_LATTICE',
    'MESH_DEFORM': 'MOD_MESHDEFORM',
    'SHRINKWRAP': 'MOD_SHRINKWRAP',
    'SIMPLE_DEFORM': 'MOD_SIMPLEDEFORM',
    'SMOOTH': 'MOD_SMOOTH',
    'CORRECTIVE_SMOOTH': 'MOD_SMOOTH',
    'LAPLACIANSMOOTH': 'MOD_SMOOTH',
    'SURFACE_DEFORM': 'MOD_MESHDEFORM',
    'WARP': 'MOD_WARP',
    'WAVE': 'MOD_WAVE',
    'VOLUME_DISPLACE': 'VOLUME_DATA',
    'CLOTH': 'MOD_CLOTH',
    'COLLISION': 'MOD_PHYSICS',
    'DYNAMIC_PAINT': 'MOD_DYNAMICPAINT',
    'EXPLODE': 'MOD_EXPLODE',
    'FLUID': 'MOD_FLUIDSIM',
    'OCEAN': 'MOD_OCEAN',
    'PARTICLE_INSTANCE': 'MOD_PARTICLE_INSTANCE',
    'PARTICLE_SYSTEM': 'MOD_PARTICLES',
    'SOFT_BODY': 'MOD_SOFT',
    'SURFACE': 'MODIFIER',
}

BAKE_MOD_TYPES = [
    'ARMATURE', 'CAST', 'CURVE', 'DISPLACE', 'HOOK', 'LAPLACIANDEFORM', 'LATTICE', 'MESH_DEFORM', 'SHRINKWRAP',
    'SIMPLE_DEFORM', 'SMOOTH', 'CORRECTIVE_SMOOTH', 'LAPLACIANSMOOTH', 'SURFACE_DEFORM', 'WARP', 'WAVE',
    'VOLUME_DISPLACE', 'DATA_TRANSFER', 'MESH_CACHE', 'MESH_SEQUENCE_CACHE', 'VERTEX_WEIGHT_EDIT', 'VERTEX_WEIGHT_MIX',
    'VERTEX_WEIGHT_PROXIMITY', 'CLOTH']

# HIDE_MOD_TYPES = ['SURFACE_DEFORM']
GENERATORS = [
    'ARRAY',
    'BEVEL',
    'BOOLEAN',
    'BUILD',
    'DECIMATE',
    'EDGE_SPLIT',
    'MASK',
    'MIRROR',
    'MULTIRES',
    'REMESH',
    'SCREW',
    'SKIN',
    'SOLIDIFY',
    'SUBSURF',
    'TRIANGULATE',
    'WELD',
    'WIREFRAME',
    'NODES'
]

DEFORMERS = [
    'ARMATURE',
    'CAST',
    'CURVE',
    'DISPLACE',
    'HOOK',
    'LAPLACIANDEFORM',
    'LAPLACIANSMOOTH',
    'LATTICE',
    'MESH_DEFORM',
    'SHRINKWRAP',
    'SIMPLE_DEFORM',
    'SMOOTH',
    'WARP',
    'WAVE',
    'SURFACE_DEFORM',
    'CLOTH',
    'SOFT_BODY',
]

# ---------------- ASYMMETRIC ------------------------
# | - 0-70 : vertices in the reference mesh
# | - 100-.. : other world points such as eye or jaw


bone_dict_asymmetric = {
    0: {
        'head': ['DEF-chin'],
        'tail': ['jaw_master', 'DEF-jaw'],
        'all': ['chin', ],
    },
    1: {
        'head': ['DEF-jaw'],
        'tail': [],
        'all': ['jaw'],
    },
    2: {
        'head': ['DEF-chin.001'],
        'tail': ['DEF-chin', ],
        'all': ['chin.001', ],
    },
    3: {
        'head': [],
        'tail': ['DEF-chin.001'],
        'all': ['chin.002'],
    },
    4: {
        'head': ['DEF-chin.R'],
        'tail': ['DEF-jaw.R.001'],
        'all': ['chin.R'],
    },
    5: {
        'head': ['DEF-chin.L'],
        'tail': ['DEF-jaw.L.001'],
        'all': ['chin.L'],
    },
    6: {
        'head': ['DEF-lip.B.L', 'DEF-lip.B.R'],
        'tail': [],
        'all': ['lip.B'],
    },
    7: {
        'head': ['DEF-lip.B.R.001'],
        'tail': ['DEF-lip.B.R'],
        'all': ['lip.B.R.001'],
    },
    8: {
        'head': ['DEF-lip.B.L.001'],
        'tail': ['DEF-lip.B.L'],
        'all': ['lip.B.L.001'],
    },
    9: {
        'head': ['DEF-lip.T.L', 'DEF-lip.T.R'],
        'tail': [],
        'all': ['lip.T'],
    },
    10: {
        'head': ['DEF-lip.T.R.001'],
        'tail': ['DEF-lip.T.R'],
        'all': ['lip.T.R.001'],
    },
    11: {
        'head': ['DEF-lip.T.L.001'],
        'tail': ['DEF-lip.T.L'],
        'all': ['lip.T.L.001'],
    },
    12: {
        'head': ['DEF-cheek.B.L'],
        'tail': ['DEF-chin.L', 'DEF-lip.T.L.001', 'DEF-lip.B.L.001'],
        'all': ['lips.L'],
    },
    13: {
        'head': ['DEF-cheek.B.R'],
        'tail': ['DEF-chin.R', 'DEF-lip.T.R.001', 'DEF-lip.B.R.001'],
        'all': ['lips.R'],
    },
    14: {
        'head': [],
        'tail': ['DEF-nose.003'],
        'all': ['DEF-nose.004', 'nose.004', 'nose_master'],
    },
    # cheeck low
    15: {
        'head': ['DEF-cheek.B.R.001'],
        'tail': ['DEF-cheek.B.R'],
        'all': ['cheek.B.R.001'],
    },
    16: {
        'head': ['DEF-cheek.B.L.001'],
        'tail': ['DEF-cheek.B.L'],
        'all': ['cheek.B.L.001'],
    },
    17: {
        'head': ['DEF-nose.L.001'],
        'tail': ['DEF-nose.L'],
        'all': ['nose.L.001'],
    },
    18: {
        'head': ['DEF-nose.R.001'],
        'tail': ['DEF-nose.R'],
        'all': ['nose.R.001'],
    },
    19: {
        'head': ['DEF-jaw.L.001'],
        'tail': ['DEF-jaw.L'],
        'all': ['jaw.L.001'],
    },
    20: {
        'head': ['DEF-jaw.R.001'],
        'tail': ['DEF-jaw.R'],
        'all': ['jaw.R.001'],
    },
    21: {
        'head': ['DEF-nose.002'],
        'tail': ['DEF-nose.L.001', 'DEF-nose.R.001', 'DEF-nose.001'],
        'all': ['nose.002'],
    },
    22: {
        'head': ['DEF-cheek.T.R.001'],
        'tail': ['DEF-cheek.T.R'],
        'all': ['cheek.T.R.001'],
    },
    23: {
        'head': ['DEF-cheek.T.L.001'],
        'tail': ['DEF-cheek.T.L'],
        'all': ['cheek.T.L.001'],
    },

    24: {
        'head': ['DEF-jaw.R'],
        'tail': ['DEF-temple.R'],
        'all': ['jaw.R'],
    },
    25: {
        'head': ['DEF-jaw.L'],
        'tail': ['DEF-temple.L'],
        'all': ['jaw.L'],
    },
    26: {
        'head': ['DEF-nose.L'],
        'tail': ['DEF-cheek.T.L.001'],
        'all': ['nose.L'],
    },
    27: {
        'head': ['DEF-nose.R'],
        'tail': ['DEF-cheek.T.R.001'],
        'all': ['nose.R'],
    },
    28: {
        'head': ['DEF-lid.B.R.001'],
        'tail': ['MCH-lid.B.R.001', 'DEF-lid.B.R'],
        'all': ['lid.B.R.001'],
    },
    29: {
        'head': ['DEF-lid.B.L.001'],
        'tail': ['MCH-lid.B.L.001', 'DEF-lid.B.L'],
        'all': ['lid.B.L.001'],
    },
    30: {
        'head': ['DEF-lid.B.L.002'],
        'tail': ['DEF-lid.B.L.001', 'MCH-lid.B.L.002'],
        'all': ['lid.B.L.002'],
    },
    31: {
        'head': ['DEF-lid.B.R.002'],
        'tail': ['DEF-lid.B.R.001', 'MCH-lid.B.R.002'],
        'all': ['lid.B.R.002'],
    },
    32: {
        'head': ['DEF-lid.B.L'],
        'tail': ['DEF-lid.T.L.003', 'MCH-lid.B.L'],
        'all': ['lid.B.L'],
    },
    33: {
        'head': ['DEF-lid.B.R'],
        'tail': ['DEF-lid.T.R.003', 'MCH-lid.B.R'],
        'all': ['lid.B.R'],
    },
    34: {
        'head': ['DEF-lid.B.L.003'],
        'tail': ['DEF-lid.B.L.002', 'MCH-lid.B.L.003'],
        'all': ['lid.B.L.003'],
    },
    35: {
        'head': ['DEF-lid.B.R.003'],
        'tail': ['DEF-lid.B.R.002', 'MCH-lid.B.R.003'],
        'all': ['lid.B.R.003'],
    },
    36: {
        'head': ['DEF-nose'],
        'tail': ['DEF-brow.T.L.003', 'DEF-brow.T.R.003'],
        'all': ['nose'],
    },
    37: {
        'head': ['DEF-lid.T.L.003'],
        'tail': ['DEF-lid.T.L.002', 'MCH-lid.T.L.003'],
        'all': ['lid.T.L.003'],
    },
    38: {
        'head': ['DEF-lid.T.R.003'],
        'tail': ['DEF-lid.T.R.002', 'MCH-lid.T.R.003'],
        'all': ['lid.T.R.003'],
    },
    39: {
        'head': [],
        'tail': ['DEF-brow.B.R.003'],
        'all': ['brow.B.R.004'],
    },
    40: {
        'head': [],
        'tail': ['DEF-brow.B.L.003'],
        'all': ['brow.B.L.004'],
    },
    41: {
        'head': ['DEF-lid.T.L'],
        'tail': ['DEF-lid.B.L.003', 'MCH-lid.T.L'],
        'all': ['lid.T.L'],
    },
    42: {
        'head': ['DEF-lid.T.R'],
        'tail': ['DEF-lid.B.R.003', 'MCH-lid.T.R'],
        'all': ['lid.T.R'],
    },
    43: {
        'head': ['DEF-lid.T.R.002'],
        'tail': ['DEF-lid.T.R.001', 'MCH-lid.T.R.002'],
        'all': ['lid.T.R.002'],
    },
    44: {
        'head': ['DEF-lid.T.L.002'],
        'tail': ['DEF-lid.T.L.001', 'MCH-lid.T.L.002'],
        'all': ['lid.T.L.002'],
    },
    45: {
        'head': ['DEF-lid.T.L.001'],
        'tail': ['DEF-lid.T.L', 'MCH-lid.T.L.001'],
        'all': ['lid.T.L.001'],
    },
    46: {
        'head': ['DEF-lid.T.R.001'],
        'tail': ['DEF-lid.T.R', 'MCH-lid.T.R.001'],
        'all': ['lid.T.R.001'],
    },
    47: {
        'head': ['DEF-brow.B.L.003'],
        'tail': ['DEF-brow.B.L.002'],
        'all': ['brow.B.L.003'],
    },
    48: {
        'head': ['DEF-brow.B.R.003'],
        'tail': ['DEF-brow.B.R.002'],
        'all': ['brow.B.R.003'],
    },
    49: {
        'head': ['DEF-brow.T.L', 'DEF-cheek.T.L'],
        'tail': ['DEF-cheek.B.L.001'],
        'all': ['brow.T.L'],
    },
    50: {
        'head': ['DEF-brow.T.R', 'DEF-cheek.T.R'],
        'tail': ['DEF-cheek.B.R.001'],
        'all': ['brow.T.R'],
    },
    51: {
        'head': ['DEF-brow.B.R'],
        'tail': [],
        'all': ['brow.B.R'],
    },
    52: {
        'head': ['DEF-brow.B.L'],
        'tail': [],
        'all': ['brow.B.L'],
    },
    53: {
        'head': ['DEF-brow.B.R.002'],
        'tail': ['DEF-brow.B.R.001'],
        'all': ['brow.B.R.002'],
    },
    54: {
        'head': ['DEF-brow.B.L.002'],
        'tail': ['DEF-brow.B.L.001'],
        'all': ['brow.B.L.002'],
    },
    55: {
        'head': ['DEF-brow.B.R.001'],
        'tail': ['DEF-brow.B.R'],
        'all': ['brow.B.R.001'],
    },
    56: {
        'head': ['DEF-brow.B.L.001'],
        'tail': ['DEF-brow.B.L'],
        'all': ['brow.B.L.001'],
    },
    57: {
        'head': ['DEF-brow.T.L.003'],
        'tail': ['DEF-brow.T.L.002', 'DEF-forehead.L'],
        'all': ['brow.T.L.003'],
    },
    58: {
        'head': ['DEF-brow.T.R.003'],
        'tail': ['DEF-brow.T.R.002', 'DEF-forehead.R'],
        'all': ['brow.T.R.003'],
    },
    59: {
        'head': ['DEF_forhead_01.L', 'DEF-temple.L'],
        'tail': [],
        'all': [],
    },
    60: {
        'head': ['DEF_forhead_01.R', 'DEF-temple.R'],
        'tail': [],
        'all': [],
    },
    61: {
        'head': ['DEF-brow.T.R.001'],
        'tail': ['DEF-brow.T.R', 'DEF-forehead.R.002'],
        'all': ['brow.T.R.001'],
    },
    62: {
        'head': ['DEF-brow.T.L.001'],
        'tail': ['DEF-brow.T.L', 'DEF-forehead.L.002'],
        'all': ['brow.T.L.001'],
    },
    63: {
        'head': ['DEF-brow.T.L.002'],
        'tail': ['DEF-brow.T.L.001', 'DEF-forehead.L.001'],
        'all': ['brow.T.L.002'],
    },
    64: {
        'head': ['DEF-brow.T.R.002'],
        'tail': ['DEF-brow.T.R.001', 'DEF-forehead.R.001'],
        'all': ['brow.T.R.002'],
    },
    65: {
        'head': [],
        'tail': ['DEF_forhead_04.L', 'DEF_forhead_04.R'],
        'all': [],
    },
    66: {
        'head': ['DEF-forehead.R', 'DEF_forhead_04.R'],
        'tail': ['DEF_forhead_03.R'],
        'all': [],
    },
    67: {
        'head': ['DEF-forehead.L', 'DEF_forhead_04.L'],
        'tail': ['DEF_forhead_03.L'],
        'all': [],
    },
    68: {
        'head': ['DEF_forhead_02.R', 'DEF-forehead.R.002'],
        'tail': ['DEF_forhead_01.R'],
        'all': [],
    },
    69: {
        'head': ['DEF_forhead_02.L', 'DEF-forehead.L.002'],
        'tail': ['DEF_forhead_01.L'],
        'all': [],
    },
    70: {
        'head': ['DEF_forhead_03.R', 'DEF-forehead.R.001'],
        'tail': ['DEF_forhead_02.R'],
        'all': [],
    },
    71: {
        'head': ['DEF_forhead_03.L', 'DEF-forehead.L.001'],
        'tail': ['DEF_forhead_02.L'],
        'all': [],
    },

    101: {
        'head': ['MCH-lid.T.L', 'MCH-lid.T.L.001', 'MCH-lid.T.L.002', 'MCH-lid.T.L.003', 'MCH-lid.B.L', 'MCH-lid.B.L.001', 'MCH-lid.B.L.002', 'MCH-lid.B.L.003', ],
        'tail': [],
        'all': ['master_eye.L', 'DEF_eye.L', 'MCH-eye.L'],
    },
    102: {
        'head': [],
        'tail': [],
        'all': ['jaw_master', 'MCH-mouth_lock', 'MCH-jaw_master', 'MCH-jaw_master.001', 'MCH-jaw_master.002', 'MCH-jaw_master.003', 'MCH-jaw_master.004'],
    },
    103: {
        'head': ['DEF-nose.001'],
        'tail': ['DEF-nose'],
        'all': ['nose.001'],
    },
    104: {
        'head': [],
        'tail': ['DEF-nose.004'],
        'all': ['nose.005'],
    },
    105: {
        'head': ['DEF-nose.003'],
        'tail': ['DEF-nose.002'],
        'all': ['nose.003'],
    },
    106: {
        'head': [],
        'tail': [],
        'all': ['DEF-teeth.T', 'teeth.T'],
    },
    107: {
        'head': [],
        'tail': [],
        'all': ['DEF-teeth.B', 'teeth.B'],
    },
    108: {
        'head': [],
        'tail': [],
        'all': ['tongue_master', 'tongue', 'DEF-tongue', 'tongue.003', 'MCH-tongue.001', 'tongue.001', 'DEF-tongue.001', 'MCH-tongue.002', 'tongue.002', 'DEF-tongue.002'],
    },
    109: {
        'head': [],
        'tail': [],
        'all': ['DEF-face', 'MCH-eyes_parent']
    },
    111: {
        'head': ['MCH-lid.T.R', 'MCH-lid.T.R.001', 'MCH-lid.T.R.002', 'MCH-lid.T.R.003', 'MCH-lid.B.R', 'MCH-lid.B.R.001', 'MCH-lid.B.R.002', 'MCH-lid.B.R.003', ],
        'tail': [],
        'all': ['master_eye.R', 'DEF_eye.R', 'MCH-eye.R'],
    },
    112: {
        'head': ['DEF-tongue'],
        'tail': ['tongue_master'],
        'all': ['tongue']
    },
    113: {
        'head': ['DEF-tongue.001', 'tongue_master'],
        'tail': ['DEF-tongue'],
        'all': ['tongue.001']
    },
    114: {
        'head': ['DEF-tongue.002', 'tongue_master'],
        'tail': ['DEF-tongue.001'],
        'all': ['tongue.002']
    },
    115: {
        'head': [],
        'tail': ['DEF-tongue.002'],
        'all': ['tongue.003']
    },

}
# ---------------- SYMMETRIC -------------------------
# | - 0-40 : vertices in the reference mesh
# | - 100-.. : other world points such as eye or jaw
# ----------------------------------------------------
bone_dict_symmetric = {
    0: {
        'head': ['DEF-jaw'],
        'tail': [],
        'all': ['jaw'],
    },
    1: {
        'head': ['DEF-chin'],
        'tail': ['jaw_master', 'DEF-jaw'],
        'all': ['chin', ],
    },
    2: {
        'head': ['DEF-chin.001'],
        'tail': ['DEF-chin', ],
        'all': ['chin.001', ],
    },
    3: {
        'head': [],
        'tail': ['DEF-chin.001'],
        'all': ['chin.002'],
    },
    # chin side
    4: {
        'head': ['DEF-chin.L'],
        'tail': ['DEF-jaw.L.001'],
        'all': ['chin.L'],
    },
    # lowerlip mid
    5: {
        'head': ['DEF-lip.B.L'],
        'tail': [],
        'all': ['lip.B'],
    },
    # lower lip side
    6: {
        'head': ['DEF-lip.B.L.001'],
        'tail': ['DEF-lip.B.L'],
        'all': ['lip.B.L.001'],
    },
    # lip corner
    7: {
        'head': ['DEF-cheek.B.L'],
        'tail': ['DEF-chin.L', 'DEF-lip.T.L.001', 'DEF-lip.B.L.001'],
        'all': ['lips.L'],
    },
    # upper lip mid
    8: {
        'head': ['DEF-lip.T.L'],
        'tail': [],
        'all': ['lip.T'],
    },
    # upper lip side
    9: {
        'head': ['DEF-lip.T.L.001'],
        'tail': ['DEF-lip.T.L'],
        'all': ['lip.T.L.001'],
    },
    # nose low
    10: {
        'head': [],
        'tail': ['DEF-nose.003'],
        'all': ['DEF-nose.004', 'nose.004', 'nose_master'],
    },
    # nose tip
    11: {
        'head': ['DEF-nose.002'],
        'tail': ['DEF-nose.L.001', 'DEF-nose.001'],
        'all': ['nose.002'],
    },
    # jaw mid
    12: {
        'head': ['DEF-jaw.L.001'],
        'tail': ['DEF-jaw.L'],
        'all': ['jaw.L.001'],
    },
    # nose wing
    13: {
        'head': ['DEF-nose.L.001'],
        'tail': ['DEF-nose.L'],
        'all': ['nose.L.001'],
    },
    # cheeck low
    14: {
        'head': ['DEF-cheek.B.L.001'],
        'tail': ['DEF-cheek.B.L'],
        'all': ['cheek.B.L.001'],
    },
    # cheeck high
    15: {
        'head': ['DEF-cheek.T.L.001'],
        'tail': ['DEF-cheek.T.L'],
        'all': ['cheek.T.L.001'],
    },
    # nose side
    16: {
        'head': ['DEF-nose.L'],
        'tail': ['DEF-cheek.T.L.001'],
        'all': ['nose.L'],
    },
    # EL_lower_1
    17: {
        'head': ['DEF-lid.B.L.001'],
        'tail': ['MCH-lid.B.L.001', 'DEF-lid.B.L'],
        'all': ['lid.B.L.001'],
    },
    # EL_corner
    18: {
        'head': ['DEF-lid.B.L'],
        'tail': ['DEF-lid.T.L.003', 'MCH-lid.B.L'],
        'all': ['lid.B.L'],
    },
    # nose side
    19: {
        'head': ['DEF-lid.B.L.002'],
        'tail': ['DEF-lid.B.L.001', 'MCH-lid.B.L.002'],
        'all': ['lid.B.L.002'],
    },
    # nose side
    20: {
        'head': [],
        'tail': ['DEF-brow.B.L.003'],
        'all': ['brow.B.L.004'],
    },
    21: {
        'head': ['DEF-nose'],
        'tail': ['DEF-brow.T.L.003'],
        'all': ['nose'],
    },
    22: {
        'head': ['DEF-jaw.L'],
        'tail': ['DEF-temple.L'],
        'all': ['jaw.L'],
    },
    23: {
        'head': ['DEF-lid.T.L.003'],
        'tail': ['DEF-lid.T.L.002', 'MCH-lid.T.L.003'],
        'all': ['lid.T.L.003'],
    },
    24: {
        'head': ['DEF-lid.B.L.003'],
        'tail': ['MCH-lid.B.L.003', 'DEF-lid.B.L.002'],
        'all': ['lid.B.L.003'],
    },
    25: {
        'head': ['DEF-brow.T.L', 'DEF-cheek.T.L'],
        'tail': ['DEF-cheek.B.L.001'],
        'all': ['brow.T.L'],
    },
    26: {
        'head': ['DEF-brow.B.L.003'],
        'tail': ['DEF-brow.B.L.002'],
        'all': ['brow.B.L.003'],
    },
    27: {
        'head': ['DEF-lid.T.L.002'],
        'tail': ['DEF-lid.T.L.001', 'MCH-lid.T.L.002'],
        'all': ['lid.T.L.002'],
    },
    28: {
        'head': ['DEF-lid.T.L'],
        'tail': ['DEF-lid.B.L.003', 'MCH-lid.T.L'],
        'all': ['lid.T.L'],
    },
    29: {
        'head': ['DEF-lid.T.L.001'],
        'tail': ['DEF-lid.T.L', 'MCH-lid.T.L.001'],
        'all': ['lid.T.L.001'],
    },
    30: {
        'head': ['DEF-brow.T.L.003'],
        'tail': ['DEF-brow.T.L.002', 'DEF-forehead.L'],
        'all': ['brow.T.L.003'],
    },
    31: {
        'head': ['DEF-brow.B.L.002'],
        'tail': ['DEF-brow.B.L.001'],
        'all': ['brow.B.L.002'],
    },
    32: {
        'head': ['DEF-brow.B.L'],
        'tail': [],
        'all': ['brow.B.L'],
    },
    33: {
        'head': ['DEF-brow.B.L.001'],
        'tail': ['DEF-brow.B.L'],
        'all': ['brow.B.L.001'],
    },
    34: {
        'head': ['DEF-brow.T.L.002'],
        'tail': ['DEF-brow.T.L.001', 'DEF-forehead.L.001'],
        'all': ['brow.T.L.002'],
    },
    35: {
        'head': ['DEF-brow.T.L.001'],
        'tail': ['DEF-brow.T.L', 'DEF-forehead.L.002'],
        'all': ['brow.T.L.001'],
    },
    36: {
        'head': [],
        'tail': ['DEF_forhead_04.L'],
        'all': [],
    },
    37: {
        'head': ['DEF_forhead_01.L', 'DEF-temple.L'],
        'tail': [],
        'all': [],
    },
    38: {
        'head': ['DEF-forehead.L', 'DEF_forhead_04.L'],
        'tail': ['DEF_forhead_03.L'],
        'all': [],
    },
    39: {
        'head': ['DEF_forhead_03.L', 'DEF-forehead.L.001'],
        'tail': ['DEF_forhead_02.L'],
        'all': [],
    },
    40: {
        'head': ['DEF_forhead_02.L', 'DEF-forehead.L.002'],
        'tail': ['DEF_forhead_01.L'],
        'all': [],
    },
    101: {
        'head': ['MCH-lid.T.L', 'MCH-lid.T.L.001', 'MCH-lid.T.L.002', 'MCH-lid.T.L.003', 'MCH-lid.B.L', 'MCH-lid.B.L.001', 'MCH-lid.B.L.002', 'MCH-lid.B.L.003', ],
        'tail': [],
        'all': ['master_eye.L', 'DEF_eye.L', 'MCH-eye.L'],
    },
    102: {
        'head': [],
        'tail': [],
        'all': ['jaw_master', 'MCH-mouth_lock', 'MCH-jaw_master', 'MCH-jaw_master.001', 'MCH-jaw_master.002', 'MCH-jaw_master.003', 'MCH-jaw_master.004'],
    },
    103: {
        'head': ['DEF-nose.001'],
        'tail': ['DEF-nose'],
        'all': ['nose.001'],
    },
    104: {
        'head': [],
        'tail': ['DEF-nose.004'],
        'all': ['nose.005'],
    },
    105: {
        'head': ['DEF-nose.003'],
        'tail': ['DEF-nose.002'],
        'all': ['nose.003'],
    },
    106: {
        'head': [],
        'tail': [],
        'all': ['DEF-teeth.T', 'teeth.T'],
    },
    107: {
        'head': [],
        'tail': [],
        'all': ['DEF-teeth.B', 'teeth.B'],
    },
    108: {
        'head': [],
        'tail': [],
        'all': ['tongue_master', 'tongue', 'DEF-tongue', 'tongue.003', 'MCH-tongue.001', 'tongue.001', 'DEF-tongue.001', 'MCH-tongue.002', 'tongue.002', 'DEF-tongue.002'],
    },
    109: {
        'head': [],
        'tail': [],
        'all': ['DEF-face', 'MCH-eyes_parent']
    },
    111: {
        'head': ['MCH-lid.T.R', 'MCH-lid.T.R.001', 'MCH-lid.T.R.002', 'MCH-lid.T.R.003', 'MCH-lid.B.R', 'MCH-lid.B.R.001', 'MCH-lid.B.R.002', 'MCH-lid.B.R.003', ],
        'tail': [],
        'all': ['master_eye.R', 'DEF_eye.R', 'MCH-eye.R'],
    },
    112: {
        'head': ['DEF-tongue'],
        'tail': ['tongue_master'],
        'all': ['tongue']
    },
    113: {
        'head': ['DEF-tongue.001', 'tongue_master'],
        'tail': ['DEF-tongue'],
        'all': ['tongue.001']
    },
    114: {
        'head': ['DEF-tongue.002', 'tongue_master'],
        'tail': ['DEF-tongue.001'],
        'all': ['tongue.002']
    },
    115: {
        'head': [],
        'tail': ['DEF-tongue.002'],
        'all': ['tongue.003']
    },
}