import bpy
import bmesh
from math import acos, pi
from ..core.constants import data_list
from ..utils import vertex_utils
from ..utils import landmarks_utils
from ..utils import bpy_utils
from ..utils import setup_utils
from ..utils import rig_utils
from ..utils import bind_utils
from ..processors.setup_processor import SelectionIslands

def is_inside_dot(target_pt_global, mesh_obj, tolerance=0.05):
    '''
    checks if a point is inside a surface, by the dot product method
    @target_pt_global : the point to check
    @mesh_obj : the mesh as surface
    @tolerance : a threshold as inside tolerance
    '''
    # Convert the point from global space to mesh local space
    target_pt_local = mesh_obj.matrix_world.inverted() @ target_pt_global

    # Find the nearest point on the mesh and the nearest face normal
    _, pt_closest, face_normal, _ = mesh_obj.closest_point_on_mesh(target_pt_local)

    # Get the target-closest pt vector
    target_closest_pt_vec = (pt_closest - target_pt_local).normalized()

    # Compute the dot product = |a||b|*cos(angle)
    dot_prod = target_closest_pt_vec.dot(face_normal)

    # Get the angle between the normal and the target-closest-pt vector (from the dot prod)
    angle = acos(min(max(dot_prod, -1), 1)) * 180 / pi

    # Allow for some rounding error
    inside = angle < 90 - tolerance

    return inside

def auto_weight_selection_to_bones(setup_data, auto_weight_objects, rig, bones, faceit_group="faceit_tongue"):
    '''Bind a vertex selection to specific bones'''
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set()
    bpy_utils.clear_object_selection()
    bpy_utils.set_active_object(rig.name)
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='DESELECT')
    any_selected = False
    for bone in bones:
        pbone = rig.pose.bones.get(bone)
        if pbone:
            pbone.bone.select = True
            any_selected = True
        else:
            continue
    bpy.ops.object.mode_set(mode='OBJECT')
    for obj in auto_weight_objects:
        bpy_utils.clear_object_selection()
        bpy_utils.set_active_object(rig.name)
        bpy_utils.set_active_object(obj.name)

        vs = vertex_utils.get_verts_in_vgroup(obj, faceit_group)
        if not vs:
            continue
        # Add Faceit_Armature mod
        bind_utils.add_faceit_armature_modifier(setup_data=setup_data, obj=obj, rig=rig)
        # remove all weights of other bones that got weighted in autoweighting process
        vertex_utils.remove_vgroups_from_verts(obj, vs=vs, filter_keep=faceit_group)
        if vertex_utils.vertex_group_sanity_check(obj):
            vertex_utils.remove_zero_weights_from_verts(obj)
            vertex_utils.remove_unused_vertex_groups_thresh(obj)

        # select all verts in tongue grp
        landmarks_utils.select_vertices(obj, [v.index for v in vs], deselect_others=True)

        # go weightpaint
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
        use_mask = obj.data.use_paint_mask_vertex
        obj.data.use_paint_mask_vertex = True
        bpy.ops.paint.weight_from_bones(type='AUTOMATIC')
        # smooth deform
        bpy.ops.object.vertex_group_smooth(
            group_select_mode='BONE_SELECT', factor=.5, repeat=2, expand=1.5)
        # reset settings
        obj.data.use_paint_mask_vertex = use_mask
        bpy.ops.object.mode_set(mode='OBJECT')
        
def select_vertices_outside_face_hull(obj, face_hull):
    '''Removes all weights outside of the facial area on the main face object.
    Parameters:
        @face_obj: the object
        @face_hull: the convex hull that encompasses the face
    '''
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    # deselect all verts:
    for f in bm.faces:
        f.select = False
    bm.select_flush(False)
    # select all verts that are inside the facial hull
    # false positives included due to rounding errors
    for v in bm.verts:
        pt = obj.matrix_world @ v.co
        if is_inside_dot(pt, face_hull):
            v.select = True
    if any([v.select for v in bm.verts]):
        # SelectionIslands finds and stores selected and non-selected islands
        selection_islands = SelectionIslands(bm.verts, selection_state=True)
        _selected_islands = selection_islands.get_islands()

        def _keep_only_biggest_island(islands, select_value):
            '''keep only the biggest island, all smaller should be added to/ removed from selection/non-selection
            @islands (list) : list of list of vertices
            @select_value (Bool) : add to selection or remove from selection
            '''
            if len(islands) > 1:
                biggest = max(islands, key=lambda x: len(x))
                for i in islands:
                    if len(i) < len(biggest):
                        for v in i:
                            v.select_set(select_value)
        # keep only the biggest island, the rest should be removed from selection
        _keep_only_biggest_island(_selected_islands, select_value=False)
        bm.select_flush(True)
        bm.select_flush(False)
        bm.to_mesh(obj.data)
        bm.free()
        # sometimes single verts get ignore by the selectionislands class, remove by shrink grow selection once
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_less()
        bpy.ops.mesh.select_more()
        bpy.ops.object.mode_set(mode='OBJECT')
        # assign all vertices outside of the hull to the DEF-face vertex group
        v_face_inv = [v.index for v in obj.data.vertices if not v.select]
    else:
        v_face_inv = [v.index for v in obj.data.vertices]
    vertex_utils.assign_vertex_grp(obj, v_face_inv, 'DEF-face', overwrite=True)
    landmarks_utils.select_vertices(obj)


def scale_bind_objects(factor, objects, reverse=False,):
    # set transform pivot to 3d cursor in case scaling has to be altered

    scale_factor = (factor,) * 3 if not reverse else (1 / factor,) * 3
    bpy_utils.clear_object_selection()
    # select all facial objects
    for obj in objects:
        bpy_utils.set_active_object(obj.name)
    bpy.ops.transform.resize(value=scale_factor, orient_type='GLOBAL')


def data_transfer_vertex_groups(obj_from, obj_to, apply=True, method=''):
    bpy_utils.clear_object_selection()
    bpy_utils.set_active_object(obj_to.name)

    # create, setup data transfer modifier
    data_mod = obj_to.modifiers.new(name='DataTransfer', type='DATA_TRANSFER')
    data_mod.object = obj_from
    data_mod.use_vert_data = True
    data_mod.data_types_verts = {'VGROUP_WEIGHTS'}

    if method:
        data_mod.vert_mapping = method
    else:
        if setup_utils.get_modifiers_of_type(obj_to, 'MIRROR'):
            data_mod.vert_mapping = 'NEAREST'
        else:
            data_mod.vert_mapping = 'TOPOLOGY'

    safe_count = 100
    while obj_to.modifiers.find(data_mod.name) != 0:
        bpy.ops.object.modifier_move_up(modifier=data_mod.name)
        if safe_count <= 0:
            break
        safe_count -= 1

    bpy.ops.object.datalayout_transfer(modifier=data_mod.name)

    if apply:
        blend_version = bpy_utils.get_blender_version()

        if blend_version >= (2, 90, 0):
            bpy.ops.object.modifier_apply(modifier=data_mod.name)
        else:
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier=data_mod.name)

        bpy_utils.switch_mode(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.object.vertex_group_clean(group_select_mode='ALL')
        bpy_utils.switch_mode(mode='OBJECT')


def split_by_faceit_groups(obj):
    '''Split the object into parts by assigned faceit vertex groups'''
    bpy_utils.clear_object_selection()
    bpy_utils.set_active_object(obj.name)
    for grp in obj.vertex_groups:
        if 'faceit_' in grp.name:
            vs = vertex_utils.get_verts_in_vgroup(obj, grp.name)
            if grp.name == 'faceit_main':
                # get the vertices that are only in the main group
                vs = [v for v in vs if len(v.groups) == 1]
            if not vs:
                obj.vertex_groups.remove(grp)
                continue
            if len(vs) == len(obj.data.vertices):
                # No need to split, the object is already separated
                break
            bpy_utils.switch_mode(mode='EDIT')
            landmarks_utils.select_vertices(obj, [v.index for v in vs], deselect_others=True)
            bpy.ops.mesh.separate(type='SELECTED')
            bpy.ops.object.mode_set()

    split_objects = [split_obj for split_obj in bpy.context.selected_objects if split_obj.type == 'MESH']
    for s_obj in split_objects:
        if vertex_utils.vertex_group_sanity_check(obj):
            vertex_utils.remove_zero_weights_from_verts(s_obj)
            vertex_utils.remove_unused_vertex_groups(s_obj)
    return split_objects


def split_object(obj):

    bpy_utils.clear_object_selection()
    bpy_utils.set_active_object(obj.name)

    bpy_utils.switch_mode(mode='EDIT')

    bpy.ops.mesh.separate(type='LOOSE')

    bpy.ops.object.mode_set()

    split_objects = [split_obj for split_obj in bpy.context.selected_objects if split_obj.type == 'MESH']
    for s_obj in split_objects:
        if vertex_utils.vertex_group_sanity_check(obj):
            vertex_utils.remove_zero_weights_from_verts(s_obj)
            vertex_utils.remove_unused_vertex_groups(s_obj)

    return split_objects


def create_facial_hull(context, lm_obj):
    '''Duplicates Landmarks mesh and creates a convex hull object from it. Encompasses the face.'''

    # duplicate facial setup - create facial hull as weight envelope
    bpy_utils.clear_object_selection()
    bpy_utils.set_active_object(lm_obj.name)
    bpy.ops.object.duplicate_move()
    face_hull = context.object
    # apply the mirror mod on hull
    for mod in face_hull.modifiers:
        if mod.name == 'Mirror':
            bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy_utils.switch_mode(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.convex_hull()
    # scale up slightly to include whole deform area
    context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
    bpy.ops.transform.resize(value=(2, 1.1, 1.2))

    bpy_utils.switch_mode(mode='OBJECT')

    return face_hull

def set_bake_modifier_item(setup_data, mod, obj_item=None, set_bake=False, is_faceit_mod=False, index=-1):
    '''Set properties of a modifier to a modifier item. Create a new modifier item if it doesn't exist.'''
    
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
            rig_utils.set_bake_modifier_properties(mod, mod_item)

def reorder_armature_in_modifier_stack(obj, arm_mod=None):
    '''Reorder the armature modifier in the modifier stack.'''
    # deformers = ['SURFACE_DEFORM']
    above_faceit_arma = ['MIRROR', 'SURFACE_DEFORM', 'LATTICE', 'SMOOTH', 'SURFACE_DEFORM',
                         'LAPLACIANSMOOTH', 'SIMPLE_DEFORM', 'BEVEL', 'BOOLEAN', 'BUILD', 'EDGE_SPLIT', 'NODES', 'SKIN',
                         'SOLIDIFY', 'TRIANGULATE', 'VOLUME_TO_MESH', 'WELD', 'SHRINKWRAP', 'WARP'
                         'CURVE', 'CAST']
    if not arm_mod:
        return
    new_idx = -1
    if arm_mod:
        above_mods = [i for i, mod in enumerate(obj.modifiers) if mod.type == 'ARMATURE' and mod != arm_mod]
        if not above_mods:
            above_mods = [i for i, m in enumerate(obj.modifiers) if m.type in above_faceit_arma]
        if above_mods:
            # Move it right below other armature mods
            new_idx = max(above_mods)
            if bpy.app.version < (3, 6, 0):
                override = {'object': obj, 'active_object': obj}
                bpy.ops.object.modifier_move_to_index(
                    override,
                    modifier=arm_mod.name,
                    index=new_idx + 1
                )
            else:
                index = obj.modifiers.find(arm_mod.name)
                obj.modifiers.move(index, new_idx + 1)

def smooth_selected_weights(setup_data, objects, rig, filter_bone_names=None, filter_vertex_group=None, factor=.5, steps=2, expand=1.5):
        '''Smooth weights for a specific selection. Choose from specific bones and/or vertices.'''
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set()
        group_select_mode = 'BONE_DEFORM'
        if filter_bone_names is not None:
            group_select_mode = 'BONE_SELECT'
            bpy_utils.clear_object_selection()
            bpy_utils.set_active_object(rig.name)
            bpy.ops.object.mode_set(mode='POSE')
            # enable deform bones layer
            bpy.ops.pose.select_all(action='DESELECT')
            any_selected = False
            for bone in filter_bone_names:
                pbone = rig.pose.bones.get(bone)
                if pbone:
                    pbone.bone.select = True
                    any_selected = True
                else:
                    continue
            if not any_selected:
                print("Can't find the specified bones.")
                return
        bpy.ops.object.mode_set(mode='OBJECT')
        for obj in objects:
            add_faceit_armature_modifier(setup_data, obj, rig)
            bpy_utils.clear_object_selection()
            bpy_utils.set_active_object(rig.name)
            bpy_utils.set_active_object(obj.name)

            if filter_vertex_group is not None:
                vs = vertex_utils.get_verts_in_vgroup(obj, filter_vertex_group)
                if not vs:
                    continue
                # select all verts in grp
                landmarks_utils.select_vertices(obj, [v.index for v in vs], deselect_others=True)
                obj.data.use_paint_mask_vertex = True
                use_mask = obj.data.use_paint_mask_vertex

            # smooth weights
            bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
            bpy.ops.object.vertex_group_smooth(
                group_select_mode=group_select_mode,
                factor=factor,
                repeat=steps,
                expand=expand
            )
            if filter_vertex_group is not None:
                obj.data.use_paint_mask_vertex = use_mask
            bpy.ops.object.mode_set(mode='OBJECT')

def add_faceit_armature_modifier(setup_data, obj, rig, force=False, force_original=True):
    '''add faceit_ARMATURE modifier. Set the rig object as target. reorder and setup. return mod'''
    if rig is None:
        rig = rig_utils.get_faceit_armature(force_original=force_original)
        if rig is None and not force:
            return
    if obj is None:
        return
    mod = rig_utils.get_faceit_armature_modifier(obj, force_original=force_original)
    if mod:
        obj.modifiers.remove(mod)
    mod = obj.modifiers.new(name='Faceit_Armature', type='ARMATURE')
    mod.object = rig
    reorder_armature_in_modifier_stack(obj, mod)
    mod.show_on_cage = True
    mod.show_in_editmode = True
    mod.show_viewport = True
    mod.show_render = True
    bind_utils.set_bake_modifier_item(setup_data, mod, set_bake=True, is_faceit_mod=True)
    return mod