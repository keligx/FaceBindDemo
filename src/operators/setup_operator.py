import copy
from bpy.types import Operator
import bpy
import numpy as np

from ..processors.pivots_processor import PivotsClass
from ..core.constants import base
from mathutils import kdtree
from ..utils import bpy_utils
from ..utils import setup_utils
from ..utils import vertex_utils
from ..utils import landmarks_utils
from ..core.constants import data_list
from ..processors.setup_processor import SetupProcessor
from ..processors.setup_processor import GeometryIslands
import bmesh
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d


class FACEBINDDEMO_OT_add_facial_object(Operator):
    bl_idname = base.OT_ID_ADD_FACIAL_OBJECT
    bl_label = base.OT_LABEL_ADD_FACIAL_OBJECT
    bl_options = {"INTERNAL"}

    facial_part: bpy.props.StringProperty(
        name='Part',
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    @classmethod
    def poll(cls, context):
        setup_data = context.scene.facebinddemo_setup_data
        if any([obj.type == 'MESH' for obj in context.selected_objects]):
            if len(context.selected_objects) > 1:
                return True
            obj = context.object
            if obj is not None:
                return (obj.name not in setup_data.face_objects)
    
    def execute(self, context):

        self.processor = SetupProcessor()
        self.processor.processor_add_object(context)

        bpy.ops.faceit.init_retargeting('EXEC_DEFAULT', quick_search=True)
        return {'FINISHED'}

class FACEBINDDEMO_OT_select_facial_part(bpy.types.Operator):
    '''Select the corresponding object from the active list item. Select multiple if Shift is pressed'''
    bl_idname = base.OT_ID_SELECT_FACIAL_PART
    bl_label = base.OT_LABEL_SELECT_FACIAL_PART
    bl_options = {'UNDO', 'INTERNAL'}

    object_name: bpy.props.StringProperty(
        name='Object Name',
        options={'HIDDEN', 'SKIP_SAVE'},
    )
    clear_current_selection: bpy.props.BoolProperty(
        name='Clear current selection',
        default=True,
        options={'SKIP_SAVE'},
    )

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        if event.shift or event.ctrl:
            self.clear_current_selection = False
        return self.execute(context)

    def execute(self, context):
        if self.clear_current_selection:
            bpy_utils.clear_object_selection()
        if self.object_name in context.scene.objects:
            bpy_utils.set_active_object_by_name(self.object_name)

        return {'FINISHED'}
    
class FACEBINDDEMO_OT_remove_facial_part(bpy.types.Operator):
    '''Remove the selected Character Geometry from Registration.'''
    bl_idname = base.OT_ID_REMOVE_FACIAL_PART
    bl_label = base.OT_LABEL_REMOVE_FACIAL_PART
    bl_options = {'UNDO', 'INTERNAL'}

    prompt: bpy.props.BoolProperty()
    clear_vertex_groups: bpy.props.BoolProperty(
        name='Clear Registered Parts',
        description='Clear the assigned vertex groups or keep them on the object',
        default=False,
        options={'SKIP_SAVE'},
    )
    remove_item: bpy.props.StringProperty(
        default='',
        options={'HIDDEN', 'SKIP_SAVE'}
    )

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj is not None:
            return True 

    def invoke(self, context, event):
        scene = context.scene
        if self.prompt:
            wm = context.window_manager
            return wm.invoke_props_dialog(self)
        else:
            return self.execute(context)

    def execute(self, context):
        self.processor = SetupProcessor()
        setup_data = context.scene.facebinddemo_setup_data

        def _remove_faceit_item(item):

            if self.clear_vertex_groups:
                obj = bpy_utils.get_object(item.name)
                try:
                    remove_groups = self.processor.remove_faceit_vertex_grps(obj)
                    self.report({'INFO'}, 'Cleared Faceit Vertex Groups {} on {}.'.format(remove_groups, obj.name))
                except AttributeError:
                    self.report({'INFO'}, 'No Vertex Groups found on Object.')

        item_index = setup_data.face_objects.find(item.name)
        setup_data.face_objects.remove(item_index)

        # remove from face objects
        if len(setup_data.face_objects) > 0:
            if self.remove_item:
                item = setup_data.face_objects[self.remove_item]
            else:
                item = setup_data.face_objects[setup_data.face_index]

            _remove_faceit_item(item)

        self.processor.update_object_counter(setup_data)
        return {'FINISHED'}

class FACEBINDDEMO_OT_move_face_object(bpy.types.Operator):
    '''Move the Face Object to new index'''
    bl_idname = base.OT_ID_MOVE_FACE_OBJECT
    bl_label = base.OT_LABEL_MOVE_FACE_OBJECT
    bl_options = {'UNDO', 'INTERNAL'}

    # the name of the facial part
    direction: bpy.props.EnumProperty(
        items=(
            ('UP', 'Up', ''),
            ('DOWN', 'Down', ''),
        ),
        options={'SKIP_SAVE'},
    )

    @classmethod
    def poll(cls, context):
        return context.scene.facebinddemo_setup_data.face_objects

    def move_index(self, context, flist, index):
        setup_data = context.scene.facebinddemo_setup_data
        list_length = len(flist) - 1
        new_index = index + (-1 if self.direction == 'UP' else 1)
        setup_data.face_index = max(0, min(new_index, list_length))

    def execute(self, context):
        setup_data = context.scene.facebinddemo_setup_data

        new_index = setup_data.face_index + (-1 if self.direction == 'UP' else 1)
        setup_data.face_objects.move(new_index, setup_data.face_index)
        self.move_index(context, setup_data.face_objects, setup_data.face_index)

        return {'FINISHED'}

class FACEBINDDEMO_OT_assign_main(bpy.types.Operator):
    ''' Register the respective vertices in Edit Mode or all vertices in Object Mode'''
    bl_idname = base.OT_ID_ASSIGN_MAIN
    bl_label = base.OT_LABEL_ASSIGN_MAIN
    bl_options = {'UNDO', 'INTERNAL'}

    def __init__(self):
        self.mode_save = 'OBJECT'

    @ classmethod
    def description(self, context, properties):
        _doc_string = "Works different in Edit / Object Mode.\n"
        if context.mode == 'EDIT_MESH':
            _doc_string += "Edit Mode: Assign selected vertices to this group.\n"
        else:
            _doc_string += "Object Mode: Assign all vertices of the selected object to this group.\n"
        _doc_string += "You can assign multiple groups to one object.\n\n"
        _doc_string += "The main group: (face, skull, body, skin)\n"
        _doc_string += "This group should consist of one connected surface. In other words, all vertices assigned to this group should be linked by edges. It does not matter if this encompasses the skull or even the whole body. \n"
        _doc_string += "Read more in the Faceit documentation."
        return _doc_string
        # return 'Assign the selected vertices to the %s group' % properties.vertex_group

    @ classmethod
    def poll(cls, context):
        setup_data = context.scene.facebinddemo_setup_data
        obj = context.active_object
        if obj is not None:
            if obj.type == 'MESH' and obj.name in setup_data.face_objects:
                return (context.mode in ('EDIT_MESH', 'OBJECT'))

    def invoke(self, context, event):
        self.processor = GeometryIslands
        if len(context.selected_objects) > 1:
            self.report(
                {'ERROR'},
                'It seems you have more than one object selected. Please select only the object containing the main facial geometry.')
            return {'CANCELLED'}
        obj = context.active_object
        self.mode_save = obj.mode
        if self.mode_save == 'OBJECT':
            bm = bmesh.new()
            bm.from_mesh(obj.data)
        else:
            bm = bmesh.from_edit_mesh(obj.data)
        
        setup_utils.ensure_table(bm)
        bm.select_flush(True)

        geo_islands = self.processor(bm.verts)

        if self.mode_save == 'OBJECT':
            setup_utils.check_is_islands(bm, obj)
        else:
            if not any(v.select for v in bm.verts):
                bmesh.update_edit_mesh(obj.data)
                self.report({'ERROR'}, 'No vertices selected.')
                return {'CANCELLED'}
            islands = list(geo_islands.get_selected_islands())
            if len(islands) > 1:
                bmesh.update_edit_mesh(obj.data)
                self.report(
                    {'ERROR'},
                    'It seems you have more than one surface selected. Please select only the main surface.')
                return {'CANCELLED'}
            all_verts_selected = all(v.select for v in islands[0])
            if not all_verts_selected:
                geo_islands.select_linked()
                bm.select_flush(True)
                bmesh.update_edit_mesh(obj.data)
                return context.window_manager.invoke_props_dialog(self)
        return self.execute(context)

    def draw(self, context):
        box = self.layout.box()
        box.label(text='Warning', icon='ERROR')
        box.label(text='The Main group should hold a connected surface.')
        box.label(text='The selection has been corrected.')
        box.label(text='Do you want to continue?')

    def execute(self, context):
        obj = context.active_object
        faceit_objects = setup_utils.get_faceit_objects_list(context)
        assigned_vertex_groups = vertex_utils.get_assigned_faceit_vertex_groups()
        if 'faceit_main' in assigned_vertex_groups:
            for _obj in faceit_objects:
                if _obj != obj:
                    vgroup_name = _obj.vertex_groups.get('faceit_main')
                    if vgroup_name:
                        _obj.vertex_groups.remove(vgroup_name)
                        self.report(
                            {'WARNING'},
                            'You attempted to register multiple objects as main face. Removed previous assignments of main vertex group.')
        bpy_utils.switch_mode(mode=self.mode_save)
        bpy.ops.facebinddemo.assign_group('INVOKE_DEFAULT', vertex_group='main')
        self.report({'INFO'}, f'The main surface has been assigned in object {obj.name}.')
        return {'FINISHED'}

class FACEBINDDEMO_OT_assign_group(bpy.types.Operator):
    ''' Register the respective vertices in Edit Mode or all vertices in Object Mode'''
    bl_idname = base.OT_ID_ASSIGN_GROUP
    bl_label = base.OT_LABEL_ASSIGN_GROUP
    bl_options = {'UNDO', 'INTERNAL'}

    # the name of the facial part
    vertex_group: bpy.props.StringProperty(
        name='vertex group',
        options={'SKIP_SAVE'},
    )
    def update_selection_based_on_assing_method(self, context):
        global initial_selection, vertices_already_in_group
        if not self.vgroup_already_assigned:
            return
        obj = context.active_object
        if obj.mode == 'OBJECT':
            return
        bm = bmesh.from_edit_mesh(obj.data)
        setup_utils.ensure_table(bm)
        bm.select_flush(True)
        if self.method == 'ADD':
            for v in bm.verts:
                if v.index in set(vertices_already_in_group + initial_selection):
                    v.select = True
                else:
                    v.select = False
        else:
            for v in bm.verts:
                if v.index in initial_selection:
                    v.select = True
                else:
                    v.select = False
        bm.select_flush(True)
        bm.select_flush(False)
        bmesh.update_edit_mesh(obj.data)
        bpy.ops.ed.undo_push(message='Faceit: Selection changed')


    method: bpy.props.EnumProperty(
        items=(
            ('REPLACE', 'Replace', 'Remove vertex group from selected object and assign new selection'),
            ('ADD', 'Add', 'Add selected verts to the existing vertex groups'),
        ),
        default='REPLACE',
        options={'SKIP_SAVE'},
        update=update_selection_based_on_assing_method,
    )
    vgroup_already_assigned: bpy.props.BoolProperty(
        name='Vertex Group Already Assigned',
        default=False,
        options={'SKIP_SAVE'},
    )
    is_pivot_group: bpy.props.BoolProperty(
        name='Is Pivot Group',
        options={'SKIP_SAVE', 'HIDDEN'},
    )

    def __init__(self):
        global initial_selection, vertices_already_in_group
        # True when any of the faceit vertex groups is assigned to the vertex selection.
        self.faceit_group_in_selection = False
        # Groups that are already assigned to the selection.
        self.groups_in_selection = []
        self.mode_save = 'OBJECT'
        # The selected vertices (indices).
        initial_selection = []
        vertices_already_in_group = []

    @ classmethod
    def description(self, context, properties):
        _doc_string = "Works different in Edit / Object Mode.\n"
        if context.mode == 'EDIT_MESH':
            _doc_string += "Edit Mode: Assign selected vertices to this group.\n"
        else:
            _doc_string += "Object Mode: Assign all vertices of the selected object to this group.\n"
        _doc_string += "You can assign multiple groups to one object.\n\n"
        # _doc_string = "Quickly assign all vertices of a selected object to a group in Object Mode or assign a selection of vertices to a group in Edit Mode.\n You can assign multiple groups within the same object. "
        if properties.vertex_group == "main":
            _doc_string += "The main group: (face, skull, body, skin)\n"
            _doc_string += "This group should consist of one connected surface. In other words, all vertices assigned to this group should be linked by edges. It does not matter if this encompasses the skull or even the whole body. \n"
        elif "eyeball" in properties.vertex_group:
            _doc_string += "Left/Right Eyeball: (spheres or half-spheres)"
        elif "eyes" in properties.vertex_group:
            _doc_string += "Left/Right Eyes: All Deform Geometry(Eyeballs, Cornea, Pupils, Iris, Highlights, smaller eye parts, etc.)"
            _doc_string += "The assigned geometry will be weighted to the respective eye bone only.\n"
        elif "teeth" in properties.vertex_group:
            _doc_string += "Teeth: (Upper & Lower Teeth, Gum, Mouth Interior, etc.)\n"
            _doc_string += "The assigned geometry will be weighted to the respective teeth bone only.\n"
        elif "eyelashes" in properties.vertex_group:
            _doc_string += "Eyelashes: (Eyelashes, Eyeshells, Tearlines, etc.)\n"
            _doc_string += "The eyelashes group will be weighted to the lid bones only. You should not assign the eyelids themselves to this group\n"
        elif "tongue" in properties.vertex_group:
            _doc_string += "Tongue: (Tongue)"
            _doc_string += "The tongue group will be weighted to the tongue bones only.\n"
        elif "rigid" in properties.vertex_group:
            _doc_string += "Rigid: (All geometry that is not supposed to deform)"
        elif "facial_hair" in properties.vertex_group:
            _doc_string += "Facial Hair: (Beard, Moustache, Sideburns, etc.)"
            _doc_string += "This group is optional. Currently, geometry that is not assigned to any group will be treated as facial hair.\n"
        _doc_string += "Read more in the Faceit documentation."
        return _doc_string

    @ classmethod
    def poll(cls, context):
        obj = context.active_object
        setup_data = context.scene.facebinddemo_setup_data
        if obj is not None:
            if obj.select_get() is False:
                return False
            if obj.type == 'MESH' and obj.name in setup_data.face_objects:
                return (context.mode in ('EDIT_MESH', 'OBJECT'))

    def invoke(self, context, event):
        global initial_selection, vertices_already_in_group
        if len(context.selected_objects) > 1:
            self.report({'ERROR'}, 'It seems you have more than one object selected. Please select only one object.')
            return {'CANCELLED'}
        
        obj = context.active_object
        self.mode_save = obj.mode
        v_selected = vertex_utils.get_selected_vertex(obj)
        if not v_selected:
            self.report({'ERROR'}, 'Select vertices')
            bpy_utils.switch_mode(mode=self.mode_save)
            return {'CANCELLED'}
            
        initial_selection = [v.index for v in v_selected]
        faceit_groups = [grp for grp in data_list.VERTEX_GROUPS if grp != "faceit_main"]
        for vgroup_name in faceit_groups:
            vgroup = obj.vertex_groups.get(vgroup_name)
            if not vgroup:
                continue
            vid_in_vgroup = vertex_utils.get_vertices_in_group(obj,vertex_group=vgroup)
            if self.vertex_group in vgroup_name:
                if all((vid in initial_selection for vid in vid_in_vgroup)):
                    self.report(
                        {'INFO'},
                        f'The selected vertices are already assigned to the "{setup_utils.get_clean_name(vgroup_name)}" group.')
                vertices_already_in_group = vid_in_vgroup
                self.vgroup_already_assigned = True
            elif vid_in_vgroup:  # the vertex group is assigned.
                # Check if the faceit vertex group overlaps with the active selection
                if self.vertex_group in ("left_eyeball", "right_eyeball",):
                    continue
                if vgroup_name in ("left_eyeball", "right_eyeball",):
                    continue
                if any((vid in vid_in_vgroup for vid in initial_selection)):  # and vgroup_name != "faceit_main":
                    self.groups_in_selection.append(vgroup_name)

        if self.vgroup_already_assigned or self.groups_in_selection:
            bpy_utils.switch_mode(mode=self.mode_save)
            return context.window_manager.invoke_props_dialog(self)
        return self.execute(context)

    def draw(self, context):
        layout = self.layout
        if self.vgroup_already_assigned:
            box = layout.box()
            box.label(text="WARNING", icon='ERROR')
            box.label(text='"%s" is already assigned.' % setup_utils.get_clean_name(self.vertex_group))
            box.label(text='Do you want to overwrite the existing assignment?')
            box.prop(self, 'method', expand=True)
        if self.groups_in_selection:
            box = layout.box()
            row = box.row(align=True)
            row.label(text="WARNING", icon='ERROR')
            row = box.row(align=True)
            row.label(text="The following groups will be overwritten:")
            for grp_name in self.groups_in_selection:
                box.label(text=setup_utils.get_clean_name(grp_name))

    def execute(self, context):
        rig_data = context.scene.facebinddemo_rig_data
        obj = context.active_object
        if obj.mode != 'OBJECT':
            bpy.ops.object.mode_set()
        grp_name = 'faceit_' + self.vertex_group
        # UnLock all Faceit Groups!
        for grp in obj.vertex_groups:
            if 'faceit_' in grp.name:
                grp.lock_weight = False
        if self.mode_save == 'EDIT':
            v_selected = [v for v in obj.data.vertices if v.select]
        else:
            v_selected = obj.data.vertices
        # Remove all faceit vertex groups from the active vertex selection
        for vgroup_name in self.groups_in_selection:
            vgroup = obj.vertex_groups.get(vgroup_name)
            selected_verts_in_group = [v.index for v in v_selected if vgroup.index in [vg.group for vg in v.groups]]
            vgroup.remove(selected_verts_in_group)
            # Check if the group is empty now.
            if not any(vgroup.index in [g.group for g in v.groups] for v in obj.data.vertices):
                obj.vertex_groups.remove(vgroup)
        # assign the new group
        method = self.method
        setup_utils.assign_vertex_group(obj, grp_name, method, v_selected)

        self.report({'INFO'}, f'Assigned Vertex Group {grp_name} to the object {obj.name}')
        if obj.mode != self.mode_save:
            bpy_utils.switch_mode(mode=self.mode_save)
        if self.is_pivot_group:
            if self.vertex_group == 'right_eyes_other':
                rig_data.eye_pivot_group_R = grp_name
            if self.vertex_group == 'right_eyeball':
                rig_data.eye_pivot_group_R = grp_name
            if self.vertex_group == 'left_eyes_other':
                rig_data.eye_pivot_group_L = grp_name
            if self.vertex_group == 'left_eyeball':
                rig_data.eye_pivot_group_L = grp_name
        return {'FINISHED'}


class FACEBINDEDEMO_OT_vertex_group_picker(bpy.types.Operator):
    ''' Register the main surface. Draws an overlay to help you select the right vertices.'''
    bl_idname = base.OT_ID_VERTEX_GROUP_PICKER
    bl_label = base.OT_LABEL_VERTEX_GROUP_PICKER
    bl_options = {'UNDO', 'INTERNAL'}

    vertex_group_name: bpy.props.StringProperty(
        name='Vertex Group Name',
        default='main',
        description='Name of the vertex group to assign the selected vertices to.',
        options={'SKIP_SAVE'}
    )
    is_pivot_group: bpy.props.BoolProperty(
        name='Is Pivot Group',
        options={'SKIP_SAVE', 'HIDDEN'},
    )
    additive_group: bpy.props.BoolProperty(
        name='Additive Group',
        description="This group can be applied to the same vertex as other faceit groups. Other assigned groups won't be overridden",
    )
    pick_geometry: bpy.props.EnumProperty(
        name='Pick Geometry',
        items=(
            ('SURFACE', 'Surface', 'Assign based on connected vertices (Surfaces/Islands)'),
            ('OBJECT', 'Object', 'Assign the vertex group to the entire object'),
        ),
        default='SURFACE',
    )
    hide_assigned: bpy.props.BoolProperty(
        name='Hide Assigned',
        description='Hide the assigned vertices',
        default=False,
    )
    single_surface: bpy.props.BoolProperty(
        name='Single Surface',
        default=False,
        options={'SKIP_SAVE'},
    )

    def __init__(self):
        self._handler = None
        self._blf_handler = None
        self.dg = None
        self.obj = None
        self.bm = None
        self.mat = None
        self.vert_data = None
        self.assign_vert_data = None
        self.assign_indices = None
        # dict of type (obj: island_ids)
        self.active_assign_data: dict = None
        self.active_assign_shader_data: dict = None
        # assigned data for each faceit vertex group
        self.assigned_dict: dict = None
        self.assigned_islands: dict = None
        self.hit_assigned_group = ''
        self.operator_history = []  # Stores the history for undoing (assign data and hidden vertices)
        self.already_in_active_assign_data = False
        self.indices = None
        self.vertex_colors = None
        self.obj_data_dict: dict = {}
        self.island_ids = None
        self.geo_islands = None
        self.single_island = False
        self.cursor_pos = (0, 0)
        self.txt = "Assign Face."
        self.simplify_count = 0
        self.simplify_state = False
        self.valid_hit = False
        self.mods_disabled = {}
        self.grp_name: str = ""
        self.assigned_groups = set()

    @ classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def __end__(self):
        self.remove_handlers()

    def delete_vertices_outside_island(self, bm: bmesh.types.BMesh, island_ids: list):
        '''Deletes all vertices that are not in the island_ids'''
        verts_delete = [v for v in bm.verts if v.index not in island_ids]
        if verts_delete:
            bmesh.ops.delete(bm, geom=verts_delete, context='VERTS')
        setup_utils.ensure_table(bm)

    def get_color(self, vert_count: int, color: tuple = (0, 0, .9, .5)):
        '''Get the color for the shader.'''
        self.vertex_colors = [color for _ in range(vert_count)]

    def disable_modifiers(self, obj, mod_types=data_list.DEFORMERS):
        mods_disabled = []
        for mod in obj.modifiers:
            if mod.show_viewport and mod.type in mod_types:
                mod.show_viewport = False
                mods_disabled.append(mod)
        return mods_disabled

    def enable_modifiers(self, mods_disabled: list):
        for mod in mods_disabled:
            mod.show_viewport = True

    def get_the_hit_face_vertices(self, bm: bmesh.types.BMesh, face_index: int):
        face = bm.faces[face_index]
        v_face = face.verts[0]
        return v_face

    def get_the_hit_island(self, bm: bmesh.types.BMesh, face_index: int, geo_islands: dict):
        '''Returns the island ids of the surface with face_index'''
        v_face = self.get_the_hit_face_vertices(bm, face_index)
        for island_ids, island_bm in geo_islands.items():
            if v_face.index in island_ids:
                return island_ids, island_bm

    def get_the_hit_vertex_data(self, island_ids, island_bm):
        if not self.single_island and island_bm is None:
            island_bm = self.bm.copy()  # data_dict['bm'].copy()
            self.delete_vertices_outside_island(island_bm, island_ids)
            self.geo_islands[island_ids] = island_bm
        vertex_utils.get_vertex_data(island_bm)
        self.get_color(len(self.vert_data))

    def register_new_hit_object(self, obj_hit):
        data_dict = self.obj_data_dict[obj_hit.name]
        bm = data_dict['bm']
        self.bm = bm
        self.mat = obj_hit.matrix_world
        self.obj = obj_hit
        self.geo_islands = data_dict['geo_islands']
        self.single_island = data_dict['single_island']
        self.assigned_islands = data_dict['assigned_islands']

    def is_group_overwritable(self, grp_name):
        '''Check if the group will be overwritten by new assignment.'''
        return grp_name not in ('faceit_main', 'faceit_left_eyeball', 'faceit_right_eyeball')

    def execute_raycast(self, context, cursor_pos, ray_count=8):
        ''' Cast the ray to find valid surfaces below the cursor
            Check if the hit island is valid,
            in case it isn't cast n more rays from the hit location
            until a valid surface is found or range n is exceeded
            -------------
            The raycast function is a bit weird.
            It finds the face index of the evaluated mesh,
            but returns the original object.
        '''
        region = context.region
        rv3d = context.region_data
        view_vector = region_2d_to_vector_3d(region, rv3d, cursor_pos)  # * 100000
        ray_origin = region_2d_to_origin_3d(region, rv3d, cursor_pos)
        for i in range(ray_count):
            self.hit_assigned_group = ''
            _already_in_active_group = False
            result, location, _normal, face_index, obj_hit, _matrix = self.dg.scene_eval.ray_cast(
                self.dg, ray_origin, view_vector)
            if result:
                if obj_hit.name in self.obj_data_dict:
                    self.txt = obj_hit.name
                    hit_obj_data = self.obj_data_dict[obj_hit.name]
                    bm = hit_obj_data['bm']
                    assigned_islands = hit_obj_data['assigned_islands']
                    if assigned_islands:
                        # if self.pick_geometry == 'SURFACE':
                        v_face = self.get_the_hit_face_vertices(bm, face_index)
                        for assigned_ids, grp_name in assigned_islands.items():
                            if v_face.index in assigned_ids:
                                self.hit_assigned_group = grp_name
                                break
                        # else:
                        #     # pick the whole object
                        #     for grp_name in assigned_islands.values():
                        #         hit_any_assigned = False
                        #         if grp_name in obj_hit.vertex_groups:
                        #             hit_any_assigned = True
                        #             self.valid_hit = False
                        #             self.hit_assigned_group = grp_name
                        #             break

                    if self.active_assign_data:
                        # if self.pick_geometry == 'SURFACE':
                        if obj_hit.name in self.active_assign_data:
                            v_face = self.get_the_hit_face_vertices(bm, face_index)
                            for island_ids in self.get_active_assign_ids(obj_hit.name):
                                if v_face.index in island_ids:
                                    _already_in_active_group = True
                                    break
                            if _already_in_active_group:
                                ray_origin = location + view_vector * 0.000001
                                continue
                    self.valid_hit = True
                    break
                else:
                    self.valid_hit = False
                    self.hit_assigned_group = ''
                    ray_origin = location + view_vector * 0.00001
                    if i == 0:
                        self.txt = f"Object {obj_hit.name} not registered."
                    continue
            else:
                self.valid_hit = False
                self.hit_assigned_group = ''
                if i == 0:
                    if self.pick_geometry == 'SURFACE':
                        self.txt = "Select a Surface."
                    else:
                        self.txt = "Select an Object."
                break

        if self.valid_hit:
            # context.window_manager.popup_menu(draw, title="Info", icon='INFO')
            bpy.context.window.cursor_set("EYEDROPPER")
            if self.obj != obj_hit:
                self.register_new_hit_object(obj_hit)
            if self.pick_geometry == 'SURFACE':
                geo_islands = hit_obj_data['geo_islands']
                island_ids, island_bm = self.get_the_hit_island(bm, face_index, geo_islands)
                self.island_ids = island_ids
                self.get_the_hit_vertex_data(island_ids, island_bm)
            else:
                bm = hit_obj_data['bm']
                self.island_ids = [v.index for v in bm.verts]
                vertex_utils.get_vertex_data(bm)
                self.get_color(len(self.vert_data))
        else:
            bpy.context.window.cursor_set("DEFAULT")
    
    def modal(self, context, event):
        rig_data = context.scene.facebinddemo_rig_data
        setup_data = context.scene.facebinddemo_setup_data
        context.area.tag_redraw()
        self.dg.update()
        coord = event.mouse_region_x, event.mouse_region_y
        self.cursor_pos = coord
        if (event.oskey or event.ctrl) and event.type == 'Z' and event.value == 'PRESS':
            self.undo_step(context)
            return {'RUNNING_MODAL'}
        if event.type in {'MOUSEMOVE', 'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'TRACKPADPAN',
                          'TRACKPADZOOM', 'MOUSEROTATE', 'MOUSESMARTZOOM'} or event.shift or event.ctrl or event.oskey:
            self.execute_raycast(context, coord)
            return {'PASS_THROUGH'}
        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            # context.window_manager.popup_menu(draw, title="Info", icon='INFO')
            if not self.valid_hit:
                self.report({'WARNING'}, "You need to select a valid surface.")
                return {'RUNNING_MODAL'}
            if self.single_surface and self.active_assign_data:
                self.clear_active_assign_data(save_history=False)
                self.report({'WARNING'}, f"You can only assign one surface to the {self.vertex_group_name} group.")
            self.add_to_active_assign_data(self.obj, self.island_ids)
            setup_utils.save_active_assign_data()
            self.execute_raycast(context, coord)
            return {'RUNNING_MODAL'}
        elif event.type in {'RET', 'NUMPAD_ENTER'}:
            if not self.active_assign_data:
                self.report({'WARNING'}, "You need to make a valid selection to assign the vertex group. (ESC) to cancel.")
                return {'RUNNING_MODAL'}
            grp_name = 'faceit_' + self.vertex_group_name
            warning = None
            mode_save = None
            if context.mode != 'OBJECT':
                mode_save = True
            for obj_name, data_dict in self.obj_data_dict.items():
                obj = bpy_utils.get_object(obj_name)
                vgroup = obj.vertex_groups.get(grp_name)
                if vgroup:
                    obj.vertex_groups.remove(vgroup)
                    obj.data.update()
                    if context.object:
                        bpy.ops.object.mode_set()
                if obj_name in self.active_assign_data:
                    assigned_islands = data_dict['assigned_islands']
                    islands_to_assign = self.active_assign_data[obj_name]
                    for island_ids in islands_to_assign:
                        # Check if that island or parts of it are already assigned
                        overlapping_groups = {}
                        for assigned_island_ids, assigned_grp_name in assigned_islands.items():
                            # convert both to sets and get the intersection.
                            assigned_overlap = set(assigned_island_ids).intersection(set(island_ids))
                            if assigned_overlap:
                                if assigned_grp_name in overlapping_groups:
                                    overlapping_groups[assigned_grp_name].update(assigned_overlap)
                                else:
                                    overlapping_groups[assigned_grp_name] = assigned_overlap
                        if overlapping_groups:
                            grp_warning = False
                            if not self.additive_group:
                                for assigned_grp_name, assigned_overlap in overlapping_groups.items():
                                    if assigned_grp_name in ('faceit_main', 'faceit_left_eyeball',
                                                             'faceit_right_eyeball'):
                                        continue
                                    assigned_vgroup = obj.vertex_groups.get(assigned_grp_name)
                                    if assigned_vgroup:
                                        assigned_ids = self.get_original_indices_from_evaluated(
                                            obj,
                                            evaluated_indices=assigned_overlap
                                        )
                                        assigned_vgroup.remove(list(assigned_ids))
                                        if not any(assigned_vgroup.index in [g.group for g in v.groups]
                                                   for v in obj.data.vertices):
                                            obj.vertex_groups.remove(assigned_vgroup)
                                            warning = True
                                            if not grp_warning:
                                                self.report(
                                                    {'WARNING'},
                                                    f"Removed group {setup_utils.get_nice_group_name(assigned_grp_name)} from {obj_name} as it was overlapping with the new assignment.")
                                                grp_warning = True
                        assign_ids = self.get_original_indices_from_evaluated(
                            obj,
                            evaluated_indices=island_ids
                        )
                        # Assign the new group
                        vertex_utils.assign_vertex_grp(
                            obj, assign_ids, 'faceit_' + self.vertex_group_name, overwrite=False)
                if self.is_pivot_group:
                    if self.vertex_group_name == 'right_eyes_other':
                        if 'faceit_right_eyeball' not in obj.vertex_groups:
                            rig_data.eye_pivot_group_R = grp_name
                    if self.vertex_group_name == 'right_eyeball':
                        rig_data.eye_pivot_group_R = grp_name
                    if self.vertex_group_name == 'left_eyes_other':
                        if 'faceit_left_eyeball' not in obj.vertex_groups:
                            rig_data.eye_pivot_group_L = grp_name
                    if self.vertex_group_name == 'left_eyeball':
                        rig_data.eye_pivot_group_L = grp_name
                obj.data.update()
            if mode_save and context.object:
                bpy_utils.switch_mode(mode=self.mode_save)
            if not warning:
                self.report(
                    {'INFO'},
                    f"Successfully assigned the {setup_utils.get_nice_group_name(grp_name)} group to the object{'s' if len(self.active_assign_data) > 1 else ''} {', '.join((self.active_assign_data.keys()))}")
                # self.report({'INFO'}, "Group assigned.")
            self.obj.data.update()
            self.end(context)
            return {'FINISHED'}
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.end(context)
            self.report({'INFO'}, "Cancelled.")
            return {'CANCELLED'}
        elif event.type == 'S':
            self.report({'INFO'}, "Surface Mode activated.")
            self.pick_geometry = 'SURFACE'
            setup_data.picker_options.pick_geometry = self.pick_geometry
            self.execute_raycast(context, coord)
            return {'RUNNING_MODAL'}
        elif event.type == 'O':
            self.report({'INFO'}, "Object Mode activated.")
            self.pick_geometry = 'OBJECT'
            setup_data.picker_options.pick_geometry = self.pick_geometry
            self.execute_raycast(context, coord)
            return {'RUNNING_MODAL'}
        elif event.type == 'X':
            self.clear_active_assign_data()
            self.execute_raycast(context, coord)
        elif event.type == 'A':
            self.hide_assigned_data(context)
            self.execute_raycast(context, coord)
        elif event.type == 'H' and event.value == 'RELEASE':
            if self.valid_hit:
                self.report({'INFO'}, f"Hiding active surface in {self.obj.name}")
                self.hide_vertices(context, self.obj, evaluated_indices=self.island_ids)
                if not self.hide_assigned:
                    self.get_assigned_data()
                self.register_new_hit_object(self.obj)
                self.execute_raycast(context, coord)
        return {'RUNNING_MODAL'}

    def hide_vertices(self, context, obj, evaluated_indices, save_history=True):
        '''Creates a mask modifier and adds the indices to a vertex group hide_vg.
            the evaluated indices are part of the evaluated mesh, so we need to find the corresponding
            original indices in order to assign them to a group.
            As hiding vertices changes the evaluated mesh,
            we also need to reevaluate the geometry data,
            the assigned vertex groups and the active assign data.
        '''
        hide_vg = obj.vertex_groups.get("temp_hide_geo")
        if not hide_vg:
            hide_vg = obj.vertex_groups.new(name="temp_hide_geo")
        mode_save = None
        if context.mode != 'OBJECT':
            mode_save = True
            bpy.ops.object.mode_set()
        # Save the active assign data before hiding geo.
        active_assign_ids = self.get_active_assign_ids(obj.name)
        active_assign_cos = []
        obj_eval = obj.evaluated_get(self.dg)
        if active_assign_ids:
            active_assign_ids = set([i for ids in active_assign_ids for i in ids])
            # active assign data holds evaluated ids.
            # These need to bet matched to the new evaluated mesh.
            active_assign_cos = [obj_eval.matrix_world @
                                 v.co for v in obj_eval.data.vertices if v.index in active_assign_ids]
        hide_ids = self.get_original_indices_from_evaluated(obj, evaluated_indices=evaluated_indices)
        hide_vg.add(hide_ids, 1, 'ADD')
        obj.data.update()
        if mode_save:
           bpy_utils.switch_mode(mode=self.mode_save)
        mod = obj.modifiers.get("Temp Mask")
        if not mod:
            mod = obj.modifiers.new(type='MASK', name="Temp Mask")
            mod.vertex_group = hide_vg.name
            mod.show_viewport = True
            mod.invert_vertex_group = True
            mod.show_in_editmode = True
            mod.show_on_cage = True
        self.dg.update()
        self.get_geometry_data(obj)
        if active_assign_cos:
            new_assign_ids = set()
            bm = self.obj_data_dict[obj.name]['bm']
            size = len(bm.verts)
            kd = kdtree.KDTree(size)
            for i, v in enumerate(bm.verts):
                kd.insert(obj_eval.matrix_world @ v.co, i)
            kd.balance()
            for _co in active_assign_cos:
                co, index, dist = kd.find(_co)
                if dist is None:
                    print('dist is None')
                    continue
                if dist > 0.00001:
                    continue
                else:
                    new_assign_ids.add(index)
            if new_assign_ids:
                del self.active_assign_data[obj.name]
                self.add_to_active_assign_data(obj, new_assign_ids)
        if save_history:
            setup_utils.save_hide_data((obj.name, hide_ids))

    def unhide_vertices(self, context, obj, original_indices):
        '''Unhide the original vertices by removing them from the mask mod.
            This step requires the same evaluation.
        '''
        hide_vg = obj.vertex_groups.get("temp_hide_geo")
        if not hide_vg:
            hide_vg = obj.vertex_groups.new(name="temp_hide_geo")
        mode_save = None
        if context.mode != 'OBJECT':
            mode_save = True
            bpy.ops.object.mode_set()
        hide_vg.remove(list(original_indices))
        obj.data.update()
        if mode_save:
            bpy_utils.switch_mode(mode=self.mode_save)
        # if the vertex group is empty remove it and the modifier.
        if not any(hide_vg.index in [g.group for g in v.groups]
                   for v in obj.data.vertices):
            obj.vertex_groups.remove(hide_vg)
            mod = obj.modifiers.get("Temp Mask")
            if mod:
                obj.modifiers.remove(mod)
        self.dg.update()
        self.get_geometry_data(obj)
        self.get_assigned_data()

    def get_original_indices_from_evaluated(self, obj, evaluated_indices):
        '''Finds the corresponding vertices in the original object from the evaluated indices
            Returns: list of original indices
        '''
        if len(evaluated_indices) == len(obj.data.vertices):
            return evaluated_indices
        obj_eval = obj.evaluated_get(self.dg)
        lookup_table = self.obj_data_dict[obj.name]['vertex_lookup']
        evaluated_vertices = [obj_eval.data.vertices[i] for i in evaluated_indices]
        original_indices = []
        eval_coos = [tuple(obj_eval.matrix_world @ v.co) for v in evaluated_vertices]
        for i, co in lookup_table.items():
            if co in eval_coos:
                original_indices.append(i)
        return original_indices

    def remove_handlers(self):
        bpy.types.SpaceView3D.draw_handler_remove(self._handler, 'WINDOW')
        bpy.types.SpaceView3D.draw_handler_remove(self._blf_handler, 'WINDOW')

    def end(self, context):
        setup_data = context.scene.facebinddemo_setup_data
        bpy.context.window.cursor_set("DEFAULT")
        self.remove_handlers()
        for obj_name, data_dict in self.obj_data_dict.items():
            bm = data_dict['bm']
            if bm is not None:
                bm.free()
            obj = bpy_utils.get_object(obj_name)
            if obj is not None:
                hide_vg = obj.vertex_groups.get("temp_hide_geo")
                if hide_vg:
                    obj.vertex_groups.remove(hide_vg)
                mod = obj.modifiers.get("Temp Mask")
                if mod:
                    obj.modifiers.remove(mod)
                mods_disabled = self.mods_disabled.get(obj.name, [])
                for mod in mods_disabled:
                    mod.show_viewport = True
        context.scene.render.use_simplify = self.simplify_state
        context.scene.render.simplify_subdivision = self.simplify_count
        setup_data.picker_options.picking_group = ""

    def undo_step(self, context):
        '''undo the last active assign data'''
        if len(self.operator_history) > 1:
            history_object = self.operator_history.pop()
            if history_object[0] == 'hidden_data':
                obj_name, indices = history_object[1]
                obj = bpy_utils.get_object(obj_name)
                self.unhide_vertices(context, obj, original_indices=indices)
            for history_object in reversed(self.operator_history):
                # get the last valid assign data history step...
                if history_object[0] == 'assign_data':
                    self.active_assign_data = copy.deepcopy(history_object[1])
                    break
                else:
                    self.active_assign_data = copy.deepcopy(history_object[2])
                    break
        else:
            self.active_assign_data = copy.deepcopy(self.operator_history[0][1])
        self.load_active_assign_data_to_shader()

    def clear_active_assign_data(self, save_history=True):
        # clears the active assign data
        self.active_assign_data.clear()
        self.assign_vert_data = None
        self.assign_indices = None
        if save_history:
            setup_utils.save_active_assign_data()

    def add_to_active_assign_data(self, obj, ids):
        '''add the object and the ids to the potential assignment data'''
        if hasattr(ids, '__iter__'):
            ids = tuple(ids)
        self.active_assign_data.setdefault(obj.name, []).append(ids)
        self.load_active_assign_data_to_shader()

    def load_active_assign_data_to_shader(self):
        bm_to_assign = bmesh.new()
        for obj_name, ids_list in self.active_assign_data.items():
            data_dict = self.obj_data_dict[obj_name]
            obj = bpy_utils.get_object(obj_name)
            bm: bmesh.types.BMesh = data_dict['bm']
            bm_copy = bm.copy()
            # flatten the ids_list
            ids = [i for ids in ids_list for i in ids]
            vertex_utils.delete_vertices_outside(bm_copy, ids)
            bm_copy.transform(obj.matrix_world)
            bm_copy.verts.ensure_lookup_table()
            me = bpy.data.meshes.new('temp')
            bm_copy.to_mesh(me)
            bm_to_assign.from_mesh(me)
            bm_to_assign.verts.index_update()
            bpy.data.meshes.remove(me)
            bm_copy.free()
        self.assign_vert_data = np.array([v.co for v in bm_to_assign.verts], np.float32)
        self.assign_indices = np.array([(e.verts[0].index, e.verts[1].index)
                                        for e in bm_to_assign.edges], np.int32)
        bm_to_assign.free()

    def get_active_assign_ids(self, obj_name) -> list:
        '''returns a list of all the active assign island_ids for the given object'''
        if obj_name not in self.active_assign_data:
            return list()
        return [ids for ids in self.active_assign_data[obj_name]]

    def load_assigned_data_to_shader(self, group_filter: list = None):
        if group_filter is None:
            group_filter = list(self.assigned_groups)
            self.assigned_dict = {}  # reset the assigned dict
        if not isinstance(self.assigned_dict, dict):
            self.assigned_dict = {}
        assigned_groups_dict = {grp_name: bmesh.new() for grp_name in group_filter}
        for obj_name, data_dict in self.obj_data_dict.items():
            assigned_data = data_dict['assigned_islands']
            bm: bmesh.types.BMesh = data_dict['bm']
            obj = bpy_utils.get_object(obj_name)
            for vids, grp_name in assigned_data.items():
                bm_copy = None
                bm_copy = bm.copy()
                vertex_utils.delete_vertices_outside(bm_copy, vids)
                bm_copy.transform(obj.matrix_world)
                bm_copy.verts.ensure_lookup_table()
                me = bpy.data.meshes.new('temp')
                bm_copy.to_mesh(me)
                assigned_bm = assigned_groups_dict[grp_name]
                assigned_bm.from_mesh(me)
                assigned_bm.verts.index_update()
                bpy.data.meshes.remove(me)
                bm_copy.free()
        # self.assigned_dict = {}
        for grp_name, assigned_bm in assigned_groups_dict.items():
            if assigned_bm.verts:
                self.assigned_dict[grp_name] = {
                    'vert_data': np.array([v.co for v in assigned_bm.verts], np.float32),
                    'indices': np.array([(e.verts[0].index, e.verts[1].index)
                                        for e in assigned_bm.edges], np.int32),
                }

    def get_assigned_data(self, init_active_assign_data=False, group_filter: list = None):
        '''loads the assigned data for all registered objects and Faceit groups.'''
        if group_filter is None:
            group_filter = list(self.assigned_groups)
        for obj_name, data_dict in self.obj_data_dict.items():
            obj = bpy_utils.get_object(obj_name)
            obj = obj.evaluated_get(self.dg)
            assigned_islands = {}
            for grp_name in group_filter:
                vgroup = obj.original.vertex_groups.get(grp_name)
                if vgroup:
                    vids = [v.index for v in obj.data.vertices
                            if vgroup.index in [vg.group for vg in v.groups]]
                    if not vids:
                        continue
                    if init_active_assign_data and grp_name == 'faceit_' + self.vertex_group_name:
                        self.add_to_active_assign_data(obj, vids)
                    else:
                        assigned_islands[tuple(vids)] = grp_name
            data_dict['assigned_islands'] = assigned_islands

    def hide_assigned_data(self, context, group_filter: list = None):
        ''' Hides all assigned vertices on all objects. '''
        if group_filter is None:
            group_filter = list(self.assigned_groups)
        for obj_name, data_dict in self.obj_data_dict.items():
            assigned_islands = data_dict['assigned_islands']
            if not assigned_islands:
                continue
            obj = bpy_utils.get_object(obj_name)
            if not obj:
                continue
            vids_to_hide = set()
            for ids in assigned_islands.keys():
                vids_to_hide.update(ids)
            if not vids_to_hide:
                continue
            self.hide_vertices(context, obj, list(vids_to_hide), save_history=False)

    def get_geometry_data(self, obj):
        if not obj.is_evaluated:
            obj = obj.evaluated_get(self.dg)
        me = obj.data
        bm = bmesh.new()
        bm.from_mesh(me)
        setup_utils.ensure_table(bm)
        geo_islands = GeometryIslands(bm.verts)
        geo_island_ids = {}  # dict containing island ids and bmesh
        single_island = geo_islands.get_island_count() == 1
        for island in geo_islands.islands:
            # convert to tuple and make immutable (hashable).
            island_ids = tuple(set([v.index for v in island]))  # remove double entries and make immutable.
            geo_island_ids[island_ids] = bm if single_island else None
        self.obj_data_dict[obj.name].update({
            'bm': bm,
            'geo_islands': geo_island_ids,
            'single_island': single_island,
        })
        if self.obj:
            if obj.name == self.obj.name:
                self.register_new_hit_object(obj)

    def invoke(self, context, event):
        setup_data = context.scene.facebinddemo_setup_data
        self.active_assign_data = {}
        if context.area.type == 'VIEW_3D':
            self.simplify_state = context.scene.render.use_simplify
            self.simplify_count = context.scene.render.simplify_subdivision
            self.hide_assigned = setup_data.picker_options.hide_assigned
            self.pick_geometry = setup_data.picker_options.pick_geometry
            context.scene.render.use_simplify = True
            context.scene.render.simplify_subdivision = 0
            self.mode_save = setup_utils.get_object_mode_from_context_mode(context.mode)
            faceit_objects = setup_utils.get_faceit_objects_list()
            self.dg = context.evaluated_depsgraph_get()
            faceit_groups = setup_utils.get_list_faceit_groups()
            # Remove the eyeball groups, as they are only relevant for pivots.
            if 'eyeball' not in self.vertex_group_name:
                faceit_groups.remove('faceit_left_eyeball')
                faceit_groups.remove('faceit_right_eyeball')
            for obj in faceit_objects:
                if landmarks_utils.get_hide_obj(obj):
                    continue
                for grp_name in faceit_groups:
                    if grp_name in obj.vertex_groups:
                        self.assigned_groups.add(grp_name)
                for mod in obj.modifiers:
                    if not mod.show_viewport:
                        continue
                    if mod.type in data_list.GENERATORS:
                        mod.show_viewport = False
                        self.mods_disabled.setdefault(obj.name, []).append(mod)
                self.obj_data_dict[obj.name] = {}
                self.dg.update()
                obj_eval = obj.evaluated_get(self.dg)
                self.get_geometry_data(obj_eval)
                # Store original locations of vertices in an array as lookup table.
                self.obj_data_dict[obj.name]['vertex_lookup'] = {v.index: tuple(
                    obj_eval.matrix_world @ v.co) for v in obj_eval.data.vertices}
            self.get_assigned_data(init_active_assign_data=True)
            self.load_assigned_data_to_shader()
            if self.hide_assigned and not self.additive_group:
                self.hide_assigned_data(context)
            setup_utils.save_active_assign_data()
            pivots = PivotsClass
            args = (self,)
            self._handler = bpy.types.SpaceView3D.draw_handler_add(pivots.draw_callback, args, 'WINDOW', 'POST_VIEW')
            # For some reason gpu drawing doesn't work in POST_PIXEL and blf doesn't work in POST_VIEW.
            self._blf_handler = bpy.types.SpaceView3D.draw_handler_add(pivots.draw_callback_blf, args, 'WINDOW', 'POST_PIXEL')
            setup_data.picker_options.picking_group = self.vertex_group_name
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

class FACEBINDDEMO_OT_draw_assigned_groups_list(bpy.types.Operator):
    bl_label = base.OT_LABEL_DRAW_ASSIGNED_GROUPS_LIST
    bl_idname = base.OT_ID_DRAW_ASSIGNED_GROUPS_LIST

    obj_name: bpy.props.StringProperty()

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self)

    def draw(self, context):
        setup_data = context.scene.facebinddemo_setup_data
        layout = self.layout
        self.processor = SetupProcessor
        obj = bpy_utils.get_object(self.obj_name)
        if obj:
            self.processor.assign_object_groups(obj, setup_data, layout)

    def execute(self, context):
        return {'FINISHED'}
    
