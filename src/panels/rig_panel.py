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

        col = layout.column(align=True)
        row = col.row()
        row.label(text='Generate')
        row = col.row()
        col.operator(base.OT_ID_GENERATE_RIG, text='Generate Rig', icon='ARMATURE_DATA')
        row = col.row()
        row.label(text='Bind')
        row = col.row()
        col.operator(base.OT_ID_SMART_BIND, text='Bind', icon='OUTLINER_OB_ARMATURE')
