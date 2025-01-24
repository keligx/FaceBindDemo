from ..utils import bpy_utils
from . import arkit_operator
from . import landmarks_operator
from . import rig_operator
from . import setup_operator
from . import bind_operator

modules = [
        arkit_operator,
        landmarks_operator,
        rig_operator,
        setup_operator,
        bind_operator

    ]

def register():
    for module in modules:
        bpy_utils.register_classes_from_module(module)

def unregister():
    for module in modules:
        bpy_utils.unregister_classes_from_module(module)