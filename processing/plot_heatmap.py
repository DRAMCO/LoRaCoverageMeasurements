import json
import math
import os

import folium
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from folium.map import Marker
from folium.plugins import HeatMap, MarkerCluster

import util as util

RSS_SERIES = "rssi"
SNR_SERIES = "snr"
LAT_SERIES = "lat"
LON_SERIES = "lon"
LAT_GRID_SERIES = "lat_discrete"
LON_GRID_SERIES = "lon_discrete"

CENTER = [51.0606959, 3.7070895]

HEADER = ["sat", "satValid", "hdopVal", "hdopValid", "lat", "lon", "locValid", "age", "ageValid", "alt",
          "altValid", "course", "courseValid", "speed", "speedValid", "rssi", "snr", "freqError", "tp", "sf", "isPacket"]

currentDir = os.path.dirname(os.path.abspath(__file__))
data_file = os.path.abspath(os.path.join(currentDir, '..', 'data', "PACKETS.TXT"))
output_file = os.path.abspath(os.path.join(currentDir, '..', 'result', "heatmap.html"))

grid_size = 10

for_map = pd.read_csv(data_file, sep=',', header=None,
                      names=HEADER)

util.addDistanceTo(for_map, CENTER)
util.addPathLoss(for_map)


for_map_gps = for_map.copy()

for_map_gps = for_map_gps[for_map_gps.sat > 0]
for_map_gps = for_map_gps[for_map_gps.ageValid > 0]
for_map_gps = for_map_gps[for_map_gps.hdopVal < 75]

for_map = for_map[for_map.isPacket > 0]
for_map = for_map[for_map.locValid > 0]


for_map[SNR_SERIES] = util.normalize(data=for_map[SNR_SERIES])
for_map[RSS_SERIES] = util.normalize(
    data=for_map[RSS_SERIES], min_val=-130, max_val=-50)

print(for_map[SNR_SERIES])

max_lat = for_map[LAT_SERIES].max()
max_lon = for_map[LON_SERIES].max()

min_lat = for_map[LAT_SERIES].min()
min_lon = for_map[LON_SERIES].min()

upper_right = [max_lat, max_lon]
lower_left = [min_lat, min_lon]
center = [lower_left[0]+(upper_right[0]-lower_left[0]) /
          2, lower_left[1]+(upper_right[1]-lower_left[1])/2]


hmap = folium.Map(location=center, zoom_start=18, )  # tiles="Stamen Toner")


folium.Circle(
    radius=1,
    location=CENTER,
    color='crimson',
    fill=True,
    fill_color='crimson'
).add_to(hmap)


for_map[LAT_GRID_SERIES] = util.normalize(
    data=for_map[LAT_SERIES], num_bins=grid_size)
for_map[LON_GRID_SERIES] = util.normalize(
    data=for_map[LON_SERIES], num_bins=grid_size)

print(for_map)
colors = np.zeros((grid_size, grid_size))
num_values = np.zeros((grid_size, grid_size))
transparant_matrix = np.zeros((grid_size, grid_size))

print(for_map)
for idx, row in for_map.iterrows():
    row_idx = int(row[LAT_GRID_SERIES])
    col_idx = int(row[LON_GRID_SERIES])
    colors[row_idx][col_idx] += row[RSS_SERIES]
    num_values[row_idx][col_idx] += 1
    transparant_matrix[row_idx][col_idx] = 1

colors = colors/num_values


grid = util.get_geojson_grid(
    upper_right, lower_left, colors, transparant_matrix, grid_size)


for i, geo_json in enumerate(grid):
    gj = folium.GeoJson(geo_json,
                        style_function=lambda feature: {
                            'fillColor': feature["properties"]["color"],
                            'weight': 1,
                            'opacity': 0,
                            'fillOpacity': 0.55 if feature["properties"]["show"] else 0,
                            'color': 'white'
                        }, overlay=True)

    hmap.add_child(gj)

folium.PolyLine(list(zip(for_map_gps.lat.values, for_map_gps.lon.values)),
                color="red", weight=2, opacity=0.55).add_to(hmap)


# hmap.add_child(hm_wide)
hmap.save(output_file)
