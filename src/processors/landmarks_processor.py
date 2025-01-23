from ..utils import bpy_utils
from ..utils import setup_utils
from ..utils import landmarks_utils
from ..core.constants import base
from mathutils import Matrix, Vector
import bpy

class LandmarksProcessor:

    def unlock_3d_view(self, context):
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.region_3d.lock_rotation = False
    
    def check_is_quad_view(self, area):
        if area.spaces.active.region_quadviews is not None:
            return len(area.spaces.active.region_quadviews) != 0
    
    def get_eye_pivot_from_landmarks(self, context):
        '''Get the location of the eye pivot from the landmarks'''
        # place based on landmark positions
        # Asymmetric Landmarks:
        # ...
        landmarks_data = context.scene.facebinddemo_landmarks_data

        landmarks_obj = context.scene.objects.get('facial_landmarks')
        pos = Vector((0, 0, 0))
        if landmarks_obj:
            mw = landmarks_obj.matrix_world
            if landmarks_data.is_asymmetric:
                pass
            else:
                # Symmetric Landmarks:
                # Left Eye (mirror Right Eye):
                # between vertex 19 and 27 on the z axis
                # move to vertex 25 on the y axis
                v1 = mw @ landmarks_obj.data.vertices[19].co
                v2 = mw @ landmarks_obj.data.vertices[27].co
                v3 = mw @ landmarks_obj.data.vertices[25].co
                pos = (v1 + v2) / 2
                pos.y = v3.y
        return pos
    

