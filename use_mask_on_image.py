import bpy
import bmesh
import numpy as np

import sys
sys.path.append(r"C:\Users\Shuma\Desktop\CAD_FOLDER\Blender\python_libraries")
import cv2

# sets the view transform to standard, so the image color won't change when saving
bpy.context.scene.view_settings.view_transform = 'Standard'

# Get the active object
obj = bpy.context.object
if obj.type != 'MESH':
    raise ValueError("Selected object is not a mesh")

img_size = 1024
mask_image = np.full((img_size, img_size), 255, dtype=np.uint8)

# Create a bmesh object from the mesh
bm = bmesh.new()
bm.from_mesh(obj.data)

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
    cv2.fillPoly(mask_image, [pos], (0, 0, 0))
    #print("")

save_path = r"C:\Users\Shuma\Desktop\CAD_FOLDER\Blender\temp_path"

for item in obj.data.materials:
    for i, link in enumerate(item.node_tree.links):
        if link.from_node.type == "TEX_IMAGE":
            if link.to_node.type == "BSDF_PRINCIPLED" and link.to_socket.name == "Base Color":
                print("Image Texture Connected to Principled Shader Base Color Detected")
                print(f"Image Name: {link.from_node.image.name}")
                image = bpy.data.images[link.from_node.image.name]  # Replace with your image name
                # Set color depth and format to avoid changes
                image.file_format = 'PNG'  # Or 'TIFF' for lossless formats
                image.filepath = save_path 
                image.save()
            if ((link.to_node.type == "BSDF_PRINCIPLED" and link.to_socket.name == "Normal")
                or (link.to_node.type == "NORMAL_MAP" and link.to_socket.name == "Color")):
                print("Image Texture Connected to Principled Shader Normal Detected")
                print(f"Image Name: {link.from_node.image.name}")


cv2.imshow("UV MASK", mask_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

bm.free()  # Free memory when done





'''
for item in obj.data.materials:
    for i, link in enumerate(item.node_tree.links):
        print(f"Reading link {i}: {link}")
        print(f"From Node type  : {link.from_node.type}")
        print(f"To Node type    : {link.to_node.type}")
        if link.from_node.type == "TEX_IMAGE":
            if link.to_node.type == "BSDF_PRINCIPLED" and link.to_socket.name == "Base Color":
                print("Image Texture Connected to Principled Shader Base Color Detected")
                print(f"Image Name: {link.from_node.image.name}")
            if ((link.to_node.type == "BSDF_PRINCIPLED" and link.to_socket.name == "Normal")
                or (link.to_node.type == "NORMAL_MAP" and link.to_socket.name == "Color")):
                print("Image Texture Connected to Principled Shader Normal Detected")
                print(f"Image Name: {link.from_node.image.name}")
        print(f"From Socket Name: {link.from_socket.name}")
        print(f"To Socket Name  : {link.to_socket.name}")
'''        
        
        