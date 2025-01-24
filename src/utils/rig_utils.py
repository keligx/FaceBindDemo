from random import randint
import bpy
from ..core.constants import data_list
from mathutils import Matrix, Vector
import numpy as np
from ..utils import setup_utils
from ..utils import bind_utils
from ..utils import file_utils
from ..utils import bpy_utils
from ..utils import vertex_utils
from ..utils import landmarks_utils

def get_rig_type(rig):
    if rig is None:
        rig = get_faceit_armature()
        if rig is None:
            return None
    # if is_faceit_original_armature(rig):
    #     return 'FACEIT'
    if 'ORG-face' in rig.data.bones or 'DEF-face' in rig.data.bones:
        if any(b.name in ('lip_end.L.001', 'eye_common') for b in rig.data.bones):
            return 'RIGIFY_NEW'
        else:
            return 'RIGIFY'
    else:
        return 'ANY'
    
def get_faceit_armature(force_original=False):
    '''Get the faceit armature object.'''
    rig_data = bpy.context.scene.facebinddemo_rig_data
    rig = rig_data.lh_armature
    if rig is not None and force_original is True:
        if not is_faceit_original_armature(rig):
            return None
    return rig

def is_faceit_original_armature(rig):
    '''Check if the Faceit Armature is created with Faceit.'''
    if rig.name == 'Rig':
        return True
    if all([b.name in data_list.BONES for b in rig.data.bones]) or rig.get('faceit_rig_id'):
        return True
    return False


def get_faceit_armature_modifier(obj, force_original=True):
    '''Get the faceit armature modifier for a specific object.'''
    rig = get_faceit_armature(force_original=force_original)
    if rig is None:
        print("No Rig found")
        return
    for mod in obj.modifiers:
        if mod.type == 'ARMATURE':
            if mod.object == rig:
                return mod

def set_bake_modifier_properties(mod, mod_item):
    mod_item.show_viewport = mod.show_viewport
    mod_item.show_render = mod.show_render
    mod_item.show_in_editmode = mod.show_in_editmode
    mod_item.show_on_cage = mod.show_on_cage
    mod_item.show_expanded = mod.show_expanded
    mod_item.show_in_editmode = mod.show_in_editmode
    mod_item.show_in_editmode = mod.show_in_editmode
    if mod.type == 'SURFACE_DEFORM':
        mod_item.strength = mod.strength
        mod_item.target = mod.target
        mod_item.use_sparse_bind = mod.use_sparse_bind
        mod_item.vertex_group = mod.vertex_group
        mod_item.invert_vertex_group = mod.invert_vertex_group
        mod_item.is_bound = mod.is_bound
        mod_item.falloff = mod.falloff
    elif mod.type == 'SHRINKWRAP':
        mod_item.target = mod.target
        mod_item.offset = mod.offset
        mod_item.project_limit = mod.project_limit
        mod_item.subsurf_levels = mod.subsurf_levels
        mod_item.use_invert_cull = mod.use_invert_cull
        mod_item.use_negative_direction = mod.use_negative_direction
        mod_item.use_positive_direction = mod.use_positive_direction
        mod_item.use_project_x = mod.use_project_x
        mod_item.use_project_y = mod.use_project_y
        mod_item.use_project_z = mod.use_project_z
        mod_item.wrap_method = mod.wrap_method
        mod_item.wrap_mode = mod.wrap_mode
        mod_item.vertex_group = mod.vertex_group
        mod_item.invert_vertex_group = mod.invert_vertex_group
    elif mod.type == 'ARMATURE':
        mod_item.object = mod.object
        mod_item.use_bone_envelopes = mod.use_bone_envelopes
        mod_item.use_deform_preserve_volume = mod.use_deform_preserve_volume
        mod_item.use_multi_modifier = mod.use_multi_modifier
        mod_item.use_vertex_groups = mod.use_vertex_groups
        mod_item.vertex_group = mod.vertex_group
        mod_item.invert_vertex_group = mod.invert_vertex_group
    elif mod.type == 'CORRECTIVE_SMOOTH':
        mod_item.factor = mod.factor
        mod_item.is_bind = mod.is_bind
        mod_item.iterations = mod.iterations
        mod_item.smooth_type = mod.smooth_type
        mod_item.scale = mod.scale
        mod_item.smooth_type = mod.smooth_type
        mod_item.use_only_smooth = mod.use_only_smooth
        mod_item.use_pin_boundary = mod.use_pin_boundary
    elif mod.type == 'LATTICE':
        mod_item.object = mod.object
        mod_item.vertex_group = mod.vertex_group
        mod_item.invert_vertex_group = mod.invert_vertex_group
        mod_item.strength = mod.strength
    elif mod.type == 'SMOOTH':
        mod_item.factor = mod.factor
        mod_item.iterations = mod.iterations
        mod_item.use_x = mod.use_x
        mod_item.use_y = mod.use_y
        mod_item.use_z = mod.use_z
        mod_item.vertex_group = mod.vertex_group
        mod_item.invert_vertex_group = mod.invert_vertex_group
    elif mod.type == 'LAPLACIANSMOOTH':
        mod_item.lambda_factor = mod.lambda_factor
        mod_item.lambda_border = mod.lambda_border
        mod_item.iterations = mod.iterations
        mod_item.use_volume_preserve = mod.use_volume_preserve
        mod_item.use_normalized = mod.use_normalized
        mod_item.use_x = mod.use_x
        mod_item.use_y = mod.use_y
        mod_item.use_z = mod.use_z
        mod_item.vertex_group = mod.vertex_group
        mod_item.invert_vertex_group = mod.invert_vertex_group
    if mod.type == 'MESH_DEFORM':
        mod_item.precision = mod.precision
        mod_item.object = mod.object
        mod_item.is_bound = mod.is_bound
        mod_item.use_dynamic_bind = mod.use_dynamic_bind
        mod_item.vertex_group = mod.vertex_group
        mod_item.invert_vertex_group = mod.invert_vertex_group

def populate_bake_modifier_items(setup_data, objects):
    
    for obj in objects:
        obj_item = setup_data.face_objects.get(obj.name)
        if obj_item is None:
            continue
        bake_mods = []
        faceit_mods = []
        if not obj_item.modifiers:
            arma_mod = get_faceit_armature_modifier(obj, force_original=False)
            if arma_mod:
                bake_mods = faceit_mods = [arma_mod.name, ]
        else:
            bake_mods = [mod_item.name for mod_item in obj_item.modifiers if mod_item.bake]
            faceit_mods = [mod_item.name for mod_item in obj_item.modifiers if mod_item.is_faceit_modifier]
        obj_item.modifiers.clear()
        for i, mod in enumerate(obj.modifiers):
            bind_utils.set_bake_modifier_item(setup_data, mod, obj_item=obj_item, set_bake=mod.name in bake_mods,
                                   is_faceit_mod=mod.name in faceit_mods, index=i)

def get_median_pos(locations):
    return Vector(np.mean(locations, axis=0).tolist())

def rig_counter(context, rig_data, setup_data):
    body_rig_counter = {}
    # if not scene.faceit_body_armature:
    if rig_data.lh_body_armature is None:
        for obj in setup_utils.get_faceit_objects_list(context):
            mods = setup_utils.get_modifiers_of_type(obj, 'ARMATURE')
            for mod in mods:
                if mod.object is None:
                    continue
                if mod.object not in body_rig_counter:
                    body_rig_counter[mod.object] = 1
                else:
                    body_rig_counter[mod.object] += 1
            # set active index to new item
        if body_rig_counter:
            setup_data.armature = max(body_rig_counter, key=body_rig_counter.get)

def get_random_rig_id():
    range_start = 10**4
    range_end = (10**5) - 1
    return randint(range_start, range_end)

def load_rig_from_blend(rig_data):
    rig_filepath = file_utils.get_rig_file()
    faceit_collection = bpy_utils.get_collection()
    rig = get_faceit_armature(force_original=True)
    if rig:
        bpy.data.objects.remove(rig)
    # load the objects data in the rig file
    with bpy.data.libraries.load(rig_filepath) as (data_from, data_to):
        data_to.objects = data_from.objects
    # add only the armature
    for obj in data_to.objects:
        if obj.type == 'ARMATURE' and obj.name == 'Rig':
            faceit_collection.objects.link(obj)
            rig = obj
            break
    rig['faceit_rig_id'] = get_random_rig_id()

    bpy_utils.clear_object_selection()
    bpy_utils.set_active_object(rig.name)

    rig_data.lh_armature = rig
    if rig.animation_data:
        rig.animation_data.action = None
    return rig

def update_bone_collection():
    rig = get_faceit_armature()
    blender_version = bpy_utils.get_blender_version()
    if blender_version >= (4, 0, 0):
        face_coll = rig.data.collections["Layer 1"]
        face_coll.name = 'Face'
        rig.data.collections.get("Layer 2").name = 'Face (Primary)'
        rig.data.collections.get("Layer 3").name = 'Face (Secondary)'
        rig.data.collections["Layer 30"].name = 'DEF'
        rig.data.collections["Layer 31"].name = 'MCH'
        eye_master_L = rig.data.bones['master_eye.L']
        eye_master_R = rig.data.bones['master_eye.R']
        face_coll.assign(eye_master_L)
        face_coll.assign(eye_master_R)
        # remove old bone groups.
        if blender_version >= (4, 1, 0):
            coll_remove = []
            for coll in rig.data.collections_all:
                if coll.name in ['FK', 'IK', 'Special', 'Layer 32']:
                    coll_remove.append(coll)
            for coll in coll_remove:
                rig.data.collections.remove(coll)
        else:
            coll_remove = []
            for coll in rig.data.collections:
                if coll.name in ['FK', 'IK', 'Special', 'Layer 32']:
                    coll_remove.append(coll)
            for coll in coll_remove:
                rig.data.collections.remove(coll)

def adapt_rig_scale(rig, landmarks_data, rig_data):
    edit_bones = rig.data.edit_bones
    landmarks = landmarks_data.landmarks_object
    # adapt scale
    bpy_utils.switch_mode(mode='EDIT')
    # bones that fall too far off the rigs dimensions, hinder the scale adaption
    bones = ['eyes', 'eye.L', 'eye.R', 'DEF-face', 'MCH-eyes_parent']
    bone_translation = {}
    # temporarilly move bones to center of rig (only Y Axis/ dimensions[1] matters)
    for bone in bones:
        bone = edit_bones.get(bone)
        # store bone position
        bone_translation[bone.name] = (bone.head[1], bone.tail[1])
        # move to rig center
        bone.head[1] = bone.tail[1] = 0

    bpy_utils.switch_mode(mode='OBJECT')
    rig.location = landmarks.location
    rig.rotation_euler = landmarks.rotation_euler
    # get average dimensions
    dim_lm = landmarks.dimensions.copy()
    avg_dim_lm = sum(dim_lm) / len(dim_lm)

    dim_rig = rig.dimensions.copy()
    avg_dim_rig = sum(dim_rig) / len(dim_rig)

    scale_factor = avg_dim_lm / avg_dim_rig  # landmarks.dimensions[0] / rig.dimensions[0]
    rig.dimensions = dim_rig * scale_factor  # rig.dimensions.copy() * scale_factor
    bpy_utils.switch_mode(mode='EDIT')

    # restore the original positions
    for bone, pos in bone_translation.items():
        bone = edit_bones.get(bone)
        bone.head[1], bone.tail[1] = pos



def reset_stretch(rig_obj=None, bone=None):
    ''' reset stretch constraints '''
    # it is important to frame_set before resetting!
    bpy.context.scene.frame_set(1)

    def reset_bones_contraints(bone):
        for c in b.constraints:
            if c.name == 'Stretch To':
                c.rest_length = 0
    if bone:
        reset_bones_contraints(bone)
    elif rig_obj:
        for b in rig_obj.pose.bones:
            reset_bones_contraints(b)

def get_bone_delta(bone1, bone2) -> Vector:
    '''returns object space vector between two pose bones'''
    pos1 = bone1.matrix.translation
    pos2 = bone2.matrix.translation
    vec = pos1 - pos2
    return vec

def set_lid_follow_constraints(rig, side="L"):
    '''Set best follow location constraint influence on the lid bones.'''
    # All bottom lid bones
    bot_inner_lid = rig.pose.bones.get(f"lid.B.{side}.001")
    bot_mid_lid = rig.pose.bones.get(f"lid.B.{side}.002")
    bot_outer_lid = rig.pose.bones.get(f"lid.B.{side}.003")
    # All upper lid bones
    top_outer_lid = rig.pose.bones.get(f"lid.T.{side}.001")
    top_mid_lid = rig.pose.bones.get(f"lid.T.{side}.002")
    top_inner_lid = rig.pose.bones.get(f"lid.T.{side}.003")
    # Calculate a delta vector for each pair (top to bottom)
    mid_delta = get_bone_delta(top_mid_lid, bot_mid_lid)
    outer_lid_delta = get_bone_delta(top_outer_lid, bot_outer_lid)
    inner_lid_delta = get_bone_delta(top_inner_lid, bot_inner_lid)
    # Set the influence of the copy location constraint
    outer_lid_influence = outer_lid_delta.length / mid_delta.length
    constraint = top_outer_lid.constraints.get("Copy Location")
    if constraint:
        constraint.influence = outer_lid_influence
    constraint = bot_outer_lid.constraints.get("Copy Location")
    if constraint:
        constraint.influence = outer_lid_influence
    inner_lid_influence = inner_lid_delta.length / mid_delta.length
    constraint = top_inner_lid.constraints.get("Copy Location")
    if constraint:
        constraint.influence = inner_lid_influence
    constraint = bot_inner_lid.constraints.get("Copy Location")
    if constraint:
        constraint.influence = inner_lid_influence

def set_lid_follow_constraints_new_rigify(rig, side="L"):
    '''Set best follow location constraint influence on the lid bones.'''
    # All bottom lid bones
    # MCH-lid_offset.T.L.001
    # MCH-lid_offset.T.R.001
    bot_inner_lid = rig.pose.bones.get(f"MCH-lid_offset.B.{side}.001")
    bot_mid_lid = rig.pose.bones.get(f"MCH-lid_offset.B.{side}.002")
    bot_outer_lid = rig.pose.bones.get(f"MCH-lid_offset.B.{side}.003")
    # All upper lid bones
    top_outer_lid = rig.pose.bones.get(f"MCH-lid_offset.T.{side}.001")
    top_mid_lid = rig.pose.bones.get(f"MCH-lid_offset.T.{side}.002")
    top_inner_lid = rig.pose.bones.get(f"MCH-lid_offset.T.{side}.003")
    # Calculate a delta vector for each pair (top to bottom)
    mid_delta = get_bone_delta(top_mid_lid, bot_mid_lid)
    outer_lid_delta = get_bone_delta(top_outer_lid, bot_outer_lid)
    inner_lid_delta = get_bone_delta(top_inner_lid, bot_inner_lid)
    # Set the influence of the copy location constraint
    outer_lid_influence = outer_lid_delta.length / mid_delta.length
    constraint = top_outer_lid.constraints.get("Copy Location.002")
    if constraint:
        constraint.influence = outer_lid_influence
    constraint = bot_outer_lid.constraints.get("Copy Location.002")
    if constraint:
        constraint.influence = outer_lid_influence
    inner_lid_influence = inner_lid_delta.length / mid_delta.length
    constraint = top_inner_lid.constraints.get("Copy Location.002")
    if constraint:
        constraint.influence = inner_lid_influence
    constraint = bot_inner_lid.constraints.get("Copy Location.002")
    if constraint:
        constraint.influence = inner_lid_influence
        
def get_rig_from_blend_file(context, rig_data):
    rig_filepath = file_utils.get_rig_file()
    lh_collection = bpy_utils.get_collection(context, create=False)
    rig = get_faceit_armature(force_original=True)
    if rig:
        bpy.data.objects.remove(rig)
    # load the objects data in the rig file
    with bpy.data.libraries.load(rig_filepath) as (data_from, data_to):
        data_to.objects = data_from.objects
    # add only the armature
    for obj in data_to.objects:
        if obj.type == 'ARMATURE' and obj.name == 'Rig':
            lh_collection.objects.link(obj)
            # bpy.context.scene.collection.objects.link(obj) 
            if obj.name in lh_collection.objects:
                rig = bpy_utils.get_object(name=obj.name)
            break
    rig['faceit_rig_id'] = get_random_rig_id()

    bpy_utils.clear_object_selection()
    bpy_utils.set_active_object_by_name(rig)

    rig_data.lh_armature = rig
    if rig.animation_data:
        rig.animation_data.action = None
    return rig
