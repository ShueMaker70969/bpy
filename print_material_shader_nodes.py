import bpy
print("=========================")
obj = bpy.context.object
mat = obj.active_material
for item in obj.data.materials:
    for node in item.node_tree.nodes:
        print(f"Node name: {node.name}")
        print(f"Node type: {node.type}")
        print(node)

mat = obj.active_material
nodes = mat.node_tree.nodes
node = nodes.new('ShaderNodeBsdfDiffuse')
print(node)

#material.node_tree.nodes.remove(material.node_tree.nodes.get('Diffuse BSDF'))
