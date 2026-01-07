"""
File: functions.py
Author: TORREGROSSA Dylan 
Repository: https://github.com/P-Joss-P/map-to-3d.git
License: GNU GENERAL PUBLIC LICENSE Version 3 (see LICENSE file)

Description:
    This file will allow users to keep located at the same place all the information they need to enter.

Usage:
    - python main.py 

Dependencies:
    - Python 3.13+
    - library used : genericpath, json, numpy, matplotlib, os, osmnx, shapely, trimesh

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
from shapely.geometry import LineString, MultiLineString, MultiPolygon, Polygon
import trimesh
from trimesh.creation import extrude_polygon

# function/variable import
from configuration import DEFAULT_CONFIG, FILTERED_DIR, interest_types
from constant import Z_LAYERS


###########################
####### OSM to plot #######
###########################

def osm2plot(gdf, interest_types, save_setting, save_folder_path, show_setting):

    """
    This function will allow users to plot figures which will contain the extracted values of osm files. 
    The values which are print could be modified thank's to configuration.py files throught the list interest_types.
    """

    nb_types = len(interest_types)

    # Automaticly select nb_types colors thank's to matplotlib.colors methode
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


    ax.legend(handles=legend_patches, title="Categories",
            loc="upper left", bbox_to_anchor=(1, 1))

    plt.title("Final plot type colored")

    fig = plt.figure()


    # Save plot as png files in save_folder_path folder
    if save_setting == True:
        if not exists(save_folder_path):
            os.mkdir(save_folder_path)

        fig.savefig(os.path.join(save_folder_path, "Final plot type colored"))
    
    # Show condition
    if show_setting == True:
        plt.show()


########################
####### 3D scene #######
########################

def load_and_filter_osm(path, save_filtered=True, filtered_path=None):
    """
    Load an OSM/XML file thank's OSMnx lib, automaticly filtered the values  
    relative to interest_types list. 
    This function will also normalized tags in a single data field 'entity_type'.
    """

    # Load osm file 
    print("OSM file is loading...")
    gdf = ox.features_from_xml(path)    


    # Graphics settings    
    gdf = gdf.to_crs(gdf.estimate_utm_crs())    # Convert to metrical units

    center = gdf.geometry.unary_union.centroid      #Center the scene
    gdf["geometry"] = gdf.translate(xoff=-center.x, yoff=-center.y)

    # Rescale (if desired)
    # scale = 0.1  # 1 Blender unit = 10 m
    # gdf["geometry"] = gdf.scale(scale, scale, origin=(0, 0))

    print("Automatic detection of relevant columns...")
    available_tags = [col for col in interest_types if col in gdf.columns]

    if not available_tags:
        raise ValueError("None of the interest_types are present in this OSM file!")

    print("Founded columns :", available_tags)

    def detect_entity(row):
        """
        Creating a unique field : entity_type
        """
        for tag in available_tags:
            val = row.get(tag, None)
            if val is not None and val != "" and not (isinstance(val, float) and np.isnan(val)):
                return tag
        return None

    gdf["entity_type"] = gdf.apply(detect_entity, axis=1)

    # Filter only those for which a type has been identified
    filtered = gdf[gdf["entity_type"].notnull()].copy()
    print(f"Éléments retenus : {len(filtered)} / {len(gdf)}")

    # Option : Save cleaned file
    if save_filtered:
        if filtered_path is None:
            filtered_path = os.path.join(FILTERED_DIR, "filtered.geojson")
        print(f"Cleaned file has been saved → {filtered_path}")
        filtered.to_file(filtered_path, driver="GeoJSON")

    return filtered


def build_scene(gdf, config_path=DEFAULT_CONFIG):
    """
    Build a 3D scene from a GeoDataFrame already filtered and which contain 
    'entity_type' columns.
    """

    # Load and read json file
    with open(config_path, "r", encoding="utf-8") as f:
        rules = json.load(f)    

    # Variable and scene initialization 
    scene = trimesh.Scene()
    counter = 0

    for idx, row in gdf.iterrows():
        typ = row["entity_type"]
        geom = row.geometry

        # Select only types which are in json file
        if typ not in rules:
            continue

        rule = rules[typ]
        color_3Dobject = rule["color"]

        mesh_type = rule.get("mesh_type", "extrusion")

        z_offset = 0 # default value
        z_offset = Z_LAYERS.get(typ, 0.0) # values taken in constant.py file


        try:
            if mesh_type == "extrusion":
                if not isinstance(geom, (Polygon, MultiPolygon)):
                    continue
                # priority height : The value of the tag indicated in rules

                height_tag = rule.get("height_from_tag", None)
                if height_tag and height_tag in row and row.get(height_tag) not in [None, "", float("nan")]:
                    h = float(row[height_tag])
                else:
                    h = float(rule.get("default_height", 5.0))
                mesh = mesh_from_polygon(geom, height=h, color=tuple(rule.get("color")))

            elif mesh_type == "extrusion_line":
                if not isinstance(geom, (LineString, MultiLineString)):
                    continue
                w = float(rule.get("width", 3.0))
                h = float(rule.get("height", 0.1))
                mesh = mesh_from_line(geom, width=w, height=h, color=tuple(rule.get("color")))

            elif mesh_type == "flat":
                if not isinstance(geom, (Polygon, MultiPolygon)):
                    continue
                mesh = mesh_from_flat_surface(geom, color=tuple(rule.get("color")))

            else:
                print(f"Unknown mesh_type '{mesh_type}' for type '{typ}' — skipping")
                continue
            
            # Secure the export 
            mesh.apply_translation([0, 0, z_offset])
            mesh.apply_transform(trimesh.transformations.identity_matrix())

            scene.add_geometry(mesh, node_name=f"{typ}_{counter}")
            counter += 1

        except Exception as e:
            print(f"Error creating mesh for {typ} (index OSM {idx} (index {counter})) : {e}")
            print("mesh_type =", mesh_type)
            print("geom type =", geom.geom_type)
            print("rule =", rule)
            continue

    return scene


def mesh_from_polygon(poly, height, color):
    """This function will create a new mesh for a polygon type osm object."""
    meshes = []

    if isinstance(poly, MultiPolygon):
        for p in poly.geoms:
            meshes.append(mesh_from_polygon(p, height, color))
        return trimesh.util.concatenate(meshes)

    mesh = extrude_polygon(poly, height=height)     # Extrude the geometry of a given height

    # Color the vertex of the mesh
    n_vertices = mesh.vertices.shape[0]
    mesh.visual.vertex_colors = np.tile(np.array(color, dtype=np.uint8), (n_vertices, 1))
    return mesh

def mesh_from_line(line:LineString, width:float, height:float, color=[255, 255, 0, 255]):
    """Extrude line to small prism"""
    if line.is_empty:
        raise ValueError("Empty LineString")

    poly = line.buffer(width / 2, cap_style=2)

    if poly.is_empty:
        raise ValueError("Buffer resulted in empty geometry")

    if not isinstance(poly, (Polygon, MultiPolygon)):
        raise TypeError(f"Buffered line produced {poly.geom_type}")

    return mesh_from_polygon(poly, height, color=color)

def mesh_from_flat_surface(poly:Polygon, color=[100, 100, 255, 150]):
    """Extrude Flat mesh from z = 0"""
    height = 0.1 # default heignt for flat surface
    poly = force_polygon(poly)
    if poly is None:
        raise ValueError("Geometry is not a polygon")

    return mesh_from_polygon(poly, height, color=color)

def force_polygon(geom):
    if isinstance(geom, Polygon):
        return geom
    elif isinstance(geom, MultiPolygon):
        return max(geom.geoms, key=lambda g: g.area)
    else:
        return None