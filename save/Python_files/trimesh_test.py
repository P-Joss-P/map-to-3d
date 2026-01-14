"""
File: trimesh.py
Author: TORREGROSSA Dylan 
Repository: https://github.com/P-Joss-P/map-to-3d.git
License: GNU GENERAL PUBLIC LICENSE Version 3 (see LICENSE file)

Description:
    Short description of what this module does.
    Explain briefly the goal and its role in the project.

Usage:
    python script_name.py [options]

Example:
    python script_name.py --input data.osm --verbose

Dependencies:
    - Python 3.13+
    - libraries used : trimesh

Notes:
    - Add any implementation detail important for developers.
    - Keep this section optional.

"""


import json
import os
import osmnx as ox
import trimesh
import geopandas as gpd
from shapely.geometry import Polygon, LineString, MultiPolygon, MultiLineString
from trimesh.creation import extrude_polygon
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import numpy as np
from configuration import interest_types
from constant import Z_LAYERS

BASE_DIR = r"C:\data\Ecole\ENSE3\Cours\2A\Semestre1\Parcours_numerique\Projet_MapTo3D\map-to-3d\Config"
DEFAULT_CONFIG = os.path.join(BASE_DIR, "mapping_entities.json")

savepath = r"C:\data\Ecole\ENSE3\Cours\2A\Semestre1\Parcours_numerique\Projet_MapTo3D\map-to-3d\fichiers_osm\phase_de_developpement\filtered_data"
FILTERED_DIR = os.path.join(savepath, "filtrered_data")
os.makedirs(FILTERED_DIR, exist_ok=True)


##############################
#### Test trimesh library ####
##############################
"""
poly = Polygon([(0, 0), (10, 0), (10, 5), (0, 5)])

### Create mesh
mesh = extrude_polygon(poly, height=15.0)
box = trimesh.creation.box(extents=[1, 2, 3])
sphere = trimesh.creation.icosphere(subdivisions=3, radius=1)
sphere_ref = trimesh.creation.icosphere(subdivisions=3, radius=1)
cylinder = trimesh.creation.cylinder(radius=1, height=5)

### Import mesh
#import_mesh = trimesh.load("modele.obj")

### Merge meshes
combined = trimesh.util.concatenate([box, cylinder, sphere])

### Color mesh
# number of faces
n_faces = sphere.faces.shape[0]
n_vertex = cylinder.vertices.shape[0]

# color RGBA (uint8)
red = np.array([255, 0, 0, 255], dtype=np.uint8)

## Face color
# Repeat the same color on each face
sphere.visual.face_colors = np.tile(red, (n_faces, 1))

## Vertex color (Better for glb export)
cylinder.visual.vertex_colors = np.tile(red, (n_vertex, 1))

# Random color for each face 
mesh.visual.face_colors = np.random.randint(0, 255, (mesh.faces.shape[0], 4))

### Move object
mesh.apply_translation([10, 0, 0])
box.apply_translation([5, 5, 0])
sphere.apply_translation([5, 5, 5])
sphere_ref.apply_translation([5, 10, 5])
cylinder.apply_translation([-5, -5, 0])

### Scale object
sphere.apply_scale(2.0)

### Add to scene
scene = trimesh.Scene()
scene.add_geometry(mesh)
scene.add_geometry(box)
scene.add_geometry(sphere)
scene.add_geometry(sphere_ref)
scene.add_geometry(cylinder)
scene.add_geometry(combined)

scene.show()

scene.export("test.glb")
"""
def prepare_geom(g):
    if g.is_empty:
        return None
    if not isinstance(g, (Polygon, MultiPolygon)):
        return None

    
    if not g.is_valid:
        g = g.buffer(0)
    
    return g

def force_polygon(geom):
    if isinstance(geom, Polygon):
        return geom
    elif isinstance(geom, MultiPolygon):
        return max(geom.geoms, key=lambda g: g.area)
    else:
        return None


def extrude_from_gdf(gdf, height_attr=None, default_height=5.0, prefix="obj"):
    scene = trimesh.Scene()
    index = 0

    for _, row in gdf.iterrows():
        g = prepare_geom(row.geometry)
        if g is None:
            continue

        if height_attr and height_attr in row:
            h = float(row[height_attr]) if row[height_attr] else default_height
        else:
            h = default_height

        
        if isinstance(g, MultiPolygon):
            polygons = g.geoms
        else:
            polygons = [g]

        
        for poly in polygons:
            try:
                mesh = extrude_polygon(poly, height=h)
                scene.add_geometry(mesh, node_name=f"{prefix}_{index}")
                index += 1
            except Exception as e:
                print(f"Erreur extrusion objet {index} : {e}")
    
    return scene


def mesh_from_polygon(poly, z_base, height, color):
    meshes = []

    if isinstance(poly, MultiPolygon):
        for p in poly.geoms:
            meshes.append(mesh_from_polygon(p, height, color))
        return trimesh.util.concatenate(meshes)

    mesh = extrude_polygon(poly, height=height)

    mesh.apply_translation([0, 0, z_base])

    n_faces = mesh.faces.shape[0]
    mesh.visual.face_colors = np.tile(np.array(color, dtype=np.uint8), (n_faces, 1))
    return mesh

def mesh_from_line(line:LineString, width:float, height:float, z_base=0.0, color=[255, 255, 0, 255]):
    """Etrude line to small prism"""
    if line.is_empty:
        raise ValueError("Empty LineString")


    poly = line.buffer(width / 2, cap_style=2)

    if poly.is_empty:
        raise ValueError("Buffer resulted in empty geometry")

    if not isinstance(poly, (Polygon, MultiPolygon)):
        raise TypeError(f"Buffered line produced {poly.geom_type}")

    return mesh_from_polygon(poly, z_base, height, color=color)



def mesh_from_flat_surface(poly:Polygon, z_base=0.0, color=[100, 100, 255, 150]):
    """Flat mesg at z = 0"""
    poly = force_polygon(poly)
    if poly is None:
        raise ValueError("Geometry is not a polygon")

    mesh = extrude_polygon(poly, height=0.1)

    mesh.apply_translation([0, 0, z_base])

    n_faces = mesh.faces.shape[0]
    mesh.visual.face_colors = np.tile(np.array(color, dtype=np.uint8), (n_faces, 1))

    return mesh


def load_and_filter_osm(path, save_filtered=True, filtered_path=None):
    """
    Charge un fichier OSM/XML via OSMnx, filtre automatiquement 
    selon interest_types, et normalise les tags en un champ 'entity_type'.
    """

    print("Chargement du fichier OSM...")
    gdf = ox.features_from_xml(path)

    #Convert to metrical units
    gdf = gdf.to_crs(gdf.estimate_utm_crs())

    #Center the scene
    center = gdf.geometry.unary_union.centroid
    gdf["geometry"] = gdf.translate(xoff=-center.x, yoff=-center.y)

    # Rescale (if desired)
    # scale = 0.1  # 1 Blender unit = 10 m
    # gdf["geometry"] = gdf.scale(scale, scale, origin=(0, 0))

    print("Détection automatique des colonnes pertinentes...")
    available_tags = [col for col in interest_types if col in gdf.columns]

    if not available_tags:
        raise ValueError("Aucun des interest_types n’est présent dans ce fichier OSM !")

    print("Colonnes trouvées :", available_tags)

    # Création d’un champ unique : entity_type
    def detect_entity(row):
        for tag in available_tags:
            val = row.get(tag, None)
            if val is not None and val != "" and not (isinstance(val, float) and np.isnan(val)):
                return tag
        return None

    gdf["entity_type"] = gdf.apply(detect_entity, axis=1)

    # Filtrer uniquement ceux dont on a identifié un type
    filtered = gdf[gdf["entity_type"].notnull()].copy()
    print(f"Éléments retenus : {len(filtered)} / {len(gdf)}")

    # Option : sauvegarder un fichier nettoyé
    if save_filtered:
        if filtered_path is None:
            filtered_path = os.path.join(FILTERED_DIR, "filtered.geojson")
        print(f"Sauvegarde du fichier filtré → {filtered_path}")
        filtered.to_file(filtered_path, driver="GeoJSON")

    return filtered


def build_scene(gdf, config_path=DEFAULT_CONFIG):
    """
    Construit une scène 3D à partir d'un GeoDataFrame
    déjà filtré et contenant une colonne 'entity_type'.
    """

    with open(config_path, "r", encoding="utf-8") as f:
        rules = json.load(f)


    scene = trimesh.Scene()
    counter = 0

    for idx, row in gdf.iterrows():
        typ = row["entity_type"]
        geom = row.geometry

        if typ not in rules:
            continue

        rule = rules[typ]
        color_3Dobject = rule["color"]
        #print(rule)
        mesh_type = rule.get("mesh_type", "extrusion")
        #print(f"\nmesh_type = {mesh_type}")

        z_offset = Z_LAYERS.get(typ, 0.0)


        try:
            if mesh_type == "extrusion":
                if not isinstance(geom, (Polygon, MultiPolygon)):
                    continue
                # hauteur prioritaire : valeur du tag indiqué dans la règle (p.ex. "height")
                height_tag = rule.get("height_from_tag", None)
                if height_tag and height_tag in row and row.get(height_tag) not in [None, "", float("nan")]:
                    h = float(row[height_tag])
                else:
                    h = float(rule.get("default_height", 5.0))
                mesh = mesh_from_polygon(geom, height=h, z_base=z_offset, color=tuple(rule.get("color", [200,200,200,255])))
                #mesh = mesh_from_polygon(geom, height=0.001, color=tuple(rule.get("color", [200,200,200,255])))

            elif mesh_type == "extrusion_line":
                if not isinstance(geom, (LineString, MultiLineString)):
                    continue
                w = float(rule.get("width", 3.0))
                h = float(rule.get("height", 0.1))
                mesh = mesh_from_line(geom, width=w, height=h, z_base=z_offset, color=tuple(rule.get("color", [255,255,0,255])))
                #mesh = mesh_from_line(geom, width=0.00005, height=0.0002, color=tuple(rule.get("color", [255,255,0,255])))

            elif mesh_type == "flat":
                if not isinstance(geom, (Polygon, MultiPolygon)):
                    continue
                mesh = mesh_from_flat_surface(geom, z_base=z_offset, color=tuple(rule.get("color", [100,100,255,150])))

            else:
                print(f"Unknown mesh_type '{mesh_type}' for type '{typ}' — skipping")
                continue
            
            

            scene.add_geometry(mesh, node_name=f"{typ}_{counter}")
            counter += 1

        except Exception as e:
            print(f"Erreur lors de la création du mesh pour {typ} (index OSM {idx} (index {counter})) : {e}")
            print("mesh_type =", mesh_type)
            print("geom type =", geom.geom_type)
            print("rule =", rule)
            continue

    return scene