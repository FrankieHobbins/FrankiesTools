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

classes = (
    main.ViewportSetup,
    main.SetOriginInEditMode,
    main.ToggleEditMode,
    main.ToggleWeightMode,
    main.ToggleAllCollections,
    main.IsolateCollections,
    main.DeleteKeyFrame,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
