import bpy

# Naming convention, "CATEGORY_PT_name"
class VIEW3D_PT_my_custom_panel(bpy.types.Panel):
    # Tell blender where to add the panel
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    # add labels
    bl_label = "My Custom Panel"
    bl_category = "Custom Panel"
    
    def draw(self, context):
        "define the layout of the panel"
        row = self.layout.row()
        row.operator("mesh.primitive_cube_add", text = "Add cube")
        row = self.layout.row()
        row.operator("object.shade_smooth", text = "Shade Smooth")
        
            
# register the panel with Blender
def register():
    bpy.utils.register_class(VIEW3D_PT_my_custom_panel)
    
def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_my_custom_panel)
    
if __name__ == "__main__":
    register()