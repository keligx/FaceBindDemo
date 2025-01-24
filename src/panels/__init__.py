from ..utils import bpy_utils
from . import base_panel
from . import setup_panel
from . import landmarks_panel
from . import rig_panel

modules = [
        base_panel,
        setup_panel,
        landmarks_panel,
        rig_panel

    ]

def register():
    for module in modules:
        bpy_utils.register_classes_from_module(module)

def unregister():
    for module in modules:
        bpy_utils.unregister_classes_from_module(module)