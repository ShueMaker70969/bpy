import bpy

# Get the active object
obj = bpy.context.active_object

print("")
print("")
print("Beginning of the material Analysis")
print("______________________________________________")
if obj and obj.type == 'MESH':  # Ensure it's a mesh object
    for slot in obj.material_slots:
        mat = slot.material
        if mat and mat.use_nodes:  # Check if the material uses nodes
            print(f"Material: {mat.name}")
            for node in mat.node_tree.nodes:
                print(f" - Node: {node.name} (Type: {node.type})")
                if node.type == 'TEX_IMAGE':
                    if node.image:
                        img = bpy.data.images[node.image.name]
                        print("===============================")
                        print(f"Image Name: {node.image.name}")
                        print(f"Image Size (W, H): {node.image.size[0]} X {node.image.size[1]}")
                        print(f"Object Type {type(img)}")
                        if img.filepath:
                            print(f"Image Path: {img.filepath}")
                        else:
                            print("image path does not exist")
                        print("===============================")
                    else:
                        print(f" - Node: {node.name} has no image assigned")
        else:
            print(f"Material: {mat.name} (No nodes)")
else:
    print("No active mesh object found.")
    
