import bpy

# Get the active object
obj = bpy.context.active_object

if obj and obj.type == 'MESH':  # Ensure it's a mesh object
    for slot in obj.material_slots:
        mat = slot.material
        if mat and mat.use_nodes:  # Check if the material uses nodes
            print(f"Material: {mat.name}")
            for node in mat.node_tree.nodes:
                print(f" - Node: {node.name} (Type: {node.type})")
                if node.type == 'TEX_IMAGE':
                    if node.image:
                        print(f" -  This {node.name} uses image: {node.image.name}")
                    else:
                        print(f" - Node: {node.name} has no image assigned")
        else:
            print(f"Material: {mat.name} (No nodes)")
else:
    print("No active mesh object found.")
    
