from .base_panel import Base_Panel
from ..core.constants import base
import bpy
from ..utils import setup_utils
from ..utils import vertex_utils
from ..utils import bpy_utils
from ..utils import landmarks_utils

class FACEBINDDEMO_PT_setup(Base_Panel):
    bl_label = base.PT_LABEL_SETUP
    bl_parent_id = base.PT_ID_INTERFACE
    bl_idname = base.PT_ID_SETUP
    bl_options = set()
    
    @classmethod
    def poll(self, context):
        parent_poll = super().poll(context) if hasattr(super(), "poll") else True
        return parent_poll and context.scene.facebinddemo_interface_data.active_tab == base.PT_LABEL_SETUP
    
    
    def draw(self, context):
        layout = self.layout
        setup_data = context.scene.facebinddemo_setup_data

        col = layout.column(align=True)

        if not setup_data.face_objects:
            row = col.row(align=True)
            op = row.operator(base.OT_ID_ADD_FACIAL_OBJECT, text='Setup Object', icon='ADD')
            op.facial_part = 'main'
        else:
            col.separator(factor=1.0)
            row = col.row()
            row.template_list(base.UL_ID_OBJECT_LIST, '', setup_data, 'face_objects', setup_data, 'face_index')
            col_ul = row.column(align=True)
            # row.prop(scene, 'show_warnings', text='', icon='ERROR')
            row = col_ul.row(align=True)
            op = row.operator(base.OT_ID_ADD_FACIAL_OBJECT, text='', icon='ADD')
            row = col_ul.row(align=True)
            op = row.operator(base.OT_ID_REMOVE_FACIAL_PART, text='', icon='REMOVE')
            op.prompt = False
            col_ul.separator()
            row = col_ul.row()
            row.menu(base.MT_ID_REGISTER_OBJECTS, text='', icon='DOWNARROW_HLT')
            col_ul.separator()
            row = col_ul.row(align=True)
            op = row.operator(base.OT_ID_MOVE_FACE_OBJECT, text='', icon='TRIA_UP')
            op.direction = 'UP'

            row = col_ul.row(align=True)
            op = row.operator(base.OT_ID_MOVE_FACE_OBJECT, text='', icon='TRIA_DOWN')
            op.direction = 'DOWN'
            row = col.row(align=True)
            op = row.operator(base.OT_ID_ADD_FACIAL_OBJECT, icon='ADD')
            row = col.row(align=True)
            
class FACEBINDDEMO_PT_setup_vertexgroups(Base_Panel):
    bl_label = base.PT_LABEL_SETUP_VERTEXGROUPS
    bl_idname = base.PT_ID_SETUP_VERTEXGROUPS
    bl_parent_id = base.PT_ID_SETUP
    bl_options = set()
    predecessor = base.PT_ID_SETUP

    def __init__(self):
        super().__init__()
        self.predecessor = base.PT_ID_SETUP
        self.mask_modifiers = {}
        self.assigned_vertex_groups = []

    @classmethod
    def poll(cls, context):
        setup_data = context.scene.facebinddemo_setup_data
        rig_data = context.scene.facebinddemo_rig_data
        if setup_data.face_objects:
            return not rig_data.lh_use_existing_armature

    def draw_assign_group_options(self, row, grp_name, grp_name_ui, can_pick=True, is_pivot_group=False, picker_running=False):
        # vgroup_names = get_list_faceit_groups()
        faceit_grp_name = 'faceit_' + grp_name
        is_assigned = faceit_grp_name in self.assigned_vertex_groups
        is_masked = f"Mask {faceit_grp_name}" in self.mask_modifiers
        mask_inverted = self.mask_modifiers.get(f"Mask {faceit_grp_name}", False)
        is_drawn = False
        single_surface = False
        additive_group = False
        if 'main' in grp_name:
            row.operator(base.OT_ID_ASSIGN_MAIN, text=grp_name_ui, icon='GROUP_VERTEX')
            single_surface = True
            additive_group = True
        else:
            op = row.operator(base.OT_ID_ASSIGN_GROUP, text=grp_name_ui,icon='GROUP_VERTEX')
            op.vertex_group = grp_name
            op.is_pivot_group = is_pivot_group
        if can_pick:
            op = row.operator(base.OT_ID_VERTEX_GROUP_PICKER, text='', icon='EYEDROPPER', depress=picker_running)
            op.vertex_group_name = grp_name
            op.single_surface = single_surface
            op.additive_group = additive_group
        sub = row.row(align=True)
        sub.enabled = is_assigned
        op = sub.operator('faceit.draw_faceit_vertex_group', text='',icon='HIDE_OFF', depress=is_drawn)
        op.faceit_vertex_group_name = 'faceit_' + grp_name
        op = sub.operator('faceit.mask_group', text='', icon='MOD_MASK',depress=is_masked)
        op.vgroup_name = 'faceit_' + grp_name
        op.operation = 'REMOVE' if is_masked else 'ADD'
        if is_masked:
            op = sub.operator('faceit.mask_group', text='', icon='ARROW_LEFTRIGHT',depress=mask_inverted)
            op.vgroup_name = 'faceit_' + grp_name
            op.operation = 'INVERT'
        sub.operator('faceit.remove_faceit_groups', text='',icon='X').vgroup_name = 'faceit_' + grp_name

    def get_all_mask_modifiers(self, objects):
        mask_modifiers = {}
        for obj in objects:
            for mod in obj.modifiers:
                if mod.type == 'MASK':
                    if 'faceit' in mod.name:
                        mask_modifiers[mod.name] = mod.invert_vertex_group
                        continue
        return mask_modifiers

    def draw(self, context):
        setup_data = context.scene.facebinddemo_setup_data
        layout = self.layout
        objects = setup_utils.get_faceit_objects_list(context)
        self.assigned_vertex_groups = vertex_utils.get_assigned_faceit_vertex_groups(objects=objects)
        self.mask_modifiers = self.get_all_mask_modifiers(objects=objects)
        box = layout.box()
        coll_pick = box.column(align=True)
        picker_options = setup_data.picker_options
        picking_group = picker_options.picking_group
        row = coll_pick.row(align=True)
        row.label(text='Picker Options', icon='EYEDROPPER')
        row = coll_pick.row(align=True)
        row.prop(picker_options, 'pick_geometry', expand=True)
        row = coll_pick.row(align=True)
        row.prop(picker_options, 'hide_assigned', icon='HIDE_OFF', toggle=True)
        box = layout.box()
        col_main = box.column(align=True)
        row = col_main.row(align=True)
        row.label(text='Face Main (Mandatory)')
        row = col_main.row(align=True)
        row = col_main.row(align=True)

        self.draw_assign_group_options(
            row,
            'main',
            'Main',
            can_pick=True,
            picker_running=picking_group == 'main',
        )
        box = layout.box()
        col = box.column(align=True)
        separate_factor = .3
        col.separator(factor=separate_factor)
        col.label(text='Eyes (Eyeballs, Cornea, Iris, Spots, Highlights)')

        grid = col.grid_flow(columns=2, align=False)
        row = grid.row(align=True)
        self.draw_assign_group_options(row, 'right_eyes_other', 'Right Eye',
                                       is_pivot_group=True, picker_running=picking_group == 'right_eyes_other')

        row = grid.row(align=True)
        self.draw_assign_group_options(row, 'left_eyes_other', 'Left Eye', is_pivot_group=True,
                                       picker_running=picking_group == 'left_eyes_other')

        col.separator(factor=separate_factor)
        col.label(text='Teeth, Gum')

        row = col.row(align=True)
        self.draw_assign_group_options(
            row,
            'upper_teeth',
            'Upper Teeth',
            picker_running=picking_group == 'upper_teeth'
        )

        row = col.row(align=True)
        self.draw_assign_group_options(
            row,
            'lower_teeth',
            'Lower Teeth',
            picker_running=picking_group == 'lower_teeth'
        )

        # Tongue
        col.separator(factor=separate_factor)
        col.label(text='Tongue')

        row = col.row(align=True)
        self.draw_assign_group_options(
            row,
            'tongue',
            'Tongue',
            picker_running=picking_group == 'tongue'
        )

        # Eyelashes
        col.separator(factor=separate_factor)
        col.label(text='Eyelashes, Eyeshells, Tearlines')

        row = col.row(align=True)
        self.draw_assign_group_options(
            row,
            'eyelashes',
            'Eyelashes',
            picker_running=picking_group == 'eyelashes'
        )

        # Facial Hair
        col.separator(factor=separate_factor)
        col.label(text='Eyebrows, Beards, Facial Hair etc.')

        row = col.row(align=True)
        self.draw_assign_group_options(
            row,
            'facial_hair',
            'Facial Hair',
            picker_running=picking_group == 'facial_hair'
        )

        # Rigid
        col.separator(factor=separate_factor)
        col.label(text='Rigid, No Deform')

        row = col.row(align=True)
        self.draw_assign_group_options(
            row,
            'rigid',
            'Rigid',
            picker_running=picking_group == 'rigid'
        )

        if context.object:
            if context.object.mode != 'OBJECT':
                if context.object.type != 'MESH':
                    layout.enabled = False

        box = layout.box()
        col_utils = box.column(align=True)
        row = col_utils.row(align=True)
        row.label(text='Utilities')
        row = col_utils.row(align=True)
        row.operator('faceit.draw_faceit_vertex_group', text='Show Unassigned',
                     icon='HIDE_OFF', depress=False).faceit_vertex_group_name = 'UNASSIGNED'
        col_utils.separator()
        row = col_utils.row(align=True)
        row.operator(base.OT_ID_REMOVE_ALL_GROUPS, text='Reset All', icon='TRASH')


class FACEBINDDEMO_UL_object_list(bpy.types.UIList):
    bl_label = base.UL_LABEL_OBJECT_LIST
    bl_idname = base.UL_ID_OBJECT_LIST

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        scene = context.scene
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            obj = bpy_utils.get_object(item.name)
            row = layout.row(align=True)
            sub = row.row(align=True)
            sub.label(text=item.name, icon='OUTLINER_OB_MESH')
            if obj:
                if vertex_utils.get_faceit_vertex_grps(obj):
                    row.operator(base.OT_ID_DRAW_ASSIGNED_GROUPS_LIST, text='', icon='GROUP_VERTEX').obj_name = item.name
                if landmarks_utils.get_hide_obj(obj):
                    sub.enabled = False
            op = row.operator(base.OT_ID_REMOVE_FACIAL_PART, text='', icon='X')
            op.prompt = False
            op.remove_item = item.name
        else:
            layout.alignment = 'CENTER'
            layout.label(text='',)


class FACEBINDDEMO_OT_clear_objects(bpy.types.Operator):
    '''Remove the selected Character Geometry from Registration.'''
    bl_idname = base.OT_ID_CLEAR_OBJECT
    bl_label = base.OT_LABEL_CLEAR_IOBJECT
    bl_options = {'UNDO', 'INTERNAL'}

    clear_vertex_groups: bpy.props.BoolProperty(
        name='Clear Vertex Groups',
        description='Clear the assigned vertex groups or keep them on the object',
        default=False,
        options={'SKIP_SAVE'},
    )

    @classmethod
    def poll(cls, context):
        return context.scene.facebinddemo_setup_data.face_objects

    def execute(self, context):
        setup_data = context.scene.facebinddemo_setup_data

        face_objects_list = setup_data.face_objects

        if self.clear_vertex_groups:
            for obj in setup_utils.get_faceit_objects_list():
                try:
                    remove_groups = vertex_utils.remove_faceit_vertex_grps(obj)
                    self.report({'INFO'}, 'Cleared Faceit Vertex Groups {} on {}.'.format(remove_groups, obj.name))
                except AttributeError:

                    self.report({'INFO'}, 'No Vertex Groups found on Object.')
                    pass

        setup_data.face_index = 0
        face_objects_list.clear()
        setup_data.lh_body_armature = None

        return {'FINISHED'}

class FACEBINDDEMO_OT_remove_all_groups(bpy.types.Operator):
    '''Remove Faceit group(s) from selected object'''
    bl_idname = base.OT_ID_REMOVE_ALL_GROUPS
    bl_label = base.OT_LABEL_REMOVE_ALL_GROUPS
    bl_options = {'UNDO', 'INTERNAL'}

    operate_scope: bpy.props.EnumProperty(
        name='Objects to Operate on',
        items=(
            ('ALL', 'All Objects', 'Remove all Faceit Vertex Groups from all registered Objects'),
            ('SELECTED', 'Selected Objects', 'Remove All Vertex Groups from Selected Objects in Scene'),
        ),
        default='SELECTED',
    )

    @ classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, 'operate_scope', expand=True)

    def execute(self, context):
        setup_data = context.scene.facebinddemo_setup_data
        if self.operate_scope == 'ALL':
            operate_objects = [item.get_object() for item in setup_data.face_objects]
            self.report({'INFO'}, 'Cleared Vertex Groups for all registered objects')
        elif self.operate_scope == 'SELECTED':
            operate_objects = [obj for obj in context.selected_objects if obj.name in setup_data.face_objects]
            if not operate_objects:
                self.report({'WARNING'}, 'You need to select at least one object for this operation to work.')
                return {'CANCELLED'}
        groups_to_remove = setup_utils.get_list_faceit_groups()
        for grp_name in groups_to_remove:
            bpy.ops.faceit.mask_group('INVOKE_DEFAULT', vgroup_name=grp_name, operation='REMOVE')
            for obj in operate_objects:
                grp = obj.vertex_groups.get(grp_name)
                if grp:
                    obj.vertex_groups.remove(grp)
        return {'FINISHED'}
    
class FACEBINDDEMO_MT_register_objects(bpy.types.Menu):
    bl_label = base.MT_LABEL_REGISTER_OBJECTS
    bl_idname = base.MT_ID_REGISTER_OBJECTS

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        op = row.operator(base.OT_ID_CLEAR_OBJECT, text='Clear All Registered Objects', icon='TRASH')
        row = layout.row(align=True)
        row.operator(base.OT_ID_REMOVE_ALL_GROUPS, text='Reset All Vertex Groups', icon='TRASH')
        # op = row.operator('faceit.remove_faceit_groups', text='Reset All Vertex Groups', icon='TRASH')
        op.all_groups = True

    
class FACEIT_OT_InitRetargeting(bpy.types.Operator):
    '''Initialize the retargeting list and try to match shapes automatically'''
    bl_idname = 'faceit.init_retargeting'
    bl_label = 'Smart Match'
    bl_options = {'UNDO', 'INTERNAL'}

    levenshtein_ratio: bpy.props.FloatProperty(
        name='Similarity Ratio',
        default=1.0,
        description='The ratio can be used for fuzzy name comparison. Default: 1.0'
    )

    standart_shapes: bpy.props.BoolProperty(
        name='Standart',
        default=False,
        description='Register for ARKit Standart Names',
        options={'HIDDEN', 'SKIP_SAVE'}
    )

    empty: bpy.props.BoolProperty(
        name='Empty',
        default=False,
        description='Register with Empty Targets',
        options={'HIDDEN', 'SKIP_SAVE'}
    )

    remove_prefix_target: bpy.props.StringProperty(
        name='Prefix',
        description='Specify a Prefix in Shape Key names that will be ignore during ARKIT Shape matching.'
    )
    remove_suffix_target: bpy.props.StringProperty(
        name='Suffix',
        description='Specify a Suffix in Shape Key names that will be ignore during ARKIT Shape matching.'
    )
    expression_sets: bpy.props.EnumProperty(
        name='Expression Sets',
        items=(
            ('ALL', 'All', 'Search for all available expressions'),
            ('ARKIT', 'ARKit', 'The 52 ARKit Expressions that are used in all iOS motion capture apps'),
            ('A2F', 'Audio2Face', 'The 46 expressions that are used in Nvidias Audio2Face app by default.'),
        ),
        default='ALL'
    )
    quick_search: bpy.props.BoolProperty(
        name="Quick Search",
        description="Only check for exact matches",
        default=False,
        options={'HIDDEN', 'SKIP_SAVE'}
    )

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        if self.empty is False and self.standart_shapes is False:
            wm = context.window_manager
            return wm.invoke_props_dialog(self)
        else:
            return self.execute(context)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        row.label(text='Expression Sets:')
        row = box.row(align=True)
        row.prop(self, 'expression_sets', expand=True,)

        box = layout.box()
        row = box.row(align=True)
        row.label(text='Fuzzy Name Comparison:')
        row = box.row(align=True)
        row.prop(self, 'levenshtein_ratio')
        box = layout.box()
        row = box.row(align=True)
        row.label(text='Ignore in Name Comparison:')

        row = box.row(align=True)
        row.prop(self, 'remove_prefix_target')
        row = box.row(align=True)
        row.prop(self, 'remove_suffix_target')

    def execute(self, context):

        scene = context.scene

        expression_sets_dict = {}
        if self.expression_sets in ('ALL', 'ARKIT'):
            name_scheme = scene.faceit_retargeting_naming_scheme
            if name_scheme == 'ARKIT':
                expression_sets_dict['ARKIT'] = fdata.get_arkit_shape_data()
            elif name_scheme == 'FACECAP':
                expression_sets_dict['ARKIT'] = fdata.get_face_cap_shape_data()
        if self.expression_sets in ('ALL', 'A2F'):
            expression_sets_dict['A2F'] = fdata.get_a2f_shape_data()

        faceit_objects = futils.get_faceit_objects_list()
        shape_key_names = sk_utils.get_shape_key_names_from_objects(faceit_objects)

        if not shape_key_names:
            self.report({'WARNING'}, 'The registered object have no shape keys.')
            return {'CANCELLED'}

        # Remove prefix /suffix from shape names
        match_names = {}
        new_names = []
        if self.remove_prefix_target or self.remove_suffix_target:
            new_names = []
            for name in shape_key_names:
                name_match = name
                if self.remove_prefix_target:
                    if name.startswith(self.remove_prefix_target):
                        name_match = name[len(self.remove_prefix_target):]
                if self.remove_suffix_target:
                    if name.endswith(self.remove_suffix_target):
                        name_match = name[:-len(self.remove_suffix_target)]
                new_names.append(name_match)
                match_names[name_match] = name

        for expression_set, shape_dict in expression_sets_dict.items():
            if expression_set == 'ARKIT':
                retarget_list = scene.faceit_arkit_retarget_shapes
            else:
                retarget_list = scene.faceit_a2f_retarget_shapes

            retarget_list.clear()
            missing_shapes = []

            for expression_name, data in shape_dict.items():

                display_name = data['name']
                item = retarget_list.add()

                item.name = expression_name
                item.display_name = display_name

                if self.empty:
                    continue

                if self.standart_shapes:
                    target_item = item.target_shapes.add()
                    target_item.name = expression_name
                    continue

                if display_name in shape_key_names:
                    target_item = item.target_shapes.add()
                    target_item.name = display_name
                    shape_key_names.remove(display_name)
                    continue
                elif not self.quick_search:
                    if new_names:
                        found_shape = detect_shape(
                            new_names,
                            display_name,
                            min_levenshtein_ratio=self.levenshtein_ratio,
                            remove_suffix=self.remove_suffix_target,
                        )
                        found_shape = match_names.get(found_shape)
                        print(found_shape)
                    else:
                        found_shape = detect_shape(
                            shape_key_names,
                            display_name,
                            min_levenshtein_ratio=self.levenshtein_ratio,
                            remove_suffix=self.remove_suffix_target,
                        )
                    if found_shape:

                        target_item = item.target_shapes.add()
                        target_item.name = found_shape
                        shape_key_names.remove(found_shape)
                        continue

                missing_shapes.append(display_name)

            set_base_regions_from_dict(retarget_list)

            if missing_shapes and not self.quick_search:
                self.report(
                    {'WARNING'},
                    f'Couldn\'t find all {expression_set} target shapes. Did you generate the expressions')

        for region in context.area.regions:
            # if region.type == 'UI':
            region.tag_redraw()

        return {'FINISHED'}

