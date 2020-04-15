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
            if ao.type == "GPENCIL":
                if mode == "OBJECT":
                    bpy.ops.object.mode_set(mode="EDIT_GPENCIL")
                elif mode == "EDIT_GPENCIL":
                    bpy.ops.object.mode_set(mode="OBJECT")
                else:
                    bpy.ops.object.mode_set(mode="EDIT_GPENCIL")
            else:
                if mode == "OBJECT":
                    bpy.ops.object.mode_set(mode="EDIT")
                elif mode == "EDIT":
                    bpy.ops.object.mode_set(mode="OBJECT")
                else:
                    bpy.ops.object.mode_set(mode="EDIT")
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
            elif ao.type == "GPENCIL":
                if mode == "OBJECT":
                    bpy.ops.object.mode_set(mode="PAINT_GPENCIL")
                elif mode == "PAINT_GPENCIL":
                    bpy.ops.object.mode_set(mode="OBJECT")
                else:
                    bpy.ops.object.mode_set(mode="PAINT_GPENCIL")
            else:
                if mode == "OBJECT":
                    bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
                elif mode == "WEIGHT_PAINT":
                    bpy.ops.object.mode_set(mode="OBJECT")
                else:
                    bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
        return {"FINISHED"}


class DeleteKeyFrame(bpy.types.Operator):
    bl_label = "F Delete Keyframe"
    bl_idname = "frankiestools.f_delete_keyframe"
    bl_description = "delete keyframe and update motion path"

    def execute(self, context):
        last_frame = bpy.context.scene.frame_end

        bpy.ops.anim.keyframe_delete()
        bpy.ops.pose.paths_calculate(
            start_frame=0, end_frame=last_frame, bake_location='HEADS')
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
            bpy.types.Scene.collections_isolated = False
            for i in bpy.types.Scene.previously_active_collections_A:
                try:
                    i[0].hide_viewport = i[1]
                except:
                    print("error trying to unhide collection, but probably fine")
            for i in bpy.types.Scene.previously_active_collections_B:
                try:
                    i[0].hide_viewport = i[2]
                except:
                    print("error trying to unhide collection, but probably fine")
            bpy.types.Scene.collections_all_visible = False
            bpy.types.Scene.previously_active_collections_A = []
            bpy.types.Scene.previously_active_collections_B = []

        else:
            for i in view_layer.collection.children:
                bpy.types.Scene.previously_active_collections_A.append(
                    [i, i.hide_viewport])
                i.hide_viewport = False
            for i in view_layer.children:
                bpy.types.Scene.previously_active_collections_B.append(
                    [i, i.exclude, i.hide_viewport])
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
        # make a list of collections currently selected object is in
        list_of_collections = IsolateCollections.get_collections(self)
        # toggle isolation of collections
        IsolateCollections.toggle_hide_isolate(list_of_collections, bpy.types.Scene.collections_isolated)
        return {"FINISHED"}

    def find_vlc(self, vlc, collection):
        # for each child of view layer collection
        for child in vlc.children:
            # return the target collection is found
            if child.collection == collection:
                return child
            # otherwise for each child loop round and find another
            elif child.children:
                foreach i in child.children:
                    find_vlc(self, child, child.collection)

    def addParentsToList(self, collection, col_parent_list):
        # if any collection has children
        for c in bpy.data.collections:
            if c.children:
                for child in c.children:
                    # if child is the collection we're looking for
                    if child == collection:
                        col_parent_list.append(c)
                        IsolateCollections.addParentsToList(self, c, col_parent_list)
        return col_parent_list

    def addChildrenToList(self, collection, col_children_list):
        # if collection has children
        if collection.children:
            for child in collection.children:
                # add to list
                col_children_list.append(child)
                print(child)
                # if child has children, runn again on child
                if child.children:
                    IsolateCollections.addChildrenToList(self, child, col_children_list)
        return col_children_list

    def get_collections(self):
        list_of_objects = bpy.context.selected_objects
        list_of_collections = []

        for i in bpy.data.collections:
            for o in i.objects:
                for obj in list_of_objects:
                    if o == obj:
                        list_of_collections.append(i)

        list_of_collections_children = []
        for collection in list_of_collections:
            list_of_collections_children = IsolateCollections.addChildrenToList(self, collection, list_of_collections_children)

        list_of_collections_parents = []
        for collection in list_of_collections:
            list_of_collections_parents = IsolateCollections.addParentsToList(self, collection, list_of_collections_parents)

        list_of_collections += list_of_collections_children + list_of_collections_parents
        return list_of_collections

    def toggle_hide_isolate(collections, isolated):
        # TODO: check if currently selected selection is the one we isolated with
        if not isolated:
            # save collection state for later and hide unactive ones
            for i in bpy.data.collections:
                vlc = IsolateCollections.find_vlc()
                bpy.types.Scene.previously_active_collections_C.append([i, i.hide_viewport])
                if i in collections:
                    i.hide_viewport = False
                else:
                    i.hide_viewport = True

            bpy.types.Scene.collections_isolated = True

        elif isolated:
            # unhide / return to previous state
            for i in bpy.types.Scene.previously_active_collections_C:
                i[0].hide_viewport = i[1]
            bpy.types.Scene.collections_isolated = False
            bpy.types.Scene.previously_active_collections_C = []

