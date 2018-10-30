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
from matplotlib.ticker import ScalarFormatter, FormatStrFormatter
import numpy as np
import pandas as pd
from scipy import stats

import util as util

nice_fonts = {
    # Use LaTex to write all text
    # "text.usetex": True,
    "font.family": "serif",
    # Use 10pt font in plots, to match 10pt font in document
    "axes.labelsize": 10,
    "font.size": 10,
    # Make the legend/label fonts a little smaller
    "legend.fontsize": 8,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
}

mpl.rcParams.update(nice_fonts)


time_string_file = "2018_10_30"

currentDir = os.path.dirname(os.path.abspath(__file__))
input_path = os.path.abspath(os.path.join(
    currentDir, '..', 'result'))
input_file = "preprocessed_data_{}.pkl".format(time_string_file)
input_file_path = os.path.join(input_path, input_file)

output_fig = os.path.join(
    input_path, 'path_loss_model_{}.pdf'.format(time_string_file))

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

ax.scatter(df['distance'], df['pl_db'], color='0.50', marker='x')
ax.set_xlabel('Log distance (m)')
ax.set_ylabel('Path Loss (dB)')

x, y = zip(*sorted(zip(df['distance'], df['epl_log'])))
ax.plot(x,y, ls='dashed')
x, y = zip(*sorted(zip(df['distance'], df['epl_free_log'])))
ax.plot(x,y, ls='dashed')

#def format_func(value, tick_number):
#    return 10**(value/10)*d0

#ax.xaxis.set_major_formatter(plt.FuncFormatter(format_func))
# print(n)
# print(pl0)



#print(sigma)
#sns.scatterplot(x='distance_log', y='epl', data=df)
#plt.scatter(x=df.distance_log, y=df.epl)
#
#plt.plot([0, df['distance_log'].max()], [137+20, 137+20])
##plt.plot(x=for_map['distance_log'].values, y=y)
#plt.plot(x=for_map['distance_log'].values, y=y_free_space)
#plt.show()

plt.savefig(output_fig, format='pdf', bbox_inches='tight')
