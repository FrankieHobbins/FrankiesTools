import bpy


class ViewportSetup(bpy.types.Operator):
    bl_label = "F Viewport Setup"
    bl_idname = "frankiestools.f_viewport_setup"
    bl_description = "sets the viewport just how I like it"

    clip_start: bpy.props.FloatProperty(
        name='min clip value',
        default=0.01
    )

    clip_end: bpy.props.FloatProperty(
        name='max clip value',
        default=1000
    )

    def execute(self, context):
        print("setting viewport")
        bpy.context.space_data.clip_start = self.clip_start
        bpy.context.space_data.clip_end = self.clip_end
        bpy.context.space_data.show_gizmo = True
        bpy.context.space_data.show_gizmo_navigate = False
        bpy.context.space_data.show_gizmo_tool = False
        bpy.context.space_data.show_gizmo_context = True
        bpy.context.space_data.show_gizmo_object_translate = True
        bpy.ops.wm.tool_set_by_id(name="builtin.select_lasso")
        bpy.ops.wm.tool_set_by_id(name="builtin.cursor")
        bpy.context.space_data.shading.show_backface_culling = True
        return {"FINISHED"}


class SetOriginInEditMode(bpy.types.Operator):
    bl_label = "F et Origin"
    bl_idname = "frankiestools.f_set_origin"
    bl_description = "sets origin even if in edit mode"

    def execute(self, context):
        ao = bpy.context.active_object
        if ao:
            mode = ao.mode
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='BOUNDS')
            bpy.ops.object.mode_set(mode=mode)
        return {"FINISHED"}


class ToggleEditMode(bpy.types.Operator):
    bl_label = "F Toggle Edit Mode"
    bl_idname = "frankiestools.f_editmode"
    bl_description = "toggle object and edit mode"

    def execute(self, context):
        ao = bpy.context.active_object
        mode = ao.mode
        if ao:
            if mode == "OBJECT":
                bpy.ops.object.mode_set(mode="EDIT")
            elif mode == "EDIT":
                bpy.ops.object.mode_set(mode="OBJECT")
            else:
                bpy.ops.object.mode_set(mode="EDIT")
        return {"FINISHED"}


class DeleteKeyFrame(bpy.types.Operator):
    bl_label = "F Delete Keyframe"
    bl_idname = "frankiestools.f_delete_keyframe"
    bl_description = "delete keyframe and update motion path"

    def execute(self, context):
        last_frame = bpy.context.scene.frame_end

        bpy.ops.anim.keyframe_delete()
        bpy.ops.pose.paths_calculate(start_frame=0, end_frame=last_frame, bake_location='HEADS')       
        return {"FINISHED"}


class ToggleWeightMode(bpy.types.Operator):
    bl_label = "F Toggle Weight Mode"
    bl_idname = "frankiestools.f_weightmode"
    bl_description = "toggle object and weight paint or pose"

    def execute(self, context):
        ao = bpy.context.active_object
        mode = ao.mode
        if ao:
            if ao.type == "ARMATURE":
                if mode == "OBJECT":
                    bpy.ops.object.mode_set(mode="POSE")
                elif mode == "POSE":
                    bpy.ops.object.mode_set(mode="OBJECT")
                else:
                    bpy.ops.object.mode_set(mode="POSE")
            else:
                if mode == "OBJECT":
                    bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
                elif mode == "WEIGHT_PAINT":
                    bpy.ops.object.mode_set(mode="OBJECT")
                else:
                    bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
        return {"FINISHED"}


class ToggleAllCollections(bpy.types.Operator):
    bl_label = "F Toggle All Collections Visibility"
    bl_idname = "frankiestools.f_toggleallcollections"
    bl_description = "turn all collection visibility on"

    bpy.types.Scene.previously_active_collections_A = []
    bpy.types.Scene.previously_active_collections_B = []
    bpy.types.Scene.collections_all_visible = False

    def execute(self, context):
        ToggleAllCollections.toggle_hide(bpy.context.view_layer.layer_collection, bpy.types.Scene.collections_all_visible)
        return {"FINISHED"}

    def toggle_hide(view_layer, hide):
        if hide:
            for i in bpy.types.Scene.previously_active_collections_A:
                i[0].hide_viewport = i[1]
            for i in bpy.types.Scene.previously_active_collections_B:
                i[0].hide_viewport = i[2]
            bpy.types.Scene.collections_all_visible = False
            bpy.types.Scene.previously_active_collections_A = []
            bpy.types.Scene.previously_active_collections_B = []

        else:
            for i in view_layer.collection.children:                
                bpy.types.Scene.previously_active_collections_A.append([i, i.hide_viewport])
                i.hide_viewport = False
            for i in view_layer.children:
                bpy.types.Scene.previously_active_collections_B.append([i, i.exclude, i.hide_viewport])
                i.hide_viewport = False
                if i.children:
                    ToggleAllCollections.toggle_hide(i, False)
            bpy.types.Scene.collections_all_visible = True

class IsolateCollections(bpy.types.Operator):
    bl_label = "F Isolate Collections Visibility"
    bl_idname = "frankiestools.f_isolatecollections"
    bl_description = "isolate collection"

    bpy.types.Scene.previously_active_collections_C = []
    bpy.types.Scene.previously_active_collections_D = []
    bpy.types.Scene.collections_isolated = False

    def execute(self, context):
        for i in bpy.data.collections:
            for o in i.objects:
                if o == bpy.context.active_object:
                    IsolateCollections.toggle_hide(i, bpy.types.Scene.collections_isolated)
        return {"FINISHED"}

    def toggle_hide(collection, isolated):
        if isolated:
            print("A")
            # unhide / return to previous state
            for i in bpy.types.Scene.previously_active_collections_C:
                i[0].hide_viewport = i[1]
            bpy.types.Scene.collections_isolated = False
            bpy.types.Scene.previously_active_collections_C = []
        else:
            print("B")
            # hide collections and save their state for later
            for i in bpy.data.collections:
                if i != collection:
                    bpy.types.Scene.previously_active_collections_C.append([i, i.hide_viewport])
                    i.hide_viewport = True
            bpy.types.Scene.collections_isolated = True
