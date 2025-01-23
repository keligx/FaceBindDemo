from . import setup_utils
from . import bpy_utils
import bmesh
from operator import attrgetter

def get_hide_obj(obj):
    return (obj.hide_get() or obj.hide_viewport)


def find_collection_in_children(collection, name):
    ''' Recursively searches for a collection in the children of a collection'''
    if collection.name == name:
        return collection
    for child in collection.children:
        found = find_collection_in_children(child, name)
        if found:
            return found

def get_collection(context, force_access=True, create=True):
    '''Returns the faceit collection, if it does not exist, it creates it'''
    collection_name = 'LH_Collection'
    lh_collection = bpy_utils.create_colletion(collection_name)
    if lh_collection is None:
        if create:
            lh_collection = bpy_utils.create_colletion(collection_name)
        else:
            return None
    lh_layer_collection = bpy_utils.get_layer_collection(collection_name)
    if lh_layer_collection is None:
        context.scene.collection.children.link(lh_collection)
        lh_layer_collection = bpy_utils.get_layer_collection(collection_name)
    if force_access:
        lh_collection.hide_viewport = False
        lh_layer_collection.exclude = False
        lh_layer_collection.hide_viewport = False
    return lh_collection

def set_3d_view(context):
    area = context.area
    for space in area.spaces:
        if space.type == 'VIEW_3D':
            if space.local_view:
                bpy_utils.set_local_view()
            shading = space.shading
            shading.show_xray = False
            shading.show_xray_wireframe = False
    if check_is_quad_view(area):
        bpy_utils.region_quadview()
        
def set_hidden_state_object(object_to_hide, hide_viewport, hide_render):
    '''
    object_to_hide : object to hide
    hide_viewport : hide the object itself
    hide_render : hide the objectBase in renderlayer
    '''
    object_to_hide.hide_viewport = hide_viewport
    object_to_hide.hide_set(hide_render)

def check_is_quad_view(area):
    if area.spaces.active.region_quadviews is not None:
        return len(area.spaces.active.region_quadviews) != 0
    
def get_verts_in_vgroup(obj, grp_name):
    '''
    get all vertices in a vertex group
    Returns : list of vertices in group, else None
    @obj : object holds group and verts
    @grp_name : the name of the vertex group to get verts from
    '''
    vg_idx = obj.vertex_groups.find(grp_name)
    if vg_idx == -1:
        return
    # get all vertices in faceit group
    return [v for v in obj.data.vertices if vg_idx in [vg.group for vg in v.groups]]

def select_vertices(obj, vids=None, deselect_others=False) -> None:
    '''
    select vertices using the bmesh module
    @obj: the object that holds mesh data
    @vs : vert subset to select
    @deselect_others : deselect all other vertices
    '''
    if not vids:
        vids = [v.index for v in obj.data.vertices]
    if obj.mode == 'EDIT':
        bm = bmesh.from_edit_mesh(obj.data)
    else:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
    select_vertices_bmesh(vids, bm, deselect_others)
    if obj.mode == 'EDIT':
        bmesh.update_edit_mesh(obj.data)
    else:
        bm.to_mesh(obj.data)
        bm.free()

def select_vertices_bmesh(vids, bm, deselect_others=False):
    '''select vertices using the bmesh module'''
    for v in bm.verts:
        if v.index in vids:
            v.select = True
        elif deselect_others:
            v.select = False
    bm.select_flush(True)
    bm.select_flush(False)

def get_max_dim_in_direction(obj, direction, vertex_group_name=None):
    '''Get the furthest point of the mesh in a specified direction'''
    # world matrix
    mat = obj.matrix_world
    far_distance = 0
    far_point = direction

    if vertex_group_name:
        vs = get_verts_in_vgroup(obj, vertex_group_name)
    else:
        vs = obj.data.vertices

    for v in vs:
        point = mat @ v.co
        temp = direction.dot(point)
        # new high?
        if far_distance < temp:
            far_distance = temp
            far_point = point
    return far_point

def get_evaluated_vertex_group_positions(obj, vgroup_name, context) -> list:
    '''Returns a list world location vectors for each vertex in vertex group'''
    dg = context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(dg)
    vs = get_verts_in_vgroup(obj_eval, vgroup_name)
    # Remve group if it's empty
    if not vs:
        grp = obj_eval.vertex_groups.get(vgroup_name)
        if grp:
            obj_eval.vertex_groups.remove(grp)
        return None  # position
    mw = obj_eval.matrix_world
    return [mw @ v.co for v in vs]

def get_bounds_from_locations(locations, axis):
    '''Returns the bounds (max, min) for the specified locations
    @locations: list of vector3 elements,
    @axis: string in x, y, z
    '''
    if not locations:
        return
    axis = str(axis).lower()
    if axis not in ('x', 'y', 'z'):
        return
    bounds = [(max(locations, key=attrgetter(axis))), (min(locations, key=attrgetter(axis)))]
    return bounds

def check_if_area_is_active(area, x, y):
    if (x >= area.x and y >= area.y and x < area.width + area.x and y < area.height + area.y):
        return True
    
def get_object_center(obj):
    '''Find the center of a mesh object using the outside cage.'''
    vcos = [obj.matrix_world @ v.co for v in obj.data.vertices]

    def findCenter(vcos):
        return (max(vcos) + min(vcos)) / 2

    x, y, z = [[v[i] for v in vcos] for i in range(3)]
    center = [findCenter(axis) for axis in [x, y, z]]
    return center

def set_scale_to_head_height(context, lm_obj):
    '''Set scale after applying the chin position.'''
    main_obj = get_main_faceit_object(context)
    mw = main_obj.matrix_world
    vs = get_verts_in_vgroup(main_obj, "faceit_main")
    # get the global coordinates
    v_highest = max([(mw @ v.co).z for v in vs])
    # get the highest point in head mesh (temple)
    # v_highest = max([co.z for co in global_v_co])
    # get distance from chin to temple
    head_height = lm_obj.location[2] - v_highest
    # apply scale
    lm_obj.dimensions[2] = head_height * 0.7
    lm_obj.scale = [lm_obj.scale[2], ] * 3

def get_main_faceit_object(context, clear_invalid_objects=True):
        '''Returns the main object (head or face)'''
        faceit_objects = setup_utils.get_faceit_objects_list(context, clear_invalid_objects=clear_invalid_objects)
        for obj in faceit_objects:
            if "faceit_main" in obj.vertex_groups:
                return obj
        return None

def reset_snap_settings(context):
    scene = context.scene
    scene.tool_settings.use_snap = True
    scene.tool_settings.snap_elements = {'FACE'}
    scene.tool_settings.snap_target = 'CLOSEST'
    scene.tool_settings.use_snap_translate = True
    scene.tool_settings.use_snap_rotate = True
    scene.tool_settings.use_snap_scale = True
    blender_version = bpy_utils.get_blender_version()
    if blender_version[0] < 4:
        scene.tool_settings.use_snap_project = True
    else:
        scene.tool_settings.use_snap_time_absolute = True
        scene.tool_settings.snap_elements_individual = {'FACE_PROJECT'}
        scene.tool_settings.use_snap_backface_culling = True