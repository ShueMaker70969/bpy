import bpy
from pathlib import Path
from collections import defaultdict
import bmesh
import numpy as np

import sys
sys.path.append(r"C:\Users\Shuma\Desktop\CAD_FOLDER\Blender\python_libraries")
import cv2

# ------------------------------------------------ helpers
def nodes_with_images(mat):
    if not (mat and mat.use_nodes):
        return []
    return [n for n in mat.node_tree.nodes if getattr(n, "image", None)]

def get_image_as_numpy(image, keep_alpha=False):
    """
    Converts a Blender image to a NumPy array with shape (height, width, 4).
    Forces Blender to load image pixels if they are not loaded yet.
    """
    if not image:
        print("No image provided.")
        return None

    if not image.has_data:
        try:
            image.reload()
            print(f"Reloaded image: {image.name}")
        except RuntimeError:
            print(f"⚠️ Image '{image.name}' could not be reloaded.")
            return None

    # Now safe to proceed
    pixel_data = np.array(image.pixels[:], dtype=np.float32)
    width, height = image.size
    pixel_data = pixel_data.reshape((height, width, 4))
    
    pixel_data = np.flipud(pixel_data)  # Flip vertically

    if not keep_alpha:
        pixel_data = cv2.cvtColor(pixel_data, cv2.COLOR_RGB2BGR)
    else:
        pixel_data = cv2.cvtColor(pixel_data, cv2.COLOR_RGBA2BGRA)

    img_uint8 = (pixel_data * 255).clip(0, 255).astype(np.uint8)
    return img_uint8

def groups_by_image():
    """Return {image_name: [live_object, …]}."""
    groups = defaultdict(list)
    for ob in bpy.context.scene.objects:
        if ob.type != 'MESH':
            continue
        imgs = {n.image.name
                for slot in ob.material_slots
                for n in nodes_with_images(slot.material)}
        for img in imgs:
            groups[img].append(ob)
    return groups

def join_group(objects):
    """Join a group, return the survivor, ignore dead references safely."""
    alive = []
    for ob in objects:
        try:
            _ = ob.name                  # may raise ReferenceError
            alive.append(ob)
        except ReferenceError:
            pass                         # skip vanished object

    if len(alive) < 2:
        return alive[0] if alive else None

    bpy.ops.object.select_all(action='DESELECT')
    active = alive[0]
    bpy.context.view_layer.objects.active = active
    for ob in alive:
        ob.select_set(True)

    bpy.ops.object.join()                # destroys everything except active
    return active

def merge_by_shared_image():
    merged = []
    while True:
        big_groups = [g for g in groups_by_image().values() if len(g) > 1]
        if not big_groups:
            break
        for g in big_groups:
            survivor = join_group(g)
            if survivor:
                merged.append(survivor)
    return merged

import bpy

def promote_first_mesh_child():
    """
    If the current active object is not a mesh, find the first mesh
    in its hierarchy and make THAT mesh the active object.
    """
    root = bpy.context.active_object
    if root is None:
        raise RuntimeError("No active object in the scene.")

    # If it’s already a mesh we’re done
    if root.type == 'MESH':
        return root

    # Search direct and recursive children for a mesh
    for child in root.children_recursive:
        if child.type == 'MESH':
            # Deselect everything, then select & activate the mesh
            bpy.ops.object.select_all(action='DESELECT')
            child.select_set(True)
            bpy.context.view_layer.objects.active = child
            print(f" {child.name} is now the active mesh object.")
            return child

    raise RuntimeError("No mesh object found under the current root.")

# ---------------------------------------------

def mask_from_mesh_UV(mask_size):
    mask_image = np.full((mask_size, mask_size), 0, dtype=np.uint8)
    obj = bpy.context.object
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
                coordinate.append((round(uv[0]*mask_size), round(uv[1]*mask_size)))
        #print(coordinate)
        pos = np.array(coordinate)
        cv2.fillPoly(mask_image, [pos], (255, 255, 255))
        #print("")

    #Flip the image vertically
    mask_image = cv2.flip(mask_image, 0)
    bm.free()  # Free memory when done
    return mask_image

def is_node_connected_to_sockets(start_node, target_node, *target_socket_names):
    visited = set()
    target_sockets = set(target_socket_names)  # convert to set for faster lookup

    def traverse(node):
        if node in visited:
            return False
        visited.add(node)

        for output_socket in node.outputs:
            for link in output_socket.links:
                if link.to_node == target_node and link.to_socket.name in target_sockets:
                    return True
                if traverse(link.to_node):
                    return True
        return False

    return traverse(start_node)

def find_nodes_of_type(material, node_idname):
    """Return all Image Texture nodes in a material."""
    if not material.use_nodes:
        return []
    return [node for node in material.node_tree.nodes if node.bl_idname == node_idname]

def find_single_node(node_idname):
    material = bpy.context.active_object.active_material
    if not material or not material.use_nodes:
        print("No active material or material does not use nodes.")
        return None

    for node in material.node_tree.nodes:
        if node.bl_idname == node_idname:
            return node

    print(f"Node of type '{node_idname}' not found.")
    return None

# ------------------------------------------------ batch importer
def process_folder(folder, limit=1):
    for i, gltf_file in enumerate(Path(folder).iterdir()):
        if i >= limit:
            break
        print(f"importing  {gltf_file.name}")
        bpy.ops.import_scene.gltf(filepath=str(gltf_file), merge_vertices=True)
        promote_first_mesh_child()
        
        merge_by_shared_image()          # safe merging, no ReferenceError
        
        mat = bpy.context.active_object.active_material
        nodes = find_nodes_of_type(mat, "ShaderNodeTexImage")
        
        mask = mask_from_mesh_UV(4096)
        mask = cv2.merge([mask, mask, mask])  # shape (4096, 4096, 3)
        
        target_node = find_single_node("ShaderNodeBsdfPrincipled")
        
        for node in nodes:
            print(node)
            if is_node_connected_to_sockets(node, target_node, "Base Color"):
                texture = node.image
                texture = get_image_as_numpy(texture)  # shape (H, W, 4)
                
                texture = cv2.bitwise_and(mask, texture)
                
                cv2.imshow("UV MASK", texture)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            
            elif is_node_connected_to_sockets(node, target_node, "Normal"):
                normal = node.image
                normal = get_image_as_numpy(normal)  # shape (H, W, 4)
                
                normal = cv2.bitwise_and(mask, normal)
                
                cv2.imshow("UV MASK", normal)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
        
        cv2.imshow("UV MASK", mask)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

# ---------------- run
process_folder(r"D:\CMA_Repository", limit=8)