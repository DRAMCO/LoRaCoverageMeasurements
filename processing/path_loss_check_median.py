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
import os
from math import sqrt

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.formula.api as smf
from matplotlib.ticker import FormatStrFormatter, ScalarFormatter
from statsmodels.sandbox.regression.predstd import wls_prediction_std
from scipy.stats import shapiro
from scipy.stats import normaltest
from scipy import stats

import util as util
import math

BIN_SIZE = 20 # in meter


currentDir = os.path.dirname(os.path.abspath(__file__))
path_to_measurements = os.path.abspath(os.path.join(
    currentDir, '..', 'data'))
input_path = os.path.abspath(os.path.join(
    currentDir, '..', 'result'))
input_file_name = "preprocessed_data.pkl"



with open(os.path.join(path_to_measurements, "measurements.json")) as f:

    config = json.load(f)
    measurements = config["measurements"]
    for measurement in measurements:
        print("--------------------- PATH LOSS MODEL {} ---------------------".format(measurement))
        CENTER = config[measurement]["center"]

        input_file_path = os.path.join(
            input_path, measurement, input_file_name)

        df = pd.read_pickle(input_file_path)
        df = util.onlyPackets(df)

        #numl_observations = df.shape[0]

        num_bins = math.ceil((df.distance.max() - df.distance.min())/BIN_SIZE)

        df['distance_bins'], bins = pd.cut(x=df.distance, bins=num_bins, retbins=True)
        print(bins.size)
        


        summary_df = df.groupby('distance_bins')['rss'].describe().reset_index()
        summary_df['bins'] = pd.Series(bins[:-1])
        print(summary_df)

        ax = sns.lineplot(x="bins", y="50%", data=summary_df, label=measurement)
        std = summary_df['std']
        ax.fill_between(summary_df['bins'], y1=summary_df['50%'] - std, y2=summary_df['50%']+std, alpha=0.2)

plt.legend()
plt.show()
        #input("Press Enter to continue...")
