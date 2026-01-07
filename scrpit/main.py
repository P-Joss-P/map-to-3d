"""
File: main.py
Author: TORREGROSSA Dylan 
Repository: https://github.com/P-Joss-P/map-to-3d.git
License: GNU GENERAL PUBLIC LICENSE Version 3 (see LICENSE file)

Description:
    Main python file that will contain all the executable functions to run the entire project 

Usage:
    None

Dependencies:
    - Python 3.13+
    - libraries used : os, osmnx


"""

# library import
import os
import osmnx as ox

# function/variable import
from configuration import full_path, interest_types, save_folder_path, FILTERED_DIR
from functions import osm2plot
from functions import build_scene, load_and_filter_osm

# General settings and load data
os.makedirs(FILTERED_DIR, exist_ok=True) # creation of filter_directory

gdf = ox.features_from_xml(full_path)

# Plot interest_types
#osm2plot(gdf, interest_types, True, save_folder_path, show_setting=False)

# Scene creation and operation
gdf = load_and_filter_osm(full_path, save_filtered=True)
scene = build_scene(gdf)  # utilise mapping_entities.json par défaut

scene.export("map3d.glb")
scene.show()



