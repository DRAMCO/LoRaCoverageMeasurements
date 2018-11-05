"""
    ____  ____      _    __  __  ____ ___
   |  _ \|  _ \    / \  |  \/  |/ ___/ _ \
   | | | | |_) |  / _ \ | |\/| | |  | | | |
   | |_| |  _ <  / ___ \| |  | | |__| |_| |
   |____/|_| \_\/_/   \_\_|  |_|\____\___/
                             research group
                               dramco.be/

    KU Leuven - Technology Campus Gent,
    Gebroeders De Smetstraat 1,
    B-9000 Gent, Belgium

           File: plt_heatmap.py
        Created: 2018-10-26
         Author: Gilles Callebaut
        Version: 1.0
    Description:
"""

import os

import folium
import numpy as np
import pandas as pd
from folium.map import Marker
from folium.plugins import HeatMap, MarkerCluster

import util as util

PLOT_SNR = False
PLOT_RSS = not PLOT_SNR


time_string_file = "2018_10_31"

currentDir = os.path.dirname(os.path.abspath(__file__))
input_path = os.path.abspath(os.path.join(
    currentDir, '..', 'result'))
input_file = "preprocessed_data_{}.pkl".format(time_string_file)
input_file_path = os.path.join(input_path, input_file)

output_fig_pdf = os.path.join(
    input_path, 'path_loss_model_{}.pdf'.format(time_string_file))
output_fig_pgf = os.path.join(
    input_path, 'path_loss_model_{}.pgf'.format(time_string_file))

for_map = pd.read_pickle(input_file_path)
for_map = util.onlyPackets(for_map)


output_file_name = "heatmap_SNR.html" if PLOT_SNR else "heatmap_RSS.html"
output_file = os.path.abspath(os.path.join(
    currentDir, '..', 'result', output_file_name))

grid_size = 25


CENTER = [51.0595576, 3.7085241]

for_map = for_map[(for_map['time'].dt.day == 30) | (
    for_map['time'].dt.day == 31)]  # filter only today

hmap = folium.Map(location=CENTER, zoom_start=18,  tiles="cartodbpositron", control_scale = True)

folium.Circle(
    radius=1,
    location=CENTER,
    color='crimson',
    fill=True,
    fill_color='crimson'
).add_to(hmap)


grid, colormap = util.get_geojson_grid(
    for_map, grid_size, PLOT_SNR)
hmap.add_child(colormap)

for i, geo_json in enumerate(grid):
    gj = folium.GeoJson(geo_json,
                        style_function=lambda feature: {
                            'fillColor': colormap(feature["properties"]["val"]),
                            'weight': 1,
                            'opacity': 0,
                            'fillOpacity': 0.55 if feature["properties"]["show"] else 0,
                            'color': 'white'
                        }, overlay=True)

    hmap.add_child(gj)

# folium.PolyLine(list(zip(for_map_gps.lat.values, for_map_gps.lon.values)),
#                color="red", weight=2, opacity=0.4).add_to(hmap)

hmap.save(output_file)
