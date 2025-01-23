from .base_panel import Base_Panel
from ..core.constants import base
import bpy
from ..utils import bpy_utils
from ..processors.landmarks_processor import LandmarksProcessor
    
class FACEBINDDEMO_PT_landmarks(Base_Panel):
    bl_label = base.PT_LABEL_LANDMARKS
    bl_idname = base.PT_ID_LANDMARKS
    bl_options = set()

    @classmethod
    def poll(self, context):
        return context.scene.facebinddemo_interface_data.active_tab == base.PT_LABEL_LANDMARKS


    def draw(self, context):
        self.processor = LandmarksProcessor()
        layout = self.layout
        landmarks_data = context.scene.facebinddemo_landmarks_data
        lm_obj = bpy_utils.get_object('facial_landmarks')
        adaption_state = 0
        col = layout.column(align=True)
        # landmarks setup
        text = 'Generate Landmarks'
        if lm_obj:
            adaption_state = 1
            adaption_state += lm_obj["state"]
            if adaption_state:
                if adaption_state == 1:
                    text = 'Align to Chin'
                elif adaption_state == 11:
                    text = 'Align Rotation'
                elif adaption_state == 2:
                    text = 'Match Face Height'
                elif adaption_state == 3:
                    text = 'Match Face Width'
        if adaption_state == 0:
            row = col.row()
            row.prop(landmarks_data, 'is_asymmetric', text='Asymmetry', icon='MOD_MIRROR')
        if adaption_state in (0, 1, 11, 2, 3):
            row = col.row()
            row.operator(base.OT_ID_SET_LANDMARKS, text=text, icon='TRACKER')
        
                
        if adaption_state == 4:
            row = col.row()
            row.label(text='Return')
            row = col.row(align=True)
            row.operator('faceit.reset_facial_landmarks', icon='BACK')
            col.label(text='Landmarks')
            col.operator(base.OT_ID_PROJECT_LANDMARKS, icon='CHECKMARK')
        elif adaption_state == 5:
            row = col.row()
            row.label(text='Return')
            row = col.row(align=True)
            row.operator('faceit.reset_facial_landmarks', icon='BACK')
            row = col.row(align=True)
            row.operator(base.OT_ID_EDIT_LANDMARKS, icon='EDITMODE_HLT')
            row.operator(base.OT_ID_FINISH_EDIT_LANDMARKS, text='', icon='CHECKMARK')    