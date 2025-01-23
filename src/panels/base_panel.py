import bpy
from ..core.constants import base as base


class Base_Panel(bpy.types.Panel):
    bl_space_type = base.VIEW_3D
    bl_region_type = base.UI
    bl_category = base.ADDON_NAME
    bl_options = {"HEADER_LAYOUT_EXPAND"}

    def draw(self, context):
        pass

class FACEBINDDEMO_PT_interface(Base_Panel):
    bl_label = base.PT_LABEL_INTERFACE
    bl_idname = base.PT_ID_INTERFACE
    bl_options = {"HEADER_LAYOUT_EXPAND"}

    def draw(self, context):
        layout = self.layout

        interface_data = context.scene.facebinddemo_interface_data
        layout.row().prop(interface_data, "active_tab", expand=True)