"""
File: configuration.py
Author: TORREGROSSA Dylan 
Repository: https://github.com/P-Joss-P/map-to-3d.git
License: GNU GENERAL PUBLIC LICENSE Version 3 (see LICENSE file)

Description:
    This file will allow users to keep located at the same place all the information they need to enter.

Usage:
    - python main.py 
    - python ident_tag.py 


Example:
    python script_name.py --input data.osm --verbose

Dependencies:
    - Python 3.13+
    - library used : os

Notes:
    - Add any implementation detail important for developers.
    - Keep this section optional.

"""

# library import
from genericpath import exists
import json
import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import os
import osmnx as ox
from shapely.geometry import Polygon, LineString, MultiPolygon, MultiLineString
import trimesh
from trimesh.creation import extrude_polygon

# function/variable import
from configuration import DEFAULT_CONFIG, interest_types, FILTERED_DIR
from constant import Z_LAYERS


###########################
####### OSM to plot #######
###########################

def osm2plot(gdf, interest_types, save_setting, save_folder_path, show_setting):

    nb_types = len(interest_types)

    colormap = cm.get_cmap("jet", nb_types)
    colors = [mcolors.to_hex(colormap(i)) for i in range(nb_types)]
    legend_patches = []


    # Each type plot 
    for i in range(nb_types):
        color = colors[i]
        type_name = interest_types[i]

        mask = gdf[type_name].notnull()
        
        if mask.any():
            fig, ax = plt.subplots(figsize=(10, 10))
            gdf[mask].plot(
                ax = ax,
                color=color
            )
        plt.title(type_name)
        if save_setting == True:
            if not exists(save_folder_path):
                os.mkdir(save_folder_path)

            fig.savefig(os.path.join(save_folder_path, type_name))

    # Global plot
    fig, ax = plt.subplots(figsize=(10, 10))

    for i in range(nb_types):
        color = colors[i]
        type_name = interest_types[i]

        mask = gdf[type_name].notnull()
        
        if mask.any():
            gdf[mask].plot(
                ax = ax,
                color=color, 
                label=type_name
            )

        legend_patches.append(mpatches.Patch(color=color, label=type_name))


    ax.legend(handles=legend_patches, title="Catégories",
            loc="upper left", bbox_to_anchor=(1, 1))

    plt.title("Final plot type colored")

    fig = plt.figure()

    if save_setting == True:
        if not exists(save_folder_path):
            os.mkdir(save_folder_path)

        fig.savefig(os.path.join(save_folder_path, "Final plot type colored"))
    
    if show_setting == True:
        plt.show()


########################
####### 3D scène #######
########################

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

        mesh_type = rule.get("mesh_type", "extrusion")


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

            elif mesh_type == "extrusion_line":
                if not isinstance(geom, (LineString, MultiLineString)):
                    continue
                w = float(rule.get("width", 3.0))
                h = float(rule.get("height", 0.1))
                mesh = mesh_from_line(geom, width=w, height=h, z_base=z_offset, color=tuple(rule.get("color", [255,255,0,255])))

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

def force_polygon(geom):
    if isinstance(geom, Polygon):
        return geom
    elif isinstance(geom, MultiPolygon):
        return max(geom.geoms, key=lambda g: g.area)
    else:
        return None