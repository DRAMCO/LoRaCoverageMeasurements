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
        Created: 2018-10-30
         Author: Gilles Callebaut
    Description:
"""

import json
import math
import os
from functools import reduce, partial
from math import sqrt

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import util as util

import math

BIN_SIZE_DISTANCE = 0.001 # in degrees
OUTPUT_IMG_FORMAT = "png"


currentDir = os.path.dirname(os.path.abspath(__file__))
path_to_measurements = os.path.abspath(os.path.join(
    currentDir, '..', 'data'))
input_path = os.path.abspath(os.path.join(
    currentDir, '..', 'result'))
input_file_name = "preprocessed_data.pkl"

output_path = input_path
output_file_name = "preprocessed_averaged_data.pkl"


def hexagonify(x, y, values=None, func=None, val_name=None,  x_name=None, y_name=None):

    if val_name is None:
        val_name = "val"

    if x_name is None:
        x_name = "x"
    if y_name is None:
        y_name = "y"

    hexagonized_list = list()

    fig = plt.figure()
    fig.set_visible(False)
    if values is None:
        image = plt.hexbin(x=x, y=y)
    else:
        if func is not None:
            image = plt.hexbin(x=x, y=y, C=values, reduce_C_function=func)
        else:
            image = plt.hexbin(x=x, y=y, C=values)

    values = image.get_array()

    verts = image.get_offsets()
    for offc in range(verts.shape[0]):
        binx, biny = verts[offc][0], verts[offc][1]
        val = values[offc]
        if val:
            hexagonized_list.append({x_name: binx, y_name: biny, val_name: val})

    fig.clear()
    plt.close(fig)
    return pd.DataFrame(hexagonized_list)


with open(os.path.join(path_to_measurements, "measurements.json")) as f:

    config = json.load(f)
    measurements = config["measurements"]
    for measurement in measurements:
        print("--------------------- PATH LOSS MODEL {} ---------------------".format(measurement))
        CENTER = config[measurement]["center"]
        output_fig_pgf = os.path.join(
            input_path, 'location_density_{}.{}'.format(measurement, OUTPUT_IMG_FORMAT))


        input_file_path = os.path.join(
            input_path, measurement, input_file_name)

        df = pd.read_pickle(input_file_path)
        df = util.onlyPackets(df)



        #plt.scatter(CENTER[0], CENTER[1])
        sns.jointplot(x=df['lat'], y=df['lon'], kind="kde",
                      n_levels=25, joint_kws={'shade_lowest': False})  # , gridsize=num_bins)
        
        #if OUTPUT_IMG_FORMAT == "png":
        #    plt.savefig(output_fig_pgf, format=OUTPUT_IMG_FORMAT, dpi=1200,
        #                bbox_inches='tight')
        #else:
        #    plt.savefig(output_fig_pgf, format=OUTPUT_IMG_FORMAT, bbox_inches='tight')


        #plt.show()

        cmap = sns.cubehelix_palette(dark=1, light=0, as_cmap=True)
        g = sns.jointplot(x=df['lon'], y=df['lat'], kind="hex", gridsize=25, cmap="viridis")  # , color="k") #, gridsize=num_bins) C=df['snr'],
        plt.show()

        function = [np.mean, np.std, np.median, np.amin, np.amax, partial(np.percentile, q=25), partial(np.percentile, q=75)]
        function_name = ['mean', 'std', 'median', 'min' , 'max', '25%', '75%']
        for_values = ['rss', 'snr']
        dataframes = []  # will hold all the df's

        for val in for_values:
            for func, func_name in zip(function, function_name):
                dataframes.append(hexagonify(x=df['lon'], y=df['lat'], values=df[val], x_name='lon', y_name='lat',func=func, val_name="{}_{}".format(val, func_name)))

        dataframes.append(hexagonify(x=df['lon'], y=df['lat'], x_name='lon', y_name='lat', val_name='num_obs'))

        values_per_hex = reduce(lambda left, right: pd.merge(left, right, on=['lon', 'lat'], how='inner'), dataframes)

        #print(values_per_hex[['snr_50%','snr_median']])
        output_file_path = os.path.join(output_path, measurement, output_file_name)
        values_per_hex.to_pickle(output_file_path)

        plt.show()

        # input("Press Enter to continue...")
