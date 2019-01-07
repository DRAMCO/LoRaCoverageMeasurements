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

SPINE_COLOR = 'gray'


def latexify(fig_width=None, fig_height=None, columns=1):
    """Set up matplotlib's RC params for LaTeX plotting.
    Call this before plotting a figure.

    Parameters
    ----------
    fig_width : float, optional, inches
    fig_height : float,  optional, inches
    columns : {1, 2}
    """

    # code adapted from http://www.scipy.org/Cookbook/Matplotlib/LaTeX_Examples

    # Width and max height in inches for IEEE journals taken from
    # computer.org/cms/Computer.org/Journal%20templates/transactions_art_guide.pdf

    assert(columns in [1, 2])

    if fig_width is None:
        fig_width = 2.7 if columns == 1 else 6.9  # width in inches

    if fig_height is None:
        golden_mean = (sqrt(5)-1.0)/2.0    # Aesthetic ratio
        fig_height = fig_width*golden_mean  # height in inches

    MAX_HEIGHT_INCHES = 8.0
    if fig_height > MAX_HEIGHT_INCHES:
        print("WARNING: fig_height too large:" + fig_height +
              "so will reduce to" + MAX_HEIGHT_INCHES + "inches.")
        fig_height = MAX_HEIGHT_INCHES

    params = {
        'backend': 'ps',
        'axes.labelsize': 8,
        'axes.titlesize': 8,
        'legend.fontsize': 8,
        'xtick.labelsize': 8,
        'ytick.labelsize': 8,
        'text.usetex': True,
        "pgf.rcfonts": False,
        "pgf.texsystem": "pdflatex",
        'figure.figsize': [fig_width, fig_height],
        'font.family': 'serif'
    }

    mpl.rcParams.update(params)


def format_axes(ax):

    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)

    for spine in ['left', 'bottom']:
        ax.spines[spine].set_color(SPINE_COLOR)
        ax.spines[spine].set_linewidth(0.5)

    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    for axis in [ax.xaxis, ax.yaxis]:
        axis.set_tick_params(direction='out', color=SPINE_COLOR)

    return ax


def plot_normality(df):
    alpha = 0.05
    bin_size = 2
    start = df["distance"].min()
    end = df["distance"].max()
    bin_pointer = start - 1

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    while bin_pointer + bin_size < end:
        bin_pointer = bin_pointer + 1
        data_to_check = df[(df["distance"] < bin_pointer +
                            bin_size) & (df["distance"] >= bin_pointer)]
        if(data_to_check.shape[0] > 5):
            stat, p = shapiro(data_to_check.pl_db)
            # if(data_to_check.shape[0] > 20 ):
            #     ax.scatter(bin_pointer, p, color='k')
            # else:
            ax.scatter(bin_pointer, p, color='red',
                       alpha=data_to_check.shape[0]/20 if data_to_check.shape[0]/20 < 1 else 1)
            # if p > alpha:
            #     print('T1: Statistics=%.3f, p=%.3f' % (stat, p))
            #     print("distance [{},{}]".format(lower_bin, higher_bin))
            # stat, p = normaltest(data_to_check.pl_db)
            # if p > alpha:
            #     print('T2: Statistics=%.3f, p=%.3f' % (stat, p))
            #     print("distance [{},{}]".format(lower_bin, higher_bin))

    plt.plot([start, end], [alpha, alpha],
             color='k', linestyle='-', linewidth=2)
    plt.show()

#latexify()


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
        output_fig_pgf = os.path.join(
            input_path, 'path_loss_{}.{}'.format(measurement, 'pgf'))
        CENTER = config[measurement]["center"]
        #d0 = config[measurement]["d0"]
        #pl0 = config[measurement]["pl0"]

        input_file_path = os.path.join(
            input_path, measurement, input_file_name)

        df = pd.read_pickle(input_file_path)
        df = util.onlyPackets(df)

        d0 = 1

        df = df[df.distance > d0]
        df['distance_log'] = 10*np.log10(df.distance/d0)

        results = []
        distances = range(10, int(df.distance.max()))
        for max_distance in distances:
            data = df[df['distance_log'] < 10*np.log10(max_distance/d0)]
            results.append(
                smf.ols('pl_db ~ distance_log', data=data).fit().params[1])
            
        plt.plot(distances, results)
        plt.show()

       
