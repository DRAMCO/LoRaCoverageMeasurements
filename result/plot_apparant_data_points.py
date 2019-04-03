r"""
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

           File:
        Created: 2018-10-30
         Author: Gilles Callebaut
    Description:
"""

import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

currentDir = os.path.dirname(os.path.abspath(__file__))
path_to_measurements = os.path.abspath(os.path.join(
    currentDir, '..', 'data'))

input_path = os.path.abspath(os.path.join(
    currentDir, '..', 'result'))
input_file_name = "processed_data_with_censored_data.pkl"
input_file_path = os.path.join(input_path, input_file_name)

PL_THRESHOLD = 148

result = dict()

with open(os.path.join(path_to_measurements, "measurements.json")) as f:
    config = json.load(f)
    measurements = config["measurements"]

    data = pd.read_pickle(input_file_path)

    N = 100

    for measurement in measurements:
        print(F"--------------------- {measurement} ---------------------")
        df = data[measurement]["data"]
        d = df["distance"].values

        (hist_lin, *_) = np.histogram(d, bins=N)
        (hist_log, *_) = np.histogram(d, bins=N)
        (hist_sq, *_) = np.histogram(np.power(d,2), bins=N)

        plt.plot(hist_lin)
        plt.plot(hist_log)
        plt.plot(hist_sq)

        plt.show()

        # Ns = len(d)
        #
        # w = (Ns / N)
        #
        # (hist, bin_edges) = np.histogram(d, bins=N)
        # inds = np.digitize(d, bin_edges)
        #
        # w_d = [w * (1 / hist[np.minimum((i - 1), len(bin_edges) - 2)]) for i in inds]
        #
        # (hist_log, bin_edges_log) = np.histogram(np.log10(d), bins=N)
        # inds = np.digitize(np.log10(d), bin_edges_log)
        # w_log = [w * (1 / hist_log[np.minimum((i - 1), len(bin_edges) - 2)]) for i in inds]
        #
        # (hist_sq, bin_edges_sq) = np.histogram(d ** 2, bins=N)
        # inds = np.digitize(d ** 2, bin_edges_sq)
        # w_sq = [w * (1 / hist_sq[np.minimum((i - 1), len(bin_edges) - 2)]) for i in inds]
        #
        # # apparant_data_points = zip(d, w_d, w_log, w_sq)
        #
        # num_bins = int(20 / (d.max() - d.min()))
        # (hist, bin_edges) = np.histogram(d, bins=N)
        #
        # plt.plot(bin_edges[:-1], hist)
        # plt.plot(bin_edges[:-1], hist * w_d)
        # plt.plot(bin_edges[:-1], hist * w_log)
        # plt.plot(bin_edges[:-1], hist * w_sq)

        plt.show()
