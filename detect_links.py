import bpy
print("=========================")
obj = bpy.context.object
mat = obj.active_material
for item in obj.data.materials:
    for link in item.node_tree.links:
        print(link.from_node)
        print(link.to_node)
        print(link.from_socket)
        print(link.to_socket)
        
        
