import copy
from ..core.constants import data_list
from ..utils import bpy_utils
from ..utils import vertex_utils
from ..core.constants import base
from ..processors.setup_processor import GeometryIslands



def remove_item_from_collection_prop(collection, item):
    '''Removes an @item from a given @collection'''
    item = collection.find(item.name)
    if item != -1:
        collection.remove(item)

def get_modifiers_of_type(obj, type):
    mods = []
    for mod in obj.modifiers:
        if mod.type == type:
            mods.append(mod)
    return mods

def get_faceit_objects_list(context, clear_invalid_objects=True):
    setup_data = context.scene.facebinddemo_setup_data
    faceit_objects_property_collection = setup_data.face_objects
    faceit_objects = []

    for obj_item in faceit_objects_property_collection:
        # try to find by obj_pointer
        obj = bpy_utils.get_object(obj_item.name)
        if obj is not None:
            faceit_objects.append(obj)
            continue
        elif clear_invalid_objects:
            print('removing item {} from faceit objects, because it does not exist in scene.'.format(obj_item.name))
            remove_item_from_collection_prop(faceit_objects_property_collection, obj_item)

    return faceit_objects


def add_context_object(context, setup_data):
    # hidden object is not in selected objects, append context
    objects_add = list(filter(lambda x: x.type == 'MESH', context.selected_objects))
    if not objects_add:
        objects_add.append(context.object)

    for obj in objects_add:
        # check if that item exists
        obj_exists = any([obj.name == item.name for item in setup_data.face_objects])
        if not obj_exists:
            item = setup_data.face_objects.add()
            item.name = obj.name
            item.obj_pointer = obj
        setup_data.face_index = setup_data.face_objects.find(obj.name)

def ensure_table(bm):
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    
def get_nice_group_name(grp_name):
    '''splits the faceit group names by underscores and removes the faceit prefix'''
    split_name = grp_name.split('_')[1:]
    nice_name = ' '.join(split_name).title()
    return nice_name

def check_is_islands(bm, obj):
    geo_islands = GeometryIslands(bm.verts)
    islands = geo_islands.get_islands()
    if len(islands) > 1:
        bm.free()
        bpy_utils.set_scene_data(base.PROP_SETUP_DATA, base.ATTR_REPORT_INFO, "There is more than one surface in the selected object. \nPlease switch to edit mode and select only the main facial surface.")
        return {'CANCELLED'}
    else:
        # make sure all verts are selected.
        for v in bm.verts:
            v.select = True
        bm.select_flush(True)
        bm.to_mesh(obj.data)
        bm.free()

def get_clean_name(name):
    return name.replace("faceit_", "").replace("_", " ").title()

def assign_vertex_group(obj, grp_name, method, v_selected):
    vertex_utils.assign_vertex_grp(
            obj,
            [v.index for v in v_selected],
            grp_name,
            overwrite = method == 'REPLACE'
        )
    vgroup = obj.vertex_groups.get(grp_name)
    # Select the new assingment
    for v in obj.data.vertices:
        if vgroup.index in [vg.group for vg in v.groups]:
            v.select = True
        else:
            v.select = False

def save_hide_data(self, hidden_data: tuple):
    '''save the vert indices that have been hidden last.
        @hidden_data: tuple containing (obj_name, vert_indices (original))
    '''
    copy_assign_data = copy.deepcopy(self.active_assign_data)
    history_object = ('hidden_data', hidden_data, copy_assign_data)
    self.operator_history.append(history_object)

def save_active_assign_data(self):
    '''save the active assign data to the object data dict'''
    copy_assign_data = copy.deepcopy(self.active_assign_data)
    history_object = ('assign_data', copy_assign_data)
    self.operator_history.append(history_object)
    
def get_object_mode_from_context_mode(context_mode):
    '''Return the object mode for operator mode_set from the current context.mode'''
    return data_list.CONTEXT_TO_OBJECT_MODE.get(context_mode, base.MODE_OBJECT)

def get_list_faceit_groups():
    ''' Returns the faceit vertex group names. '''
    return data_list.VERTEX_GROUPS.copy()