import bpy
import inspect
from . import landmarks_utils
from mathutils import Quaternion
from ..core.constants import base


def register_classes_from_module(module):
    clsmembers = inspect.getmembers(module, inspect.isclass)
    for (name, cls) in clsmembers:
        if name.startswith("FACEBINDDEMO"):
            bpy.utils.register_class(cls)

def unregister_classes_from_module(module):
    clsmembers = inspect.getmembers(module, inspect.isclass)
    for (name, cls) in clsmembers:
        if name.startswith("FACEBINDDEMO"):
            bpy.utils.unregister_class(cls)


def get_object(name):
    
    if isinstance(name, str):
        obj = bpy.context.scene.objects.get(name)
        if obj:
            return obj
        else:
            pass
    return None

def get_object_from_all(name):
    
    if isinstance(name, str):
        obj = bpy.data.objects.get(name)
        if obj:
            return obj
        else:
            pass
    return None

def set_local_view():
    return bpy.ops.view3d.localview()

def load_object_from_blend(file_path):
    with bpy.data.libraries.load(file_path, link=False) as (data_from, data_to):
        data_to.objects = data_from.objects

def switch_mode(mode):
    bpy.ops.object.mode_set(mode=mode)

def register_timer(method):
    bpy.app.timers.register(method)

def get_scene_data(data_name):
    return getattr(bpy.context.scene, data_name)

def set_scene_data(data_name, attr_name, value):
    def set_data():
        data = get_scene_data(data_name)
        setattr(data, attr_name, value)
    register_timer(set_data)
    ui_refresh_all()

def set_data(data, attr_name, value):
    def set_data():
        setattr(data, attr_name, value)
    register_timer(set_data)
    ui_refresh_all()

def ui_refresh_all():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()

def adjuest_view():
    switch_mode(mode='EDIT')
    bpy.ops.view3d.view_selected(use_all_regions=False)
    bpy.ops.view3d.view_axis(type='FRONT')
    switch_mode(mode='OBJECT')

def region_quadview():
    return bpy.ops.screen.region_quadview()

def get_layer_collection(collection_name):
    master_collection = bpy.context.view_layer.layer_collection
    return find_collection_in_children(master_collection, collection_name)

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
    lh_collection = bpy.data.collections.get(collection_name)
    if create:
        lh_collection = create_colletion(collection_name)
    lh_layer_collection = get_layer_collection(collection_name)
    if lh_layer_collection is None:
        context.scene.collection.children.link(lh_collection)
        lh_layer_collection = get_layer_collection(collection_name)
    if force_access:
        lh_collection.hide_viewport = False
        lh_layer_collection.exclude = False
        lh_layer_collection.hide_viewport = False
    return lh_collection

def create_colletion(collection_name):
    return bpy.data.collections.new(name=collection_name)

def clear_object_selection():
    bpy.ops.object.select_all(action='DESELECT')

def smooth_weights(context, objects, rig):
    '''Smooth weights on all objects.'''
    bind_data = context.scene.facebinddemo_bind_data
    for obj in objects:
        clear_object_selection()
        rig.select_set(state=True)
        set_active_object(obj.name)
        use_mask = obj.data.use_paint_mask_vertex
        obj.data.use_paint_mask_vertex = False
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
        bpy.ops.object.vertex_group_smooth(group_select_mode='BONE_DEFORM',
                                            factor=bind_data.smooth_factor,
                                            repeat=bind_data.smooth_steps,
                                            expand=bind_data.smooth_expand,
                                            )
        obj.data.use_paint_mask_vertex = use_mask
        bpy.ops.object.mode_set()


def get_blender_version():
    return bpy.app.version

def get_layer_state(rig):
    blend_version = get_blender_version()
    if blend_version < (4, 0, 0):
        layer_state = rig.data.layers[:]
        # enable all armature layers; needed for armature operators to work properly
        for i in range(len(rig.data.layers)):
            rig.data.layers[i] = True
    else:
        layer_state = [c.is_visible for c in rig.data.collections]
        for c in rig.data.collections:
            c.is_visible = True
    return layer_state
def set_active_object(obj, select=True):
    '''
    select the object
    @object_name: String or id
    '''
    if isinstance(obj, str):
        obj = bpy.data.objects.get(obj)
    if obj:
        if select:
            obj.select_set(state=True)
        bpy.context.view_layer.objects.active = obj
    else:
        print('WARNING! Object {} does not exist'.format(obj.name))
        return {'CANCELLED'}

def set_front_view(region_3d, lock_rotation=True, view_selected=True):

    if view_selected:
        view_center = landmarks_utils.get_object_center(bpy.context.object)
        region_3d.view_location = view_center

    region_3d.view_rotation = Quaternion((0.7071067690849304, 0.7071067690849304, -0.0, -0.0))
    region_3d.view_perspective = 'ORTHO'
    region_3d.lock_rotation = lock_rotation

def update_objects_collection(setup_data):
    bpy.context.view_layer.update()
    return setup_data.face_objects

def safe_get_faceit_objects(setup_data):
    faceit_objects = setup_data.face_objects

    if isinstance(faceit_objects, bpy.types._PropertyDeferred):
        print("Collection is not yet initialized.")
        return None 
    return faceit_objects

def set_active_object_by_name(obj):
    obj = bpy.data.objects.get(obj.name)
    if obj:
        if obj.hide_viewport:
            obj.hide_viewport = False
        obj.hide_render = False
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

def exit_nla_tweak_mode(context):
    '''exit the nla tweak mode (important for nla editor actions)'''
    current_type = bpy.context.area.type
    bpy.context.area.type = 'NLA_EDITOR'
    bpy.ops.nla.tweakmode_exit()
    bpy.context.area.type = current_type

def set_undo_push():
    return bpy.ops.ed.undo_push()