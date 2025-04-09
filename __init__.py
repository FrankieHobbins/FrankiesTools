from . import main
import importlib
import bpy

bl_info = {
    "name": "Frankies Tools",
    "description": "Misc tools",
    "author": "Frankie Hobbins",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "category": "Misc"
}

if "main" in locals():
    importlib.reload(main)

extra_classes = (
    main.FCV_VisibilityState,
    main.FTOOLS_PT_VisibilityPanel,
)

core_classes = (
    main.CollectionVisibility,
    main.ViewportSetup,
    main.SetOriginInEditMode,
    main.SetOriginInEditModeActive,
    main.SetCursor,
    main.ToggleEditMode,
    main.ToggleWeightMode,
    main.DeleteKeyFrame,
    main.ModifierSync,
    main.SetSmoothing,
    main.CopyParents,
    main.RemoveUvFromSelected,
    main.BadFcurves
)

register_core, unregister_core = bpy.utils.register_classes_factory(core_classes + extra_classes)

def register():
    register_core()

    bpy.types.Scene.fcv_use_exclude = bpy.props.BoolProperty(
        name="Use Exclude",
        description="Use View Layer Exclude instead of Hide Viewport",
        default=True
    )
    bpy.types.Scene.fcv_reveal_active = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.fcv_hide_active = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.fcv_isolate_active = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.fcv_previous = None
    bpy.types.Scene.fcv_reveal_vlc_list = bpy.props.CollectionProperty(type=main.FCV_VisibilityState)
    bpy.types.Scene.fcv_hide_vlc_list = bpy.props.CollectionProperty(type=main.FCV_VisibilityState)
    bpy.types.Scene.fcv_isolate_vlc_list = bpy.props.CollectionProperty(type=main.FCV_VisibilityState)

def unregister():
    unregister_core()

    del bpy.types.Scene.fcv_use_exclude
    del bpy.types.Scene.fcv_reveal_active
    del bpy.types.Scene.fcv_hide_active
    del bpy.types.Scene.fcv_isolate_active
    del bpy.types.Scene.fcv_previous
    del bpy.types.Scene.fcv_reveal_vlc_list
    del bpy.types.Scene.fcv_hide_vlc_list
    del bpy.types.Scene.fcv_isolate_vlc_list

if __name__ == "__main__":
    register()
