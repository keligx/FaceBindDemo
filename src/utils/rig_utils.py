import bpy
from ..core.constants import data_list
from mathutils import Matrix, Vector
import numpy as np
from ..utils import setup_utils

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
    rig_data = bpy.context.scene.facebinddemo_setup_data
    rig = rig_data.lh_armature
    if rig is not None and force_original is True:
        if not is_faceit_original_armature(rig):
            return None
    return rig

def is_faceit_original_armature(rig):
    '''Check if the Faceit Armature is created with Faceit.'''
    if rig.name == 'FaceitRig':
        return True
    if all([b.name in data_list.BONES for b in rig.data.bones]) or rig.get('faceit_rig_id'):
        return True
    return False


def get_faceit_armature_modifier(obj, force_original=True):
    '''Get the faceit armature modifier for a specific object.'''
    rig = get_faceit_armature(force_original=force_original)
    if rig is None:
        print("No FaceitRig found")
        return
    for mod in obj.modifiers:
        if mod.type == 'ARMATURE':
            if mod.object == rig:
                return mod

def set_bake_modifier_item(mod, obj_item=None, set_bake=False, is_faceit_mod=False, index=-1):
    '''Set properties of a modifier to a modifier item. Create a new modifier item if it doesn't exist.'''
    setup_data = bpy.context.scene.setup_data
    if obj_item is None:
        obj_item = setup_data.face_objects.get(mod.id_data.name)
        if obj_item is None:
            return None
    mod_item = obj_item.modifiers.get(mod.name)
    if mod_item is None:
        mod_item = obj_item.modifiers.add()
    mod_item.name = mod.name
    mod_item.type = mod.type
    mod_item.mod_icon = data_list.MOD_TYPE_ICON_DICT.get(mod.type, 'MODIFIER')
    mod_item.bake = set_bake
    if index != -1:
        mod_item.index = index
    mod_item.is_faceit_modifier = is_faceit_mod
    if mod.type in data_list.BAKE_MOD_TYPES:
        mod_item.can_bake = True
        if mod_item.bake:
            set_bake_modifier_properties(mod, mod_item)

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

def populate_bake_modifier_items(objects):
    setup_data = bpy.context.scene.setup_data
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
            set_bake_modifier_item(mod, obj_item=obj_item, set_bake=mod.name in bake_mods,
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


