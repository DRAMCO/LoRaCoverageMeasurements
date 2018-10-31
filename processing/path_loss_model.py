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
        Version: 1.0
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

    assert(columns in [1,2])

    if fig_width is None:
        fig_width = 3.39 if columns==1 else 6.9 # width in inches

    if fig_height is None:
        golden_mean = (sqrt(5)-1.0)/2.0    # Aesthetic ratio
        fig_height = fig_width*golden_mean # height in inches

    MAX_HEIGHT_INCHES = 8.0
    if fig_height > MAX_HEIGHT_INCHES:
        print("WARNING: fig_height too large:" + fig_height + 
              "so will reduce to" + MAX_HEIGHT_INCHES + "inches.")
        fig_height = MAX_HEIGHT_INCHES

    params = {
            'backend': 'ps',
             # 'text.latex.preamble': ['\usepackage{gensymb}'],
              'axes.labelsize': 8, # fontsize for x and y labels (was 10)
              'axes.titlesize': 8,
              #'text.fontsize': 8, # was 10
              'legend.fontsize': 8, # was 10
              'xtick.labelsize': 8,
              'ytick.labelsize': 8,
             # 'text.usetex': True,
              'figure.figsize': [fig_width,fig_height],
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
#nice_fonts = {
#    # Use LaTex to write all text
#    # "text.usetex": True,
#    "font.family": "serif",
#    # Use 10pt font in plots, to match 10pt font in document
#    "axes.labelsize": 10,
#    "font.size": 10,
#    # Make the legend/label fonts a little smaller
#    "legend.fontsize": 8,
#    "xtick.labelsize": 8,
#    "ytick.labelsize": 8,
#    #"pgf.rcfonts" : False TODO
#}
#
#mpl.rcParams.update(nice_fonts)


time_string_file = "2018_10_30"

currentDir = os.path.dirname(os.path.abspath(__file__))
input_path = os.path.abspath(os.path.join(
    currentDir, '..', 'result'))
input_file = "preprocessed_data_{}.pkl".format(time_string_file)
input_file_path = os.path.join(input_path, input_file)

output_fig = os.path.join(
    input_path, 'path_loss_model_{}'.format(time_string_file))

df = pd.read_pickle(input_file_path)
df = util.onlyPackets(df)

#for_map.plot.scatter(x='distance', y='pl_db', c='sf',  colormap='viridis')
# plt.show()
#
d0 = 20  # old data
#
df = df[df.distance > d0]
df['distance_log'] = 10*np.log10(df.distance/20)

#sns.lmplot(x='distance_log', y='pl_db', data=df)


slope, intercept, r_value, p_value, std_err = stats.linregress(
    df['distance_log'], df['pl_db'])
pl0 = intercept
n = slope

df['epl'] = n*df['distance_log']+pl0
df['epl_free'] = 2*df['distance_log']+pl0
sigma = np.std(df['epl'] - df['pl_db'])

df['epl_log'] = 10*n*np.log10(df['distance'])+(-10*n*np.log10(d0) + pl0)
df['epl_free_log'] = 10*2*np.log10(df['distance'])+(-10*2*np.log10(d0) + pl0)


fig = plt.figure(figsize=(4, 3))
ax = fig.add_subplot(1, 1, 1)
plt.xscale('log')
ax.xaxis.set_major_formatter(ScalarFormatter())
ax.xaxis.set_minor_formatter(FormatStrFormatter("%.1f"))
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

ax.scatter(df['distance'], df['pl_db'], color='0.50', marker='x',label="Measured Path Loss")
ax.set_xlabel('Log distance (m)')
ax.set_ylabel('Path Loss (dB)')

x, y = zip(*sorted(zip(df['distance'], df['epl_log'])))
ax.plot(x,y, ls='-', label="Expected Path Loss", linewidth=2, color='k')
x, y = zip(*sorted(zip(df['distance'], df['epl_free_log'])))
ax.plot(x,y, ls='dashed', label="Free Space Path Loss", linewidth=2, color='k')
plt.legend()

#def format_func(value, tick_number):
#    return 10**(value/10)*d0

#ax.xaxis.set_major_formatter(plt.FuncFormatter(format_func))
# print(n)
# print(pl0)



#print(sigma)
#sns.scatterplot(x='distance_log', y='epl', data=df)
#plt.scatter(x=df.distance_log, y=df.epl)
#
#plt.plot([0, df['distance'].max()], [136+20, 136+20])
#plt.plot([0, df['distance'].max()], [120+20, 120+20])
#plt.plot([0, df['distance'].max()], [125+20, 125+20])
format_axes(ax)
plt.tight_layout()
plt.show()

#plt.savefig(output_fig, format='pdf', bbox_inches='tight')
#plt.savefig(output_fig, format='pgf', bbox_inches='tight')


fig = plt.figure(figsize=(4, 3))
ax = fig.add_subplot(1, 1, 1)
ax.scatter(df['distance'], df['snr'], color='0.50', marker='x')
plt.show()