"""
File: main.py
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
    - libraries used : matplotlib, numpy, os, osmnx

Notes:
    - Add any implementation detail important for developers.
    - Keep this section optional.

"""

# library import
import os
import osmnx as ox

# function/variable import
from configuration import full_path, interest_types, save_folder_path, FILTERED_DIR
from functions import osm2plot
from functions import build_scene, load_and_filter_osm


os.makedirs(FILTERED_DIR, exist_ok=True) # creation of filter_directory

gdf = ox.features_from_xml(full_path)


#osm2plot(gdf, interest_types, True, save_folder_path, show_setting=False)

gdf = load_and_filter_osm(full_path, save_filtered=True)
scene = build_scene(gdf)  # utilise mapping_entities.json par défaut
scene.export("map3d.glb")
scene.show()
