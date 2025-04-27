import bpy
import sys
import os
script_dir = r"C:\Users\Shuma\Desktop\CAD_FOLDER\Blender\bpy_codes"
if script_dir not in sys.path:
    sys.path.append(script_dir)
from utils import find_single_node_by_type
node = find_single_node_by_type("ShaderNodeTexImage")
print(node)