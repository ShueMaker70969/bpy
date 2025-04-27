import bpy
def join_objects(objects):
    if not objects:
        print("No objects selected")
        return
    # Ensure we're in object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    # Select the objects to join
    for obj in objects:
        obj.select_set(True)

    # Set the active object (needed for joining)
    bpy.context.view_layer.objects.active = objects[0]

    # Join them
    bpy.ops.object.join()
    print(f"Joined {len(objects)} objects.")

def find_nodes_of_type(material, node_idname):
    """Return all Image Texture nodes in a material."""
    if not material.use_nodes:
        return []
    return [node for node in material.node_tree.nodes if node.bl_idname == node_idname]

def find_single_node_by_type(node_idname):
    material = bpy.context.active_object.active_material
    if not material or not material.use_nodes:
        print("No active material or material does not use nodes.")
        return None

    for node in material.node_tree.nodes:
        if node.bl_idname == node_idname:
            return node

    print(f"Node of type '{node_idname}' not found.")
    return None