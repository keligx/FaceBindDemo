import bpy

from ..core.constants import base

class FACEBINDDEMO_PG_landmarks_data(bpy.types.PropertyGroup):
    is_asymmetric: bpy.props.BoolProperty(
        name='Symmetry or no symmetry',
        description='Enable this if the Character Geometry is not symmetrical in X Axis. \
                    Use the manual Mirror tools instead of the Mirror modifier',
        default=False,
    )
