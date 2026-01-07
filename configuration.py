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
import os

path = r"C:\data\Ecole\ENSE3\Cours\2A\Semestre1\Parcours_numerique\Projet_MapTo3D\map-to-3d\fichiers_osm\phase_de_developpement"
Name_OSM_File = "echantillon_premiers_tests.osm"
full_path = os.path.join(path, Name_OSM_File)

BASE_DIR = r"C:\data\Ecole\ENSE3\Cours\2A\Semestre1\Parcours_numerique\Projet_MapTo3D\map-to-3d\Config"
DEFAULT_CONFIG = os.path.join(BASE_DIR, "mapping_entities.json")

savepath = r"C:\data\Ecole\ENSE3\Cours\2A\Semestre1\Parcours_numerique\Projet_MapTo3D\map-to-3d\fichiers_osm\phase_de_developpement\filtered_data"
FILTERED_DIR = os.path.join(savepath, "filtrered_data")

Name_Fig_save_Folder = "Fig_save"
save_folder_path = os.path.join(path, Name_Fig_save_Folder)

Save_osm_to_csv_path = r"C:\data\Ecole\ENSE3\Cours\2A\Semestre1\Parcours_numerique\Projet_MapTo3D\map-to-3d\fichiers_osm\phase_de_developpement\csv_export"


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