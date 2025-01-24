import bpy
from ..utils import rig_utils
from ..utils import setup_utils
from ..utils import vertex_utils
from ..core.constants import base
from ..processors.pivots_processor import PivotManager

def armature_poll(self, obj):
    '''Return True if the object is a valid faceit rig (armature).'''
    if obj.type == 'ARMATURE' and obj.name in self.objects:
        return True


def update_armature(self, context):
    if self.lh_armature is not None:
        self.lh_armature_missing = False
        rig_type = rig_utils.get_rig_type(self.lh_armature)
        self.faceit_armature_type = rig_type
        rig = self.lh_armature
        if not self.lh_control_bones:
            # Populate the control bones list
            ctrl_bone_names = []
            if rig_type in ('RIGIFY', 'RIGIFY_NEW'):
                # ctrl_bone_names = FACEIT_CTRL_BONES
                # Even better would be to get the control bones from the collection / layers
                # The faceit rig should be adapted to match the rigify layers / collections
                # Get the first three layers
                if bpy.app.version < (4, 0, 0):
                    ctrl_bone_names = [b.name for b in rig.data.bones if any(b.layers[:3])]
                else:
                    colls = rig.data.collections[:3]
                    for b in rig.data.bones:
                        if any(coll in colls for coll in b.collections):
                            ctrl_bone_names.append(b.name)
                # elif rig_type == 'RIGIFY_NEW':
                #     ctrl_bone_names = FACEIT_CTRL_BONES
            else:
                # ANY type needs to be populated manually
                pass
            for b in rig.data.bones:
                if b.name in ctrl_bone_names:
                    ctrl_bone = self.lh_control_bones.add()
                    ctrl_bone.name = b.name


def body_armature_poll(self, obj):
    '''Return True if the object is a valid body rig (armature).'''
    if obj.type == 'ARMATURE' and obj.name in self.objects:
        if not rig_utils.is_faceit_original_armature(obj):
            return True


def update_body_armature(self, context):
    rig = self.lh_body_armature
    self.lh_use_existing_armature = False
    if rig is None:
        return
    if rig_utils.get_rig_type(rig) in ('RIGIFY', 'RIGIFY_NEW'):
        self.lh_use_existing_armature = True
    # try to find head bone name
    for b in rig.data.bones:
        if b.use_deform:
            b_name = b.name.lower()
            if "head" in b_name:
                self.lh_body_armature_head_bone = b.name
                break


def update_use_existing_armature(self, context):
    setup_data = context.scene.facebinddemo_setup_data
    if self.lh_use_existing_armature:
        if not self.lh_armature:
            self.lh_armature = self.lh_body_armature
        self.show_warnings = False
        objects = setup_utils.get_faceit_objects_list(context)
        # clear bake modifiers
        for obj_item in context.scene.face_objects:
            obj_item.modifiers.clear()
        rig_utils.populate_bake_modifier_items(setup_data, objects)
    else:
        if self.lh_armature == self.lh_body_armature:
            self.lh_armature = None


def update_eye_bone_pivots(self, context):
    rig = self.pivot_ref_armature
    if not rig:
        return
    # Find the eye bones
    left_eye_bones = []
    right_eye_bones = []
    for b in rig.data.bones:
        if not b.use_deform:
            continue
        b_name = b.name.lower()
        if "eye" in b_name:
            if "left" in b_name or b_name.endswith("_l") or b_name.endswith(".l") or "_l_" in b_name:
                left_eye_bones.append(b.name)
            elif "right" in b_name or b_name.endswith("_r") or b_name.endswith(".r") or "_r_" in b_name:
                right_eye_bones.append(b.name)
    if left_eye_bones and right_eye_bones:
        self.eye_pivot_bone_L = min(left_eye_bones, key=len)
        self.eye_pivot_bone_R = min(right_eye_bones, key=len)
        update_eye_pivot_from_bone(self, context)


def update_eye_pivot_from_bone(self, context):
    if self.eye_pivot_bone_L:
        self.eye_pivot_point_L = vertex_utils.copy_pivot_from_bone(
            self.pivot_ref_armature, self.eye_pivot_bone_L)
    else:
        self.eye_pivot_point_L = vertex_utils.get_eye_pivot_from_landmarks(context)
    if self.eye_pivot_bone_R:
        self.eye_pivot_point_R = vertex_utils.copy_pivot_from_bone(
            self.pivot_ref_armature, self.eye_pivot_bone_R)
    else:
        self.eye_pivot_point_R = vertex_utils.get_eye_pivot_from_landmarks(context)


def update_eye_pivot_options(self, context):
    pass


def update_pivot_geo_type(self, context):
    if self.eye_geometry_type == 'SPHERE':
        update_right_pivot_from_vertex_group(self, context)
        update_left_pivot_from_vertex_group(self, context)
    else:
        if not self.pivot_ref_armature:
            self.pivot_ref_armature = self.lh_body_armature
        update_eye_pivot_from_bone(self, context)


def update_left_pivot_from_vertex_group(self, context):
    if self.eye_pivot_group_L:
        self.eye_pivot_point_L = PivotManager.get_eye_pivot_from_vertex_group(
            context,
            vgroup_name=self.eye_pivot_group_L)


def update_right_pivot_from_vertex_group(self, context):
    if self.eye_pivot_group_R:
        self.eye_pivot_point_R = PivotManager.get_eye_pivot_from_vertex_group(
            context,
            vgroup_name=self.eye_pivot_group_R)


def update_pivot_placement_method(self, context):
    if self.eye_pivot_placement == 'AUTO':
        if self.eye_geometry_type == 'SPHERE':
            update_right_pivot_from_vertex_group(self, context)
            update_left_pivot_from_vertex_group(self, context)
        else:
            update_eye_pivot_from_bone(self, context)
    # if self.eye_pivot_placement == 'MANUAL':


def update_draw_pivots(self, context):
    if self.draw_pivot_locators:
        PivotManager.start_drawing(context)


def get_enum_vgroups(self, context):
    global vg_items
    vg_items = []
    vgroups = vertex_utils.get_vertex_groups_from_objects()
    # for a in get_all_shape_key_actions():
    for vg in vgroups:
        vg_items.append((vg,) * 3)

    if not vg_items:
        vg_items.append(("None", "None", "None"))

    return vg_items


class FACEBINDDEMO_PG_bones(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Bone Name")


class FACEBINDDEMO_PG_rig_data(bpy.types.PropertyGroup):
    lh_armature: bpy.props.PointerProperty(
        name='Faceit Armature',
        description='The armature to be used in the binding and baking operators. Needs to be a Rigify layout.',
        type=bpy.types.Object,
        poll=armature_poll,
        update=update_armature,
    )
    lh_armature_type: bpy.props.EnumProperty(
        name='Armature Type',
        items=(
            ('RIGIFY', 'Rigify', 'The armature is a Rigify face rig.'),
            ('RIGIFY_NEW', 'Rigify New', 'The armature is a Rigify face rig (3.6+).'),
            ('ANY', 'Any', 'The armature is a custom rig or currently not supported.'),
        ),
        default='RIGIFY',
    )
    lh_control_bones: bpy.props.CollectionProperty(
        name='Pose Bones',
        type=FACEBINDDEMO_PG_bones,
    )
    lh_armature_missing: bpy.props.BoolProperty(
        name='Missing Armature',
        description='The armature is missing. Did you remove it intentionally?',
    )
    lh_body_armature: bpy.props.PointerProperty(
        name='Existing Rig',
        type=bpy.types.Object,
        poll=body_armature_poll,
        update=update_body_armature
    )
    lh_body_armature_head_bone: bpy.props.StringProperty(
        name='Bone',
        default='',
    )
    lh_use_existing_armature: bpy.props.BoolProperty(
        name='Use Existing Face Rig', default=False,
        description='Use the existing face rig of your character to create the facial expressions. Premade expression packs are only available for Rigify face rigs.',
        update=update_use_existing_armature)
    lh_pivot_manager_initialized: bpy.props.BoolProperty(
        name='Pivot Manager Initialized',
        default=False,
    )
    eye_pivot_placement: bpy.props.EnumProperty(
        name='Eye Pivot Placement Method',
        items=[('AUTO', 'Auto Find',
                'The pivot locator will be placed automatically, based on assigned vertex groups or existing eye bones.'),
               ('MANUAL', 'Manual', 'The pivot locator will be placed manually, using empties.'), ],
        default='AUTO', update=update_pivot_placement_method,)
    eye_geometry_type: bpy.props.EnumProperty(
        name='Geometry Type',
        items=[
            ('SPHERE', 'Spherical', 'The eye geometry is a  sphere or half sphere.'),
            ('FLAT', 'Flat', 'The eye geometry is flat. Typical in anime characters.'),
        ],
        default=0,
        update=update_pivot_geo_type,
    )
    pivot_vertex_auto_snap: bpy.props.BoolProperty(
        name='Auto Snap',
        default=True,
        description='When enabled, the snap settings will be disabled automatically when selecting the pivot vertex and re-enabled upon selecting other vertices. Currently this setting does not respect user preferences.',
    )
    draw_pivot_locators: bpy.props.BoolProperty(
        name='Draw Pivot Locators',
        default=True,
        description='Draw the pivot locators in the viewport.',
        update=update_draw_pivots
    )
    pivot_ref_armature: bpy.props.PointerProperty(
        name='Pivot Reference Armature',
        type=bpy.types.Object,
        poll=armature_poll,
        update=update_eye_bone_pivots
    )
    eye_pivot_group_L: bpy.props.StringProperty(
        name='Left Eye Geometry',
        update=update_left_pivot_from_vertex_group
    )
    eye_pivot_group_R: bpy.props.StringProperty(
        name='Left Eye Geometry',
        update=update_right_pivot_from_vertex_group
    )
    eye_pivot_point_L: bpy.props.FloatVectorProperty(
        name='Eye Pivot Point Left',
        default=(0, 0, 0),
        subtype='XYZ',
        size=3,
        update=update_eye_pivot_options,
    )
    eye_pivot_point_R: bpy.props.FloatVectorProperty(
        name='Eye Pivot Point Right',
        default=(0, 0, 0),
        subtype='XYZ',
        size=3,
        update=update_eye_pivot_options,
    )
    eye_manual_pivot_point_L: bpy.props.FloatVectorProperty(
        name='Eye Pivot Point Left',
        default=(0, 0, 0),
        subtype='XYZ',
        size=3,
        update=update_eye_pivot_options,
    )
    eye_manual_pivot_point_R: bpy.props.FloatVectorProperty(
        name='Eye Pivot Point Right',
        default=(0, 0, 0),
        subtype='XYZ',
        size=3,
        update=update_eye_pivot_options,
    )
    eye_pivot_bone_L: bpy.props.StringProperty(
        name="Left Eye Bone",
        description="The left eye bone of the anime character.",
        default="",
        update=update_eye_pivot_from_bone,
    )
    eye_pivot_bone_R: bpy.props.StringProperty(
        name="Right Eye Bone",
        description="The right eye bone of the anime character.",
        default="",
        update=update_eye_pivot_from_bone,
    )
    jaw_pivot: bpy.props.FloatVectorProperty(
        name='Jaw Pivot',
        default=(0, 0, 0),
        subtype='XYZ',
        size=3,
    )
    use_jaw_pivot: bpy.props.BoolProperty(
        name='Use Jaw Pivot',
        default=False,
    )
    miss_armature: bpy.props.BoolProperty(
        name='Missing Armature',
        description='The armature is missing. Did you remove it intentionally?',
    )
    weights_restorable: bpy.props.BoolProperty(
        default=False,
    )
    expressions_restorable: bpy.props.BoolProperty(
        default=False,
    )
    corrective_sk_restorable: bpy.props.BoolProperty(
        default=False,
    )

