import bpy

from ..core.constants import base
from bpy.props import EnumProperty, FloatProperty


class FACEBINDDEMO_PG_interface_data(bpy.types.PropertyGroup):
    active_tab: EnumProperty(
        name="Select Work Tab",
        description="Select Work Tab",
        items=(
            (base.PT_LABEL_SETUP, base.PT_LABEL_SETUP, ""),
            (base.PT_LABEL_LANDMARKS, base.PT_LABEL_LANDMARKS, ""),
            (base.PT_LABEL_RIG, base.PT_LABEL_RIG, "")
        )
    )
