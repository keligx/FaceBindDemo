import os
import pathlib
import addon_utils
from ..core.constants import base

def get_addon_dir():
    return pathlib.Path(os.path.dirname(__file__)).parent.resolve()

def get_addon_directory(addon_name):
    for module in addon_utils.modules():
        if module.bl_info.get(base.NAME) == addon_name:
            return os.path.dirname(module.__file__)
        
def get_landmarks_file():
    addon_dir = get_addon_directory(base.ADDON_NAME)
    return addon_dir + "/assets/Landmarks.blend"
