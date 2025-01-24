import bpy
from ..utils import bpy_utils
from ..utils import setup_utils
from ..utils import rig_utils
from ..utils import vertex_utils

class SetupProcessor:

    def select_facial_part(self,object_name, clear_current_selection=True, shift_pressed=False, ctrl_pressed=False):
        if shift_pressed or ctrl_pressed:
            clear_current_selection = False  
        if clear_current_selection:
            bpy_utils.clear_object_selection()
        if object_name in bpy.context.scene.objects:
            bpy_utils.set_active_object_by_name(object_name)

        return {'FINISHED'}
    
    def remove_faceit_vertex_grps(self,obj):
        if len(obj.vertex_groups) <= 0:
            return
        removed = []
        for grp in obj.vertex_groups:
            if 'faceit' in grp.name:
                removed.append(grp.name)
                obj.vertex_groups.remove(grp)
        return removed
    
    
    def processor_add_object(self, context):
        setup_data = context.scene.facebinddemo_setup_data
        rig_data = context.scene.facebinddemo_rig_data
        
        setup_utils.add_context_object(context, setup_data)
        rig_utils.rig_counter(context, rig_data, setup_data)
        
    def assign_object_groups(self, obj, setup_data, layout):
        faceit_groups = vertex_utils.get_faceit_vertex_grps(obj)
        if faceit_groups:
            layout.label(text='Faceit Vertex Groups')
            box = layout.box()
            col = box.column()
            index = setup_data.face_objects.find(self.obj_name)
            for fgroup in faceit_groups:
                row = col.row(align=True)
                op = row.operator('faceit.remove_faceit_group_list', text='', icon='X')
                op.vgroup_name = fgroup
                op.object_list_index = index
                op = row.operator('faceit.select_faceit_groups', text='', icon='EDITMODE_HLT')
                op.faceit_vertex_group_name = fgroup
                op.object_list_index = index
                row.label(text=fgroup)

    def update_object_counter(setup_data):
        obj_count = len(setup_data.face_objects)

        if setup_data.face_index >= obj_count:
            setup_data.face_index = obj_count - 1


    
class GeometryIslands:
    """
    Traces the graph of edges and verts to find the islands
    @verts : bmesh vertices
    @islands : list of connected vertex islands, i.e. surfaces
    """

    verts = []
    islands = []
    # wether selected or non selected islands should be searched

    def __init__(self, bmesh_verts):
        self.verts = bmesh_verts
        self.islands = self.make_islands(self.verts)

    def make_vert_paths(self, verts):
        # Init a set for each vertex
        result = {v: set() for v in verts}
        # Loop over vertices to store connected other vertices
        for v in verts:
            for e in v.link_edges:
                other = e.other_vert(v)
                result[v].add(other)
        return result

    def make_island(self, starting_vert, paths):
        # Initialize the island
        island = [starting_vert]
        # Initialize the current vertices to explore
        current = [starting_vert]
        follow = True
        while follow:
            # Get connected vertices that are still in the paths
            eligible = set([v for v in current if v in paths])
            if len(eligible) == 0:
                follow = False  # Stops if no more
            else:
                # Get the corresponding links
                next = [paths[i] for i in eligible]
                # Remove the previous from the paths
                for key in eligible:
                    island.append(key)
                    paths.pop(key)
                # Get the new links as new inputs
                current = set([vert for sub in next for vert in sub])
        return island

    def make_islands(self, bm_verts):
        paths = self.make_vert_paths(bm_verts)
        result = []
        found = True
        while found:
            try:
                # Get one input as long there is one
                vert = next(iter(paths.keys()))
                # Deplete the paths dictionary following this starting vertex
                result.append(self.make_island(vert, paths))
            except StopIteration:
                found = False
        return result

    def get_islands(self):
        return self.islands

    def get_island_count(self):
        return len(self.islands)

    def get_island_by_vertex_index(self, index):
        for island in self.islands:
            if any(v.index == index for v in island):
                return island
        # return next((x for x in self.islands if any(index == v.index for v in x)), None)

    def get_selected_islands(self):
        for island in self.islands:
            if any(v.select for v in island):
                yield island

    def select_linked(self):
        ''' Select all linked vertices for surfaces that have a partial selection'''
        for island in self.get_selected_islands():
            for v in island:
                v.select = True

class SelectionIslands(GeometryIslands):
    '''
    Traces the graph of edges and verts to find the islands
    @verts : bmesh vertices
    @selection_islands : the islands of adjacent selected vertices
    @non_selected_islands : the islands of adjacent non selected vertices
    '''

    def __init__(self, bmesh_verts, selection_state):
        self.verts = [v for v in bmesh_verts if v.select == selection_state]
        self.islands = self.make_islands(self.verts, selection_state)

    def make_vert_paths(self, verts, selection_state):
        # Init a set for each vertex
        result = {v: set() for v in verts}
        # Loop over vertices to store connected other vertices
        for v in verts:
            for e in v.link_edges:
                other = e.other_vert(v)
                if other.select == selection_state:
                    result[v].add(other)
        return result

    def make_islands(self, bm_verts, selection_state):
        paths = self.make_vert_paths(bm_verts, selection_state)
        result = []
        found = True
        while found:
            try:
                # Get one input as long there is one
                vert = next(iter(paths.keys()))
                # Deplete the paths dictionary following this starting vertex
                result.append(self.make_island(vert, paths))
            except StopIteration:
                found = False
        return result