from .base_panel import Base_Panel
from ..core.constants import base
import bpy
from ..utils import setup_utils
from ..utils import rig_utils
from ..utils import bpy_utils
from ..utils import landmarks_utils

class FACEBINDDEMO_PT_Rig(Base_Panel):
    bl_label = base.PT_LABEL_RIG
    bl_options = set()
    bl_idname = base.PT_ID_RIG

    landmarks_predecessor = base.PT_ID_LANDMARKS

    @classmethod
    def poll(cls, context):
        return context.scene.facebinddemo_interface_data.active_tab == base.PT_LABEL_RIG

    def draw(self, context):
        layout = self.layout
        arkit_data = context.scene.facebinddemo_arkit_data
        rig_data = context.scene.facebinddemo_rig_data

        if arkit_data.shapes_generated:
            col_reset = layout.column(align=True)
            row = col_reset.row()
            row.operator('faceit.back_to_rigging', icon='BACK')
            col_reset.separator(factor=2)
        col = layout.column(align=True)
        col.enabled = not arkit_data.shapes_generated or rig_data.miss_armature

        if rig_utils.get_faceit_armature(force_original=True):

            row = col.row()
            row.label(text='Return')
            row = col.row(align=True)
            row.operator('faceit.reset_to_landmarks', icon='BACK')
            row = col.row()
            row.label(text='Bind')
            row = col.row(align=True)
            row.operator('faceit.smart_bind', text='Bind', icon='OUTLINER_OB_ARMATURE')

        else:
            row = col.row()
            row.label(text='Generate')
            row = col.row()
            col.operator('faceit.generate_rig', text='Generate Rig', icon='ARMATURE_DATA')
