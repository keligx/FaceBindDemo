from contextlib import redirect_stdout
import io
import time
import bpy
from mathutils import Matrix, Vector
from ..core.constants import base
from ..core.constants import data_list
from ..utils import landmarks_utils
from ..utils import vertex_utils
from ..utils import bpy_utils
from ..utils import setup_utils
from ..utils import rig_utils
from ..utils import arkit_utils
from ..utils import bind_utils


class FACEBINDDEMO_OT_smart_bind(bpy.types.Operator):
    '''Bind main objects (Face, Eyes, Teeth, Tongue)'''
    bl_idname = base.OT_ID_SMART_BIND
    bl_label = base.OT_LABEL_SMART_BIND
    bl_options = {'UNDO', 'INTERNAL', 'REGISTER'}

    found_faceit_eyelashes_grp = False
    found_faceit_eyes_grp = False
    found_faceit_teeth_grp = False
    found_faceit_tongue_grp = False

    @ classmethod
    def poll(cls, context):
        setup_data = context.scene.facebinddemo_setup_data
        rig = rig_utils.get_faceit_armature(force_original=True)
        if rig and setup_data.face_objects:
            if rig.hide_viewport is False and context.mode == 'OBJECT':
                return True

    def invoke(self, context, event):
        objects = setup_utils.get_faceit_objects_list(context)
        self.bind_data = getattr(context.scene, base.PROP_BIND_DATA)
        self.found_faceit_eyelashes_grp = bool(vertex_utils.get_objects_with_vertex_group(
            "faceit_eyelashes", objects=objects, get_all=False))
        if not self.found_faceit_eyelashes_grp:
            self.bind_data.smooth_expand_eyelashes = self.bind_data.clean_eyelashes_weights = False
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        self.bind_data = getattr(context.scene, base.PROP_BIND_DATA)
        layout = self.layout
        col_bind = layout.column()
        row = col_bind.row(align=True)
        row.prop(self.bind_data, "bind_scale_objects", icon='EMPTY_DATA')
        if self.bind_data.bind_scale_objects:
            row.prop(self.bind_data, "bind_scale_factor")
        row = col_bind.row()
        row.prop(self.bind_data, "show_advanced_settings", icon="COLLAPSEMENU")
        if self.bind_data.show_advanced_settings:
            row = col_bind.row()
            row.prop(self.bind_data, "smart_weights")
            if self.bind_data.smart_weights:
                row = col_bind.row()
                row.prop(self.bind_data, "smooth_main_edges")
                if self.bind_data.smooth_main_edges:
                    col_bind.use_property_split = True
                    row = col_bind.row()
                    row.prop(self.bind_data, "main_smooth_factor")
                    row = col_bind.row()
                    row.prop(self.bind_data, "main_smooth_steps")
                    row = col_bind.row()
                    row.prop(self.bind_data, "main_smooth_expand")
                    col_bind.use_property_split = False
                    row = col_bind.row()
            row = col_bind.row()
            row.label(text="Weight Method")
            row = col_bind.row()
            row.prop(self.bind_data, "weight_secondary_method", expand=True)
            row = col_bind.row()
            row.prop(self.bind_data, "remove_old_faceit_weights")
            row.prop(self.bind_data, "remove_rigid_weights")
            row = col_bind.row()
            row.prop(self.bind_data, "weight_eyes")
            row.prop(self.bind_data, "weight_teeth")
            row = col_bind.row()
            row.prop(self.bind_data, "weight_tongue")
            row = col_bind.row()
            row.label(text="Note: Assign the Groups in Setup.")
            row = col_bind.row()
            row.prop(self.bind_data, "smooth_bind")
            if self.bind_data.smooth_bind:
                col_bind.use_property_split = True
                row = col_bind.row()
                row.prop(self.bind_data, "smooth_factor")
                row = col_bind.row()
                row.prop(self.bind_data, "smooth_steps")
                row = col_bind.row()
                row.prop(self.bind_data, "smooth_expand")
                col_bind.use_property_split = False
            if self.bind_data.weight_secondary_method == 'TRANSFER':
                row = col_bind.row()
                row.prop(self.bind_data, "tranfer_to_hair_only")
            row = col_bind.row()
            row.prop(self.bind_data, "clean_eyelashes_weights")
            row.prop(self.bind_data, "smooth_expand_eyelashes")
            if not self.found_faceit_eyelashes_grp:
                row.enabled = False
                row.active = False
                row = col_bind.row()
                row.label(text="No Eyelashes Found.")

            if self.bind_data.smooth_expand_eyelashes:
                col_bind.use_property_split = True
                row = col_bind.row()
                row.prop(self.bind_data, "eyelashes_smooth_factor")
                row = col_bind.row()
                row.prop(self.bind_data, "eyelashes_smooth_steps")
                row = col_bind.row()
                row.prop(self.bind_data, "eyelashes_smooth_expand")
                col_bind.use_property_split = False
                row = col_bind.row()
            row = col_bind.row()
            row.prop(self.bind_data, "make_single_user")
            row.prop(self.bind_data, "keep_split_objects")

    def execute(self, context):
        if not self.validate_data(context):
            return self.cancel(context)
        landmarks_data = context.scene.facebinddemo_landmarks_data
        setup_data = context.scene.facebinddemo_setup_data
        self.bind_data = getattr(context.scene, base.PROP_BIND_DATA)
        
        start_time = time.time()
        faceit_objects = setup_utils.get_faceit_objects_list(context)
        lm_obj = bpy_utils.get_object("facial_landmarks")
        rig = rig_utils.get_faceit_armature()

        # --------------- SCENE SETTINGS -------------------
        auto_key = context.scene.tool_settings.use_keyframe_insert_auto
        use_auto_normalize = context.scene.tool_settings.use_auto_normalize
        context.scene.tool_settings.use_auto_normalize = False
        transform_orientation = context.scene.transform_orientation_slots[0].type
        context.scene.transform_orientation_slots[0].type = 'GLOBAL'
        mesh_select_mode = context.scene.tool_settings.mesh_select_mode[:]
        context.scene.tool_settings.mesh_select_mode = (True, True, True)
        context.scene.tool_settings.use_keyframe_insert_auto = False
        pivot_setting = context.scene.tool_settings.transform_pivot_point
        simplify_value = context.scene.render.use_simplify
        simplify_subd = context.scene.render.simplify_subdivision
        context.scene.render.use_simplify = True
        context.scene.render.simplify_subdivision = 0

        landmarks_utils.set_hidden_state_object(lm_obj,False,False)
        landmarks_utils.set_hidden_state_object(rig,False,False)
        rig.data.pose_position = 'REST'
        blend_version = bpy_utils.get_blender_version()
        # enable all armature layers
        if blend_version < (4, 0, 0):
            layer_state = rig.data.layers[:]
            # enable all armature layers; needed for armature operators to work properly
            for i in range(len(rig.data.layers)):
                rig.data.layers[i] = True
        else:
            layer_state = [c.is_visible for c in rig.data.collections]
            for c in rig.data.collections:
                c.is_visible = True
        # --------------- OBJECT & ARMATURE SETTINGS -------------------
        # | - Unhide Objects
        # | - Hide Generators (Modifier)
        # | - Set Mirror Settings (asymmetry or not)
        # -------------------------------------------------------
        obj_mod_show_dict = {}
        obj_mod_drivers = {}
        obj_settings = {}
        obj_sk_dict = {}
        for obj in faceit_objects:

            obj_settings[obj.name] = {
                "topology_mirror": obj.data.use_mirror_topology,
                "lock_location": obj.lock_location[:],
                "lock_rotation": obj.lock_rotation[:],
                "lock_scale": obj.lock_scale[:],
            }
            obj.lock_scale[:] = (False,) * 3
            obj.lock_location[:] = (False,) * 3
            obj.lock_rotation[:] = (False,) * 3
            obj.data.use_mirror_topology = False
            obj.data.use_mirror_x = False if landmarks_data.is_asymmetric else True

            if obj.data.users > 1:
                if self.bind_data.make_single_user:
                    obj.data = obj.data.copy()
                    print(f"Making Single user copy of objects {obj.name} data")
                else:
                    self.report(
                        {'WARNING'},
                        f"The object {obj.name} has multiple users. Check Make Single User in Bind Settings if binding fails.")

            landmarks_utils.set_hidden_state_object(obj, False, False)
            bpy_utils.clear_object_selection()
            bpy_utils.set_active_object(obj.name)
            bpy_utils.switch_mode(mode='EDIT')
            bpy.ops.mesh.reveal()
            bpy_utils.switch_mode(mode='OBJECT')

            other_rigs = []
            # Hide Modifiers and mute drivers if necessary
            for mod in obj.modifiers:
                if mod.type in data_list.GENERATORS:
                    if obj.animation_data:
                        for dr in obj.animation_data.drivers:
                            # If it's muted anyways, continue
                            if dr.mute:
                                continue
                            if "modifiers" in dr.data_path:
                                try:
                                    obj_mod_drivers[obj.name].append(dr.data_path)
                                except KeyError:
                                    obj_mod_drivers[obj.name] = [dr.data_path]
                                dr.mute = True
                    try:
                        obj_mod_show_dict[obj.name][mod.name] = mod.show_viewport
                    except KeyError:
                        obj_mod_show_dict[obj.name] = {mod.name: mod.show_viewport}
                    mod.show_viewport = False

            # Remove all FaceitRig vertex groups
            if self.bind_data.remove_old_faceit_weights:
                other_deform_groups = []
                if other_rigs:
                    for o_rig in other_rigs:
                        other_deform_groups.extend(vertex_utils.get_deform_bones_from_armature(o_rig))
                # Just get current vertex groups
                deform_groups = vertex_utils.get_deform_bones_from_armature(rig)
                vertex_group_intersect = (set(deform_groups).intersection(set(other_deform_groups)))
                if vertex_group_intersect:
                    self.report(
                        {'WARNING'},
                        "There seems to be another rig with similar bone names: {}. This can lead to weight conflicts. Faceit will add the influence.".
                        format(vertex_group_intersect))
                for grp in obj.vertex_groups:
                    if grp.name in deform_groups:
                        if grp.name not in other_deform_groups:
                            obj.vertex_groups.remove(grp)

            if arkit_utils.has_shape_keys(obj):
                for sk in obj.data.shape_keys.key_blocks:
                    if sk.name.startswith('faceit_cc_'):
                        sk.mute = True
                # --------------- DUPLICATE OBJECT(S) -------------------
                # | - Preserve Data (Vertex Groups + Shape Keys)
                # -------------------------------------------------------
        dup_objects_dict = {}
        dup_face_objects = []
        obj_data_dict = {}
        dg = bpy.context.evaluated_depsgraph_get()
        bpy_utils.clear_object_selection()
        for obj in faceit_objects:
            eval_mesh_data = arkit_utils.get_mesh_data(obj, dg)
            # Create static duplicates of all meshes for binding.
            if blend_version < (3, 0, 0):
                # this is a workaround... new_from_object disregards the vertex groups
                dup_obj = obj.copy()
                dup_obj.data = obj.data.copy()
            else:
                obj_eval = obj.evaluated_get(dg)
                me = bpy.data.meshes.new_from_object(obj_eval)
                dup_obj = bpy.data.objects.new(obj.name, me)
                dup_obj.matrix_world = obj.matrix_world
            dup_objects_dict[obj] = dup_obj
            dup_face_objects.append(dup_obj)
            context.scene.collection.objects.link(dup_obj)
            dup_obj.select_set(state=True)

            # Original Object: Store Shape Keys + delete (for data transfer to work!)
            if arkit_utils.has_shape_keys(obj):
                sk_dict = arkit_utils.store_shape_keys(obj)
                sk_action = None
                if obj.data.shape_keys.animation_data:
                    sk_action = obj.data.shape_keys.animation_data.action
                obj_sk_dict[obj] = {
                    "sk_dict": sk_dict,
                    "sk_action": sk_action,
                }
                arkit_utils.remove_all_sk_apply_basis(obj, apply_basis=True)

            basis_data = arkit_utils.get_mesh_data(obj, evaluated=False)
            obj_data_dict[obj.name] = [basis_data, eval_mesh_data]
            # Remove all vertex groups from duplicates, except for faceitgroups
            for grp in dup_obj.vertex_groups:
                if "faceit_" not in grp.name:
                    dup_obj.vertex_groups.remove(grp)
        # Remove parent - keep transform! Parent objects with Transforms can mess up the process!
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        # --------------- SCALE OBJECT(S) -------------------
        # | - Scale armature, bind objects, landmarks to avoid Auto Weight error. Known Issue in Blender
        # -------------------------------------------------------
        context.scene.cursor.location = Vector()
        context.scene.tool_settings.transform_pivot_point = 'CURSOR'

        if self.bind_data.bind_scale_objects:
            scale_factor = self.bind_data.bind_scale_factor
            bind_utils.scale_bind_objects(factor=scale_factor, objects=[rig, *dup_face_objects, lm_obj])
        # --------------- MAIN BINDING PROCESS -------------------
        # | - Bind (main geo) +
        # | - Data Transfer (hair, beard,brows etc.) +
        # | - Secondary Assigns (eyes, teeth, tongue)
        # -------------------------------------------------------
        bind_success = self._bind(
            context,
            bind_objects=dup_face_objects,
            rig=rig,
            lm_obj=lm_obj,
        )
        # --------------- RESTORE SCALE(S) -------------------
        context.scene.cursor.location = Vector()
        context.scene.tool_settings.transform_pivot_point = 'CURSOR'

        if self.bind_data.bind_scale_objects:
            bind_utils.scale_bind_objects(factor=scale_factor, objects=[rig, *dup_face_objects, lm_obj], reverse=True)
            rig.scale = Vector((1,) * 3)

        # --------------- RESTORE OBJECT DATA -------------------
        # | - Data Transfer the original data
        # -------------------------------------------------------
        for obj, dup_obj in dup_objects_dict.items():
            # Bring original mesh to evaluated shape
            obj.data.vertices.foreach_set('co', obj_data_dict[obj.name][1].ravel())
            dg.update()
            bind_utils.data_transfer_vertex_groups(obj_from=dup_obj, obj_to=obj, apply=True, method='NEAREST')
            dg.update()
            # Bring original mesh back to basis shape
            obj.data.vertices.foreach_set('co', obj_data_dict[obj.name][0].ravel())
            bpy.data.objects.remove(dup_obj, do_unlink=True)
            bpy_utils.clear_object_selection()
            bpy_utils.set_active_object(obj.name)
            # --------------- OBJECT & ARMATURE SETTINGS -------------------
            # | - Unhide Objects
            # | - Restore Modifier States
            # | - Restore Shape Keys
            # --------------------------------------------------------------
            obj.data.use_mirror_topology = obj_settings[obj.name]["topology_mirror"]
            obj.lock_location = obj_settings[obj.name]["lock_location"]
            obj.lock_rotation = obj_settings[obj.name]["lock_rotation"]
            obj.lock_scale = obj_settings[obj.name]["lock_scale"]
            dr_dict = obj_mod_drivers.get(obj.name)
            if dr_dict:
                for dr_dp in dr_dict:
                    if obj.animation_data:
                        dr = obj.animation_data.drivers.find(dr_dp)
                        if dr:
                            dr.mute = False

            show_mod_dict = obj_mod_show_dict.get(obj.name)
            if show_mod_dict:
                for mod_name, show_value in show_mod_dict.items():
                    mod = obj.modifiers.get(mod_name)
                    if mod:
                        mod.show_viewport = show_value
            sk_data_dict = obj_sk_dict.get(obj)
            if sk_data_dict:
                sk_dict = sk_data_dict["sk_dict"]
                sk_action = sk_data_dict["sk_action"]
                arkit_utils.apply_stored_shape_keys(obj, sk_dict, apply_drivers=True)
                for sk in obj.data.shape_keys.key_blocks:
                    if sk.name.startswith('faceit_cc_'):
                        sk.mute = False
            if arkit_utils.has_shape_keys(obj):
                if sk_action:
                    if not obj.data.shape_keys.animation_data:
                        obj.data.shape_keys.animation_data_create()
                    obj.data.shape_keys.animation_data.action = sk_action

            # ----------------- FACEIT MODIFIER --------------------------
            # | - Check for bind groups and ensure the modifier is applied
            # -------------------------------------------------------------
            deform_groups = vertex_utils.get_deform_bones_from_armature(rig)
            if not any([grp in obj.vertex_groups for grp in deform_groups]):
                continue
            bind_utils.add_faceit_armature_modifier(setup_data, obj, rig)
        # --------------- RESTORE SETTINGS -------------------
        rig.data.pose_position = 'POSE'
        # restore the layer visibillity to its original state
        if bpy.app.version < (4, 0, 0):
            rig.data.layers = layer_state[:]
        else:
            for i, c in enumerate(rig.data.collections):
                c.is_visible = layer_state[i]
        landmarks_utils.set_hidden_state_object(lm_obj, True, True)
        context.scene.tool_settings.transform_pivot_point = pivot_setting
        context.scene.tool_settings.use_auto_normalize = use_auto_normalize
        context.scene.transform_orientation_slots[0].type = transform_orientation
        context.space_data.overlay.show_relationship_lines = False
        context.scene.tool_settings.use_keyframe_insert_auto = auto_key
        context.scene.render.use_simplify = simplify_value
        context.scene.render.simplify_subdivision = simplify_subd
        context.scene.tool_settings.mesh_select_mode = mesh_select_mode
        context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
        bpy_utils.clear_object_selection()
        bpy_utils.set_active_object(rig.name)
        bpy.ops.outliner.orphans_purge()
        if bind_success:
            self.report({'INFO'}, "Binding Successful")
            print("Bound in {}".format(round(time.time() - start_time, 2)))
        else:
            self.report({'ERROR'}, "Faceit Binding Failed. See Console for more info.")
        return {'FINISHED'}

    def _bind(self, context, bind_objects, rig, lm_obj) -> bool:
        """Start the Faceit Binding progress on the passed bind objects
        @face_obj: the main object, can also be retrieved from bind_objects (main group)
        @bind_objects: the bind objects. Should have cleared vertex groups except for faceit groups
        @rig: the armature object to bind to
        Returns True if binding was successful, False if not
        """

        faceit_vertex_groups = [
            "faceit_right_eyeball",
            "faceit_left_eyeball",
            "faceit_left_eyes_other",
            "faceit_right_eyes_other",
            "faceit_upper_teeth",
            "faceit_lower_teeth",
            "faceit_tongue",
            # "faceit_rigid",
        ]
        # "faceit_eyelashes", "faceit_facial_hair", "faceit_main",
        # ----------------------- SPLIT OBJECTS BEFORE BIND ----------------------------
        # | - Split by Faceit Group assignments
        # | - Sort objects for different bind methods
        # ------------------------------------------------------------------------------
        bind_problem = False
        auto_weight_objects = []
        main_obj = None
        transfer_weights_objects = []
        eyelashes_objects = []
        secondary_bind_objects = []
        all_split_objects = []
        split_bind_objects_dict = {}
        is_new_rigify = any(b.name in ('lip_end.L.001', 'eye_common') for b in rig.data.bones)
        setup_data = context.scene.facebinddemo_setup_data

        for obj in bind_objects:
            # Unlock all groups:
            for grp in obj.vertex_groups:
                grp.lock_weight = False
            split_objects = bind_utils.split_by_faceit_groups(obj)
            all_split_objects.extend(split_objects)
            split_bind_objects_dict[obj] = split_objects
        # Remove double entries
        all_split_objects = list(set(all_split_objects))
        bpy_utils.clear_object_selection()
        for s_obj in all_split_objects:
            if "faceit_main" in s_obj.vertex_groups and len(
                    s_obj.vertex_groups) == 1:  # or "faceit_tongue" in s_obj.vertex_groups:
                main_obj = s_obj
                continue
            # Remove all vertex groups that don't cover the whole split surface.
            for grp in s_obj.vertex_groups:
                if 'faceit_' in grp.name:
                    vs = vertex_utils.get_verts_in_vgroup(s_obj, grp.name)
                    if len(vs) != len(s_obj.data.vertices):
                        # No need to split, the object is already separated
                        print(f'removing {grp.name} from {s_obj.name}')
                        s_obj.vertex_groups.remove(grp)
            if any([grp.name in faceit_vertex_groups for grp in s_obj.vertex_groups]):
                secondary_bind_objects.append(s_obj)
            elif "faceit_facial_hair" in s_obj.vertex_groups or not self.bind_data.tranfer_to_hair_only:
                transfer_weights_objects.append(s_obj)
                if "faceit_eyelashes" in s_obj.vertex_groups:
                    eyelashes_objects.append(s_obj)

        if self.bind_data.weight_secondary_method == 'AUTO':
            auto_weight_objects = all_split_objects
        else:
            auto_weight_objects = [main_obj]

        if self.bind_data.keep_split_objects:
            print("------- SPLIT OBJECTS ----------")
            print(all_split_objects)
            print("------- Auto Bind ----------")
            print(auto_weight_objects)
            print("------- Data Transfer ----------")
            print(transfer_weights_objects)
            print("------- Secondary Bind ----------")
            print(secondary_bind_objects)
        # --------------- AUTO WEIGHT ---------------------------
        # | - ...
        # -------------------------------------------------------
        start_time = time.time()
        bind_problem, warnings = self._auto_weight_objects(
            auto_weight_objects,
            rig,
        )
        if warnings:
            for w in warnings:
                self.report({'WARNING'}, w)
            self.report({'WARNING'}, "Automatic Weights failed! {}".format("Try to use a higher Scale factor."))
        print("Auto Weights in {}".format(round(time.time() - start_time, 2)))
        # ----------------------- SMART WEIGHTS ---------------------------
        # | Remove weights out of the face.
        # -----------------------------------------------------------------
        if self.bind_data.smart_weights:
            start_time = time.time()
            self._apply_smart_weighting(
                context,
                [main_obj],
                rig,
                lm_obj,
                smooth_weights=self.bind_data.smooth_main_edges
            )
            # return
            print("Smart Weights in {}".format(round(time.time() - start_time, 2)))

        # brow_bones = ['DEF-brow.B.L', 'DEF-brow.B.L.001', 'DEF-brow.B.L.002', 'DEF-brow.B.L.003',
        #               'DEF-brow.B.R', 'DEF-brow.B.R.001', 'DEF-brow.B.R.002', 'DEF-brow.B.R.003']
        # self._smooth_bone_selection(
        #     auto_weight_objects,
        #     rig,
        #     brow_bones,
        #     factor=.5,
        #     steps=4,
        #     expand=-1.0,
        # )
        # ----------------------- TRANSFER WEIGHTS ---------------------------
        # | Transfer Weights from auto bound geo to secondary geo (hair,...)
        # --------------------------------------------------------------------
        if self.bind_data.weight_secondary_method == 'TRANSFER':
            if transfer_weights_objects:
                start_time = time.time()
                self._transfer_weights(
                    auto_weight_objects,
                    transfer_weights_objects,
                )
                print("Transfer Weights in {}".format(round(time.time() - start_time, 2)))
        if eyelashes_objects:
            # remove all non lid deform groups from eyelashes
            lid_bones = [
                "DEF-lid.B.L",
                "DEF-lid.B.L.001",
                "DEF-lid.B.L.002",
                "DEF-lid.B.L.003",
                "DEF-lid.T.L",
                "DEF-lid.T.L.001",
                "DEF-lid.T.L.002",
                "DEF-lid.T.L.003",
                "DEF-lid.B.R",
                "DEF-lid.B.R.001",
                "DEF-lid.B.R.002",
                "DEF-lid.B.R.003",
                "DEF-lid.T.R",
                "DEF-lid.T.R.001",
                "DEF-lid.T.R.002",
                "DEF-lid.T.R.003",
            ]
            if self.bind_data.clean_eyelashes_weights:
                for obj in eyelashes_objects:
                    for vgroup in obj.vertex_groups:
                        if "DEF" in vgroup.name:
                            if vgroup.name not in lid_bones:
                                obj.vertex_groups.remove(vgroup)
            # smooth expand eyelashes weights
            if self.bind_data.smooth_expand_eyelashes:
                bind_utils.smooth_selected_weights(
                    setup_data,
                    eyelashes_objects,
                    rig,
                    lid_bones,
                    factor=self.bind_data.eyelashes_smooth_factor,
                    steps=self.bind_data.eyelashes_smooth_steps,
                    expand=self.bind_data.eyelashes_smooth_expand,
                )
        # ----------------------- USER WEIGHTS ---------------------------
        # | Faceit groups -> eyes, teeth, tongue, rigid
        # --------------------------------------------------------------------
        if self.bind_data.weight_eyes:
            eye_grps = ("faceit_left_eyes_other", "faceit_right_eyes_other",
                        "faceit_left_eyeball", "faceit_right_eyeball")
            for vgroup in eye_grps:
                if is_new_rigify:
                    new_grp = "DEF-eye.L" if "left" in vgroup else "DEF-eye.R"
                else:
                    new_grp = "DEF_eye.L" if "left" in vgroup else "DEF_eye.R"
                self.overwrite_faceit_group(all_split_objects, vgroup, new_grp)

        if self.bind_data.weight_teeth:
            teeth_grps = ("faceit_upper_teeth", "faceit_lower_teeth")
            for vgroup in teeth_grps:
                if "lower_teeth" in vgroup:
                    if rig.pose.bones.get("DEF-teeth.B"):
                        new_grp = "DEF-teeth.B"
                    else:
                        self.report(
                            {'WARNING'},
                            "Lower Teeth bone 'DEF - teeth.B' does not exist. Create the bone manually or specify Teeth Vertex Groups and regenerate the Rig.")
                        continue
                if "upper_teeth" in vgroup:
                    if rig.pose.bones.get("DEF-teeth.T"):
                        new_grp = "DEF-teeth.T"
                    else:
                        self.report(
                            {'WARNING'},
                            "Uppper Teeth bone 'DEF - teeth.T' does not exist. Create the bone manually or specify Teeth Vertex Groups and regenerate the Rig.")
                        continue
                self.overwrite_faceit_group(all_split_objects, vgroup, new_grp)

        if self.bind_data.weight_tongue:
            objects_with_vgroup = vertex_utils.get_objects_with_vertex_group(
                "faceit_tongue", objects=secondary_bind_objects, get_all=True)
            tongue_bones = [
                "DEF-tongue",
                "DEF-tongue.001",
                "DEF-tongue.002"
            ]
            bind_utils.auto_weight_selection_to_bones(setup_data, objects_with_vgroup, rig, tongue_bones, "faceit_tongue")

        # ----------------------- MERGE SPLIT OBJECTS ---------------------------
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set()
        for obj, split_objects in split_bind_objects_dict.items():
            bpy_utils.clear_object_selection()
            for s_obj in split_objects:
                if s_obj:
                    if self.bind_data.keep_split_objects:
                        debug_duplicate = s_obj.copy()
                        debug_duplicate.data = s_obj.data.copy()
                        context.scene.collection.objects.link(debug_duplicate)
                        debug_duplicate.name = debug_duplicate.name + "_debug"
                    bpy_utils.set_active_object(s_obj.name)
            if len(split_objects) > 1:
                bpy_utils.set_active_object(obj.name)
                bpy.ops.object.join()
            bind_utils.add_faceit_armature_modifier(setup_data=setup_data, obj=obj, rig=rig)

        # ----------------------- SMOOTH ALL ---------------------------
        # | Smooth pass on all bind objects
        # -----------------------------------------------------------------
        if self.bind_data.smooth_bind:
            bpy_utils.smooth_weights(context, objects=bind_objects, rig=rig)
        # ----------------------- REMOVE RIGID ---------------------------
        # | Remove Weights from Verts with faceit_rigid group (pass only faceit_rigid)
        # -----------------------------------------------------------------
        if self.bind_data.remove_rigid_weights:
            self.overwrite_faceit_group(bind_objects, "faceit_rigid", new_grp=None)

        for obj in bind_objects:
            for grp in obj.vertex_groups:
                if "faceit_" in grp.name:
                    obj.vertex_groups.remove(grp)

        return not bind_problem

    def _auto_weight_objects(self, auto_weight_objects, rig):
        '''Apply Automatic Weights to main geometry.'''
        auto_weight_problem = False
        all_warnings = []
        # Disable bones for auto weighting
        no_auto_weight = [
            "DEF-tongue",
            "DEF-tongue.001",
            "DEF-tongue.002",
            "DEF-teeth.B",
            "DEF-teeth.T",
            "DEF_eye.R",
            "DEF_eye.L",
        ]
        for b in no_auto_weight:
            bone = rig.data.bones.get(b)
            if bone:
                bone.use_deform = False
        warning = "Warning: Bone Heat Weighting: failed to find solution for one or more bones"
        for obj in auto_weight_objects:
            bpy_utils.clear_object_selection()
            obj.select_set(state=True)
            bpy_utils.set_active_object(rig.name)
            _stdout_warning = ""
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                bpy.ops.object.parent_set(type='ARMATURE_AUTO', keep_transform=True)
            stdout.seek(0)
            _stdout_warning = stdout.read()
            del stdout
            if warning in _stdout_warning:
                all_warnings.append(
                    warning + " for object {}".format(obj.name))
                auto_weight_problem = True
        # Reenable Auto weight for bones
        for b in no_auto_weight:
            bone = rig.data.bones.get(b)
            if bone:
                bone.use_deform = True
        return auto_weight_problem, all_warnings

    def _apply_smart_weighting(self, context, objects, rig, lm_obj, smooth_weights=True):
        '''Remove weights outside of the facial region (landmarks).'''
        # Create the facial hull object encompassing the facial geometry.
        bpy.ops.object.mode_set(mode='OBJECT')
        deform_groups = vertex_utils.get_deform_bones_from_armature(rig)
        for obj in objects:

            if any([grp in obj.vertex_groups for grp in deform_groups]):
                face_hull = bind_utils.create_facial_hull(context, lm_obj)
                bind_utils.select_vertices_outside_face_hull(obj, face_hull)
                bpy.data.objects.remove(face_hull)
            else:
                print(f"found no auto weights on object {obj.name}. Skipping smart weights")
                continue

            bpy_utils.clear_object_selection()
            rig.select_set(state=True)
            bpy_utils.set_active_object(obj.name)
            # Make Def-face the active vertex group before normalizing
            face_grp_idx = obj.vertex_groups.find("DEF-face")
            if face_grp_idx != -1:
                obj.vertex_groups.active_index = face_grp_idx
            use_mask = obj.data.use_paint_mask_vertex
            obj.data.use_paint_mask_vertex = False
            bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
            if smooth_weights:
                # ------------------------- SMOOTH BORDER WEIGHTS -------------------------------
                if face_grp_idx != -1:
                    bpy.ops.object.vertex_group_smooth(group_select_mode='ACTIVE',
                                                       factor=self.bind_data.main_smooth_factor,
                                                       repeat=self.bind_data.main_smooth_steps,
                                                       expand=self.bind_data.main_smooth_expand,
                                                       )
                obj.data.use_paint_mask_vertex = use_mask
            # ------------------------- NORMALIZE WEIGHTS -------------------------------
            # lock and normalize - so the facial influences get restricted
            if len(obj.vertex_groups) > 0 and face_grp_idx != -1:
                bpy.ops.object.vertex_group_normalize_all(lock_active=True)
            # bpy.ops.object.vertex_group_clean(group_select_mode='ALL')
            bpy.ops.object.mode_set()
    

    def _transfer_weights(self, transfer_from_objects, transfer_to_objects):
        if transfer_to_objects and transfer_from_objects:
            for from_obj in transfer_from_objects:
                bpy_utils.clear_object_selection()
                for obj in transfer_to_objects:
                    faceit_groups_per_obj = set(vertex_utils.get_faceit_vertex_grps(obj))
                    # get objects that were not bound and are registered in faceit objects
                    bind_utils.data_transfer_vertex_groups(obj_from=from_obj, obj_to=obj, method='NEAREST')
                    # remove all faceit groups that were transferred from the auto bind objects. These will messup re-binding.
                    for grp in set(vertex_utils.get_faceit_vertex_grps(obj)) - faceit_groups_per_obj:
                        false_assigned_faceit_group = obj.vertex_groups.get(grp)
                        obj.vertex_groups.remove(false_assigned_faceit_group)

    def overwrite_faceit_group(self, objects, faceit_vertex_group, new_grp=""):
        """
        bind user defined vertices to respective bones with constant weight of 1 on all vertices
        @objects - the bind objects
        @faceit_vertex_group - the user defined groups holding all vertices that should be assigned to new group
        @new_grp - the name of the new vertex group
        """
        # get all vertices in the faceit group
        objects_with_vgroup = vertex_utils.get_objects_with_vertex_group(
            faceit_vertex_group, objects=objects, get_all=True)
        for obj in objects_with_vgroup:
            vs = vertex_utils.get_verts_in_vgroup(obj, faceit_vertex_group)
            if not vs:
                continue
            vertex_utils.remove_all_weight(obj, vs)
            if new_grp:
                vertex_utils.assign_vertex_grp(obj, [v.index for v in vs], new_grp)
    
    def validate_data(self, context):
        facial_objects = setup_utils.get_faceit_objects_list(context)
        if not facial_objects:
            self.report({'ERROR'}, "No objects registered! Complete Setup")
            return False
        
        landmarks_obj = bpy_utils.get_object("facial_landmarks")
        if not landmarks_obj:
            self.report({'ERROR'}, "Landmarks not found!")
            return False
        
        rig = rig_utils.get_faceit_armature()
        if not rig:
            self.report({'ERROR'}, "Rig not found!")
            return False
        
        face_obj = landmarks_utils.get_main_faceit_object(context)
        if not face_obj:
            self.report({'ERROR'},"Please assign the Main group to the face before Binding.")
            return False
        return True