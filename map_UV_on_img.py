import bpy
import bmesh
import numpy as np
from mathutils import Vector

# Get the active object
obj = bpy.context.object
if obj.type != 'MESH':
    raise ValueError("Selected object is not a mesh")

# Create a new image for the mask (black on the face)
image_size = 1024  # Set resolution for the image
image = bpy.data.images.new(name="UV_Mask", width=image_size, height=image_size, alpha=True)

# Create an empty mask (white background)
mask = np.ones((image_size, image_size, 4), dtype=np.uint8) * 255  # White image

# Get the active bmesh
bm = bmesh.new()
bm.from_mesh(obj.data)

# Access the active UV layer
uv_layer = bm.loops.layers.uv.active

# Helper function to check if a point is inside a triangle (barycentric method)
def is_point_in_triangle(pt, v0, v1, v2):
    # v0, v1, v2 are the 2D coordinates of the triangle vertices (UVs)
    v0, v1, v2 = Vector(v0), Vector(v1), Vector(v2)
    v2_v0 = v2 - v0
    v1_v0 = v1 - v0
    pt_v0 = pt - v0
    
    # Barycentric coordinates formula
    d00 = v2_v0.dot(v2_v0)
    d01 = v2_v0.dot(v1_v0)
    d11 = v1_v0.dot(v1_v0)
    d20 = pt_v0.dot(v2_v0)
    d21 = pt_v0.dot(v1_v0)
    
    denom = d00 * d11 - d01 * d01
    if denom == 0:
        return False  # Degenerate triangle (collinear points)
    
    v = (d11 * d20 - d01 * d21) / denom
    w = (d00 * d21 - d01 * d20) / denom
    u = 1.0 - v - w
    
    # Check if point is inside the triangle
    return (u >= 0) and (v >= 0) and (w >= 0)

# Function to split quad into two triangles
def split_quad_to_triangles(uvs):
    # A quad has four vertices, and we split it into two triangles
    # Here we split the quad between vertices 0, 1, 2 and 0, 2, 3
    return [
        (uvs[0], uvs[1], uvs[2]),
        (uvs[0], uvs[2], uvs[3])
    ]

# Iterate through faces and fill the interior in the mask
for face in bm.faces:
    # Get the UV coordinates of the face's vertices
    uv_coords = [loop[uv_layer].uv for loop in face.loops]
    
    # Handle both triangles and quads
    if len(uv_coords) == 3:
        # If it's a triangle, just use the UVs as they are
        triangles = [(uv_coords[0], uv_coords[1], uv_coords[2])]
    elif len(uv_coords) == 4:
        # If it's a quad, split it into two triangles
        triangles = split_quad_to_triangles(uv_coords)
    else:
        # For n-gons, you could implement further triangulation if needed
        continue

    # For each triangle, fill the interior in the mask
    for triangle in triangles:
        pixel_coords = [(int(uv.x * image_size), int(uv.y * image_size)) for uv in triangle]
        
        # Draw on the mask using barycentric checking
        for y in range(image_size):
            for x in range(image_size):
                pt = Vector((x / image_size, y / image_size))  # Normalized 2D coordinates in UV space
                if is_point_in_triangle(pt, pixel_coords[0], pixel_coords[1], pixel_coords[2]):
                    mask[y, x] = [0, 0, 0, 255]  # Fill with black

# Update the image with the modified mask
image.pixels = (mask / 255).flatten()

# Save the image to a file
image.file_format = 'PNG'
image.filepath_raw = r'C:\Users\Shuma\Desktop"\UV_Mask.png'
image.save()

# Free BMesh data
bm.free()