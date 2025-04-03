import bpy

# Addon information (bl_info)
bl_info = {
    "name": "サンプル2-1: オブジェクトを生成するアドオン",
    "author": "Nutti",
    "version": (2, 0),
    "blender": (2, 75, 0),
    "location": "3Dビュー > 追加 > メッシュ",
    "description": "オブジェクトを生成するサンプルアドオン",
    "warning": "",
    "support": "TESTING",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
}

# Operator to create an object (ICO sphere)
class CreateObject(bpy.types.Operator):
    bl_idname = "object.create_object"
    bl_label = "球"
    bl_description = "ICO球を追加します"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.mesh.primitive_ico_sphere_add()
        print("サンプル2-1: 3DビューにICO球を生成しました。")
        return {'FINISHED'}

# Menu function to add the operator
def menu_fn(self, context):
    self.layout.separator()
    self.layout.operator(CreateObject.bl_idname)

# Register addon
def register():
    bpy.utils.register_class(CreateObject)  # Register the operator
    bpy.types.VIEW3D_MT_mesh_add.append(menu_fn)  # Append the menu
    print("サンプル2-1: アドオン「サンプル2-1」が有効化されました。")

# Unregister addon
def unregister():
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_fn)  # Remove the menu
    bpy.utils.unregister_class(CreateObject)  # Unregister the operator
    print("サンプル2-1: アドオン「サンプル2-1」が無効化されました。")

# Main
if __name__ == "__main__":
    register()
