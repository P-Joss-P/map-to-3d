import bpy
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR) 

from configuration import GLB_path 
from configuration import interest_types 

GLB_PATH = os.path.join(GLB_path, "map3d.glb")
OUTPUT_BLEND = os.path.join(GLB_path, "import_automatique_blender.blend")

# Clean Scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for collection in bpy.data.collections:
    bpy.data.collections.remove(collection)

# Import GLB
bpy.ops.import_scene.gltf(filepath=GLB_PATH)

# Save 
bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_BLEND)

print("Import succesfully done")



##############################
### MATERIALS FOR OSM TYPE ###
##############################


MATERIALS = {}

for elements in interest_types:
    MATERIALS[elements] = f"MAT_{elements}"


def get_or_create_material(name):
    if name in bpy.data.materials:
        return bpy.data.materials[name]

    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Nodes
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    vcol = nodes.new("ShaderNodeVertexColor")

    # Connexions
    links.new(vcol.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    return mat


#########################
#### ASSIGN MATERIALS ###
#########################

for obj in bpy.context.scene.objects:
    if obj.type != "MESH":
        continue

    name = obj.name.lower()

    for key, mat_name in MATERIALS.items():
        if name.startswith(key):
            mat = get_or_create_material(mat_name)

            if obj.data.materials:
                obj.data.materials[0] = mat
            else:
                obj.data.materials.append(mat)

            break
