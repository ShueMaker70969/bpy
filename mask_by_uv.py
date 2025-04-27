import bpy
import bmesh
import numpy as np
import sys
sys.path.append(r"C:\Users\Shuma\Desktop\CAD_FOLDER\Blender\python_libraries")
import cv2

# sets the view transform to standard, so the image color won't change when saving
bpy.context.scene.view_settings.view_transform = 'Standard'
# Save path where everything is saved
save_path = r"C:\Users\Shuma\Desktop\CAD_FOLDER\Blender\temp_path"

def mask_by_uv(img_size):
    # Get the active object
    obj = bpy.context.object
    if obj.type != 'MESH':
        raise ValueError("Selected object is not a mesh")

    mask_image = np.full((img_size, img_size), 0, dtype=np.uint8)

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
                coordinate.append((round(uv[0] * img_size), round((1 - uv[1]) * img_size)))
        #print(coordinate)
        pos = np.array(coordinate)
        cv2.fillPoly(mask_image, [pos], (255, 255, 255))
        #print("")
    cv2.imwrite(save_path + r"/mask.png", mask_image)

    for item in obj.data.materials:
        for i, link in enumerate(item.node_tree.links):
            if link.from_node.type == "TEX_IMAGE":
                if link.to_node.type == "BSDF_PRINCIPLED" and link.to_socket.name == "Base Color":
                    print("Image Texture Connected to Principled Shader Base Color Detected")
                    print(f"Image Name: {link.from_node.image.name}")
                    image = bpy.data.images[link.from_node.image.name]              
                    image.file_format = 'PNG'  # Or 'TIFF' for lossless formats
                    image.filepath = save_path + r"/" + link.from_node.image.name + ".png"
                    image.save()
                    img = cv2.imread(image.filepath)
                    img2 = cv2.imread(save_path + r"/mask.png")
                    output = cv2.bitwise_and(img, img2)
                    cv2.imshow("Masked Image", output)
                    cv2.imwrite(save_path + r"/masked_texture.png", output)
                if ((link.to_node.type == "BSDF_PRINCIPLED" and link.to_socket.name == "Normal")
                    or (link.to_node.type == "NORMAL_MAP" and link.to_socket.name == "Color")):
                    print("Image Texture Connected to Principled Shader Normal Detected")
                    print(f"Image Name: {link.from_node.image.name}")
                    image = bpy.data.images[link.from_node.image.name]              
                    image.file_format = 'PNG'  # Or 'TIFF' for lossless formats
                    image.filepath = save_path + r"/" + link.from_node.image.name + ".png"
                    image.save()
                    img = cv2.imread(image.filepath)
                    img2 = cv2.imread(save_path + r"/mask.png")
                    output = cv2.bitwise_and(img, img2)
                    cv2.imshow("Masked Image", output)
                    cv2.imwrite(save_path + r"/masked_normal.png", output)
    bm.free()  # Free memory in case

if __name__ == "__main__":
    mask_by_uv(4096)
