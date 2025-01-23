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
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.view3d.view_selected(use_all_regions=False)
    bpy.ops.view3d.view_axis(type='FRONT')
    bpy.ops.object.mode_set(mode='OBJECT')

def region_quadview():
    return bpy.ops.screen.region_quadview()

def get_layer_collection(collection_name):
    master_collection = bpy.context.view_layer.layer_collection
    return landmarks_utils.find_collection_in_children(master_collection, collection_name)

def create_colletion(collection_name):
    return bpy.data.collections.new(name=collection_name)

def clear_object_selection():
    bpy.ops.object.select_all(action='DESELECT')

def get_blender_version():
    return bpy.app.version

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

def set_active_object_by_name(object_name):
    obj = bpy.context.scene.objects.get(object_name)
    if obj:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj