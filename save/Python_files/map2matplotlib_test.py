"""
File: map2maitplotlib_test.py
Author: TORREGROSSA Dylan 
Repository: https://github.com/P-Joss-P/map-to-3d.git
License: GNU GENERAL PUBLIC LICENSE Version 3 (see LICENSE file)

Description:
    file which is usefull to test the new fonctionnalities before implementing into main or other files

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
import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import os
import osmnx as ox


# function/variable import
from configuration import full_path, interest_types


gdf = ox.features_from_xml(full_path)

###################################################
#### First approach to create a matplotlib map ####
###################################################
"""

print(gdf.head())
gdf["type"].value_counts()
print(gdf.columns)
print("=========================\n")

gdf["highway"].dropna().unique()
gdf["building"].dropna().unique()
gdf["waterway"].dropna().unique()
gdf["landuse"].dropna().unique()


roads = gdf[gdf["highway"].notnull()]
buildings = gdf[gdf["building"].notnull()] # 2 types de géométrie : Polygon → batiment sumple / MultiPolygon → bâtiments complexes

water = gdf[gdf["waterway"].isin(["stream", "river"])]

forest = gdf[gdf["landuse"].isin(["forest", "grass", "meadow", "orchard"])]


#Print : 
roads.plot(figsize=(8, 8))

plt.title("roads")

buildings["geom_type"] = buildings.geometry.apply(lambda g: g.geom_type) #ajout de colone geom_type pour déterminer la géimétrie du batiment


colors = {
    "Polygon": "gray",
    "MultiPolygon": "blue"
}

buildings.plot(
    figsize=(10, 10),
    color=buildings["geom_type"].map(colors),
    edgecolor="black",
    linewidth=0.5
)
plt.title("buidings")

#print(buildings["height"])
print(buildings["geom_type"].value_counts())


water.plot(figsize=(8, 8))

plt.title("water")
forest.plot(figsize=(8, 8))

plt.title("forest")

gdf.plot(figsize=(10, 10))
plt.title("rendu final")


plt.show()


#type de géométrie
gdf.geometry.geom_type.value_counts()


#Export vers un fichier GeoJSON
buildings.to_file("buildings.geojson", driver="GeoJSON")

"""


#####################################################)####)#######
#### Second approach to create a matplotlib map (more general)####
#####################################################)####)#######

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
plt.show()
