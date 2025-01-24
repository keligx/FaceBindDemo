import bpy

from ..core.constants import base



class FACEBINDDEMO_PG_bind_data(bpy.types.PropertyGroup):   

    show_advanced_settings: bpy.props.BoolProperty(
            name="Show Advanced Options",
            default=False,
        )
    bind_scale_objects: bpy.props.BoolProperty(
        name="Scale Geometry",
        description="Temporarilly scales the geometry for Binding. Use if Auto Weights fails.",
        default=True
    )
    bind_scale_factor: bpy.props.IntProperty(
        name="Scale Factor",
        description="Factor to scale by. Tweak this if your binding fails",
        default=100,
        max=1000,
        min=1,
    )
    smart_weights: bpy.props.BoolProperty(
        name="Smart Weights",
        description="Improves weights for most characters, by detecting rigid skull/body vertices and assigning them to DEF-face group",
        default=True)
    smooth_main_edges: bpy.props.BoolProperty(
        name="Smooth Main borders/edge",
        description="Ensures a smooth transition between face and body/rigid geometry.",
        default=True
    )
    main_smooth_factor: bpy.props.FloatProperty(
        name="Smooth Factor",
        description="Factor to smooth by.",
        default=0.5,
        min=0.0,
        max=1.0,
    )
    main_smooth_steps: bpy.props.IntProperty(
        name="Smooth Steps",
        description="Number of smoothing steps (Iterations).",
        default=10,
        min=1,
        max=10000
    )
    main_smooth_expand: bpy.props.FloatProperty(
        name="Smooth Expand",
        description="Expand/contract weights during smoothing",
        default=0.1,
        min=-1.0,
        max=1.0,
    )
    weight_eyes: bpy.props.BoolProperty(
        name="Eyes",
        description="Overwrite Faceit Vertex Groups with specific bone weights (Eyes)",
        default=True
    )
    weight_teeth: bpy.props.BoolProperty(
        name="Teeth",
        description="Overwrite Faceit Vertex Groups with specific bone weights (Teeth)",
        default=True
    )
    weight_tongue: bpy.props.BoolProperty(
        name="Tongue",
        description="Auto weight the tongue geometry separately.",
        default=True
    )
    weight_secondary_method: bpy.props.EnumProperty(
        name="Weight Secondary Method",
        items=(
            ('AUTO', "Auto", "Automatically assign weights to all secondary objects"),
            ('TRANSFER', "Transfer", "Transfer the weights from the main object to the secondary objects"),
        )
    )
    transfer_weights: bpy.props.BoolProperty(
        name="Transfer Weights",
        description="Transfer the Main Weights to hair/secondary Geometry",
        default=True
    )
    tranfer_to_hair_only: bpy.props.BoolProperty(
        name="Transfer to Hair Only",
        description="Automatically find hair geometry. All geometry that is not assigned to Faceit vertex groups.",
        default=False,
    )
    clean_eyelashes_weights: bpy.props.BoolProperty(
        name="Clean Eyelashes Weights",
        description="Remove all non-lid deform groups from the eyelashes gemometry. Only available if the eyelashes have been defined in setup.",
        default=True,)
    remove_rigid_weights: bpy.props.BoolProperty(
        name="Clear Rigid Geometry",
        description="Removes all weights from geometry assigned to the faceit_rigid group.",
        default=True
    )
    keep_split_objects: bpy.props.BoolProperty(
        name="Keep Split Objects",
        description="Keep the Split objects for inspection. This can be useful when binding fails.",
        default=False
    )
    smooth_bind: bpy.props.BoolProperty(
        name="Apply Smoothing",
        description="Applies automatic weight-smoothing after binding. Affects all deform bones.",
        default=True
    )
    smooth_factor: bpy.props.FloatProperty(
        name="Smooth Factor",
        description="Factor to smooth by.",
        default=0.5,
        min=0.0,
        max=1.0,
    )
    smooth_steps: bpy.props.IntProperty(
        name="Smooth Steps",
        description="Number of smoothing steps (Iterations).",
        default=1,
        min=1,
        max=10000
    )
    smooth_expand: bpy.props.FloatProperty(
        name="Smooth Expand",
        description="Expand/contract weights during smoothing",
        default=0.0,
        min=-1.0,
        max=1.0,
    )
    smooth_expand_eyelashes: bpy.props.BoolProperty(
        name="Smooth Expand Eyelashes",
        description="Smooth the eyelashes in an extra pass.",
        default=True,
    )
    eyelashes_smooth_factor: bpy.props.FloatProperty(
        name="Smooth Factor",
        description="Factor to smooth by.",
        default=0.5,
        min=0.0,
        max=1.0,
    )
    eyelashes_smooth_steps: bpy.props.IntProperty(
        name="Smooth Steps",
        description="Number of smoothing steps (Iterations).",
        default=2,
        min=1,
        max=10000
    )
    eyelashes_smooth_expand: bpy.props.FloatProperty(
        name="Smooth Expand",
        description="Expand/contract weights during smoothing",
        default=1.0,
        min=-1.0,
        max=1.0,
    )
    remove_old_faceit_weights: bpy.props.BoolProperty(
        name="Remove Old Faceit Weights",
        description="Removes all weights associated with the FaceitRig before rebinding.",
        default=True
    )
    make_single_user: bpy.props.BoolProperty(
        name="Make Single User",
        description="Makes single user copy before binding. Otherwise Binding will likely fail.",
        default=True
    )