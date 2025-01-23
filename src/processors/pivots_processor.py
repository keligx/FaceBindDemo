import bpy
import bmesh
import blf
import gpu
from ..utils import vertex_utils
from ..utils import landmarks_utils
from ..utils import rig_utils
from mathutils import Matrix, Vector
from .landmarks_processor import LandmarksProcessor 

from gpu_extras.batch import batch_for_shader
from bpy_extras.view3d_utils import location_3d_to_region_2d




class PivotsClass:
    """Class to manage the eye pivot points in the viewport"""

    def __init__(self) -> None:
        self._handle = None
        self._handle_blf = None
        self.lm_obj = None
        self.pivot_left = Vector((0, 0, 0))
        self.pivot_right = Vector((0, 0, 0))
        self.manual_pivot_left = Vector((0, 0, 0))
        self.manual_pivot_right = Vector((0, 0, 0))
        self.area_3d = None
        self.is_drawing = False
        self.mode = 'AUTO'  # AUTO, MANUAL
        self.rv3d = None
        self.region = None
        self.selected_verts = []
        self.lm_pivot_vert_idx_left = 41
        self.lm_pivot_vert_idx_right = 73
        self.lm_default_vert_count = 41
        self._symmetric = True
        self.locator_scale = 0.2
        self.snap_toggled = False
        self.last_active_vertex: int = None
        self.jaw_pivot = Vector((0, 0, 0))
        self.draw_jaw_pivot = False

    @property
    def symmetric(self):
        return self._symmetric

    @symmetric.setter
    def symmetric(self, value):
        self._symmetric = value
        if value:
            self.lm_pivot_vert_idx_left = 41
            self.lm_default_vert_count = 41
        else:
            self.lm_pivot_vert_idx_left = 72
            self.lm_default_vert_count = 73

    def initialize_pivots(self, context):
        '''Initialize the pivot points when loading a new scene.'''
        self.load_saved_pivots(context)
        landmarks_data = context.scene.facebinddemo_landmarks_data
        rig_data = context.scene.facebinddemo_rig_data
        self.symmetric = not landmarks_data.is_asymmetric
        self.landmark_processor = LandmarksProcessor()
        if self.mode == 'AUTO':
            vgroups = vertex_utils.get_vertex_groups_from_objects()
            if self.pivot_left == Vector((0, 0, 0)):
                if not rig_data.eye_pivot_group_L:
                    if 'faceit_left_eyeball' in vgroups:
                        rig_data.eye_pivot_group_L = 'faceit_left_eyeball'
                    elif 'faceit_left_eyes_other' in vgroups:
                        rig_data.eye_pivot_group_L = 'faceit_left_eyes_other'
            if self.pivot_right == Vector((0, 0, 0)):
                if not rig_data.eye_pivot_group_R:
                    if 'faceit_right_eyeball' in vgroups:
                        rig_data.eye_pivot_group_R = 'faceit_right_eyeball'
                    elif 'faceit_right_eyes_other' in vgroups:
                        rig_data.eye_pivot_group_R = 'faceit_right_eyes_other'
        # initialize the pivot locator scale based on landmarks size
        lm_obj = context.scene.objects.get('facial_landmarks')
        if lm_obj:
            self.locator_scale = lm_obj.dimensions.x / 20
        if self.pivot_left == Vector((0, 0, 0)):
            
            pivot_left = rig_data.eye_pivot_point_L = self.landmark_processor.get_eye_pivot_from_landmarks(context=context)
            rig_data.eye_pivot_point_R = Vector((-pivot_left[0], pivot_left[1], pivot_left[2]))
            return False

        if rig_data.use_jaw_pivot:
            jaw_pivot_object = context.scene.objects.get('Jaw Pivot')
            if jaw_pivot_object:
                self.jaw_pivot = jaw_pivot_object.location
        return True

    def reset_pivots(self, context):
        rig_data = context.scene.facebinddemo_rig_data
        self.pivot_left = self.pivot_right = self.manual_pivot_left = self.manual_pivot_right = rig_data.eye_manual_pivot_point_L = rig_data.eye_manual_pivot_point_R = rig_data.eye_pivot_point_L = rig_data.eye_pivot_point_R = Vector()
        rig_data.eye_pivot_placement = 'AUTO'

    def save_pivots(self, context):
        '''Save the manual pivot points to the scene'''
        rig_data = context.scene.facebinddemo_rig_data
        rig_data.eye_manual_pivot_point_L = self.manual_pivot_left
        rig_data.eye_manual_pivot_point_R = self.manual_pivot_right

    def load_saved_pivots(self, context):
        '''Load the manual pivot points from the scene'''
        rig_data = context.scene.facebinddemo_rig_data
        self.mode = rig_data.eye_pivot_placement
        self.pivot_left = rig_data.eye_pivot_point_L
        self.pivot_right = rig_data.eye_pivot_point_R
        self.manual_pivot_left = rig_data.eye_manual_pivot_point_L
        self.manual_pivot_right = rig_data.eye_manual_pivot_point_R

    def _save_manual_pivot(self):
        self.manual_pivot_left = self.pivot_left
        self.manual_pivot_right = self.pivot_right

    def _restore_manual_pivot(self):
        if self.manual_pivot_left != Vector((0, 0, 0)):
            self.pivot_left = self.manual_pivot_left
        if self.manual_pivot_right != Vector((0, 0, 0)):
            self.pivot_right = self.manual_pivot_right

    def change_mode(self, new_mode):
        if new_mode == self.mode:
            return
        elif new_mode == 'AUTO' and self.mode == 'MANUAL':
            self._save_manual_pivot()
        elif new_mode == 'MANUAL' and self.mode == 'AUTO':
            self._restore_manual_pivot()
        self.mode = new_mode

    def __del__(self):
        self.remove_handle()
        self.remove_blf_hanlde()
        self.lm_obj = None

    def cancel(self):
        self.remove_handle()
        self.remove_blf_hanlde()
        self.lm_obj = None

    def get_3d_area(self, context):
        if context.area is not None:
            if context.area.type == 'VIEW_3D':
                return context.area
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                return area
        return None

    def get_region_data_from_area(self, area):
        region = None
        for r in area.regions:
            if r.type == 'WINDOW':
                region = r
        rv3d = area.spaces.active.region_3d
        return region, rv3d

    def is_valid(self, lm_obj):
        if lm_obj is None:
            return False
        elif lm_obj["state"] < 4:
            return False
        elif (lm_obj.hide_viewport or lm_obj.hide_get()):
            return False
        return True

    def get_pivot_points(self, context, lm_obj):
        rig_data = context.scene.facebinddemo_rig_data
        jaw_pivot_obj = context.scene.objects.get('Jaw Pivot')
        if jaw_pivot_obj:
            self.draw_jaw_pivot = True
            rig_data.jaw_pivot = self.jaw_pivot = jaw_pivot_obj.location
        else:
            self.draw_jaw_pivot = False
        if rig_data.eye_pivot_placement == 'MANUAL':
            if lm_obj.mode == 'EDIT':
                bm = bmesh.from_edit_mesh(lm_obj.data)
                bm.verts.ensure_lookup_table()
                self.pivot_left = lm_obj.matrix_world @ bm.verts[self.lm_pivot_vert_idx_left].co
                if self.symmetric:
                    self.pivot_right = Vector((-self.pivot_left[0], self.pivot_left[1], self.pivot_left[2]))
                else:
                    self.pivot_right = lm_obj.matrix_world @ bm.verts[self.lm_pivot_vert_idx_right].co
                self.selected_verts = self.get_selected_vert_indices(bm)
                if rig_data.pivot_vertex_auto_snap:
                    active_vert = self.get_active_vert_index(bm)
                    if active_vert != self.last_active_vertex:
                        self.last_active_vertex = active_vert
                        if active_vert == self.lm_pivot_vert_idx_left:
                            context.scene.tool_settings.use_snap = False
                            self.snap_toggled = True
                        elif self.snap_toggled:
                            context.scene.tool_settings.use_snap = True
                            self.snap_toggled = False
                bmesh.update_edit_mesh(lm_obj.data)
        else:
            self.pivot_left = rig_data.eye_pivot_point_L
            self.pivot_right = rig_data.eye_pivot_point_R

    def get_selected_vert_indices(self, bm: bmesh.types.BMesh):
        '''Returns a list of indices of selected vertices'''
        return [v.index for v in bm.verts if v.select]

    def get_active_vert_index(self, bm: bmesh.types.BMesh):
        '''Returns the index of the active vertex'''
        elem = bm.select_history.active
        if isinstance(elem, bmesh.types.BMVert):
            return elem.index

    def draw_line(self, shader, origin, direction, scale):
        '''Draw a line from a given origin in a given direction'''
        end = (origin + direction * scale)
        # Create the batch for the shader and return it
        return batch_for_shader(shader, 'LINES', {"pos": [origin, end]}, indices=((0, 1),))

    def draw_callback(self, context):
        rig_data = context.scene.facebinddemo_rig_data
        '''Draws a cross at the empty object's location'''
        if not rig_data.draw_pivot_locators:
            return
        self.lm_obj = context.scene.objects.get('facial_landmarks')
        if not self.is_valid(self.lm_obj):
            # self.cancel() can't remove draw_handles from here -> crashes blender
            return
        self.get_pivot_points(context, self.lm_obj)
        # Start the shader
        shader_name = 'UNIFORM_COLOR' if bpy.app.version[0] >= 4 else '3D_UNIFORM_COLOR'
        shader = gpu.shader.from_builtin(shader_name)
        shader.bind()
        shader.uniform_float("color", (0.0, 1, 0.0, 1.0))
        # Define directions
        directions = [
            Vector((1, 0, 0)),
            Vector((0, 1, 0)),
            Vector((0, 0, 1)),
            Vector((-1, 0, 0)),
            Vector((0, -1, 0)),
            Vector((0, 0, -1))]
        # scale of the lines
        batches = []
        pivots = [self.pivot_left, self.pivot_right]
        if self.draw_jaw_pivot:
            pivots.append(self.jaw_pivot)
        # Draw lines for the left and right pivot
        for pivot in pivots:
            mat = Matrix.Translation(pivot)
            origin = mat @ Vector((0, 0, 0))  # Convert coordinates in world space
            for direction in directions:
                batches.append(self.draw_line(shader, origin, direction, self.locator_scale))
        # Draw all the batches
        for batch in batches:
            batch.draw(shader)
        try:
            if self.mode == 'MANUAL':
                self._save_manual_pivot()
                self.save_pivots(context)
        except Exception as e:
            print(e)
            pass

    def draw_callback_blf(self, context, region, rv3d):
        ''' Write the name of each pivot in the view port.'''
        rig_data = context.scene.facebinddemo_rig_data
        if not rig_data.draw_pivot_locators:
            return
        lm_obj = self.lm_obj
        if not self.is_valid(lm_obj):
            # self.cancel()
            return
        font_id = 0
        font_offset = 10
        select_color = (1, 1, 1, 1)
        deselect_color = (0.0, 0.0, 0.0, 1)
        if bpy.app.version < (3, 6):
            blf.size(0, 20, 72)
        else:
            blf.size(font_id, 20)
        # if left_pivot_selected:
        x, y = location_3d_to_region_2d(region, rv3d, self.pivot_left)
        draw_selected = self.mode == 'AUTO' or context.mode == 'OBJECT'
        draw_left_selected = draw_selected or self.lm_pivot_vert_idx_left in self.selected_verts
        if draw_left_selected:
            blf.color(font_id, *select_color)
        else:
            blf.color(font_id, *deselect_color)
        blf.position(font_id, x + font_offset, y - font_offset * 2, 0)
        blf.draw(font_id, 'Left Pivot')
        if draw_selected or self.lm_pivot_vert_idx_right in self.selected_verts or self.symmetric and draw_left_selected:
            blf.color(font_id, *select_color)
        else:
            blf.color(font_id, *deselect_color)
        x, y = location_3d_to_region_2d(region, rv3d, self.pivot_right)
        blf.position(font_id, x + font_offset, y - font_offset * 2, 0)
        blf.draw(font_id, 'Right Pivot')
        if self.draw_jaw_pivot:
            blf.color(font_id, *select_color)
            x, y = location_3d_to_region_2d(region, rv3d, self.jaw_pivot)
            blf.position(font_id, x + font_offset, y - font_offset * 2, 0)
            blf.draw(font_id, 'Jaw Pivot')

    def remove_handle(self):
        if self._handle is not None:
            try:
                bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            except Exception as e:
                print('error removing handle')
                print(e)
            self._handle = None
        self.is_drawing = False

    def add_handle(self, context, initialize_pivots=True):
        if self._handle is None:
            if initialize_pivots:
                self.initialize_pivots(context)
            area_3d = self.get_3d_area(context)
            if area_3d is not None:
                self.area_3d = area_3d
                self._handle = bpy.types.SpaceView3D.draw_handler_add(
                    self.draw_callback, ((context,)), 'WINDOW', 'POST_VIEW')
                self.is_drawing = True
            else:
                self.is_drawing = False

    def remove_blf_hanlde(self):
        if self._handle_blf is not None:
            try:
                bpy.types.SpaceView3D.draw_handler_remove(self._handle_blf, 'WINDOW')
            except Exception as e:
                print('error removing handle')
                print(e)
            self._handle_blf = None

    def add_blf_handle(self, context):
        if self._handle_blf is None:
            if self.area_3d is None:
                self.area_3d = self.get_3d_area(context)
            if self.area_3d is not None:
                region, rv3d = self.get_region_data_from_area(self.area_3d)
                if region is not None and rv3d is not None:
                    self._handle_blf = bpy.types.SpaceView3D.draw_handler_add(
                        self.draw_callback_blf, ((context, region, rv3d)), 'WINDOW', 'POST_PIXEL')

    def get_eye_pivot_from_vertex_group(self, context, vgroup_name):
        '''Get the location of the eye pivot from the vertex group'''
        pos = Vector((0, 0, 0))
        objects = vertex_utils.get_objects_with_vertex_group(vgroup_name, get_all=True)
        # get the evaluated objects
        if context is None:
            context = bpy.context
        objects = [o.evaluated_get(context.evaluated_depsgraph_get()) for o in objects]
        # Get the global vertex positions of all verts in vgroup in all objects
        global_vs = []
        for obj in objects:
            obj_vs = vertex_utils.get_verts_in_vgroup(obj, vgroup_name)
            global_vs.extend([obj.matrix_world @ v.co for v in obj_vs])
        bounds = landmarks_utils.get_bounds_from_locations(global_vs, 'z')
        pos = rig_utils.get_median_pos(bounds)
        return pos

    def start_drawing(self, context, initialize=True):
        print('start drawing')
        if not self.is_drawing:
            self.add_handle(context, initialize_pivots=initialize)
            self.add_blf_handle(context)

    def stop_drawing(self):
        print('stop drawing')
        self.remove_handle()
        self.remove_blf_hanlde()

    def get_is_drawing(self):
        return self.is_drawing


if "PivotManager" not in globals():
    PivotManager: PivotsClass = PivotsClass()

def unregister():
    if "PivotManager" in globals():
        PivotManager.cancel()