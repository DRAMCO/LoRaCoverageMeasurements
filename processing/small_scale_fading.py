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
# mpl.use('pgf')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.formula.api as smf
from matplotlib.ticker import FormatStrFormatter, ScalarFormatter
from statsmodels.sandbox.regression.predstd import wls_prediction_std
from scipy.stats import shapiro
from scipy.stats import normaltest
from scipy.stats import norm, rayleigh, rice
from scipy import stats as st
import distributions as dist
import math as math

import util as util

SPINE_COLOR = 'gray'
FORMAT = "png"
MARKER = "+"
NUM_BINS_m = 50


currentDir = os.path.dirname(os.path.abspath(__file__))
path_to_measurements = os.path.abspath(os.path.join(
    currentDir, '..', 'data'))
input_path = os.path.abspath(os.path.join(
    currentDir, '..', 'result'))
input_file_name = "preprocessed_data.pkl"


def dist_per_bin(gb):
    best_fit_dist = []
    for name, group in gb:
        data = group['esp']

        if(len(data) > 1):

            # Plot for comparison
            ax = sns.distplot(data)

            # Find best fit distribution
            best_fit_name, best_fit_params, best_sse = dist.best_fit_distribution(
                data, 200, ax, distributions=[st.rayleigh, st.rice, st.norm, st.nakagami])
            best_dist = getattr(st, best_fit_name)

            # Update plots
            ax.set_title(u'All Fitted Distributions')
            ax.set_xlabel(u'RSS')
            ax.set_ylabel('Frequency')

            # Make PDF with best params
            pdf = dist.make_pdf(best_dist, best_fit_params)

            # Display
            plt.figure(figsize=(12, 8))
            ax = pdf.plot(lw=2, label='PDF', legend=True)
            data.plot(kind='hist', bins=50, normed=True,
                      alpha=0.5, label='Data', legend=True, ax=ax)

            param_names = (best_dist.shapes +
                           ', loc, scale').split(', ') if best_dist.shapes else ['loc', 'scale']
            param_str = ', '.join(['{}={:0.2f}'.format(k, v)
                                   for k, v in zip(param_names, best_fit_params)])
            dist_str = '{}({})'.format(best_fit_name, param_str)

            best_fit_dist.append((name.right, best_fit_name, best_sse))
            ax.set_title(u'best fit distribution \n' + dist_str)
            ax.set_xlabel(u'RSS')
            ax.set_ylabel('Frequency')
            # plt.show()
        plt.close('all')
        df = pd.DataFrame(best_fit_dist, columns=[
                          'interval', 'best_fit', 'sse'])
        sns.scatterplot(x="interval", y="sse", data=df, hue="best_fit")
    plt.show()


def dist_all_bin(gb):
    # TODO
    pass


with open(os.path.join(path_to_measurements, "measurements.json")) as f:
    config = json.load(f)
    measurements = config["measurements"]
    for measurement in measurements:
        print(
            "--------------------- RSS MODEL {} ---------------------".format(measurement))

        CENTER = config[measurement]["center"]

        input_file_path = os.path.join(
            input_path, measurement, input_file_name)

        df = pd.read_pickle(input_file_path)
        df = util.onlyPackets(df)

        fig = plt.figure(figsize=(4, 3))
        ax = fig.add_subplot(1, 1, 1)

        output_fig_pgf = os.path.join(
            input_path, 'small_scale_fading_{}.{}'.format(measurement, FORMAT))
        num_bins = math.floor((df['distance'].max()-df['distance'].min())/NUM_BINS_m)
        
        df['distance_bins'], bins = pd.cut(
            x=df.distance, bins=num_bins, retbins=True)

        gb = df.groupby('distance_bins')
        dist_per_bin(gb)
