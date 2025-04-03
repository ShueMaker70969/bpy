import bpy

bl_info = {
    "name": "Toon Outliner",
    "blender": (4, 2, 0),
    "category": "Object",
}

def create_material_with_shader(name, shader_type, shader_output="BSDF"):
    """
    Create a new material with a specified shader type and link it to the Material Output.

    :param name: Name of the material.
    :param shader_type: Type of shader node (e.g., "ShaderNodeEmission", "ShaderNodeDiffuseBSDF").
    :param shader_output: The name of the output socket to connect (default is "BSDF").
    :return: The created material.
    """
    # Create a new material
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True  # Enable node-based shading

    # Get the node tree and remove the default Principled BSDF
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Remove all existing shader nodes (Principled BSDF)
    for node in nodes:
        if node.type.startswith("BSDF") or node.type == "BSDF_PRINCIPLED":
            nodes.remove(node)

    # Add the new shader node
    shader_node = nodes.new(type=shader_type)
    
    # Get the Material Output node
    output_node = next(node for node in nodes if node.type == 'OUTPUT_MATERIAL')

    # Link the new shader to the Material Output (Surface input)
    links.new(shader_node.outputs[shader_output], output_node.inputs["Surface"])
    return mat

def apply_solidify_with_offset(offset, thickness):
    # Create solidify modifier with negative thickness, flipped normal and material offset
    bpy.ops.object.modifier_add(type='SOLIDIFY')
    bpy.context.object.modifiers["Solidify"].thickness = thickness
    bpy.context.object.modifiers["Solidify"].use_flip_normals = True
    bpy.context.object.modifiers["Solidify"].material_offset = offset

def show_popup_message(message):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title="Message", icon='INFO')

class CreateOutline(bpy.types.Operator):
    bl_idname = "object.create_outline"
    bl_label = "Outline Creator"
    bl_description = "Adds a toon outline"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context): # These arguments are given automatically
        obj = bpy.context.object  
        thickness = -0.03
        if obj and obj.type == 'MESH':
            has_solidify = False
            for i in range(len(obj.modifiers)):
                if obj.modifiers[i].name == "Solidify":
                    has_solidify = True

            # This code runs by assumption that the object has no solidify and must have at least one material
            if has_solidify or len(obj.data.materials) == 0:
                show_popup_message('object already has solidify or has no material, incompatible for outline')   
            else:
                mat = bpy.data.materials.get("Outline")
                if mat is None:
                    # create material and assign
                    mat = create_material_with_shader("Outline", "ShaderNodeEmission", "Emission")
                    mat.use_nodes = True
                    
                    # This section removes the unused material slots
                    for i in reversed(range(len(obj.material_slots))):  # Loop in reverse to avoid index shifting
                        if obj.material_slots[i].material is None:  # Check if the slot has no material
                            obj.active_material_index = i
                            bpy.ops.object.material_slot_remove()
                    
                    obj.data.materials.append(mat)
                    bpy.data.materials["Outline"].node_tree.nodes["Emission"].inputs[0].default_value = (0, 0, 0, 1)
                    mat.use_backface_culling = True
                    
                    apply_solidify_with_offset(len(obj.material_slots), thickness)
                else:
                    obj.data.materials.append(mat)
                    apply_solidify_with_offset(len(obj.material_slots), thickness)
        else:
            show_popup_message('object is not a mesh!')    
        return {'FINISHED'}
    
def menu_fn(self, context):
    self.layout.separator()
    self.layout.operator(CreateOutline.bl_idname)
    
def register():
    bpy.utils.register_class(CreateOutline)  # Register the operator

    print("Outliner addon was enabled.")

def unregister():
    bpy.types.VIEW3D_MT_object_context_menu.remove(menu_fn)  # Remove the menu
    bpy.utils.unregister_class(CreateOutline)  # Unregister the operator
    print("Outliner addon was diabled.")

if __name__ == "__main__":
    register()