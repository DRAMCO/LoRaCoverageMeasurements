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
mpl.use('pgf')
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

SPINE_COLOR = 'gray'
FORMAT = "pdf"
MARKER = "+"
spreading_factors = ["SF7", "SF9", "SF12"]



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
        "pgf.texsystem": "lualatex",
        'figure.figsize': [fig_width, fig_height],
        'font.family': 'serif',
        "pgf.preamble": [
            r"\usepackage[utf8x]{inputenc}",    # use utf8 fonts
            r"\usepackage[T1]{fontenc}",        # plots will be generated
            r"\usepackage[detect-all]{siunitx}", # to use si units,
            r"\DeclareSIUnit{\belmilliwatt}{Bm}",
            r"\DeclareSIUnit{\dBm}{\deci\belmilliwatt}"
        ]
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





currentDir = os.path.dirname(os.path.abspath(__file__))
path_to_measurements = os.path.abspath(os.path.join(
    currentDir, '..', 'data'))
input_path = os.path.abspath(os.path.join(
    currentDir, '..', 'result'))
input_file_name = "preprocessed_data.pkl"


palette = dict(zip(spreading_factors, sns.color_palette()))

first = True

with open(os.path.join(path_to_measurements, "measurements.json")) as f:
    config = json.load(f)
    measurements = config["measurements"]
    for measurement in measurements:
        print("--------------------- RSS MODEL {} ---------------------".format(measurement))
        
        CENTER = config[measurement]["center"]

        input_file_path = os.path.join(
            input_path, measurement, input_file_name)

        df = pd.read_pickle(input_file_path)
        df = util.onlyPackets(df)

        latexify()
        fig = plt.figure(figsize=(4, 3))
        ax = fig.add_subplot(1, 1, 1)
        format_axes(ax)

        output_fig_pgf = os.path.join(
            input_path, 'snr_distance_{}.{}'.format(measurement, FORMAT))

        df['sf'] = "SF" + df['sf'].astype(int).astype(str)
        sns.scatterplot(x='distance', y='snr', hue='sf',
                        data=df, ci=None, palette=palette, color=".1", marker=MARKER, alpha=0.3)

        max_distance = df.distance.max()

        # RSS limit SF7
        x_range = [0, max_distance]

        # SNR limit SF7
        plt.plot(x_range, [-7.5, -7.5], '-', lw=1, color="white")
        plt.plot(x_range, [-7.5, -7.5], '--', lw=1)
        

        # SNR limit SF9
        plt.plot(x_range, [-12.5, -12.5], '-', lw=1, color="white")
        plt.plot(x_range, [-12.5, -12.5], '--', lw=1)
        

        # SNR limit SF12
        plt.plot(x_range, [-20, -20], '-', lw=1, color="white")
        plt.plot(x_range, [-20, -20], '--', lw=1)
        
        
        
        ax.set_xlabel(r'Distance (\si{\meter})')
        ax.set_ylabel(r'Signal-to-noise ratio (\si{\deci\bel})')

        if(first):
            # PLOT legend
            handles, labels = ax.get_legend_handles_labels()
            order = []
            for sf in spreading_factors:
                order.append(labels.index(sf))

            lgd = plt.legend([handles[idx] for idx in order],
                       spreading_factors, frameon=False)
            for l in lgd.get_lines():
                l.set_alpha(1)
                l.set_marker(MARKER)
        else:
            ax.get_legend().remove()

        plt.savefig(output_fig_pgf, format=FORMAT, bbox_inches='tight')

        print(
            "--------------------- SNR MODEL {} ---------------------".format(measurement))

        #latexify()
        fig = plt.figure(figsize=(4, 3))
        ax = fig.add_subplot(1, 1, 1)
        format_axes(ax)

        output_fig_pgf = os.path.join(
            input_path, 'rss_distance_{}.{}'.format(measurement, FORMAT))

        sns.scatterplot(x='distance', y='rss', hue='sf',
                        data=df, ci=None, palette=palette, color=".1", marker=MARKER, alpha=0.3)

        plt.plot(x_range, [-123, -123], '-', lw=1, color="white")
        plt.plot(x_range, [-123, -123], '--', lw=1)

        # RSS limit SF9
        plt.plot(x_range, [-129, -129], '-', lw=1, color="white")
        plt.plot(x_range, [-129, -129], '--', lw=1)

        # RSS limit SF12
        plt.plot(x_range, [-136, -136], '-', lw=1, color="white")
        plt.plot(x_range, [-136, -136], '--', lw=1)


        ax.set_xlabel(r'Distance (\si{\meter})')
        ax.set_ylabel(r'Received Signal Strength (\si{\dBm})')

        if(first):
            # PLOT legend
            handles, labels = ax.get_legend_handles_labels()
            order = []
            for sf in spreading_factors:
                order.append(labels.index(sf))

            lgd = plt.legend([handles[idx] for idx in order],
                       spreading_factors, frameon=False)
            for l in lgd.get_lines():
                l.set_alpha(1)
                l.set_marker(MARKER)
            first = False
        else:
            ax.get_legend().remove()
        

        plt.savefig(output_fig_pgf, format=FORMAT, bbox_inches='tight')
