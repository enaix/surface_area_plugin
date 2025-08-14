bl_info = {
    "name": "Calculate surface area",
    "blender": (4, 5, 0),
    "category": "Object",
}

import bpy
from bpy.props import BoolProperty
import numpy as np
import bmesh

class ObjectSurfaceSettings(bpy.types.AddonPreferences):
    bl_idname = __package__ if __package__ else __name__
    
    create_clone: BoolProperty(
        name = "Apply scale transformation to a clone",
        default = False,
    )
    
    use_advanced_method: BoolProperty(
        name = "Use bmesh instead of fast iteration",
        default = False,
    )
    
    create_context: BoolProperty(
        name = "Create another context for an object clone (not implemented)",
        default = False,
        options={'ANIMATABLE', 'HIDDEN'}
    )
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="General")
        layout.prop(self, "create_clone")
        layout.label(text="Advanced")
        layout.prop(self, "use_advanced_method")
        layout.prop(self, "create_context")
    

class ObjectSurface(bpy.types.Operator):
    bl_idname = "mesh.surface_area"
    bl_label = "Calculate surface area"
    bl_options = {'REGISTER'}
    
    def handle_prefs(self, context):
        # Resolve addon preferences robustly across single-file and package installs
        addon_key_candidates = [
            getattr(ObjectSurfaceSettings, 'bl_idname', None),
            __name__,
            __package__ if __package__ else None,
        ]
        addon_prefs = None
        for key in addon_key_candidates:
            if not key:
                continue
            addon = context.preferences.addons.get(key)
            if addon:
                addon_prefs = addon.preferences
                break
        if addon_prefs is None:
            # Fallback to default values if preferences are unavailable
            self.create_clone = False
            self.use_advanced_method = False
            self.create_context = False
            return
        self.create_clone = addon_prefs.create_clone
        self.use_advanced_method = addon_prefs.use_advanced_method
        self.create_context = addon_prefs.create_context
    
    def update_context(self, context):
        if self.create_context and self.create_clone:
            raise NotImplementedError
            
            ctx = context.copy()
            return ctx
        return context
    
    def apply_scale(self, context, source):
        if self.create_clone:
            clone = source.copy()
            clone.data = source.data.copy()
            context.collection.objects.link(clone)
            bpy.ops.object.select_all(action='DESELECT')
            clone.select_set(True)
        
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        
        if self.create_clone:
            return clone
        return None
        
    def destroy_obj(self, context, clone, source):
        if clone is None:
            return
        
        # Safely remove the temporary clone without relying on operators
        try:
            bpy.data.objects.remove(clone, do_unlink=True)
        except ReferenceError:
            pass
        
        # Restore selection to the original source object
        bpy.ops.object.select_all(action='DESELECT')
        if source is not None:
            source.select_set(True)
    
    def get_area_bmesh(self, context, obj):
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        
        #bmesh.ops.triangulate(bm, faces=bm.faces)
        bm.faces.ensure_lookup_table()
        area = 0
        for f in bm.faces:
            if f.select:
                area += f.calc_area()
        
        bm.free()
        return area
        
    def get_area_simple(self, context, obj):
        pol = obj.data.polygons
        f_areas = np.zeros(len(pol), dtype=np.float32)
        f_select = np.zeros(len(pol), dtype=np.bool_)
        
        pol.foreach_get('select', f_select)
        pol.foreach_get('area', f_areas)
        area = f_areas[f_select].sum()
        
        #bpy.ops.ed.undo()
        return area

    def get_area(self, context, obj):
        if self.use_advanced_method:
            return self.get_area_bmesh(context, obj)
        return self.get_area_simple(context, obj)

    def execute(self, context):
        self.handle_prefs(context)
        source = context.active_object
        mode = source.mode
        # We need to update the selection
        bpy.ops.object.mode_set(mode='OBJECT')
        
        ctx = self.update_context(context)
        clone = self.apply_scale(ctx, source)
        if clone is None:
            obj = source
        else:
            obj = clone
        
        area = self.get_area(ctx, obj)
        
        self.destroy_obj(ctx, clone, source)
        
        bpy.ops.object.mode_set(mode=mode)
        self.report({'INFO'}, "Selected surface area is " + str(area) + " m²")
        
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(ObjectSurface.bl_idname)

def register():
    bpy.utils.register_class(ObjectSurfaceSettings)
    bpy.utils.register_class(ObjectSurface)
    bpy.types.VIEW3D_MT_edit_mesh.append(menu_func)

def unregister():
    bpy.utils.unregister_class(ObjectSurfaceSettings)
    bpy.utils.unregister_class(ObjectSurface)
    try:
        bpy.types.VIEW3D_MT_edit_mesh.remove(menu_func)
    except Exception:
        pass
    
if __name__ == "__main__":
    register()