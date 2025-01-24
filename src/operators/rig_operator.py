import bpy
from ..core.constants import base
from ..core.constants import data_list
from ..processors.pivots_processor import PivotManager
from ..utils import landmarks_utils
from ..utils import vertex_utils
from ..utils import bpy_utils
from ..utils import setup_utils
from ..utils import rig_utils
from ..utils import arkit_utils
from ..utils import file_utils
from operator import attrgetter
from mathutils import Matrix, Vector

class FACEBINDDEMO_OT_generate_rig(bpy.types.Operator):
    '''Generates the Rig that holds the shapekey animation'''
    bl_idname = base.OT_ID_GENERATE_RIG
    bl_label = base.OT_LABEL_GENERATE_RIG
    bl_options = {'UNDO', 'INTERNAL'}

    use_existing_weights: bpy.props.BoolProperty(
        name='Bind with Existing Weights',
        default=False,
    )

    use_existing_expressions: bpy.props.BoolProperty(
        name='Activate Existing Expressions',
        default=False,
    )
    use_existing_corr_sk: bpy.props.BoolProperty(
        name='Use Existing Corrective Shape Keys',
        default=False,
    )
    weights_restorable = False
    expressions_restorable = False
    corr_sk_restorable = False

    @classmethod
    def poll(cls, context):
        setup_data = context.scene.facebinddemo_setup_data
        return setup_data.face_objects

    def invoke(self, context, event):
        rig_data = context.scene.facebinddemo_rig_data
        if rig_data.lh_armature_missing:
            self.weights_restorable = True
            self.expressions_restorable = True
            self.use_existing_corr_sk = True
            self.corr_sk_restorable = True
        else:
            self.weights_restorable = rig_data.weights_restorable
            self.expressions_restorable = rig_data.expressions_restorable
            self.use_existing_corr_sk = rig_data.corrective_sk_restorable
            self.corr_sk_restorable = rig_data.corrective_sk_restorable
        if self.weights_restorable or self.expressions_restorable:
            wm = context.window_manager
            return wm.invoke_props_dialog(self)
        else:
            return self.execute(context)

    def draw(self, context):
        layout = self.layout
        if self.weights_restorable:
            row = layout.row()
            row.prop(self, 'use_existing_weights', icon='GROUP_VERTEX')
        if self.expressions_restorable:
            row = layout.row()
            row.prop(self, 'use_existing_expressions', icon='ACTION')
            row = layout.row()
            row.prop(self, 'use_existing_corr_sk', icon='SCULPTMODE_HLT')
            row.enabled = self.corr_sk_restorable and self.use_existing_expressions

    def execute(self, context):
        rig_data = context.scene.facebinddemo_rig_data
        landmarks_data = context.scene.facebinddemo_landmarks_data
        arkit_data = context.scene.facebinddemo_arkit_data
        setup_data = context.scene.facebinddemo_setup_data
        
        global rig_create_warning
        PivotManager.save_pivots(context)
        bpy.ops.ed.undo_push()
        rig_create_warning = False
        auto_key = context.scene.tool_settings.use_keyframe_insert_auto
        context.scene.tool_settings.use_keyframe_insert_auto = False
        if context.scene.is_nla_tweakmode:
            bpy_utils.exit_nla_tweak_mode(context)
        landmarks = bpy_utils.get_object('facial_landmarks')
        if not landmarks:
            self.report(
                {'WARNING'},
                'You need to setup the Faceit Landmarks for your character in order to fit the Control Rig to your character.')
            return {'CANCELLED'}
        # PivotManager.remove_handle()
        if context.object:
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except RuntimeError:
                pass
        bpy.ops.faceit.unmask_main('EXEC_DEFAULT')
        # set_locator_hidden_state(hide=True)
        rig_filepath = file_utils.get_rig_file()
        lh_collection = bpy_utils.get_collection(context, create=False)
        rig = rig_utils.get_faceit_armature(force_original=True)
        if rig:
            bpy.data.objects.remove(rig)
        # load the objects data in the rig file
        with bpy.data.libraries.load(rig_filepath) as (data_from, data_to):
            data_to.objects = data_from.objects
        # add only the armature
        for obj in data_to.objects:
            if obj.type == 'ARMATURE' and obj.name == 'Rig':
                lh_collection.objects.link(obj)
                # bpy.context.scene.collection.objects.link(obj) 
                if obj.name in lh_collection.objects:
                    rig = bpy_utils.get_object(name=obj.name)
                break
        rig['faceit_rig_id'] = rig_utils.get_random_rig_id()

        bpy_utils.clear_object_selection()
        bpy_utils.set_active_object_by_name(rig)

        # bpy.ops.faceit.match()
        rig_data.lh_armature = rig
        if rig.animation_data:
            rig.animation_data.action = None

        # Update the bone collections to 4.0
        rig_utils.update_bone_collection()
        
        bpy.ops.object.mode_set(mode='EDIT')
        edit_bones = rig.data.edit_bones
       
        bones = ['eyes', 'eye.L', 'eye.R', 'DEF-face', 'MCH-eyes_parent']
        bone_translation = {}
        # temporarilly move bones to center of rig (only Y Axis/ dimensions[1] matters)
        for bone in bones:
            bone = edit_bones.get(bone)
            # store bone position
            bone_translation[bone.name] = (bone.head[1], bone.tail[1])
            # move to rig center
            bone.head[1] = bone.tail[1] = 0

        bpy.ops.object.mode_set(mode='OBJECT')
        rig.location = landmarks.location
        rig.rotation_euler = landmarks.rotation_euler
        # get average dimensions
        dim_lm = landmarks.dimensions.copy()
        avg_dim_lm = sum(dim_lm) / len(dim_lm)

        dim_rig = rig.dimensions.copy()
        avg_dim_rig = sum(dim_rig) / len(dim_rig)

        scale_factor = avg_dim_lm / avg_dim_rig  # landmarks.dimensions[0] / rig.dimensions[0]
        rig.dimensions = dim_rig * scale_factor  # rig.dimensions.copy() * scale_factor
        bpy.ops.object.mode_set(mode='EDIT')

        # restore the original positions
        for bone, pos in bone_translation.items():
            bone = edit_bones.get(bone)
            bone.head[1], bone.tail[1] = pos

        # the dictionary containing
        if landmarks_data.is_asymmetric:
            vert_dict = data_list.bone_dict_asymmetric
        else:
            vert_dict = data_list.bone_dict_symmetric

        # the mesh world matrix
        w_mat = rig.matrix_world
        # the bone space local matrix
        l_mat = rig.matrix_world.inverted()

        # save Settings
        if bpy.app.version < (4, 0, 0):
            layer_state = rig.data.layers[:]
            # enable all armature layers; needed for armature operators to work properly
            for i in range(len(rig.data.layers)):
                rig.data.layers[i] = True
        else:
            layer_state = [c.is_visible for c in rig.data.collections]
            for c in rig.data.collections:
                c.is_visible = True

        jaw_pivot_object = context.scene.objects.get('Jaw Pivot')
        if jaw_pivot_object:
            rig_data.use_jaw_pivot = True
            rig_data.jaw_pivot = jaw_pivot_object.location
        else:
            rig_data.use_jaw_pivot = False
        for i, bone_dict in vert_dict.items():
            target_point = None
            if i in (101, 111):
                rig.data.use_mirror_x = False
            else:
                rig.data.use_mirror_x = not landmarks_data.is_asymmetric

            # all vertices in the reference mesh
            if i < 100:
                # the world coordinates of the specified vertex
                target_point = landmarks.matrix_world @ landmarks.data.vertices[i].co

            ############# Special Cases ##############

            # eyes extra positions
            elif i == 101:
                if rig_data.eye_pivot_placement == 'MANUAL':
                    target_point = rig_data.eye_manual_pivot_point_L
                else:
                    target_point = rig_data.eye_pivot_point_L
            elif i == 111:
                if rig_data.eye_pivot_placement == 'MANUAL':
                    target_point = rig_data.eye_manual_pivot_point_R
                else:
                    target_point = rig_data.eye_pivot_point_R
            # jaw extra positions
            elif i == 102:
                empty_locator = jaw_pivot_object
                if empty_locator:
                    target_point = rig_data.jaw_pivot
                else:
                    jaw_L = edit_bones.get('jaw.L').head
                    jaw_R = edit_bones.get('jaw.R').head
                    target_point = w_mat @ rig_utils.get_median_pos([jaw_L, jaw_R])
                    # target_point = w_mat @ edit_bones['jaw.L'].head
                    # target_point.x = 0
            elif i == 109:
                jaw_L = edit_bones.get('jaw.L').head
                jaw_R = edit_bones.get('jaw.R').head
                target_point = w_mat @ rig_utils.get_median_pos([jaw_L, jaw_R])

            # nose extra positions
            elif i == 103:
                b_tip = edit_bones['nose.002'].head
                b_top = edit_bones['nose'].head
                vec = b_tip - b_top
                target_point = w_mat @ (b_top + vec * 0.7)

            elif i == 104:
                b_1 = edit_bones['nose.004'].head
                b_2 = edit_bones['lip.T'].head
                target_point = w_mat @ rig_utils.get_median_pos([b_1, b_2])
            elif i == 105:
                b_1 = edit_bones['nose.002'].head
                b_2 = edit_bones['nose.004'].head
                target_point = w_mat @ rig_utils.get_median_pos([b_1, b_2])

            # teeth extra positions
            elif i == 106:
                empty_locator = bpy.data.objects.get('teeth_upper_locator')
                if empty_locator:
                    target_point = empty_locator.location
                else:
                    upper_teeth_obj = vertex_utils.get_objects_with_vertex_group("faceit_upper_teeth")
                    if upper_teeth_obj:
                        vertex_locations = landmarks_utils.get_evaluated_vertex_group_positions(upper_teeth_obj, "faceit_upper_teeth", context=context)
                        if vertex_locations:
                            # target_point = max(vertex_locations, key=attrgetter('y'))
                            bounds = landmarks_utils.get_bounds_from_locations(vertex_locations, 'y')
                            target_point = rig_utils.get_median_pos(bounds)
                            if landmarks_data.is_asymmetric:
                                bounds = landmarks_utils.get_bounds_from_locations(vertex_locations, 'x')
                                target_point.x = rig_utils.get_median_pos(bounds).x
                            else:
                                target_point.x = 0
                if not target_point:
                    self.report(
                        {'WARNING'},
                        'could not find Upper Teeth, define vertex group in Setup panel first! Removed bones from the rig')
                    rig_create_warning = True
                    for b in vert_dict[106]['all']:
                        bone = edit_bones[b]
                        edit_bones.remove(bone)
                    continue
            elif i == 107:
                empty_locator = bpy.data.objects.get('teeth_lower_locator')
                if empty_locator:
                    target_point = empty_locator.location
                else:
                    lower_teeth_obj = vertex_utils.get_objects_with_vertex_group("faceit_lower_teeth")
                    if lower_teeth_obj:
                        vertex_locations = landmarks_utils.get_evaluated_vertex_group_positions(lower_teeth_obj, "faceit_lower_teeth", context=context)
                        if vertex_locations:
                            bounds = landmarks_utils.get_bounds_from_locations(vertex_locations, 'y')
                            target_point = rig_utils.get_median_pos(bounds)
                            if landmarks_data.is_asymmetric:
                                bounds = landmarks_utils.get_bounds_from_locations(vertex_locations, 'x')
                                target_point.x = rig_utils.get_median_pos(bounds).x
                            else:
                                target_point.x = 0
                if not target_point:
                    self.report(
                        {'WARNING'},
                        'could not find Lower Teeth, define vertex group in Setup panel first! Removed bones from the rig')
                    rig_create_warning = True
                    for b in vert_dict[107]['all']:
                        bone = edit_bones[b]
                        edit_bones.remove(bone)
                    continue
            elif i == 108:
                continue
            ############# Matching ##############
            if target_point:
                # all - translates head and tail by vector to target_point
                for b in bone_dict['all']:
                    bone = edit_bones[b]
                    l_point = l_mat @ target_point
                    vec = l_point - bone.head
                    bone.translate(vec)
                # head - translates head to target_point
                for b in bone_dict['head']:
                    bone = edit_bones[b]
                    bone.head = l_mat @ target_point
                # tail - translates tail to target_point
                for b in bone_dict['tail']:
                    bone = edit_bones[b]
                    bone.tail = l_mat @ target_point
        # apply same offset to all tongue bones

        tongue_obj = vertex_utils.get_objects_with_vertex_group("faceit_tongue")
        if tongue_obj:
            tongue_bones = [edit_bones[b] for b in vert_dict[108]["all"]]
            vertex_locations = landmarks_utils.get_evaluated_vertex_group_positions(tongue_obj, "faceit_tongue", context=context)
            if vertex_locations:
                target_point = min(vertex_locations, key=attrgetter('y'))
                if landmarks_data.is_asymmetric:
                    bounds = landmarks_utils.get_bounds_from_locations(vertex_locations, 'x')
                    target_point.x = rig_utils.get_median_pos(bounds).x
                else:
                    target_point.x = 0
                vec = l_mat @ target_point - edit_bones["tongue"].head
                for b in tongue_bones:
                    b.translate(vec)
                # squash/stretch bones into tongue geometry range (bounds)
                bone_locations = [b.head for b in tongue_bones]
                b_max_y, b_min_y = landmarks_utils.get_bounds_from_locations(bone_locations, 'y')
                v_max_y, v_min_y = (l_mat @ v for v in landmarks_utils.get_bounds_from_locations(vertex_locations, 'y'))
                old_range = b_max_y.y - b_min_y.y
                new_range = v_max_y.y - v_min_y.y
                new_range *= .9
                for b in tongue_bones:
                    old_value = b.head.y
                    new_value = (((old_value - b_min_y.y) * new_range) / old_range) + v_min_y.y
                    add_y = new_value - old_value
                    b.head.y += add_y
                    b.tail.y += add_y
                for i in range(112, 116):
                    b_dict = vert_dict[i]
                    pos = edit_bones[b_dict['all'][0]].head
                    for b in b_dict['tail']:
                        b = edit_bones[b]
                        b.tail = pos
        else:
            self.report(
                {'WARNING'},
                'could not find Tongue, define vertex group in Setup panel first! Removed Tongue bones from the Rig')
            rig_create_warning = True
            for b in vert_dict[108]['all']:
                bone = edit_bones[b]
                edit_bones.remove(bone)

        # translate the extra eye bone to the proper location
        eyes = edit_bones['eyes']
        eyes_length = Vector((0, 0, eyes.length))
        eye_master_L = edit_bones['master_eye.L']
        eye_master_R = edit_bones['master_eye.R']
        vec = eye_master_L.tail - edit_bones['MCH-eye.L.001'].head
        edit_bones['MCH-eye.L.001'].translate(vec)
        vec = eye_master_R.tail - edit_bones['MCH-eye.R.001'].head
        edit_bones['MCH-eye.R.001'].translate(vec)
        # position eye target bones
        eye_target_L = edit_bones['eye.L']
        eye_target_R = edit_bones['eye.R']
        eyes.head[2] = eye_master_L.head[2]
        eyes.tail = eyes.head + eyes_length
        eye_target_L.head[2] = eye_master_L.head[2]
        eye_target_L.tail = eye_target_L.head + eyes_length
        eye_target_R.head[2] = eye_master_R.head[2]
        eye_target_R.tail = eye_target_R.head + eyes_length
        # Orient all jaw bones to chin / Y Axis.
        bpy.ops.armature.select_all(action='DESELECT')
        jaw_master = edit_bones['jaw_master']
        chin_bone = edit_bones['chin']
        jaw_master.tail = chin_bone.head
        for bone in vert_dict[102]['all']:
            edit_bone = edit_bones[bone]
            edit_bone.head.x = edit_bones['chin'].head.x
            if edit_bone is not jaw_master:
                edit_bone.align_orientation(jaw_master)
            edit_bone.select = True
        bpy.ops.armature.calculate_roll(type='POS_X')
        bpy.ops.object.mode_set(mode='OBJECT')
        if rig.scale != Vector((1, 1, 1)):
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        rig_utils.reset_stretch(rig_obj=rig)

        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.armature_apply()
        rig_utils.set_lid_follow_constraints(rig, "L")
        rig_utils.set_lid_follow_constraints(rig, "R")
        bpy.ops.object.mode_set(mode='OBJECT')

        # restore the layer visibillity to its original state
        if bpy.app.version < (4, 0, 0):
            rig.data.layers = layer_state[:]
        else:
            for i, c in enumerate(rig.data.collections):
                c.is_visible = layer_state[i]

        landmarks.hide_viewport = True
        if jaw_pivot_object:
            bpy.data.objects.remove(jaw_pivot_object)
        if self.use_existing_weights:
            bpy.ops.faceit.pair_armature()
            self.report({'INFO'}, 'Restored Existing Weights. You can regenerate weights by using the Bind operator')

        if self.use_existing_expressions:
            # sh_action = bpy.data.actions.get('faceit_shape_action')
            ow_action = bpy.data.actions.get('overwrite_shape_action')
            expression_list = setup_data.expression_list

            if not expression_list:
                self.report({'WARNING'}, 'The Expression List could not be found.')

            if ow_action:
                rig.animation_data_create()
                rig.animation_data.action = ow_action
            else:
                self.report({'WARNING'}, 'Could not find expressions action {}'.format('overwrite_shape_action'))

            if self.corr_sk_restorable:
                faceit_objects = setup_utils.get_faceit_objects_list()
                corrective_sk_action = bpy.data.actions.get('faceit_corrective_shape_keys', None)
                for obj in faceit_objects:
                    if arkit_utils.has_shape_keys(obj):
                        has_corrective_shape_keys = False
                        for sk in obj.data.shape_keys.key_blocks:
                            if sk.name.startswith('faceit_cc_'):
                                if self.use_existing_corr_sk:
                                    has_corrective_shape_keys = True
                                    sk.mute = False
                                else:
                                    obj.shape_key_remove(sk)
                        if len(obj.data.shape_keys.key_blocks) == 1:
                            obj.shape_key_clear()
                        else:
                            if has_corrective_shape_keys and corrective_sk_action:
                                if not obj.data.shape_keys.animation_data:
                                    obj.data.shape_keys.animation_data_create()
                                obj.data.shape_keys.animation_data.action = corrective_sk_action
                rig_data.corrective_sk_restorable = False
        else:
            setup_data.expression_list.clear()

        if rig_create_warning:
            self.report({'WARNING'}, 'Rig generated with warnings. Please see Console Output for details.')
        else:
            self.report({'INFO'}, 'Rig generated successfully!')

        context.scene.tool_settings.use_keyframe_insert_auto = auto_key
        context.scene.tool_settings.use_snap = False

        return {'FINISHED'}
