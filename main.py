import bpy
from mathutils import Vector


class ViewportSetup(bpy.types.Operator):
    bl_label = "F Viewport Setup"
    bl_idname = "frankiestools.f_viewport_setup"
    bl_description = "sets the viewport just how I like it"
    bl_options = {'REGISTER', 'UNDO'}

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
    bl_options = {'REGISTER', 'UNDO'}

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
    bl_options = {'REGISTER', 'UNDO'}

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
    bl_options = {'REGISTER', 'UNDO'}

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
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.context.scene.cursor.location == Vector((0.0, 0.0, 0.0)) and bpy.context.scene.cursor.location != bpy.context.view_layer.objects.active.location:
            bpy.context.scene.cursor.location = bpy.context.view_layer.objects.active.location
        elif bpy.context.scene.cursor.location == bpy.context.view_layer.objects.active.location:
            bpy.ops.view3d.snap_cursor_to_selected()
        else:
            bpy.context.scene.cursor.location = Vector((0, 0, 0))
        # bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
        return {"FINISHED"}


class BadFcurves(bpy.types.Operator):
    bl_label = "F print bad fcurves to console"
    bl_idname = "frankiestools.f_print_bad_fcurves"
    bl_description = "print bad fcurves to console"
    bl_options = {'REGISTER', 'UNDO'}

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
    bl_options = {'REGISTER', 'UNDO'}

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
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ao = bpy.context.active_object
        mode = ao.mode
        if ao:
            bpy.context.space_data.show_gizmo = True
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
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ao = bpy.context.active_object
        mode = ao.mode
        if ao:
            bpy.context.space_data.show_gizmo = True
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


class CopyParents(bpy.types.Operator):
    bl_label = "F Copy Parent"
    bl_idname = "frankiestools.f_copy_parent"
    bl_description = "copy parent and transform"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        a = bpy.context.active_object
        for i in bpy.context.selected_objects:
            if i == a:
                continue
            i.parent = a.parent
            i.matrix_world = a.matrix_world
            i.matrix_parent_inverse.identity()  # remove parent inverse
        return {"FINISHED"}

        


class SetSmoothing(bpy.types.Operator):
    bl_label = "F set smoothing"
    bl_idname = "frankiestools.f_set_smoothing"
    bl_description = "set smoothing"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for ob in bpy.context.selected_objects:
            for f in ob.data.polygons:
                f.use_smooth = True
            ob.data.use_auto_smooth = True
            ob.data.auto_smooth_angle = 0.523599  # 30deg
        return {"FINISHED"}


class DeleteKeyFrame(bpy.types.Operator):
    bl_label = "F Delete Keyframe"
    bl_idname = "frankiestools.f_delete_keyframe"
    bl_description = "delete keyframe and update motion path"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        last_frame = bpy.context.scene.frame_end
        bpy.ops.anim.keyframe_delete()
        headOrTail = "HEADS"
        try:
            if not bpy.context.preferences.addons["AnimScrubber"].preferences.recalculate_curves_at_head:
                headOrTail = "TAILS"
        except:
            print("Animscrubber addon not found, using heads to bake curve")
        bpy.ops.pose.paths_calculate(display_type='RANGE', range='SCENE', bake_location=headOrTail)
        return {"FINISHED"}


class RemoveUvFromSelected(bpy.types.Operator):
    bl_label = "F Remove UV from selected"
    bl_idname = "frankiestools.f_uv_remove"
    bl_description = "remove uvs from selected"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for o in bpy.context.selected_objects:
            if o.type == "MESH":
                for u in o.data.uv_layers:
                    o.data.uv_layers.remove(u)
        return {"FINISHED"}

class CollectionVisibility(bpy.types.Operator):
    bl_label = "F Isolate Visibility"
    bl_idname = "frankiestools.f_collection_visibility"
    bl_description = "Isolate or toggle visibility of collections"
    bl_options = {'REGISTER', 'UNDO'}

    f_collection_visibility_mode: bpy.props.EnumProperty(
        name="Mode",
        items=[
            ('reveal', 'Reveal', '', '', 0),
            ('hide', 'Hide', '', '', 1),
            ('isolate', 'Isolate', '', '', 2)
        ],
        default='reveal'
    )

    def execute(self, context):
        if self.f_collection_visibility_mode == "reveal":
            self.reveal(context)
        elif self.f_collection_visibility_mode == "hide":
            self.hide(context)
        elif self.f_collection_visibility_mode == "isolate":
            self.isolate(context)
        return {"FINISHED"}

    def reveal(self, context):
        scene = context.scene
        use_exclude = scene.fcv_use_exclude

        if not scene.fcv_reveal_active or context.active_object.name != scene.get("fcv_previous", ""):
            scene.fcv_reveal_vlc_list.clear()
            for c in bpy.data.collections:
                vlc = self.find_vlc(context.view_layer.layer_collection, c)
                if vlc:
                    item = scene.fcv_reveal_vlc_list.add()
                    item.name = vlc.name
                    item.state = vlc.exclude if use_exclude else vlc.hide_viewport
                    if use_exclude:
                        vlc.exclude = False
                    else:
                        vlc.hide_viewport = False
            self.set_mode_state(scene, reveal=True)
            scene["fcv_previous"] = context.active_object.name if context.active_object else ""
        else:
            for item in scene.fcv_reveal_vlc_list:
                vlc = self.get_vlc_by_name(context.view_layer.layer_collection, item.name)
                if vlc:
                    if use_exclude:
                        vlc.exclude = item.state
                    else:
                        vlc.hide_viewport = item.state
            scene.fcv_reveal_vlc_list.clear()
            self.set_mode_state(scene)

    def hide(self, context):
        scene = context.scene
        use_exclude = scene.fcv_use_exclude

        if not scene.fcv_hide_active or context.active_object.name != scene.get("fcv_previous", ""):
            scene.fcv_hide_vlc_list.clear()
            for c in bpy.data.collections:
                if any(o.name in c.objects for o in context.selected_objects):
                    vlc = self.find_vlc(context.view_layer.layer_collection, c)
                    if vlc:
                        item = scene.fcv_hide_vlc_list.add()
                        item.name = vlc.name
                        item.state = vlc.exclude if use_exclude else vlc.hide_viewport
                        if use_exclude:
                            vlc.exclude = True
                        else:
                            vlc.hide_viewport = True
            self.set_mode_state(scene, hide=True)
            scene["fcv_previous"] = context.active_object.name if context.active_object else ""
        else:
            for item in scene.fcv_hide_vlc_list:
                vlc = self.get_vlc_by_name(context.view_layer.layer_collection, item.name)
                if vlc:
                    if use_exclude:
                        vlc.exclude = item.state
                    else:
                        vlc.hide_viewport = item.state
            scene.fcv_hide_vlc_list.clear()
            self.set_mode_state(scene)

    def isolate(self, context):
        scene = context.scene
        use_exclude = scene.fcv_use_exclude
        if not scene.fcv_isolate_active or context.active_object.name != scene.get("fcv_previous", ""):
            selected_colls = [c for c in bpy.data.collections if any(o.name in c.objects for o in context.selected_objects)]
            related = self.get_collections_relations(selected_colls)
            scene.fcv_isolate_vlc_list.clear()
            for c in bpy.data.collections:
                if c.name not in [r.name for r in related]:
                    vlc = self.find_vlc(context.view_layer.layer_collection, c)
                    if vlc:
                        item = scene.fcv_isolate_vlc_list.add()
                        item.name = vlc.name
                        item.state = vlc.exclude if use_exclude else vlc.hide_viewport
                        if use_exclude:
                            vlc.exclude = True
                        else:
                            vlc.hide_viewport = True
            self.set_mode_state(scene, isolate=True)
            scene["fcv_previous"] = context.active_object.name if context.active_object else ""
        else:
            for item in scene.fcv_isolate_vlc_list:
                vlc = self.get_vlc_by_name(context.view_layer.layer_collection, item.name)
                if vlc:
                    if use_exclude:
                        vlc.exclude = item.state
                    else:
                        vlc.hide_viewport = item.state
            scene.fcv_isolate_vlc_list.clear()
            self.set_mode_state(scene)

    def set_mode_state(self, scene, reveal=False, hide=False, isolate=False):
        scene.fcv_reveal_active = reveal
        scene.fcv_hide_active = hide
        scene.fcv_isolate_active = isolate

    def find_vlc(self, vlc, collection):
        if vlc.collection == collection:
            return vlc
        for child in vlc.children:
            found = self.find_vlc(child, collection)
            if found:
                return found
        return None

    def get_vlc_by_name(self, vlc, name):
        if vlc.name == name:
            return vlc
        for child in vlc.children:
            found = self.get_vlc_by_name(child, name)
            if found:
                return found
        return None

    def get_collections_relations(self, collections):
        result = set(collections)
        for c in collections:
            result.update(self.get_parents(c))
            result.update(self.get_children(c))
        return result

    def get_parents(self, col):
        parents = set()
        for c in bpy.data.collections:
            if col.name in [child.name for child in c.children]:
                parents.add(c)
                parents.update(self.get_parents(c))
        return parents

    def get_children(self, col):
        children = set(col.children)
        for child in col.children:
            children.update(self.get_children(child))
        return children

class FCV_VisibilityState(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    state: bpy.props.BoolProperty()

class FTOOLS_PT_VisibilityPanel(bpy.types.Panel):
    bl_label = "F Visibility Tools"
    bl_idname = "FTOOLS_PT_visibility_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "F Tools"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "fcv_use_exclude", toggle=True, icon='RESTRICT_VIEW_OFF')
        layout.operator("frankiestools.f_collection_visibility", text="Reveal").f_collection_visibility_mode = 'reveal'
        layout.operator("frankiestools.f_collection_visibility", text="Hide").f_collection_visibility_mode = 'hide'
        layout.operator("frankiestools.f_collection_visibility", text="Isolate").f_collection_visibility_mode = 'isolate'
