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
    Description:
"""

import json
import os

import folium
import numpy as np
import pandas as pd
from folium.map import Marker
from folium.plugins import HeatMap, MarkerCluster

import util as util


currentDir = os.path.dirname(os.path.abspath(__file__))
path_to_measurements = os.path.abspath(os.path.join(
    currentDir, '..', 'data'))
processing_path = os.path.abspath(os.path.join(
    currentDir, '..', 'processing'))
input_path = os.path.abspath(os.path.join(
    currentDir, '..', 'result'))
input_file_name = "preprocessed_data.pkl"


with open(os.path.join(processing_path, "conf.json")) as config_file:
    config_plot = json.load(config_file)["heatmap"]
    grid_size = config_plot["grid_size"]
    plot_snr = config_plot["plot_snr"]
    plot_rss = config_plot["plot_rss"]

    with open(os.path.join(path_to_measurements, "measurements.json")) as f:
        config_measurement = json.load(f)
        measurements = config_measurement["measurements"]
        for measurement in measurements:
            print(
                "--------------------- HEATMAP {} ---------------------".format(measurement))
            CENTER = config_measurement[measurement]["center"]
            input_file_path = os.path.join(
                input_path, measurement, input_file_name)
            for_map = pd.read_pickle(input_file_path)
            for_map = util.onlyPackets(for_map)

            if plot_snr:

                hmap = folium.Map(location=CENTER, zoom_start=18,
                                  tiles="cartodbpositron", control_scale=True)

                circle = folium.Circle(
                    radius=1,
                    location=CENTER,
                    color='crimson',
                    fill=True,
                    fill_color='crimson'
                ).add_to(hmap)

                grid, colormap = util.get_geojson_grid(
                    for_map, grid_size, True)

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

                output_file = os.path.join(
                    input_path, measurement, "heatmap_SNR.html")
                hmap.save(output_file)
                print(" Saving to {}".format(output_file))

            if plot_rss:

                hmap = folium.Map(location=CENTER, zoom_start=18,
                                  tiles="cartodbpositron", control_scale=True)

                circle = folium.Circle(
                    radius=1,
                    location=CENTER,
                    color='crimson',
                    fill=True,
                    fill_color='crimson'
                ).add_to(hmap)

                grid, colormap = util.get_geojson_grid(
                    for_map, grid_size, False)

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

                output_file = os.path.join(
                    input_path, measurement, "heatmap_RSS.html")
                hmap.save(output_file)
                print(" Saving to {}".format(output_file))

            print("--------------------- DONE HEATMAP ---------------------")

    # currentDir = os.path.dirname(os.path.abspath(__file__))

    # output_file_name = "heatmap_SNR.html" if PLOT_SNR else "heatmap_RSS.html"
# output_file = os.path.abspath(os.path.join(
#     currentDir, '..', 'result', 'seaside', output_file_name))


# conf_file = os.path.abspath(os.path.join(
#     currentDir, '..', 'data', 'seaside', 'all', 'conf.json'))
# with open(conf_file) as f:
#     data = json.load(f)
# CENTER = data["center"]

# hmap = folium.Map(location=CENTER, zoom_start=18,  tiles="cartodbpositron", control_scale = True)

# folium.Circle(
#     radius=1,
#     location=CENTER,
#     color='crimson',
#     fill=True,
#     fill_color='crimson'
# ).add_to(hmap)


# grid, colormap = util.get_geojson_grid(
#     for_map, grid_size, PLOT_SNR)
# hmap.add_child(colormap)

# for i, geo_json in enumerate(grid):
#     gj = folium.GeoJson(geo_json,
#                         style_function=lambda feature: {
#                             'fillColor': colormap(feature["properties"]["val"]),
#                             'weight': 1,
#                             'opacity': 0,
#                             'fillOpacity': 0.55 if feature["properties"]["show"] else 0,
#                             'color': 'white'
#                         }, overlay=True)

#     hmap.add_child(gj)

# # folium.PolyLine(list(zip(for_map_gps.lat.values, for_map_gps.lon.values)),
# #                color="red", weight=2, opacity=0.4).add_to(hmap)

# hmap.save(output_file)
