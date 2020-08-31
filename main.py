import bpy
from mathutils import Vector


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


class ModifierSync(bpy.types.Operator):
    bl_label = "F modifier sync"
    bl_idname = "frankiestools.f_modifier_sync"
    bl_description = "sets modifiers render visilibilty to be the same as the viewport visibility"

    def execute(self, context):
        for o in bpy.context.selected_objects:
            for m in o.modifiers:
                m.show_render = m.show_viewport
                if m.type == "SUBSURF":
                    m.render_levels = m.levels

        return {"FINISHED"}


class SetOriginInEditMode(bpy.types.Operator):
    bl_label = "F set Origin"
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


class SetOriginInEditModeActive(bpy.types.Operator):
    bl_label = "F set Origin active"
    bl_idname = "frankiestools.f_set_origin_active"
    bl_description = "sets origin even if in edit mode, to active selection"

    def execute(self, context):
        ao = bpy.context.active_object
        so = bpy.context.selected_objects
        if ao and so:
            loc = bpy.context.scene.cursor.location
            for o in so:
                bpy.context.view_layer.objects.active = o
                mode = o.mode
                bpy.ops.view3d.snap_cursor_to_selected()
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='BOUNDS')
                bpy.ops.object.mode_set(mode=mode)
            bpy.context.scene.cursor.location = loc
            bpy.context.view_layer.objects.active = ao
        return {"FINISHED"}


class SetCursor(bpy.types.Operator):
    bl_label = "F set 3d cursor"
    bl_idname = "frankiestools.f_set_cursor"
    bl_description = "3d cursor workflow"

    def execute(self, context):
        if bpy.context.scene.cursor.location == Vector((0.0, 0.0, 0.0)) and bpy.context.scene.cursor.location != bpy.context.view_layer.objects.active.location:
            bpy.context.scene.cursor.location = bpy.context.view_layer.objects.active.location
        elif bpy.context.scene.cursor.location == bpy.context.view_layer.objects.active.location:
            bpy.ops.view3d.snap_cursor_to_selected()
        else:
            bpy.context.scene.cursor.location = Vector((0, 0, 0))
        bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
        return {"FINISHED"}


class BadFcurves(bpy.types.Operator):
    bl_label = "F print bad fcurves to console"
    bl_idname = "frankiestools.f_print_bad_fcurves"
    bl_description = "print bad fcurves to console"

    def execute(self, context):
        bones = ['"' + b.name + '"' for o in bpy.data.armatures for b in o.bones]
        fcurves = [f for a in bpy.data.actions for f in a.fcurves]
        lost = [f for f in fcurves if not any(f.data_path.find(el) != -1 for el in bones)]

        for a in bpy.data.actions:
            for f in a.fcurves:
                if f in lost:
                    print(f.data_path)
                    # a.fcurves.remove(f)
        return {"FINISHED"}


class KeyFrameAllActionsConstraints(bpy.types.Operator):
    bl_idname = "bone.keyframeallactionsconstraints"
    bl_label = "Unused"
    bl_description = "Propogate first keyframe from this action to all other actions if that action is missing a keyframe, handy for when you add a new bone and now need a keyframe for it on all other actions "

    def execute(self, context):
        action = bpy.context.object.animation_data.action  # current action
        actions = bpy.data.actions
        for selbone in bpy.context.selected_pose_bones:
            for f in bpy.data.actions[action.name].fcurves:
                if str("\"" + selbone.name + "\"") in str(f.data_path):
                    findex = f.data_path
                    if "constraint" in findex:
                        for a in actions:
                            booltest = False
                            for f in bpy.data.actions[a.name].fcurves:
                                if findex in str(f.data_path):
                                    booltest = True
                            if not booltest:
                                kfp = a.fcurves.new(findex)
                                kfp.keyframe_points.add(1)
                                kfp.keyframe_points[0].co = 0.0, 0.0
        return{'FINISHED'}


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


class CollectionVisibility(bpy.types.Operator):
    bl_label = "F Isolate Visibility"
    bl_idname = "frankiestools.f_collection_visibility"
    bl_description = "isolate collection"

    f_collection_visibility_mode: bpy.props.EnumProperty(
        name="Mode",
        items=[
            ('reveal', 'Reveal', '', '', 0),
            ('hide', 'Hide', '', '', 1),
            ('isolate', 'Isolate', '', '', 2)
        ],
        default='reveal'
    )

    bpy.types.Scene.reveal_active = False
    bpy.types.Scene.reveal_c_list = []
    bpy.types.Scene.reveal_vlc_list = []
    bpy.types.Scene.hide_active = False
    bpy.types.Scene.hide_vlc_list = []
    bpy.types.Scene.previous = []
    bpy.types.Scene.isolate_active = False
    bpy.types.Scene.isolate_vlc_list = []

    def execute(self, context):
        # print("-----------------------")
        if (self.f_collection_visibility_mode == "reveal"):
            self.reveal()
        elif (self.f_collection_visibility_mode == "hide"):
            self.hide()
        elif (self.f_collection_visibility_mode == "isolate"):
            self.isolate()

        return {"FINISHED"}

    def reveal(self):
        # unhide everything and cache state
        if not bpy.types.Scene.reveal_active or bpy.context.active_object != bpy.types.Scene.previous:
            for c in bpy.data.collections:
                vlc = CollectionVisibility.find_vlc(self, c.name)
                if vlc:
                    bpy.types.Scene.reveal_c_list = [[c.name, c.hide_viewport]]
                    bpy.types.Scene.reveal_vlc_list.append([vlc.name, vlc.hide_viewport])
                    c.hide_viewport = False
                    vlc.hide_viewport = False
            # bpy.types.Scene.reveal_active = True
            self.set_reveal_hide_isolate_state(True, True, True)
            bpy.types.Scene.previous = bpy.context.active_object
        # revert to previous state
        elif bpy.types.Scene.reveal_active:
            for c in bpy.data.collections:
                for i in bpy.types.Scene.reveal_c_list:
                    if c.name == i[0]:
                        c.hide_viewport = i[1]
                vlc = CollectionVisibility.find_vlc(self, c.name)
                if vlc:
                    for i in bpy.types.Scene.reveal_vlc_list:
                        if vlc.name == i[0]:
                            vlc.hide_viewport = i[1]
            bpy.types.Scene.reveal_c_list = []
            bpy.types.Scene.reveal_vlc_list = []
            self.set_reveal_hide_isolate_state(False, False, False)

    def hide(self):
        # hide collection and cache state
        if not bpy.types.Scene.hide_active or bpy.context.active_object != bpy.types.Scene.previous:
            list_of_collections = [i for i in bpy.data.collections for o in i.objects for obj in bpy.context.selected_objects if o == obj]
            for c in list_of_collections:
                vlc = CollectionVisibility.find_vlc(self, c.name)
                bpy.types.Scene.hide_vlc_list.append([vlc.name, vlc.hide_viewport])
                vlc.hide_viewport = True
            self.set_reveal_hide_isolate_state(False, True, False)
            bpy.types.Scene.previous = bpy.context.active_object
        # revert to previous state
        elif bpy.types.Scene.hide_active:
            for c in bpy.data.collections:
                vlc = CollectionVisibility.find_vlc(self, c.name)
                for i in bpy.types.Scene.hide_vlc_list:
                    if vlc.name == i[0]:
                        vlc.hide_viewport = i[1]
            bpy.types.Scene.hide_vlc_list = []
            self.set_reveal_hide_isolate_state(False, False, False)

    def isolate(self):
        # hide all unselected collections, cache state
        if not bpy.types.Scene.isolate_active or bpy.context.active_object != bpy.types.Scene.previous:
            list_of_collections = [i for i in bpy.data.collections for o in i.objects for obj in bpy.context.selected_objects if o == obj]
            list_of_collections_relations = self.get_collections_relations(list_of_collections)
            print(list_of_collections_relations)
            for c in bpy.data.collections:
                if c not in list_of_collections_relations:
                    vlc = CollectionVisibility.find_vlc(self, c.name)
                    bpy.types.Scene.isolate_vlc_list.append([vlc.name, vlc.hide_viewport])
                    vlc.hide_viewport = True
                    self.set_reveal_hide_isolate_state(False, False, True)
            bpy.types.Scene.previous = bpy.context.active_object
        # revert to previous state
        elif bpy.types.Scene.isolate_active:
            for c in bpy.data.collections:
                vlc = CollectionVisibility.find_vlc(self, c.name)
                for i in bpy.types.Scene.isolate_vlc_list:
                    if vlc.name == i[0]:
                        vlc.hide_viewport = i[1]
            bpy.types.Scene.isolate_vlc_list = []
            self.set_reveal_hide_isolate_state(False, False, False)

    def set_reveal_hide_isolate_state(self, reveal, hide, isolate):
        bpy.types.Scene.reveal_active = reveal
        bpy.types.Scene.hide_active = hide
        bpy.types.Scene.isolate_active = isolate

    def get_collections_relations(self, list_of_collections):
        # find children collections
        list_of_collections_children = []
        for collection in list_of_collections:
            list_of_collections_children = CollectionVisibility.addChildrenToList(self, collection, list_of_collections_children)
        # find parent collections
        list_of_collections_parents = []
        for collection in list_of_collections:
            list_of_collections_parents = CollectionVisibility.addParentsToList(self, collection, list_of_collections_parents)
        # combine all lists
        list_of_collections += list_of_collections_children + list_of_collections_parents
        return list_of_collections

    def addParentsToList(self, collection, col_parent_list):
        # if any collection has children
        for c in bpy.data.collections:
            if c.children:
                for child in c.children:
                    # if child is the collection we're looking for add to list and run again
                    if child == collection:
                        col_parent_list.append(c)
                        CollectionVisibility.addParentsToList(self, c, col_parent_list)
        return col_parent_list

    def addChildrenToList(self, collection, col_children_list):
        # if collection has children
        if collection.children:
            for child in collection.children:
                # add to list
                col_children_list.append(child)
                # if child has children, run again on child
                if child.children:
                    CollectionVisibility.addChildrenToList(self, child, col_children_list)
        return col_children_list

    def find_vlc(self, collection_name):
        # iterate over a list but only return the first one because we only want one
        collection = [c for c in bpy.data.collections if c.name == collection_name]  # this is a list but we only want a single item
        vlc_list = []
        CollectionVisibility.find_vlc_list(self, bpy.context.view_layer.layer_collection, collection[0], vlc_list)
        if (len(vlc_list) < 1):
            return
        return vlc_list[0]

    def find_vlc_list(self, vlc, collection, list):
        # for each child of view layer collection
        for child in vlc.children:
            # return the target collection if found
            if child.collection == collection:
                list.append(child)
            # otherwise for each child loop round and find another
            elif child.children:
                CollectionVisibility.find_vlc_list(self, child, collection, list)
