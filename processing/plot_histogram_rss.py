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

import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import ScalarFormatter, FormatStrFormatter
import numpy as np
import pandas as pd
from scipy import stats
import seaborn as sns

from math import sqrt
SPINE_COLOR = 'gray'

import util as util


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
        # 'backend': 'ps',

        'axes.labelsize': 8,
        'axes.titlesize': 8,
        'legend.fontsize': 8,  # was 10
        'xtick.labelsize': 8,
        'ytick.labelsize': 8,
        # 'text.usetex': True,
        # "pgf.rcfonts": False,
        # "pgf.texsystem": "pdflatex",
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


latexify()


currentDir = os.path.dirname(os.path.abspath(__file__))
input_path = os.path.abspath(os.path.join(
    currentDir, '..', 'result'))
input_file = "preprocessed_data.pkl"
input_file_path = os.path.join(input_path, input_file)

# output_fig_pdf = os.path.join(
#     input_path, 'path_loss_model.pdf'.format(time_string_file))
# output_fig_pgf = os.path.join(
#     input_path, 'path_loss_model.pgf'.format(time_string_file))

df = pd.read_pickle(input_file_path)
df = util.onlyPackets(df)

sns.distplot(df.rss, kde=False, rug=True);

plt.show();

