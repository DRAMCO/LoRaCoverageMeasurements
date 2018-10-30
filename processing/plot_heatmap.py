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
import glob

import seaborn as sns; sns.set()
import util as util

PLOT_SNR = False
PLOT_RSS = not PLOT_SNR

RSS_SERIES = "rssi"
SNR_SERIES = "snr"
LAT_SERIES = "lat"
LON_SERIES = "lon"
LAT_GRID_SERIES = "lat_discrete"
LON_GRID_SERIES = "lon_discrete"



HEADER = ["time", "sat", "satValid", "hdopVal", "hdopValid", "vdopVal", "pdopVal", "lat", "lon", "locValid", "age",
          "ageValid", "alt", "altValid", "course", "courseValid", "speed", "speedValid", "rssi", "snr", "freqError",  "sf", "isPacket"]

# HEADER = ["time", "sat", "satValid", "hdopVal", "hdopValid", "lat", "lon", "locValid", "age", "ageValid", "alt",
#         "altValid", "course", "courseValid", "speed", "speedValid", "rssi", "snr", "freqError",  "sf", "isPacket"]

currentDir = os.path.dirname(os.path.abspath(__file__))
#data_file = os.path.abspath(os.path.join(
#    currentDir, '..', 'data', "306309"))

path = os.path.abspath(os.path.join(
    currentDir, '..', 'data', 'measurements_2'))                     # use your path
# advisable to use os.path.join as this makes concatenation OS independent
all_files = glob.glob(os.path.join(path, "*.csv"))

print(all_files)
#os.system("pause")

df_from_each_file = (pd.read_csv(f, sep=',', header=None, names=HEADER) for f in all_files)
concatenated_df = pd.concat(df_from_each_file, ignore_index=True)


output_file_name = "heatmap_SNR.html" if PLOT_SNR else "heatmap_RSS.html"
output_file = os.path.abspath(os.path.join(
    currentDir, '..', 'result', output_file_name))

grid_size = 50

for_map = concatenated_df

#for_map = pd.read_csv(data_file, sep=',', header=None,
#                      names=HEADER)

for_map = util.sort(for_map)
for_map['time'] = pd.to_datetime(
    for_map['time'], format='%m/%d/%Y %H:%M:%S ', utc=True)
print(for_map)

for_map.sort_values(by='time')
print(for_map.rss)
for_map_gps = for_map.copy()

for_map = for_map[for_map.isPacket > 0]


CENTER = [51.0595576, 3.7085241]
util.addDistanceTo(for_map, CENTER)
util.addPathLossTo(for_map)

for_map = for_map[for_map['time'].dt.day == 30] # filter only today

print(for_map)


#for_map.plot.scatter(x='distance', y='pl_db', c='sf',  colormap='viridis')
#plt.show()
#
d0 = 20 #old data
#
for_map = for_map[for_map.distance > 20]
for_map['distance_log'] = 10*np.log10(for_map['distance']/20)
print(for_map['distance_log'])
sns.lmplot(x='distance_log', y='pl_db', hue='sf', data=for_map)


from statsmodels.formula.api import ols
model = ols("pl_db ~ distance_log", for_map).fit()
print(model.params)
pl0, n = model.params
print(model.bse)
print(model.summary())

#plt.scatter(y=for_map['pl_db'], x=for_map['distance_log'])
#print(n)
#print(pl0)

from scipy import stats
slope, intercept, r_value, p_value, std_err = stats.linregress(
    for_map['distance_log'], for_map['pl_db'])

print(slope, intercept, r_value, p_value, std_err)

for_map['epl'] = n*for_map['distance_log']+pl0
for_map['epl_free'] = 2*for_map['distance_log']+pl0
sigma = np.std(for_map['epl'] - for_map['pl_db'])
print(sigma)
sns.scatterplot(x='distance_log', y='epl', data=for_map)


plt.plot([0, for_map['distance_log'].max()], [137+20, 137+20])
#plt.plot(x=for_map['distance_log'].values, y=y)
#plt.plot(x=for_map['distance_log'].values, y=y_free_space)
plt.show()  

hmap = folium.Map(location=CENTER, zoom_start=18, )  # tiles="Stamen Toner")


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

#folium.PolyLine(list(zip(for_map_gps.lat.values, for_map_gps.lon.values)),
#                color="red", weight=2, opacity=0.4).add_to(hmap)

hmap.save(output_file)
