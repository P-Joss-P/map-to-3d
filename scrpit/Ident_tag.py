"""
File: ident_tag.py
Author: TORREGROSSA Dylan 
Repository: https://github.com/P-Joss-P/map-to-3d.git
License: GNU GENERAL PUBLIC LICENSE Version 3 (see LICENSE file)

Description:
    This file will allow you to read the OSM file, find all the tags that are used on it, adding them on a csv file with various other information.
    The csv file will contain : 
        - tag
        - subtag
        - full_key
        - occurences
        - used_by_buildings

Usage:
    None


Dependencies:
    - Python 3.13+
    - library used : os, osmnx, pandas

"""


# Library import
import os
import osmnx as ox
import pandas as pd 

# function/variable import
from configuration import full_path, Save_osm_to_csv_path, Name_OSM_File


# Initialization of variables
gdf = ox.features_from_xml(full_path)

rows = []


# Building of tags' table
for col in gdf.columns:
    count = gdf[col].notnull().sum()
    if count == 0:
        continue

    # Tags/subtags ? 
    if ":" in col:
        parent, child = col.split(":", 1)
    else:
        parent, child = col, ""

    # Use for buildings ? 
    if "building" in gdf.columns:
        used_by_buildings = gdf[gdf["building"].notnull()][col].notnull().sum() > 0
    else:
        used_by_buildings = False

    # Creation of table
    rows.append({
        "tag": parent,
        "subtag": child,
        "full_key": col,
        "occurences": count,
        "used_by_buildings": used_by_buildings
    })

# Convert to DataFrame
df_tags = pd.DataFrame(rows)


# Export to CSV
output_file = os.path.join(Save_osm_to_csv_path, f"osm_tag_catalog_{Name_OSM_File}.csv")
df_tags.to_csv(output_file, index=False)

print("File 'osm_tag_catalog.csv'succesfully generated")


