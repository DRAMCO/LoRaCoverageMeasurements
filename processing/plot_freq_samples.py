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
import seaborn as sns
import matplotlib.pyplot as plt

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
            #num_bins = config_measurement[measurement]["freq_samples_bins"]
            input_file_path = os.path.join(
                input_path, measurement, input_file_name)
            for_map = pd.read_pickle(input_file_path)
            for_map = util.onlyPackets(for_map)

            #dist_in_bins = pd.cut(x=for_map.distance, bins=num_bins)
            #rss_in_bins = pd.cut(x=for_map.rssi, bins=num_bins)
#
            #ax = sns.heatmap(for_map.pivot_table("distance", "rssi"))
            #plt.show()
#
            #sns.distplot(for_map.rssi)
            sns.jointplot(x=for_map.distance, y=for_map.rssi, kind="hex")
            plt.show()
            print("--------------------- DONE HEATMAP ---------------------")
