import bpy.utils.previews
from ..utils import bpy_utils
from . import arkit_data
from . import landmarks_data
from . import rig_data
from . import setup_data
from . import interface_data
from . import bind_data
import bpy


modules = [
        setup_data,
        interface_data,
        arkit_data,
        landmarks_data,
        rig_data,
        bind_data

    ]

def register():
    for module in modules:
        bpy_utils.register_classes_from_module(module)
    bpy.types.Scene.facebinddemo_setup_data = bpy.props.PointerProperty(type=setup_data.FACEBINDDEMO_PG_setup_data)
    bpy.types.Scene.facebinddemo_interface_data = bpy.props.PointerProperty(type=interface_data.FACEBINDDEMO_PG_interface_data)
    bpy.types.Scene.facebinddemo_arkit_data = bpy.props.PointerProperty(type=arkit_data.FACEBINDDEMO_PG_arkit_data)
    bpy.types.Scene.facebinddemo_landmarks_data = bpy.props.PointerProperty(type=landmarks_data.FACEBINDDEMO_PG_landmarks_data)
    bpy.types.Scene.facebinddemo_rig_data = bpy.props.PointerProperty(type=rig_data.FACEBINDDEMO_PG_rig_data)
    bpy.types.Scene.facebinddemo_bind_data = bpy.props.PointerProperty(type=bind_data.FACEBINDDEMO_PG_bind_data)
    
def unregister():
    for module in modules:
        bpy_utils.unregister_classes_from_module(module)
    del bpy.types.Scene.facebinddemo_setup_data
    del bpy.types.Scene.facebinddemo_interface_data
    del bpy.types.Scene.facebinddemo_arkit_data
    del bpy.types.Scene.facebinddemo_landmarks_data
    del bpy.types.Scene.facebinddemo_rig_data
    del bpy.types.Scene.facebinddemo_bind_data

