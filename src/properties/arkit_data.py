import bpy

from ..core.constants import base


class FACEBINDDEMO_PG_arkit_data(bpy.types.PropertyGroup):
    shapes_generated = bpy.props.BoolProperty(
        name='Generated Shape Keys',
        default=False,
    )