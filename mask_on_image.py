import bpy
import bmesh
import numpy as np

import sys
sys.path.append(r"C:\Users\Shuma\Desktop\CAD_FOLDER\Blender\python_libraries")
import cv2

import bpy

# Get the active object
obj = bpy.context.object

if obj.type != 'MESH': # Ensure it's a mesh object
    raise ValueError("Selected object is not a mesh")

# Create empty white image for mask
img_size = 1024
white_image = np.full((img_size, img_size), 255, dtype=np.uint8)

# Create a bmesh object from the mesh
bm = bmesh.new()
bm.from_mesh(obj.data)


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

    
# Iterate through each face and print the relevant info
for face in bm.faces:
    # print(f"Face ID: {face.index}")
    
    coordinate = []
    # Optional: UV coordinates if UV map exists
    if bm.loops.layers.uv.active:
        # print("UV Coordinates:")
        for loop in face.loops:
            uv = loop[bm.loops.layers.uv.active].uv
            coordinate.append((round(uv[0]*img_size), round(uv[1]*img_size)))
    #print(coordinate)
    pos = np.array(coordinate)
    cv2.fillPoly(white_image, [pos], (0, 0, 0))
    #print("")

cv2.imshow("UV Mask", white_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

bm.free()  # Free memory when done
