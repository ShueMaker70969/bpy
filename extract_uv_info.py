import bpy
import bmesh

import sys
sys.path.append(r"C:\Users\Shuma\Desktop\CAD_FOLDER\Blender\python_libraries")
import cv2

# Get the active object
obj = bpy.context.object
if obj.type != 'MESH':
    raise ValueError("Selected object is not a mesh")

# Create a bmesh object from the mesh
bm = bmesh.new()
bm.from_mesh(obj.data)

# Iterate through each face and print the relevant info
for face in bm.faces:
    print(f"Face ID: {face.index}")
#    print("Vertices:")
#    for loop in face.loops:
#        print(f"    Vertex {loop.vert.index}: {loop.vert.co}")
        
    # Optional: UV coordinates if UV map exists
    if bm.loops.layers.uv.active:
        print("UV Coordinates:")
        for loop in face.loops:
            uv = loop[bm.loops.layers.uv.active].uv
            print(f"    UV: {uv}")
            
    
    print("")

bm.free()  # Free memory when done
