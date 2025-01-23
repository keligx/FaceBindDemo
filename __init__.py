"""Copyright (C) 2024 LIANHENG TECH CO.,LTD."""
from .src.utils import bpy_utils
from .src import panels
from .src import properties
from .src import operators

bl_info = {
    "name": "FACEBINDDEMO",
    "author": "LIANHENG TECH CO., LTD.",
    "description": "AI Tools for Blender",
    "blender": (4, 2, 0),
    "version": (1, 0, 0),
    "location": "3D View > Properties> FaceBindDemo",
    "doc_url": "https://www.mornday.com/index.php/document/",
    "tracker_url": "",
    "support": "COMMUNITY",
    "warning": "",
    "category": "AI"
}

def register():
    properties.register()
    operators.register()
    panels.register()

def unregister():    
    panels.unregister()
    operators.unregister()
    properties.unregister()

if __name__ == "__main__":
    register()