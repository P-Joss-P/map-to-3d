"""
File: configuration.py
Author: TORREGROSSA Dylan 
Repository: https://github.com/P-Joss-P/map-to-3d.git
License: GNU GENERAL PUBLIC LICENSE Version 3 (see LICENSE file)

Description:
    This file will allow users to keep located at the same place all the information they need to setup all the project

Usage:
    - python main.py 
    - python ident_tag.py 
    - python functions.py

Dependencies:
    - Python 3.13+
    - library used : os


"""


# library import
import os

# General settings path
savepath = r"C:\data\Ecole\ENSE3\Cours\2A\Semestre1\Parcours_numerique\Projet_MapTo3D\map-to-3d\fichiers_osm\phase_de_developpement\filtered_data"
FILTERED_DIR = os.path.join(savepath, "filtrered_data")


# osm files path 
path = r"C:\data\Ecole\ENSE3\Cours\2A\Semestre1\Parcours_numerique\Projet_MapTo3D\map-to-3d\fichiers_osm\phase_de_developpement"
Name_OSM_File = "echantillon_premiers_tests.osm"
full_path = os.path.join(path, Name_OSM_File)

# Ident_tags usefull paths
Save_osm_to_csv_path = r"C:\data\Ecole\ENSE3\Cours\2A\Semestre1\Parcours_numerique\Projet_MapTo3D\map-to-3d\fichiers_osm\phase_de_developpement\csv_export"


# Osm2plot usefull paths 
Name_Fig_save_Folder = "Fig_save"
save_folder_path = os.path.join(path, Name_Fig_save_Folder)

# Build_scene usefull paths 
BASE_DIR = r"C:\data\Ecole\ENSE3\Cours\2A\Semestre1\Parcours_numerique\Projet_MapTo3D\map-to-3d\Config"
DEFAULT_CONFIG = os.path.join(BASE_DIR, "mapping_entities.json")



interest_types = [  "landuse",
                    "waterway",
                    "building",
                    "crop",
                    "electrified",
                    "highway",
                    "railway",
                    "trees",
                    "barrier",
                    "bridge",
                ]