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

BIN_SIZE_DISTANCE = 0.001 # in degrees
OUTPUT_IMG_FORMAT = "png"


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
        output_fig_pgf = os.path.join(
            input_path, 'location_density_{}.{}'.format(measurement, OUTPUT_IMG_FORMAT))


        input_file_path = os.path.join(
            input_path, measurement, input_file_name)

        df = pd.read_pickle(input_file_path)
        df = util.onlyPackets(df)

        print(df.columns)
        print(df.lat)
        #plt.scatter(CENTER[0], CENTER[1])
        sns.jointplot(x=df['lat'], y=df['lon'], kind="kde",
                      n_levels=25, joint_kws={'shade_lowest': False})  # , gridsize=num_bins)
        
        if OUTPUT_IMG_FORMAT == "png":
            plt.savefig(output_fig_pgf, format=OUTPUT_IMG_FORMAT, dpi=1200,
                        bbox_inches='tight')
        else:
            plt.savefig(output_fig_pgf, format=OUTPUT_IMG_FORMAT, bbox_inches='tight')


        #plt.show()


        #input("Press Enter to continue...")
