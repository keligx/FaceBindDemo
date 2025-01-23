import math
import bmesh
import bpy
from bpy.props import BoolProperty, StringProperty
from bpy_extras.view3d_utils import (
    location_3d_to_region_2d,
    region_2d_to_origin_3d,
    region_2d_to_location_3d)
from mathutils import Matrix, Vector
from ..processors.landmarks_processor import LandmarksProcessor 
from ..utils import landmarks_utils
from ..utils import file_utils
from ..utils import bpy_utils
from bpy.types import Operator
from ..core.constants import base
from ..core.constants import data_list
from ..processors.pivots_processor import PivotManager


class FACEBINDDEMO_OT_set_landmarks(Operator):
    bl_idname = base.OT_ID_SET_LANDMARKS
    bl_label = base.OT_LABEL_SET_LANDMARKS
    bl_options = {"INTERNAL"}

    mouse_x: bpy.props.IntProperty()
    mouse_y: bpy.props.IntProperty()

    # initial cursor position to scale with mouse movement
    initial_mouse_scale = 0
    # to check if the scale has been initialized
    init_scale = False
    init_rotation = False
    init_loc = True
    # the initial dimensions used abort scaling operation
    initial_dimensions = (0, 0, 0)
    is_asymmetric_landmarks = False
    area_width = 0
    area_height = 0
    area_x = 0
    area_y = 0
    mouse_offset_x = 0
    mouse_offset_y = 0
    rotation_offset = 0
    v2d = Vector((0, 0))
    pivot_point_2D = Vector((0, 0))
    mouse3D = Vector((0, 0, 0))
    landmarks_scale = Vector((1, 1, 1))
    face_dimensions = Vector((1, 1, 1))
    

    def invoke(self, context, event):

        landmarks_data = context.scene.facebinddemo_landmarks_data
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        self.is_asymmetric_landmarks = landmarks_data.is_asymmetric
        area = context.area
        self.area_width = area.width
        self.area_height = area.height
        self.area_x = area.x
        self.area_y = area.y
        self.mouse_offset_x = 0
        self.mouse_offset_y = 0
        self.rotation_offset = 0
        self.execute(context)
        context.scene.tool_settings.use_snap = False
        context.window_manager.modal_handler_add(self)
        # self.set_face_pos(context, event)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        bpy.ops.facebinddemo.unlock_3d_view()
        setup_data = context.scene.facebinddemo_setup_data
        self.processor = LandmarksProcessor()
        
        if context.object:
            if not landmarks_utils.get_hide_obj(context.object):  # context.object.hide_viewport == False:
                bpy_utils.switch_mode(mode=base.MODE_OBJECT)
        # create the collection that holds faceit objects
        lh_collection = landmarks_utils.get_collection(context)
        landmarks_object = bpy_utils.get_object('facial_landmarks')
        if landmarks_object is not None:
            bpy.data.objects.remove(landmarks_object, do_unlink=True)
        bpy_utils.clear_object_selection()
        main_obj = landmarks_utils.get_main_faceit_object(context)
        if main_obj is None:
            self.report({'ERROR'}, 'Please assign the Main Vertex Group to the Face Mesh! (Setup Tab)')
            return {'CANCELLED'}
        
        landmarks_utils.set_hidden_state_object(main_obj, False, False)
        landmarks_utils.set_3d_view(context)
        
        # Frame the main vertex group.
        if not context.object:
            bpy_utils.set_active_object(main_obj)
        bpy_utils.set_active_object(main_obj.name)
        vs = landmarks_utils.get_verts_in_vgroup(main_obj, 'faceit_main')
        landmarks_utils.select_vertices(main_obj, [v.index for v in vs], deselect_others=True)
        
        bpy_utils.adjuest_view()

        # load the landmarks object
        filepath = file_utils.get_landmarks_file()
        with bpy.data.libraries.load(filepath) as (data_from, data_to):
            data_to.objects = data_from.objects
        # add the objects to the scene
        for obj in data_to.objects:
            print([obj.name for obj in data_to.objects])
            if obj.type == 'MESH':
                if self.is_asymmetric_landmarks:
                    if obj.startswith('asymmetric_facial_landmarks'):
                        lh_collection.objects.link(obj)
                        landmarks_object = bpy_utils.get_object('asymmetric_facial_landmarks')
                    else:
                        bpy.data.objects.remove(obj)
                else:
                    if obj.name.startswith('symmetric_facial_landmarks') :
                        lh_collection.objects.link(obj)
                        if obj.name in lh_collection.objects:
                            landmarks_object = bpy_utils.get_object_from_all(name=obj.name)
                        else:
                            self.report({'ERROR'}, 'No obj')
                    else:
                        bpy.data.objects.remove(obj)
        landmarks_object.name = 'facial_landmarks'
        if main_obj:
            landmarks_object.location.y = landmarks_utils.get_max_dim_in_direction(
                obj=main_obj, direction=Vector((0, -1, 0)), vertex_group_name="faceit_main")[1] - landmarks_object.dimensions[1]
        bpy_utils.clear_object_selection()
        # if landmarks_object.name not in bpy.context.scene.objects:
        #     lh_collection.objects.link(landmarks_object)
        landmarks_object.hide_set(False)
        landmarks_object.hide_viewport = False
        bpy_utils.set_active_object(landmarks_object.name)
        # initialize the state prop
        if landmarks_object:
            landmarks_object["state"] = 0
        # Set scale to main obj height. Main obj can be a body mesh at this point.
        disabled_mods = []
        for mod in main_obj.modifiers:
            if not mod.show_viewport:
                continue
            if mod.type in data_list.GENERATORS:
                disabled_mods.append(mod)
                mod.show_viewport = False
        context.evaluated_depsgraph_get().update()
        vgroup_name = "faceit_main"
        vgroup_positions = landmarks_utils.get_evaluated_vertex_group_positions(main_obj, vgroup_name, context)
        bounds = landmarks_utils.get_bounds_from_locations(vgroup_positions, 'z')
        for mod in disabled_mods:
            mod.show_viewport = True
        z_dim = bounds[0][2] - bounds[1][2]
        landmarks_object.dimensions[2] = z_dim / 2
        landmarks_object.scale = [landmarks_object.scale[2], ] * 3
        self.report({'INFO'}, "Align the Landmarks with your characters chin!")
        return {'FINISHED'}

    def set_face_pos(self, context, obj=None, region=None, rv3d=None, x=0, y=0, fine_mode=False):
        if not self.is_asymmetric_landmarks:
            x = 0
        v2d = (x, y)
        mouse_3d = region_2d_to_location_3d(region, rv3d, v2d, obj.location)
        if self.init_loc:
            new_location = mouse_3d - self.mouse3D
            if fine_mode:
                new_location /= 10
            obj.location.z += new_location.z
            if self.is_asymmetric_landmarks:
                obj.location.x += new_location.x
        else:
            # obj.location.x = 0
            self.init_loc = True
        self.mouse3D = mouse_3d
        context.area.header_text_set(f"Location: {obj.location.x:.3f}, {obj.location.z:.3f} (Hold Shift for fine mode)")

    def set_face_rotation(self, context, obj=None, x=0, y=0, fine_mode=False):
        '''Get rotation angle and update object rotation'''
        v2d = Vector((x, y)) - self.pivot_point_2D
        if not v2d.length:
            return {'PASS_THROUGH'}
        a = self.v2d.angle_signed(v2d)
        if self.init_rotation:
            if fine_mode:
                a = a / 10
            t = obj.matrix_world.translation.copy()
            mw = obj.matrix_world
            mw.translation = (0, 0, 0)
            rot_mat = Matrix.Rotation(a, 4, 'Y')
            mw = rot_mat @ mw
            mw.translation = t
            obj.matrix_world = mw
        else:
            self.init_rotation = True
        self.v2d = v2d
        context.area.header_text_set(f"Rotate:  {math.degrees(obj.rotation_euler.y):.2f}° (Hold Shift for fine mode)")

    def set_face_scale(self, context, obj, axis=2, region=None, rv3d=None, x=0, y=0, fine_mode=False):
        coord = x, y
        mouse_pos = region_2d_to_origin_3d(region, rv3d, coord)
        # initialize reference scale
        if not self.init_scale:
            # get the initial dimensions before altering - used to reset
            self.initial_dimensions = obj.dimensions[:]
            # set the initial relative mouse position for scaling
            self.initial_mouse_scale = mouse_pos[axis] - obj.dimensions[axis]
            self.init_scale = True
        # get the distance from initial mouse
        face_dim = mouse_pos[axis] - self.initial_mouse_scale
        # apply the dimension on x axis
        obj.dimensions[axis] = face_dim
        # modal operations depending on current state
        context.area.header_text_set(f"Dimensions: X: {obj.dimensions.x:.3f}, Z: {obj.dimensions.z:.3f}")

    def modal(self, context, event):
        mouse_x = event.mouse_x
        mouse_y = event.mouse_y
        mouse_region_x = event.mouse_region_x
        mouse_region_y = event.mouse_region_y
        region = context.region
        rv3d = context.region_data
        lm_obj = bpy_utils.get_object('facial_landmarks')
        if not lm_obj:
            self.report({'WARNING'}, 'No landmarks object, could not finish')
            return {'CANCELLED'}
        current_state = lm_obj["state"]
        # modal operations: move, scale height, scale width
        if event.type == 'MOUSEMOVE':
            if current_state == 0:
                self.set_face_pos(
                    context,
                    lm_obj,
                    region,
                    rv3d,
                    mouse_region_x + self.mouse_offset_x,
                    mouse_region_y + self.mouse_offset_y,
                    fine_mode=event.shift
                )
            elif current_state == 10:
                self.pivot_point_2D = location_3d_to_region_2d(region, rv3d, lm_obj.matrix_world.translation)
                self.set_face_rotation(
                    context,
                    obj=lm_obj,
                    x=mouse_region_x,
                    y=mouse_region_y,
                    fine_mode=event.shift,
                )
                # don't cursor warp when rotating
                return {'RUNNING_MODAL'}
            elif current_state == 1:
                self.set_face_scale(
                    context,
                    lm_obj,
                    axis=2,
                    region=region,
                    rv3d=rv3d,
                    x=mouse_region_x + self.mouse_offset_x,
                    y=mouse_region_y + self.mouse_offset_y,
                    fine_mode=event.shift,
                )
            elif current_state == 2:
                self.set_face_scale(
                    context,
                    lm_obj,
                    axis=0,
                    region=region,
                    rv3d=rv3d,
                    x=mouse_region_x + self.mouse_offset_x,
                    y=mouse_region_y + self.mouse_offset_y,
                    fine_mode=event.shift,
                )
            if mouse_x <= self.area_x:
                context.window.cursor_warp(self.area_x + self.area_width, mouse_y)
                self.mouse_offset_x -= self.area_width
            if mouse_x >= self.area_x + self.area_width:
                context.window.cursor_warp(self.area_x, mouse_y)
                self.mouse_offset_x += self.area_width
            if mouse_y <= self.area_y:
                context.window.cursor_warp(mouse_x, self.area_y + self.area_height)
                self.mouse_offset_y -= self.area_height
            if mouse_y >= self.area_y + self.area_height:
                context.window.cursor_warp(mouse_x, self.area_y)
                self.mouse_offset_y += self.area_height
            return {'RUNNING_MODAL'}

        # go into next state / finish
        elif event.type in {'LEFTMOUSE', 'RET'} and event.value == 'RELEASE':
            context.area.header_text_set(None)
            self.mouse_offset_x = 0
            self.mouse_offset_y = 0
            if current_state == 0:
                self.init_rotation = False
                if not self.init_scale:
                    landmarks_utils.set_scale_to_head_height(context, lm_obj=lm_obj)
                    bpy.ops.view3d.view_selected(use_all_regions=False)
                self.init_scale = False
                if not self.is_asymmetric_landmarks:
                    self.report({'INFO'}, "Match the face height")
                    lm_obj["state"] = 1
                else:
                    self.report({'INFO'}, "Align Rotation")
                    lm_obj["state"] = 10
                    self.pivot_point_2D = location_3d_to_region_2d(region, rv3d, lm_obj.matrix_world.translation)
                    self.v2d = Vector((event.mouse_region_x, event.mouse_region_y)) - self.pivot_point_2D
                    # lm_obj.rotation_euler = (0, 0, 0)
                return {'RUNNING_MODAL'}

            if current_state == 10:
                # Done with rotation
                self.report({'INFO'}, "Match the face height")
                lm_obj["state"] = 1
                self.init_scale = False
                return {'RUNNING_MODAL'}

            if current_state == 1:
                # Done with head height
                self.report({'INFO'}, "Match the face width!")
                self.init_scale = False
                lm_obj["state"] = 2
                return {'RUNNING_MODAL'}

            if current_state == 2:
                final_mat = lm_obj.matrix_world
                lm_obj.matrix_world = final_mat
                bpy_utils.set_active_object(lm_obj.name)
                lm_obj["state"] = 3
                context.tool_settings.mesh_select_mode = (True, False, False)
                bpy.ops.facebinddemo.lock_3d_view_front('INVOKE_DEFAULT', lock_value=True)
                bpy_utils.switch_mode(mode=base.MODE_EDIT)
                self.report({'INFO'}, "Fine-tune the landmarks in Edit mode until they match the face.")
                return {'FINISHED'}

        # go into previous state / cancel
        elif event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'RELEASE':
            context.area.header_text_set(None)
            self.mouse_offset_x = 0
            self.mouse_offset_y = 0
            if current_state == 2:
                self.init_scale = False
                self.report({'INFO'}, "Match the face height!")
                lm_obj["state"] = 1
            elif current_state == 1:
                # self.init_scale = False
                if self.is_asymmetric_landmarks:
                    # lm_obj.rotation_euler = (0, 0, 0)
                    self.pivot_point_2D = location_3d_to_region_2d(region, rv3d, lm_obj.matrix_world.translation)
                    self.v2d = Vector((event.mouse_region_x, event.mouse_region_y)) - self.pivot_point_2D
                    lm_obj["state"] = 10
                    self.report({'INFO'}, "Match the face rotation!")
                else:
                    self.report({'INFO'}, "Align the Landmarks with your characters chin!")
                    self.init_loc = False
                    lm_obj["state"] = 0
            elif current_state == 10:
                self.init_rotation = False
                self.report({'INFO'}, "Align the Landmarks with your characters chin!")
                self.init_loc = False
                lm_obj["state"] = 0
            elif current_state == 0:
                bpy.data.objects.remove(lm_obj)
                context.area.header_text_set(None)
                return {'CANCELLED'}

        if event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} or event.shift or event.ctrl or event.oskey:
            return {'PASS_THROUGH'}
        return {'RUNNING_MODAL'}

class FACEBINDDEMO_OT_edit_landmarks(bpy.types.Operator):
    '''Edit the landmarks'''
    bl_idname = base.OT_ID_EDIT_LANDMARKS
    bl_label = base.OT_LABEL_EDIT_LANMARKS
    bl_options = {'UNDO', 'INTERNAL'}

    @ classmethod
    def poll(cls, context):
        lm_obj = bpy.data.objects.get('facial_landmarks')
        if lm_obj:
            return context.object != lm_obj or context.mode != 'EDIT_MESH'

    def execute(self, context):
        lm = bpy.data.objects.get('facial_landmarks')
        landmarks_utils.set_hidden_state_object(lm, False, False)

        if context.mode != 'OBJECT':
            # if not context.object:
            #     context.view_layer.objects.active = lm
            bpy.ops.object.mode_set(mode='OBJECT')
        # else:
        PivotManager.start_drawing(context)
        # bpy.ops.faceit.draw_pivot_point('INVOKE_DEFAULT')
        bpy_utils.clear_object_selection()
        bpy_utils.set_active_object(lm.name)
        bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'}
    
class FACEBINDDEMO_OT_finish_edit_landmarks(bpy.types.Operator):
    '''Edit the landmarks'''
    bl_idname = base.OT_ID_FINISH_EDIT_LANDMARKS
    bl_label = base.OT_LABEL_FINISH_EDIT_LANDMARKS
    bl_options = {'UNDO', 'INTERNAL'}

    @ classmethod
    def poll(cls, context):
        if context.object:
            return context.object.name == 'facial_landmarks' and context.mode == 'EDIT_MESH'

    def execute(self, context):
        bpy.ops.faceit.unmask_main('EXEC_DEFAULT')
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}


class FACEBINDDEMO_OT_lock_3d_view_front(bpy.types.Operator):
    '''Lock the 3D view rotation and enable Front view'''
    bl_idname = base.OT_ID_LOCK_3D_VIEW_FRONT
    bl_label = base.OT_LABEL_LOCK_3D_VIEW_FRONT
    bl_options = {'UNDO', 'INTERNAL'}

    mouse_x: bpy.props.IntProperty()
    mouse_y: bpy.props.IntProperty()

    lock_value: BoolProperty(
        name='Lock',
        default=False,
        description='Lock the 3D view rotation',
        options={'SKIP_SAVE'}
    )
    set_edit_mode: BoolProperty(
        name="Edit",
        default=True,
        description="useful when the context area is not available (e.g. in handlers)",
        options={'SKIP_SAVE'}
    )

    find_area_by_mouse_position: BoolProperty(
        name="Edit",
        default=False,
        description="useful when the context area is not available (e.g. in handlers)",
        options={'SKIP_SAVE'}
    )

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        return self.execute(context)

    def execute(self, context):
        # scene = context.scene
        # TODO: Exit local view
        active_area = context.area
        region_3d = None
        original_context = False
        self.processor = LandmarksProcessor()

        if active_area:
            original_context = True
            region_3d = active_area.spaces.active.region_3d
        else:
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    if landmarks_utils.check_if_area_is_active(area, self.mouse_x, self.mouse_y):
                        active_area = area
                        for space in area.spaces:
                            if space.type == 'VIEW_3D':
                                region_3d = space.region_3d
                                break
        lm_obj = bpy_utils.get_object('facial_landmarks')
        if self.set_edit_mode:
            context.view_layer.objects.active = lm_obj
            bpy.ops.object.mode_set()
            bpy_utils.clear_object_selection()
            lm_obj.select_set(state=True)

        bpy_utils.set_front_view(region_3d)
        if original_context:
            if self.processor.check_is_quad_view(active_area):
                bpy.ops.screen.region_quadview()
        #     bpy.ops.view3d.view_selected(use_all_regions=False)
        if self.set_edit_mode:
            bpy_utils.switch_mode(mode=base.MODE_EDIT)
        return {'FINISHED'}
    
class FACEBINDDEMO_OT_unlock_3d_view(bpy.types.Operator):
    '''Lock the 3D view rotation and enable Front view'''
    bl_idname = base.OT_ID_UNLOCK_3D_VIEW
    bl_label = base.OT_LABEL_UNLOCK_3D_VIEW
    bl_options = {'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        self.processor = LandmarksProcessor()
        self.processor.unlock_3d_view(context)
        return {'FINISHED'}
    
class FACEBINDDEMO_OT_project_landmarks(bpy.types.Operator):
    '''Project the Landmarks onto the Main Object. (Make sure you assigned to Main Vertex Group correctly) '''
    bl_idname = base.OT_ID_PROJECT_LANDMARKS
    bl_label = base.OT_LABEL_PROJECT_LANDMARKS
    bl_options = {'REGISTER', 'UNDO_GROUPED'}
    mouse_x: bpy.props.IntProperty()
    mouse_y: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return context.scene.objects.get('facial_landmarks')

    def invoke(self, context, event):
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        return self.execute(context)

    def execute(self, context):
        landmarks_data = context.scene.facebinddemo_landmarks_data
        rig_data = context.scene.facebinddemo_rig_data
        bpy.ops.facebinddemo.unlock_3d_view()
        lm_obj = bpy_utils.get_object('facial_landmarks')

        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        bpy_utils.set_active_object(lm_obj.name)
        # get the main object
        surface_obj = landmarks_utils.get_main_faceit_object(context)
        # move in front of face
        if surface_obj:
            lm_obj.location.y = landmarks_utils.get_max_dim_in_direction(
                obj=surface_obj, direction=Vector((0, -1, 0)))[1] - lm_obj.dimensions[1]
        else:
            self.report({'ERROR'}, 'Please assign the main group to the face mesh (Setup tab)')
            return {'CANCELLED'}

        # get vert positions before and after projecting
        vert_pos_before = [Vector(round(x, 3) for x in v.co) for v in lm_obj.data.vertices]
        # projection modifier
        mod = lm_obj.modifiers.new(name='ShrinkWrap', type='SHRINKWRAP')
        mod.target = surface_obj
        mod.wrap_method = 'PROJECT'
        mod.use_project_y = True
        mod.use_positive_direction = True
        mod.show_on_cage = True
        mod.cull_face = 'BACK'
        # apply the modifier
        bpy.ops.object.modifier_apply(modifier=mod.name)

        bpy.ops.view3d.view_selected(use_all_regions=False)
        bpy.ops.view3d.view_axis(type='RIGHT')

        chin_vert = 0 if landmarks_data.is_asymmetric else 1
        obj_origin = lm_obj.matrix_world @ lm_obj.data.vertices[chin_vert].co
        context.scene.cursor.location = obj_origin

        landmarks_utils.reset_snap_settings(context)

        # get vert positions after projecting
        vert_pos_after = [Vector(round(x, 3) for x in v.co) for v in lm_obj.data.vertices]
        success = True
        for i in range(len(vert_pos_before)):
            if vert_pos_after[i] == vert_pos_before[i]:
                success = False
                break
        if not success:
            self.report(
                {'WARNING'},
                "It looks like not all vertices were projected correctly. Align them manually or repeat the projection.")
            # return {'CANCELLED'}
        else:
            self.report({'INFO'}, "Fine-tune the landmarks in Edit mode until they match the face.")

        bpy.ops.ed.undo_push()
        lm_obj["state"] = 4
        PivotManager.symmetric = not landmarks_data.is_asymmetric
        found_pos = PivotManager.initialize_pivots(context)
        if not found_pos:
            self.report(
                {'WARNING'},
                " Pivot points are only estimated. Please assign the eyeball vertex groups or use manual placement.")
        if rig_data.eye_pivot_placement == 'MANUAL':
            bpy.ops.facebinddemo.add_pivot_vertex('EXEC_DEFAULT', select_vertex=False)
        PivotManager.start_drawing(context, initialize=True)
        # bpy.ops.faceit.draw_pivot_point('INVOKE_DEFAULT')
        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}

class FACEBINDDEMO_OT_add_manual_pivot_vertex(bpy.types.Operator):
    '''Add a vertex for editing the manual pivot point'''
    bl_idname = base.OT_ID_ADD_PIVOT_VERTEX
    bl_label = base.OT_LABEL_ADD_PIVOT_VERTEX
    bl_options = {'UNDO'}

    pivot_position: bpy.props.FloatVectorProperty(
        name='Pivot Position',
        default=(0, 0, 0),
        subtype='XYZ',
        size=3,
        description='Position of the pivot point'
    )
    select_vertex: bpy.props.BoolProperty(
        name='Select Vertex',
        default=True,
        description='Select the vertex after adding it'
    )

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        '''Adds a vertex to the mesh for manually setting the pivot point (EDIT MODE ONLY)'''
        rig_data = context.scene.facebinddemo_rig_data
        PivotManager.change_mode(new_mode='MANUAL')
        lm_obj = context.scene.objects.get('facial_landmarks')
        if lm_obj is None:
            return {'CANCELLED'}
        if lm_obj.mode == 'EDIT':
            bm = bmesh.from_edit_mesh(lm_obj.data)
        else:
            bm = bmesh.new()
            bm.from_mesh(lm_obj.data)
        bm.verts.ensure_lookup_table()
        # check vertex count
        if self.select_vertex:
            for v in bm.verts:
                v.select = False
            bm.verts.ensure_lookup_table()
            bm.select_flush(True)
            bm.select_flush(False)

        pos = lm_obj.matrix_world.inverted() @ PivotManager.pivot_left
        pivots_already_created = len(bm.verts) > PivotManager.lm_default_vert_count
        pivot_verts = []
        if pivots_already_created:
            # the extra vertex already exists, just update its position
            v_piv = bm.verts[PivotManager.lm_pivot_vert_idx_left]
            v_piv.co = pos
        else:
            v_piv = bm.verts.new(pos)
        pivot_verts.append(v_piv)
        if not PivotManager.symmetric:
            pos = lm_obj.matrix_world.inverted() @ PivotManager.pivot_right
            if pivots_already_created:
                # the extra vertex already exists, just update its position
                v_piv = bm.verts[PivotManager.lm_pivot_vert_idx_right]
                v_piv.co = pos
            else:
                v_piv = bm.verts.new(pos)
            pivot_verts.append(v_piv)
        if self.select_vertex:
            for v_piv in pivot_verts:
                v_piv.select = True
                bm.select_history.add(v_piv)
        bm.verts.ensure_lookup_table()
        if lm_obj.mode == 'EDIT':
            bmesh.update_edit_mesh(lm_obj.data)
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='EDIT')
        else:
            bm.to_mesh(lm_obj.data)
            bm.free()
            if lm_obj == context.active_object:
                bpy.ops.object.mode_set(mode='EDIT')
        rig_data.eye_pivot_placement = 'MANUAL'
        PivotManager.start_drawing(context)
        rig_data.draw_pivot_locators = True
        return {'FINISHED'}


class FACEIT_OT_RemoveManualPivotVertex(bpy.types.Operator):
    '''Remove the vertex for editing the manual pivot point'''
    bl_idname = 'faceit.remove_manual_pivot_vertex'
    bl_label = 'Remove Manual Pivot Vertex'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        PivotManager.change_mode(new_mode='AUTO')
        lm_obj = context.scene.objects.get('facial_landmarks')
        if lm_obj is None:
            return {'CANCELLED'}
        if lm_obj.mode == 'EDIT':
            bm = bmesh.from_edit_mesh(lm_obj.data)
        else:
            bm = bmesh.new()
            bm.from_mesh(lm_obj.data)
        bm.verts.ensure_lookup_table()
        # check vertex count
        if len(bm.verts) > PivotManager.lm_default_vert_count:
            bm.verts.remove(bm.verts[-1])
            bm.verts.ensure_lookup_table()
            if not PivotManager.symmetric:
                bm.verts.remove(bm.verts[-1])
                bm.verts.ensure_lookup_table()
        if lm_obj.mode == 'EDIT':
            bmesh.update_edit_mesh(lm_obj.data)
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='EDIT')
        else:
            bm.to_mesh(lm_obj.data)
            bm.free()
        context.scene.faceit_eye_pivot_placement = 'AUTO'
        PivotManager.start_drawing(context)
        return {'FINISHED'}